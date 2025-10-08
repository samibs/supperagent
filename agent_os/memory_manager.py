import logging
from . import config_loader

log = logging.getLogger('AgentOS.MemoryManager')

# --- Conditional Initialization ---
# These variables will only be populated if the memory system is enabled.
embedding_model = None
chromadb = None

class MemoryManager:
    """Manages the long-term memory of the AgentOS platform using a vector DB."""

    def __init__(self):
        """Initializes the MemoryManager and conditionally loads dependencies."""
        self.client = None
        self.collection = None
        self._initialize_if_enabled()

    def _initialize_if_enabled(self):
        """
        Checks the config and only loads the heavy libraries (Chroma, SentenceTransformer)
        if the memory feature is explicitly enabled.
        """
        global embedding_model, chromadb
        try:
            config = config_loader.load_config()
            if not config.get('memory', {}).get('enabled', False):
                log.warning("Long-term memory is disabled in the configuration. MemoryManager will not be active.")
                return

            log.info("Long-term memory is enabled. Initializing ChromaDB and embedding model...")

            # Conditionally import heavy libraries
            from sentence_transformers import SentenceTransformer
            import chromadb as cdb

            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            chromadb = cdb

            # Initialize ChromaDB client
            path = "./chroma_db"
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection(
                name="agent_os_memory",
                metadata={"hnsw:space": "cosine"}
            )
            log.info("MemoryManager initialized successfully.")

        except ImportError as e:
            log.error(f"Failed to import memory libraries. Please run 'pip install chromadb sentence-transformers'. Details: {e}")
        except Exception as e:
            log.error(f"Failed to initialize MemoryManager: {e}", exc_info=True)

    def is_enabled(self) -> bool:
        """Returns True if the memory system is configured and enabled."""
        return self.collection is not None

    def add_memory(self, text_to_remember: str, metadata: dict, doc_id: str):
        """Adds a new memory to the vector database if enabled."""
        if not self.is_enabled(): return

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
        """Queries the vector database for memories if enabled."""
        if not self.is_enabled(): return {}

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