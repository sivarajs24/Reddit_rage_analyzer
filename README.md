# 🤬 Reddit Rage Analyzer - Comprehensive Project Documentation

## 1. Problem Statement
In today's highly competitive digital market, user feedback is gold. However, a significant portion of honest, unfiltered feedback is scattered across forums like Reddit, buried in unstructured text, complaint threads, and rants. Manually sifting through thousands of Reddit posts to identify common bugs, missing features, and overall sentiment for a specific product is incredibly time-consuming and prone to human bias. 

Companies and product managers need an automated, intelligent system that can instantly scrape this unstructured feedback, understand the context, and extract actionable insights—such as top bugs, hated features, and emotional intensity—without requiring manual review.

## 2. Complete Workflow
The project implements an end-to-end Retrieval-Augmented Generation (RAG) pipeline combined with data scraping and AI summarization. The workflow is divided into the following sequential steps:

### Phase 1: Data Acquisition (Scraping)
*   **User Input:** The user enters a product name (e.g., "Instagram", "Dell laptop") and optional target subreddits in the Streamlit UI.
*   **RSS Scraping:** The `scraper.py` script bypasses Reddit's strict API rate limits and 403 blocks by hitting Reddit's public RSS search feeds instead of the JSON API.
*   **Parsing & Deduplication:** It parses the XML responses, cleans the basic HTML out of the text, and deduplicates posts based on URLs. The raw data is saved locally as a JSON file in the `data/` directory.

### Phase 2: Data Processing & Embedding
*   **Text Cleaning:** The `embedder.py` script loads the scraped JSON data and cleans the text to remove noise.
*   **Chunking:** It uses LangChain's `RecursiveCharacterTextSplitter` to chunk the text into manageable pieces (1000 characters with 150-character overlap) to preserve context.
*   **Vectorization:** These chunks are transformed into high-dimensional vector embeddings using the `sentence-transformers/all-MiniLM-L6-v2` model from HuggingFace.
*   **Storage:** The embeddings and their corresponding metadata are stored in a local ChromaDB vector database.

### Phase 3: Semantic Retrieval (RAG)
*   **Querying:** When the system needs to analyze complaints, `rag_pipeline.py` creates a retriever connected to the ChromaDB.
*   **Relevance & Diversity:** It uses a hardcoded search query ("major issues bugs hate worst features") to semantically search the vector database for the most relevant negative feedback. It utilizes Maximal Marginal Relevance (MMR) to ensure that the retrieved complaints are both relevant to the query and diverse, preventing the AI from analyzing the exact same complaint multiple times.

### Phase 4: AI Analysis & Generation
*   **Prompt Construction:** The retrieved text chunks are compiled into a single context block and passed to `analyzer.py`.
*   **LLM Inference:** A prompt is constructed instructing an LLM (LLaMA 3.3 70B via Groq) to act as a product analyst.
*   **Structured Output:** The LLM reads the context and returns a strictly formatted JSON response (enforced via Pydantic) containing the most hated features, common bugs, sentiment, emotional intensity, a summary, and top keywords.

### Phase 5: Interactive Visualization (UI)
*   **Dashboard:** The frontend (`app.py`), built with Streamlit, takes the structured JSON response and renders an interactive "Executive Dashboard".
*   **Visuals:** It displays a word cloud, sentiment pie charts (via Plotly), metrics, and deep-dive lists of bugs.
*   **Conversational AI:** Additionally, it provides an interactive chat interface where users can ask follow-up questions to the LLM, which answers strictly based on the context of the scraped Reddit data.

## 3. Architecture
The system architecture follows a classic modular RAG design:

*   **Frontend Layer (`app.py`):** Streamlit application. Handles user inputs, triggers backend processes, and renders visual analytics (Plotly, WordCloud) and chat interfaces.
*   **Data Ingestion Layer (`scraper.py`):** An RSS-based scraper that extracts raw XML from Reddit, parses it, and stores it in the local filesystem (`data/` folder).
*   **Vector & Embedding Layer (`embedder.py`):** Utilizes LangChain to manage the transformation of text into vectors. Uses HuggingFace embeddings and interacts directly with the local vector store.
*   **Retrieval Layer (`rag_pipeline.py`):** Connects to ChromaDB and performs MMR-based semantic similarity searches.
*   **LLM / Inference Layer (`analyzer.py` & `app.py` chat):** Communicates with the Groq API to access the blazing-fast LLaMA 3.3 70B model for both structured data extraction (JSON) and conversational Q&A.

## 4. Tools Used & Why

1.  **Streamlit:** 
    *   *Why:* Used for the frontend interface. Streamlit allows for rapid prototyping and building data-driven web applications purely in Python. It natively supports data visualization libraries and makes creating chat interfaces easy.
2.  **LangChain:**
    *   *Why:* Acts as the orchestration framework for the RAG pipeline. It provides standardized wrappers for document loading, text splitting (`RecursiveCharacterTextSplitter`), and integrating with vector stores and embedding models.
3.  **HuggingFace Embeddings (`sentence-transformers/all-MiniLM-L6-v2`):**
    *   *Why:* Used to convert text into numerical vectors. This specific model is chosen because it is highly efficient, runs quickly on local hardware without requiring a GPU, and provides excellent semantic representations for general text.
4.  **Groq API & LLaMA 3.3 70B Versatile:**
    *   *Why:* Groq provides ultra-fast inference speeds through its LPU technology. LLaMA 3.3 70B is an incredibly capable open-weight model that excels at instruction following and strict JSON output generation. The speed is crucial for providing a responsive user experience. *(Note: The original app used Gemini, but has been migrated to Groq/LLaMA for speed and reliability in JSON generation)*.
5.  **Pydantic:**
    *   *Why:* Used in `analyzer.py` to define the `AnalysisResult` data schema. It ensures that the JSON generated by the LLM strictly adheres to the required format (e.g., lists of strings, specific sentiment categories), preventing frontend crashes.
6.  **Plotly, WordCloud & Matplotlib:**
    *   *Why:* Used for data visualization. Plotly provides interactive, aesthetically pleasing charts (like the sentiment donut chart), while WordCloud creates visual summaries of the most frequently used terms.
7.  **Python `xml.etree.ElementTree` & `requests` (Custom RSS Scraper):**
    *   *Why:* Reddit heavily restricted its official API and blocks automated JSON requests (403 Forbidden). By scraping the legacy RSS feeds, the application bypasses these restrictions to gather data reliably without needing OAuth tokens.

## 5. Database Used
The project utilizes **ChromaDB** (specifically, the local open-source version) as its primary vector database.

*   **Why ChromaDB:** 
    *   **Local Persistence:** It runs embedded within the Python application and saves its data to the local disk (`chroma_db/` directory). This eliminates the need to set up, host, or pay for a separate cloud database service.
    *   **LangChain Integration:** It has seamless out-of-the-box integration with LangChain.
    *   **Performance:** It is highly optimized for the relatively small-to-medium scale of data scraped per product, allowing for sub-second semantic searches.
*   **Data Stored:** ChromaDB stores the chunked text of the Reddit posts, the high-dimensional vector embeddings of those chunks, and associated metadata (such as the original URL, subreddit, and upvote count) so it can be referenced later in the UI.

## 6. Conclusion
The Reddit Rage Analyzer successfully bridges the gap between unstructured social media complaints and structured, actionable product intelligence. By combining a resilient RSS scraping technique with a state-of-the-art Retrieval-Augmented Generation pipeline, the application can distill thousands of angry comments into clear bug reports, feature requests, and sentiment metrics in seconds. The use of local vector storage (ChromaDB) and high-speed LLM inference (Groq + LLaMA 3.3) ensures that the architecture is both cost-effective and highly responsive. Ultimately, this tool empowers product teams to make data-driven decisions based on what their users truly care about, transforming public "rage" into constructive engineering tasks.
