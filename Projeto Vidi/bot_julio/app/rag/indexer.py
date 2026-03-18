import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)


class DocumentIndexer:
    def __init__(self):
        # Google Embeddings para testes (gemini), OpenAI em produção
        if config.GOOGLE_API_KEY:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=config.EMBEDDING_MODEL,  # models/text-embedding-004
                google_api_key=config.GOOGLE_API_KEY
            )
        else:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=config.OPENAI_API_KEY
            )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )

    async def _insert_chunk(self, content: str, embedding: list[float], source: str, theme: str, totem_tag: str):
        # Apaga dimensão fixa — aceita qualquer tamanho de vetor
        formatted_embedding = f"[{','.join(str(f) for f in embedding)}]"
        query = """
            INSERT INTO knowledge_chunks (content, embedding, source_document, theme, totem_tag)
            VALUES ($1, $2::vector, $3, $4, $5)
        """
        await db.execute(query, content, formatted_embedding, source, theme, totem_tag)

    async def index_text(self, text: str, source: str, theme: str, totem_tag: str):
        logger.info(f"Indexando: {source} | Tema: {theme}")
        chunks = self.text_splitter.split_text(text)
        vectors = self.embeddings.embed_documents(chunks)

        for chunk, vector in zip(chunks, vectors):
            await self._insert_chunk(chunk, vector, source, theme, totem_tag)

        logger.info(f"✅ {len(chunks)} chunks indexados de '{source}'.")
