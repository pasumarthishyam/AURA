import chromadb
import uuid


class LongTermMemory:
    """
    Semantic memory using vector embeddings (ChromaDB).
    Stores summarized experiences and retrieves relevant ones.
    """

    def __init__(self, persist_path: str = "./memory_store"):
        # New ChromaDB API: PersistentClient auto-persists
        self.client = chromadb.PersistentClient(path=persist_path)

        self.collection = self.client.get_or_create_collection(
            name="agent_memory"
        )

        # Use ChromaDB's built-in embedding function instead of sentence-transformers
        # to reduce dependencies
        self._use_simple_embeddings = True

    def add_memory(self, text: str, metadata: dict):
        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[text],
            metadatas=[metadata],
            # ChromaDB will auto-embed if we don't provide embeddings
        )
        # No need to call persist() - PersistentClient auto-saves

    def retrieve(self, query: str, k: int = 3) -> str:
        if self.collection.count() == 0:
            return ""

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
        )

        documents = results.get("documents", [[]])[0]
        return "\n".join(documents)
