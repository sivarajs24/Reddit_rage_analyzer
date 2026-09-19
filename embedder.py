import os
import json
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.clean_text import clean_reddit_text

# Define embedding model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_and_clean_data(raw_data: list, product_name: str) -> list[Document]:
    """Cleans the raw text data and wraps into LangChain Documents."""
    documents = []

    for item in raw_data:
        # Combine title and body for the main text content, if available
        raw_text = f"{item.get('title', '')}. {item.get('body', '')}"
        
        # Clean text
        cleaned_text = clean_reddit_text(raw_text)
        
        # Only add if there is meaningful text left
        if len(cleaned_text.split()) > 3:
            metadata = {
                "id": item.get("id"),
                "type": item.get("type"),
                "upvotes": item.get("upvotes", 0),
                "subreddit": item.get("subreddit", ""),
                "timestamp": item.get("timestamp", 0),
                "url": item.get("url", ""),
                "product": product_name
            }
            
            # Create LangChain Document
            doc = Document(page_content=cleaned_text, metadata=metadata)
            documents.append(doc)
            
    print(f"Cleaned and prepared {len(documents)} documents.")
    return documents

def create_vector_store(documents: list[Document], collection_name: str):
    """Generates embeddings and stores them in Pinecone."""
    if not documents:
        print("No documents to embed.")
        return None

    # Text Chunking
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunked_documents = text_splitter.split_documents(documents)
    print(f"Created {len(chunked_documents)} chunks from {len(documents)} original documents.")

    print(f"Generating embeddings using {EMBEDDING_MODEL_NAME}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    if not index_name:
        raise ValueError("PINECONE_INDEX_NAME environment variable is missing.")

    print(f"Connecting to Pinecone index '{index_name}' (Namespace: {collection_name})...")
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    
    # Clear existing vectors in this namespace to avoid duplicating data on re-runs
    try:
        index.delete(delete_all=True, namespace=collection_name)
        print(f"Cleared existing vectors in namespace '{collection_name}'.")
    except Exception as e:
        print(f"Note on clearing namespace: {e}")
        
    # Generate deterministic IDs for chunks to prevent database bloat
    import hashlib
    doc_ids = []
    for chunk in chunked_documents:
        # Create a unique MD5 hash based on the chunk content and its source URL
        hash_input = f"{chunk.metadata.get('url', '')}_{chunk.page_content}"
        chunk_id = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        doc_ids.append(chunk_id)
        
    # Using PineconeVectorStore.from_documents initializes and adds documents
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunked_documents,
        embedding=embeddings,
        index_name=index_name,
        namespace=collection_name,
        ids=doc_ids
    )
    
    print("Embeddings successfully stored in Pinecone.")
    return vectorstore

def process_product(raw_data: list, product_name: str):
    """End-to-end embedding pipeline for a product."""
    docs = load_and_clean_data(raw_data, product_name)
    if docs:
        collection_name = f"reddit_{product_name.replace(' ', '_').lower()}"
        create_vector_store(docs, collection_name)
        return True
    return False

if __name__ == "__main__":
    # Test script
    process_product("Instagram")
