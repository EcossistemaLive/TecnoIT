import logging
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings  # mantido para compatibilidade prod
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self):
        # Usa Google Embeddings no modo teste (Gemini), OpenAI no prod
        if config.GOOGLE_API_KEY:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                google_api_key=config.GOOGLE_API_KEY
            )
            self.embedding_dim = 768  # text-embedding-004 é 768d
        else:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=config.OPENAI_API_KEY
            )
            self.embedding_dim = 1536

    async def search(self, query: str, limit: int = None, threshold: float = None, totem_tag: str = None) -> list[dict]:
        """Busca vetorial no pgvector (cosine similarity)"""
        if limit is None:
            limit = config.MAX_RAG_CHUNKS
        if threshold is None:
            threshold = config.RAG_SIMILARITY_THRESHOLD

        query_vector = self.embeddings.embed_query(query)
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
                "similarity": r["similarity"],
                "theme": r["theme"],
                "totem_tag": r["totem_tag"]
            }
            for r in records
        ]

retriever = DocumentRetriever()
