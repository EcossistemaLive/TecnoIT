import logging
import numpy as np
from app.db.postgres import db

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _split_text(text: str) -> list[str]:
    """Divide texto em chunks com overlap simples."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


class DocumentIndexer:
    async def _insert_chunk(
        self,
        content: str,
        embedding: list[float],
        source: str,
        theme: str,
        totem_tag: str | None,
        access_level: str,
    ):
        formatted_embedding = f"[{','.join(str(f) for f in embedding)}]"
        await db.execute(
            """
            INSERT INTO knowledge_chunks (content, embedding, source_document, theme, totem_tag, access_level)
            VALUES ($1, $2::vector, $3, $4, $5, $6)
            """,
            content,
            formatted_embedding,
            source,
            theme,
            totem_tag,
            access_level,
        )

    async def index_text(
        self,
        text: str,
        source: str,
        theme: str,
        totem_tag: str | None = None,
        access_level: str = "participant",
    ):
        """
        Indexa um texto na base RAG.

        Args:
            text: Conteúdo a indexar.
            source: Nome do documento de origem.
            theme: Categoria temática (ex: 'Governança', 'Sucessão', 'Procedimentos Internos').
            totem_tag: Zona do evento associada (opcional).
            access_level: Controle de acesso — 'public', 'participant', 'mentored' ou 'internal'.
                - 'public': visível para leads, participants, mentorados e staff
                - 'participant': visível para participants, mentorados com evento e staff
                - 'mentored': visível apenas para mentorados e staff
                - 'internal': visível apenas para staff
        """
        valid_levels = ("public", "participant", "mentored", "internal")
        if access_level not in valid_levels:
            raise ValueError(f"access_level inválido: '{access_level}'. Use um de: {valid_levels}")

        logger.info(f"Indexando: {source} | Tema: {theme} | Acesso: {access_level}")
        chunks = _split_text(text)
        # Mock embeddings (768-dim) — substituir por Gemini/Voyage quando PDFs reais chegarem
        vectors = [np.random.randn(768).tolist() for _ in chunks]

        for chunk, vector in zip(chunks, vectors):
            await self._insert_chunk(chunk, vector, source, theme, totem_tag, access_level)

        logger.info(f"[OK] {len(chunks)} chunks indexados de '{source}' (access_level={access_level}).")


indexer = DocumentIndexer()
