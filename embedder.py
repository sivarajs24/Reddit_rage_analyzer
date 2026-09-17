import os
import json
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.clean_text import clean_reddit_text

# Define embedding model and persist directory
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "chroma_db"

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
    """Generates embeddings and stores them in ChromaDB."""
    if not documents:
        print("No documents to embed.")
        return None

    # Text Chunking
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunked_documents = text_splitter.split_documents(documents)
    print(f"Created {len(chunked_documents)} chunks from {len(documents)} original documents.")

    print(f"Generating embeddings using {EMBEDDING_MODEL_NAME}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    print(f"Creating Chroma vector store at {PERSIST_DIRECTORY} (Collection: {collection_name})...")
    
    # Clear existing collection to avoid duplicating data on re-runs
    try:
        client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}' to prevent duplicates.")
    except Exception:
        # Collection might not exist yet, which is fine
        pass
        
    # Using Chroma.from_documents initializes the DB and adds documents
    vectorstore = Chroma.from_documents(
        documents=chunked_documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=collection_name
    )
    
    # In newer Chroma versions, persist() is called automatically, but we can call it to be safe
    vectorstore.persist()
    print("Embeddings successfully stored in ChromaDB.")
    
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
