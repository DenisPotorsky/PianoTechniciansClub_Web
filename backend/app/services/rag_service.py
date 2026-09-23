class RAGService:
    def __init__(self):
        self._qdrant = None
        self._model = None
        self.collection_name = "cases"

    def _ensure_initialized(self):
        """Ленивая инициализация - загружает модели только при первом запросе"""
        if self._qdrant is None:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                self._qdrant = QdrantClient(host="qdrant", port=6333)

                collections = [c.name for c in self._qdrant.get_collections().collections]
                if self.collection_name not in collections:
                    self._qdrant.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
                    print(f"✅ Коллекция '{self.collection_name}' создана")
            except ImportError:
                raise RuntimeError("qdrant-client не установлен. Запустите: pip install qdrant-client sentence-transformers")

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise RuntimeError("sentence-transformers не установлен. Запустите: pip install sentence-transformers")
        return self._model

    def index_case(self, case_id: int, title: str, symptom: str, solution: str, tags: list[str]):
        self._ensure_initialized()
        import uuid
        text = f"{title} {symptom} {solution} {' '.join(tags)}"
        embedding = self._get_model().encode(text).tolist()

        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=case_id,
            vector=embedding,
            payload={"case_id": case_id, "title": title, "symptom": symptom[:200], "tags": tags}
        )
        self._qdrant.upsert(collection_name=self.collection_name, points=[point])

    def search(self, query: str, limit: int = 5) -> list[dict]:
        self._ensure_initialized()
        embedding = self._get_model().encode(query).tolist()

        results = self._qdrant.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=limit,
            score_threshold=0.3
        )

        return [
            {"case_id": r.payload["case_id"], "title": r.payload["title"],
             "symptom": r.payload["symptom"], "score": round(r.score, 3), "tags": r.payload.get("tags", [])}
            for r in results
        ]


rag_service = RAGService()
