import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid


class LongTermMemory:
    """
    Semantic memory using vector embeddings (ChromaDB).
    Stores summarized experiences and retrieves relevant ones.
    """

    def __init__(self, persist_path: str = "./memory_store"):
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_path,
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="agent_memory"
        )

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add_memory(self, text: str, metadata: dict):
        embedding = self.embedder.encode(text).tolist()

        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[text],
            metadatas=[metadata],
            embeddings=[embedding],
        )

        self.client.persist()

    def retrieve(self, query: str, k: int = 3) -> str:
        if self.collection.count() == 0:
            return ""

        embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
        )

        documents = results.get("documents", [[]])[0]
        return "\n".join(documents)

