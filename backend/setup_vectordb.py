"""
ONE-TIME SETUP SCRIPT
Run this once to create your vector database from NELFUND documents
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("="*80)
    print("CHECKING PREREQUISITES")
    print("="*80 + "\n")
    
    errors = []
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        errors.append("❌ OPENAI_API_KEY not found in .env file")
    else:
        print(f"✓ OpenAI API key found: {api_key[:10]}...")
    
    # Check for data directory
    if not os.path.exists("./data"):
        errors.append("❌ ./data directory not found")
    else:
        print("✓ Data directory exists")
        
        # Check for PDF files
        pdf_files = list(Path("./data").glob("**/*.pdf"))
        if not pdf_files:
            errors.append("❌ No PDF files found in ./data directory")
        else:
            print(f"✓ Found {len(pdf_files)} PDF file(s):")
            for pdf in pdf_files[:5]:  # Show first 5
                print(f"    • {pdf.name}")
            if len(pdf_files) > 5:
                print(f"    ... and {len(pdf_files) - 5} more")
    
    # Check for required packages
    try:
        import langchain
        import langchain_openai
        import chromadb
        print("✓ Required packages installed")
    except ImportError as e:
        errors.append(f"❌ Missing package: {e.name}")
    
    print()
    
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
        print("\nPlease fix the errors above and run this script again.")
        return False
    
    print("✓ All prerequisites met!")
    return True


def setup_vector_database():
    """Main setup function"""
    from document_processor import NELFUNDDocumentProcessor
    from vector_store import NELFUNDVectorStore
    
    print("\n" + "="*80)
    print("NELFUND VECTOR DATABASE SETUP")
    print("="*80 + "\n")
    
    # Step 1: Load documents
    print("STEP 1: Loading NELFUND Documents")
    print("-" * 80)
    processor = NELFUNDDocumentProcessor(data_directory="./data")
    
    try:
        documents = processor.load_documents()
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return False
    
    # Step 2: Chunk documents
    print("\nSTEP 2: Chunking Documents")
    print("-" * 80)
    chunks = processor.chunk_documents(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # Show statistics
    stats = processor.get_document_stats()
    print(f"\n📊 Document Statistics:")
    print(f"   Total Pages: {stats['total_documents']}")
    print(f"   Total Chunks: {stats['total_chunks']}")
    print(f"   Total Characters: {stats['total_characters']:,}")
    print(f"   Avg Document Length: {stats['avg_doc_length']:,} characters")
    
    # Preview sample chunk
    if chunks:
        print("\n📄 Sample Chunk Preview:")
        print("-" * 80)
        sample = chunks[0]
        print(f"Source: {sample.metadata.get('source', 'unknown')}")
        print(f"Page: {sample.metadata.get('page', 'unknown')}")
        print(f"Length: {len(sample.page_content)} chars")
        print(f"\nContent:\n{sample.page_content[:300]}...")
        print("-" * 80)
    
    # Step 3: Create vector store
    print("\nSTEP 3: Creating Vector Database")
    print("-" * 80)
    print("This will embed all chunks using OpenAI...")
    print("(This may take 1-2 minutes depending on document size)\n")
    
    vector_store = NELFUNDVectorStore(
        persist_directory="./chroma_db",
        collection_name="nelfund_docs"
    )
    
    try:
        # Check if vector store already exists
        if os.path.exists("./chroma_db"):
            print("⚠️  Vector database already exists!")
            response = input("Do you want to recreate it? (y/n): ").lower()
            force_recreate = response == 'y'
        else:
            force_recreate = True
        
        vector_store.create_vectorstore(chunks, force_recreate=force_recreate)
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return False
    
    # Step 4: Test the vector store
    print("\nSTEP 4: Testing Vector Database")
    print("-" * 80)
    
    test_queries = [
        "Am I eligible for NELFUND?",
        "What documents are required?",
        "How do I apply?"
    ]
    
    print("Running test searches...\n")
    
    for query in test_queries:
        print(f"🔍 Test: '{query}'")
        results = vector_store.similarity_search(query, k=2)
        print(f"   ✓ Found {len(results)} relevant chunks")
        if results:
            print(f"   Top result: {results[0].page_content[:100]}...")
        print()
    
    return True


def main():
    """Main entry point"""
    print("\n" + "🎓" * 40)
    print("NELFUND NAVIGATOR - VECTOR DATABASE SETUP")
    print("🎓" * 40 + "\n")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Setup failed. Please fix the errors above.")
        sys.exit(1)
    
    # Confirm with user
    print("\n" + "="*80)
    print("Ready to create vector database!")
    print("="*80)
    print("\nThis will:")
    print("   1. Load all PDF documents from ./data")
    print("   2. Split them into optimized chunks")
    print("   3. Create embeddings using OpenAI")
    print("   4. Save to ./chroma_db directory")
    print("\nNote: This will use OpenAI API credits (approximately $0.01-0.10)")
    print()
    
    response = input("Continue? (y/n): ").lower()
    if response != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    
    # Run setup
    success = setup_vector_database()
    
    # Final message
    print("\n" + "="*80)
    if success:
        print("✅ SETUP COMPLETE!")
        print("="*80)
        print("\nYour vector database is ready!")
        print(f"   Location: ./chroma_db")
        print(f"   Collection: nelfund_docs")
        print("\nNext steps:")
        print("   1. Test the RAG engine: python rag_engine.py")
        print("   2. Start the API server: uvicorn main:app --reload")
        print("   3. Launch the frontend: cd ../frontend && npm run dev")
        print("\n🚀 Your NELFUND Navigator is ready to help students!")
    else:
        print("❌ SETUP FAILED")
        print("="*80)
        print("\nPlease check the errors above and try again.")
    
    print("\n")


if __name__ == "__main__":
    main()