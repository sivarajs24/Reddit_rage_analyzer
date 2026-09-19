# Reddit Rage Analyzer - Advanced RAG Edition

## 1. Problem Statement
In today's competitive digital market, user feedback is gold. However, a significant portion of honest, unfiltered feedback is scattered across Reddit—buried in unstructured text, complaint threads, and rants. Manually sifting through thousands of Reddit posts to identify common bugs, missing features, and overall sentiment for a specific product is incredibly time-consuming and prone to human bias. 

This project provides an automated, enterprise-grade AI system that instantly scrapes unstructured Reddit feedback, understands the context via a state-of-the-art Hybrid RAG pipeline, and extracts actionable insights (top bugs, hated features, emotional intensity) without requiring manual review.

## 2. Complete Workflow
The project implements a cutting-edge Retrieval-Augmented Generation (RAG) pipeline combined with headless browser scraping and asynchronous AI summarization.

### Phase 1: Data Acquisition (Apify Scraping)
*   **User Input:** The user enters a product name (e.g., "Instagram", "Dell laptop") in the Glassmorphism Web UI.
*   **Headless Scraping:** The `embedder.py` script utilizes the `Apify` API (`automation-lab/reddit-scraper`) to bypass Reddit's strict API rate limits and 403 blocks. It scrapes top posts and comments related to the product query.
*   **Deduplication:** Posts are deterministically hashed (MD5) based on URL and content to prevent database bloat before vectorization.

### Phase 2: Hybrid Data Processing & Embedding
*   **Chunking:** LangChain's `RecursiveCharacterTextSplitter` chunks the text into manageable pieces to preserve context.
*   **Dense Vectors:** Chunks are transformed into high-dimensional semantic vectors using the `sentence-transformers/all-MiniLM-L6-v2` HuggingFace model.
*   **Sparse Vectors (BM25):** The system dynamically trains a `BM25Encoder` (via `pinecone-text`) on the scraped corpus to generate exact-keyword sparse vectors, saving the model locally.
*   **Storage:** The Hybrid Embeddings (Dense + Sparse) are uploaded to a Serverless **Pinecone** vector database using the `dotproduct` metric.

### Phase 3: Advanced Semantic Retrieval (RAG Pipeline)
When analyzing complaints or answering chat questions, `rag_pipeline.py` executes a multi-stage retrieval process:
1.  **Multi-Query Expansion:** An LLM (`llama3-8b-8192` via Groq) takes the user's query and generates 3 alternative variations to ensure no edge-case complaints are missed.
2.  **Hybrid Search:** The system queries Pinecone using both semantic meaning (Dense) and exact keyword matches (Sparse) for all 3 generated queries, pulling a massive net of 100 relevant documents.
3.  **Cross-Encoder Re-Ranking:** A `CustomCrossEncoderReranker` runs the 100 documents through a heavy-duty `cross-encoder/ms-marco-MiniLM-L-6-v2` neural network to strictly re-score and filter them down to the true Top 40 most relevant documents.

### Phase 4: AI Analysis & Map-Reduce
*   **Map-Reduce Chain:** Because the Top 40 documents exceed standard LLM token limits, `analyzer.py` utilizes a Map-Reduce summarization chain to process the chunks in batches without crashing.
*   **Structured Output:** The Groq LLM (LLaMA 3.3 70B) reads the context and returns a strictly formatted JSON response containing the most hated features, common bugs, sentiment, emotional intensity, and a summary.

### Phase 5: Interactive Visualization (UI)
*   **Dashboard:** The frontend (`index.html`/`script.js`), built with Vanilla JS, CSS, and HTML, features a stunning, animated **Glassmorphism** dark-mode UI.
*   **Visuals:** It dynamically renders custom charts (using Chart.js), metrics, and deep-dive lists of bugs.
*   **Conversational AI:** Provides an interactive chat interface where users can ask follow-up questions to the LLM, strictly grounded in the scraped Reddit data context.

## 3. Architecture & Tech Stack

*   **Frontend:** HTML5, CSS3 (Glassmorphism, animations), Vanilla JavaScript, Chart.js.
*   **Backend:** FastAPI (Asynchronous, non-blocking I/O via Uvicorn).
*   **Data Ingestion:** Apify Client (`automation-lab/reddit-scraper`).
*   **Vector Database:** Pinecone (Serverless, dotproduct metric for Hybrid Search).
*   **Embedding Models:** HuggingFace `all-MiniLM-L6-v2` (Dense) & `pinecone-text` BM25 (Sparse).
*   **Reranking Model:** HuggingFace `cross-encoder/ms-marco-MiniLM-L-6-v2`.
*   **LLM / Inference:** Groq API (LLaMA 3-8B for routing/expansion, LLaMA 3.3 70B for analysis).
*   **Orchestration:** LangChain (MultiQueryRetriever, ContextualCompressionRetriever, Map-Reduce Chains).

## 4. Local Setup & Installation

### Prerequisites
1. Python 3.10+
2. API Keys for: **Groq**, **Pinecone**, and **Apify**.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/sivarajs24/Reddit_rage_analyzer.git
   cd Reddit_rage_analyzer
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX_NAME=your_index_name (MUST be created with 'dotproduct' metric)
   APIFY_API_TOKEN=your_apify_key
   ```
5. Run the Application:
   ```bash
   uvicorn api:app --reload
   ```
6. Open your browser and navigate to `http://127.0.0.1:8000`.
