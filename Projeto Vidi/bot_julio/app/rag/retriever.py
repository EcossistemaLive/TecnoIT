import logging
import numpy as np
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)

# Mapeamento user_type → níveis de acesso RAG permitidos
_ACCESS_LEVELS_BY_TYPE: dict[str, list[str]] = {
    "lead":        ["public"],
    "participant": ["public", "participant"],
    "mentored":    ["public", "mentored"],         # sem evento
    "staff":       ["public", "participant", "mentored", "internal"],
}


def _build_allowed_levels(user_type: str, has_event_access: bool) -> list[str]:
    """Retorna a lista de access_levels que este usuário pode ver."""
    levels = list(_ACCESS_LEVELS_BY_TYPE.get(user_type, ["public", "participant"]))
    # Mentorado com acesso ao evento também vê conteúdo de participant
    if user_type == "mentored" and has_event_access and "participant" not in levels:
        levels.append("participant")
    return levels


class DocumentRetriever:
    def __init__(self):
        # Mock embeddings para testes (sem API externa)
        self.embeddings = None
        self.embedding_dim = 768

    async def search(
        self,
        query: str,
        limit: int = None,
        threshold: float = None,
        totem_tag: str = None,
        user_type: str = "participant",
        has_event_access: bool = True,
    ) -> list[dict]:
        """Busca vetorial no pgvector filtrada por access_level e opcionalmente por totem_tag."""
        if limit is None:
            limit = config.MAX_RAG_CHUNKS
        if threshold is None:
            threshold = config.RAG_SIMILARITY_THRESHOLD

        allowed_levels = _build_allowed_levels(user_type, has_event_access)

        # Gera um vetor mock pseudo-aleatório baseado no hash da query
        query_hash = hash(query.lower()) % 1000000
        np.random.seed(query_hash)
        query_vector = np.random.randn(768).tolist()
        formatted_vector = f"[{','.join(str(f) for f in query_vector)}]"

        params = [formatted_vector, allowed_levels, threshold]

        sql = """
            SELECT id, content, source_document, theme, totem_tag, access_level,
                   1 - (embedding <=> $1::vector) as similarity
            FROM knowledge_chunks
            WHERE access_level = ANY($2::text[])
              AND 1 - (embedding <=> $1::vector) > $3
        """

        if totem_tag:
            sql += " AND totem_tag = $4"
            params.append(totem_tag)

        sql += " ORDER BY similarity DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)

        try:
            records = await db.fetch(sql, *params)
        except Exception as e:
            logger.warning(f"RAG search falhou (tabela vazia?): {e}")
            return []

        return [
            {
                "content": r["content"],
                "similarity": float(r["similarity"]) if r["similarity"] else 0.5,
                "theme": r["theme"],
                "totem_tag": r["totem_tag"],
                "access_level": r["access_level"],
            }
            for r in records
        ]


retriever = DocumentRetriever()
