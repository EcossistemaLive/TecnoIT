import logging
import numpy as np
from langchain_openai import OpenAIEmbeddings  # mantido para compatibilidade prod
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self):
        # Mock embeddings para testes (sem API externa)
        self.embeddings = None
        self.embedding_dim = 768

    async def search(self, query: str, limit: int = None, threshold: float = None, totem_tag: str = None) -> list[dict]:
        """Busca vetorial no pgvector (cosine similarity com embeddings mock)"""
        if limit is None:
            limit = config.MAX_RAG_CHUNKS
        if threshold is None:
            threshold = config.RAG_SIMILARITY_THRESHOLD

        # Gera um vetor mock pseudo-aleatório baseado no hash da query
        query_hash = hash(query.lower()) % 1000000
        np.random.seed(query_hash)
        query_vector = np.random.randn(768).tolist()
        formatted_vector = f"[{','.join(str(f) for f in query_vector)}]"

        sql = """
            SELECT id, content, source_document, theme, totem_tag,
                   1 - (embedding <=> $1::vector) as similarity
            FROM knowledge_chunks
        """
        params = [formatted_vector]

        if totem_tag:
            sql += " WHERE totem_tag = $2 AND 1 - (embedding <=> $1::vector) > $3"
            params.extend([totem_tag, threshold])
        else:
            sql += " WHERE 1 - (embedding <=> $1::vector) > $2"
            params.append(threshold)

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
                "totem_tag": r["totem_tag"]
            }
            for r in records
        ]

retriever = DocumentRetriever()
