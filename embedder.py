import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.clean_text import clean_reddit_text

# Define embedding model and persist directory
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "chroma_db"

def load_and_clean_data(product_name: str) -> list[Document]:
    """Loads raw json data, cleans the text, and wraps into LangChain Documents."""
    file_path = f"data/raw_{product_name.replace(' ', '_').lower()}.json"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    cleaned_data_to_save = []

    for item in data:
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
            
            # Save cleaned version for later use if needed
            item["cleaned_text"] = cleaned_text
            cleaned_data_to_save.append(item)

    # Save cleaned data to disk
    cleaned_path = f"data/cleaned_{product_name.replace(' ', '_').lower()}.json"
    with open(cleaned_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data_to_save, f, indent=4)
        
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

def process_product(product_name: str):
    """End-to-end embedding pipeline for a product."""
    docs = load_and_clean_data(product_name)
    if docs:
        collection_name = f"reddit_{product_name.replace(' ', '_').lower()}"
        create_vector_store(docs, collection_name)
        return True
    return False

if __name__ == "__main__":
    # Test script
    process_product("Instagram")
