import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration must match embedder.py
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "chroma_db"

def get_retriever(product_name: str, k: int = 15):
    """
    Initializes and returns a LangChain retriever for the given product.
    
    Args:
        product_name (str): The product name to retrieve complaints for.
        k (int): Number of top results to return.
        
    Returns:
        VectorStoreRetriever: LangChain retriever object.
    """
    collection_name = f"reddit_{product_name.replace(' ', '_').lower()}"
    
    if not os.path.exists(PERSIST_DIRECTORY):
        print(f"Vector store directory {PERSIST_DIRECTORY} does not exist.")
        return None
        
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Load existing Chroma DB
    try:
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        # We use MMR (Maximal Marginal Relevance) to diversify results
        # and ensure we aren't just fetching the exact same complaint 15 times
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": k * 3  # Fetch more documents to then select diverse k
            }
        )
        return retriever
    except Exception as e:
        print(f"Error loading Chroma DB: {e}")
        return None

def retrieve_complaints(query: str, product_name: str, k: int = 15):
    """
    Retrieves the top-k relevant complaints for a given query and product.
    
    Args:
        query (str): The user's query (e.g., 'What are the main bugs in Instagram?').
        product_name (str): The target product.
        k (int): Number of chunks to retrieve.
        
    Returns:
        list[Document]: List of LangChain documents.
    """
    retriever = get_retriever(product_name, k)
    if not retriever:
        return []
        
    print(f"Retrieving top {k} complaints for query: '{query}'")
    docs = retriever.invoke(query)
    return docs

if __name__ == "__main__":
    # Test script
    docs = retrieve_complaints("bugs and glitches", "Instagram")
    for i, doc in enumerate(docs):
        print(f"\n--- Result {i+1} ---")
        print(f"Score/Upvotes: {doc.metadata.get('upvotes', 'N/A')}")
        print(f"Text: {doc.page_content[:200]}...")
