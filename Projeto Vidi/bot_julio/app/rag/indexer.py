import logging
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)


class DocumentIndexer:
    def __init__(self):
        # Mock embeddings for testing (generates random vectors)
        self.embeddings = None

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )

    async def _insert_chunk(self, content: str, embedding: list[float], source: str, theme: str, totem_tag: str):
        # Format embedding as vector
        formatted_embedding = f"[{','.join(str(f) for f in embedding)}]"
        query = """
            INSERT INTO knowledge_chunks (content, embedding, source_document, theme, totem_tag)
            VALUES ($1, $2::vector, $3, $4, $5)
        """
        await db.execute(query, content, formatted_embedding, source, theme, totem_tag)

    async def index_text(self, text: str, source: str, theme: str, totem_tag: str):
        logger.info(f"Indexando: {source} | Tema: {theme}")
        chunks = self.text_splitter.split_text(text)
        # Generate mock embeddings (random 768-dim vectors for testing)
        vectors = [np.random.randn(768).tolist() for _ in chunks]

        for chunk, vector in zip(chunks, vectors):
            await self._insert_chunk(chunk, vector, source, theme, totem_tag)

        logger.info(f"[OK] {len(chunks)} chunks indexados de '{source}'.")
