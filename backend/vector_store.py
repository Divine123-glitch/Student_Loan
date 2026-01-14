"""
NELFUND Vector Database System
Creates and manages ChromaDB vector store for semantic search
"""

import os
import logging
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Environment Setup ---
os.environ["ANONYMIZED_TELEMETRY"] = "False"

try:
    from document_processor import NELFUNDDocumentProcessor
except ImportError:
    logger.warning("document_processor.py not found in current directory")


@dataclass
class VectorStoreConfig:
    """Configuration for vector store"""
    persist_directory: str = "./chroma_db"
    collection_name: str = "nelfund_docs"
    embedding_model: str = "text-embedding-3-large"
    request_timeout: float = 20.0
    chunk_size: int = 1000
    chunk_overlap: int = 200


class VectorStoreError(Exception):
    """Custom exception for vector store operations"""
    pass


class NELFUNDVectorStore:
    """
    Manages vector database for NELFUND document retrieval
    """
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """
        Initialize vector store with configuration
        
        Args:
            config: VectorStoreConfig instance (uses defaults if None)
            
        Raises:
            VectorStoreError: If API key is not configured
        """
        load_dotenv()
        
        self.config = config or VectorStoreConfig()
        self.vectorstore: Optional[Chroma] = None
        
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """Initialize OpenAI embeddings with error handling"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise VectorStoreError(
                "OPENAI_API_KEY not found. "
                "Create a .env file with: OPENAI_API_KEY=your-key-here"
            )
        
        try:
            self.embeddings = OpenAIEmbeddings(
                model=self.config.embedding_model,
                openai_api_key=api_key,
                request_timeout=self.config.request_timeout,
                max_retries=3,
                show_progress_bar=True
            )
            logger.info(f"✓ OpenAI embeddings initialized ({self.config.embedding_model})")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize embeddings: {e}")
    
    def create_vectorstore(
        self,
        documents: List[Document],
        force_recreate: bool = False
    ) -> Chroma:
        """
        Create or load vector store from documents
        
        Args:
            documents: List of langchain Documents
            force_recreate: If True, recreate database from scratch
            
        Returns:
            Chroma vectorstore instance
            
        Raises:
            VectorStoreError: If vector store creation fails
        """
        db_exists = os.path.exists(self.config.persist_directory)
        
        if db_exists and not force_recreate:
            logger.info(f"Loading existing vectorstore from {self.config.persist_directory}")
            return self._load_existing_store()
        
        if db_exists and force_recreate:
            logger.info("Recreating vectorstore (force_recreate=True)")
            self._clear_directory(self.config.persist_directory)
        
        return self._create_new_store(documents)
    
    def _load_existing_store(self) -> Chroma:
        """Load existing vectorstore from disk"""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.config.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.config.collection_name
            )
            logger.info("✓ Vector store loaded successfully")
            return self.vectorstore
        except Exception as e:
            raise VectorStoreError(f"Failed to load vectorstore: {e}")
    
    def _create_new_store(self, documents: List[Document]) -> Chroma:
        """Create new vectorstore from documents"""
        logger.info(f"Creating vectorstore with {len(documents)} chunks...")
        logger.info("⏳ Embedding documents (this may take 2-5 minutes)...")
        logger.info("📡 Starting batch embedding process...")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.config.persist_directory, exist_ok=True)
            
            # Test single embedding first
            logger.info("🧪 Testing single embedding...")
            test_vec = self.embeddings.embed_query("test")
            logger.info(f"✓ Single embedding works (vector size: {len(test_vec)})")
            
            # Now embed all documents
            logger.info(f"🔄 Embedding {len(documents)} documents in batch...")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.config.persist_directory,
                collection_name=self.config.collection_name
            )
            
            logger.info("✓ Embedding complete, persisting to disk...")
            
            # Handle both old and new Chroma versions
            try:
                self.vectorstore.persist()
                logger.info("✓ Vectorstore persisted to disk")
            except AttributeError:
                pass  # Newer Chroma versions auto-persist
            
            logger.info(f"✓ Vector store created at {self.config.persist_directory}")
            return self.vectorstore
        except Exception as e:
            logger.error(f"Vectorstore creation failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise VectorStoreError(f"Failed to create vectorstore: {e}")
    
    def _clear_directory(self, directory: str) -> None:
        """Safely clear directory contents"""
        try:
            import shutil
            if os.path.exists(directory):
                shutil.rmtree(directory)
                logger.info(f"Cleared {directory}")
        except Exception as e:
            logger.warning(f"Could not clear {directory}: {e}")
    
    def load_vectorstore(self) -> Chroma:
        """
        Load existing vector store from disk
        
        Returns:
            Chroma vectorstore instance
            
        Raises:
            VectorStoreError: If vectorstore doesn't exist or load fails
        """
        if not os.path.exists(self.config.persist_directory):
            raise VectorStoreError(
                f"Vector store not found at {self.config.persist_directory}. "
                "Create one first using create_vectorstore()"
            )
        
        return self._load_existing_store()
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for relevant documents using semantic similarity
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of relevant Documents
        """
        if not self.vectorstore:
            self.load_vectorstore()
        
        try:
            logger.info(f"Searching for: '{query}'")
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} relevant chunks")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search operation failed: {e}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4
    ) -> List[tuple]:
        """
        Search with relevance scores
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        if not self.vectorstore:
            self.load_vectorstore()
        
        try:
            return self.vectorstore.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.error(f"Scored search failed: {e}")
            raise VectorStoreError(f"Scored search failed: {e}")
    
    def get_retriever(self, k: int = 4):
        """
        Get a retriever object for use in RAG chains
        
        Args:
            k: Number of results to retrieve
            
        Returns:
            LangChain retriever object
        """
        if not self.vectorstore:
            self.load_vectorstore()
        
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def test_search(self, query: str, k: int = 3) -> None:
        """
        Test search and display formatted results
        
        Args:
            query: Test query string
            k: Number of results to display
        """
        print(f"\n{'='*80}")
        print(f"SEARCH: {query}")
        print(f"{'='*80}\n")
        
        try:
            results = self.similarity_search_with_score(query, k=k)
        except VectorStoreError as e:
            logger.error(f"Search error: {e}")
            return
        
        if not results:
            print("❌ No results found.\n")
            return
        
        for i, (doc, score) in enumerate(results, 1):
            self._print_result(i, doc, score)
    
    def _print_result(self, index: int, doc: Document, score: float) -> None:
        """Format and print a single search result"""
        print(f"Result {index} (Relevance: {score:.4f})")
        print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"  Page: {doc.metadata.get('page', 'Unknown')}")
        print(f"\n  Content:\n  {doc.page_content[:300]}...")
        print(f"\n{'-'*80}\n")


def setup_vector_store(
    data_directory: str = "./data",
    force_recreate: bool = False,
    config: Optional[VectorStoreConfig] = None
) -> NELFUNDVectorStore:
    """
    Setup complete vector store pipeline
    
    Args:
        data_directory: Path to PDF documents
        force_recreate: Force recreation of vectorstore
        config: Custom VectorStoreConfig
        
    Returns:
        Initialized NELFUNDVectorStore instance
        
    Raises:
        VectorStoreError: If setup fails
    """
    config = config or VectorStoreConfig()
    
    logger.info("="*80)
    logger.info("NELFUND VECTOR STORE SETUP")
    logger.info("="*80)
    
    # Load documents
    logger.info("\n[1/3] Loading documents...")
    try:
        processor = NELFUNDDocumentProcessor(data_directory=data_directory)
        documents = processor.load_documents()
        chunks = processor.chunk_documents(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        logger.info(f"✓ Loaded {len(chunks)} document chunks")
    except Exception as e:
        raise VectorStoreError(f"Document loading failed: {e}")
    
    # Create vectorstore
    logger.info("\n[2/3] Creating vector store...")
    try:
        vector_store = NELFUNDVectorStore(config)
        vector_store.create_vectorstore(chunks, force_recreate=force_recreate)
    except VectorStoreError as e:
        raise VectorStoreError(f"Vectorstore creation failed: {e}")
    
    return vector_store


def test_vector_store(vector_store: NELFUNDVectorStore) -> None:
    """
    Run test queries on vectorstore
    
    Args:
        vector_store: Initialized NELFUNDVectorStore instance
    """
    test_queries = [
        "Am I eligible for NELFUND student loan?",
        "How do I apply for student loan?",
        "What documents do I need?",
        "When do I start paying back the loan?"
    ]
    
    logger.info("\n[3/3] Testing search functionality...\n")
    
    for query in test_queries:
        try:
            vector_store.test_search(query, k=3)
        except VectorStoreError as e:
            logger.error(f"Test query failed: {e}")
    
    logger.info("="*80)
    logger.info("✓ VECTOR STORE SETUP COMPLETE!")
    logger.info("="*80)
    logger.info(f"Database location: {vector_store.config.persist_directory}")
    logger.info("Ready to build the Agentic RAG system!\n")


def main():
    """Main entry point"""
    try:
        vector_store = setup_vector_store(
            data_directory="./data",
            force_recreate=True  # Set to False to load existing DB
        )
        test_vector_store(vector_store)
    except VectorStoreError as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()