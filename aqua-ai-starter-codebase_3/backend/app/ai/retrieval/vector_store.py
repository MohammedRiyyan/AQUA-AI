"""
Vector store abstraction over the hydration knowledge base.

Two backends are supported, selected via settings.VECTOR_BACKEND:
  - "faiss"  : embedded, file-backed index — zero extra infra, good for a
               single-node deployment or fully offline/on-prem setups.
  - "qdrant" : a proper vector DB service (see docker-compose.yml) — better
               for concurrent writes, filtering, and horizontal scale.

Both implement the same tiny interface (upsert / search / delete_by_document)
so the retriever and ingestion pipeline don't need to know which is active.
"""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from app.core.config import get_settings

settings = get_settings()


@dataclass
class VectorHit:
    vector_id: str
    score: float
    text: str
    document_id: str
    document_title: str
    chunk_index: int


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, ids: list[str], vectors: np.ndarray, metadata: list[dict]) -> None: ...

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> list[VectorHit]: ...

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None: ...


class FaissVectorStore(VectorStore):
    """Simple flat FAISS index with a JSONL sidecar file for metadata."""

    def __init__(self) -> None:
        import faiss  # local import: heavy dependency, only loaded when this backend is used

        self._faiss = faiss
        self.index_path = settings.FAISS_INDEX_PATH
        self.meta_path = settings.FAISS_METADATA_PATH
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        self.dim = 384  # matches all-MiniLM-L6-v2; update if you change EMBEDDING_MODEL
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(self.dim))

        self.metadata: dict[int, dict] = {}
        if os.path.exists(self.meta_path):
            with open(self.meta_path) as f:
                for line in f:
                    row = json.loads(line)
                    self.metadata[row["int_id"]] = row

    def _save(self) -> None:
        self._faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            for row in self.metadata.values():
                f.write(json.dumps(row) + "\n")

    def upsert(self, ids: list[str], vectors: np.ndarray, metadata: list[dict]) -> None:
        int_ids = np.array([abs(hash(i)) % (2**63 - 1) for i in ids], dtype="int64")
        self.index.add_with_ids(vectors.astype("float32"), int_ids)
        for int_id, vector_id, meta in zip(int_ids, ids, metadata, strict=True):
            self.metadata[int(int_id)] = {"int_id": int(int_id), "vector_id": vector_id, **meta}
        self._save()

    def search(self, query_vector: np.ndarray, top_k: int) -> list[VectorHit]:
        scores, ids = self.index.search(query_vector.reshape(1, -1).astype("float32"), top_k)
        hits = []
        for score, int_id in zip(scores[0], ids[0], strict=True):
            if int_id == -1:
                continue
            meta = self.metadata.get(int(int_id))
            if not meta:
                continue
            hits.append(
                VectorHit(
                    vector_id=meta["vector_id"],
                    score=float(score),
                    text=meta["text"],
                    document_id=meta["document_id"],
                    document_title=meta["document_title"],
                    chunk_index=meta["chunk_index"],
                )
            )
        return hits

    def delete_by_document(self, document_id: str) -> None:
        keep = {k: v for k, v in self.metadata.items() if v["document_id"] != document_id}
        removed_ids = [k for k in self.metadata if k not in keep]
        if removed_ids:
            self.index.remove_ids(np.array(removed_ids, dtype="int64"))
        self.metadata = keep
        self._save()


class QdrantVectorStore(VectorStore):
    """Thin wrapper around a Qdrant collection for production/service deployments."""

    def __init__(self) -> None:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection = settings.QDRANT_COLLECTION
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def upsert(self, ids: list[str], vectors: np.ndarray, metadata: list[dict]) -> None:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(id=vid, vector=vec.tolist(), payload=meta)
            for vid, vec, meta in zip(ids, vectors, metadata, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: np.ndarray, top_k: int) -> list[VectorHit]:
        results = self.client.search(collection_name=self.collection, query_vector=query_vector.tolist(), limit=top_k)
        return [
            VectorHit(
                vector_id=str(r.id),
                score=float(r.score),
                text=r.payload["text"],
                document_id=r.payload["document_id"],
                document_title=r.payload["document_title"],
                chunk_index=r.payload["chunk_index"],
            )
            for r in results
        ]

    def delete_by_document(self, document_id: str) -> None:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]),
        )


def get_vector_store() -> VectorStore:
    return QdrantVectorStore() if settings.VECTOR_BACKEND == "qdrant" else FaissVectorStore()
