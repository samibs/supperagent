import logging
import chromadb
from sentence_transformers import SentenceTransformer

log = logging.getLogger('AgentOS.MemoryManager')

# Use a specific, lightweight model for generating embeddings.
# This model is loaded once and reused, which is efficient.
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class MemoryManager:
    """
    Manages the long-term memory of the AgentOS platform using a vector DB.
    """
    def __init__(self, path: str = "./chroma_db"):
        """
        Initializes the MemoryManager and the ChromaDB client.

        Args:
            path (str): The directory where the vector database will be stored.
        """
        try:
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection(
                name="agent_os_memory",
                metadata={"hnsw:space": "cosine"} # Use cosine similarity
            )
            log.info("MemoryManager initialized with ChromaDB client.")
        except Exception as e:
            log.error(f"Failed to initialize ChromaDB: {e}", exc_info=True)
            self.client = None
            self.collection = None

    def add_memory(self, text_to_remember: str, metadata: dict, doc_id: str):
        """
        Adds a new memory to the vector database.

        The text is converted into an embedding and stored along with its
        metadata and a unique ID.

        Args:
            text_to_remember (str): The actual text content of the memory.
            metadata (dict): A dictionary of metadata (e.g., project_goal).
            doc_id (str): A unique identifier for this memory.
        """
        if not self.collection:
            log.error("Cannot add memory, collection is not available.")
            return

        try:
            log.info(f"Adding new memory with ID: {doc_id}")
            embedding = embedding_model.encode(text_to_remember).tolist()
            self.collection.add(
                embeddings=[embedding],
                documents=[text_to_remember],
                metadatas=[metadata],
                ids=[doc_id]
            )
            log.info("Successfully added memory to ChromaDB.")
        except Exception as e:
            log.error(f"Failed to add memory to ChromaDB: {e}", exc_info=True)

    def query_memory(self, query_text: str, n_results: int = 3) -> dict:
        """
        Queries the vector database for memories similar to the query text.

        Args:
            query_text (str): The text to search for.
            n_results (int): The maximum number of similar results to return.

        Returns:
            dict: A dictionary containing the query results from ChromaDB.
        """
        if not self.collection:
            log.error("Cannot query memory, collection is not available.")
            return {}

        try:
            log.info(f"Querying memory for: '{query_text[:50]}...'")
            query_embedding = embedding_model.encode(query_text).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            log.info(f"Found {len(results.get('ids', [[]])[0])} relevant memories.")
            return results
        except Exception as e:
            log.error(f"Failed to query memory from ChromaDB: {e}", exc_info=True)
            return {}

# Singleton instance to be used across the application
memory_manager = MemoryManager()