import os
import warnings

warnings.filterwarnings("ignore")
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from groq import Groq

from utils.styling import apply_y2k_theme
from scraper import scrape_reddit
from embedder import process_product
from rag_pipeline import retrieve_complaints
from analyzer import analyze_complaints

st.set_page_config(page_title="Reddit Rage Analyzer", page_icon="👾", layout="wide")


def initialize_state():
    defaults = {
        "analysis_result": None,
        "retrieved_docs": [],
        "product_name": "",
        "search_product": "",
        "search_subreddits": "",
        "chat_messages": [],
        "chat_product": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_word_cloud(keywords):
    """Generates and displays a word cloud from keywords."""
    if not keywords:
        return
    text = " ".join(keywords)
    wordcloud = WordCloud(
        width=800,
        height=500,
        background_color="white",
        mode="RGB",
        colormap="spring",
        prefer_horizontal=0.92,
        contour_width=3,
        contour_color="#000000",
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    st.pyplot(fig)

def create_download_link(data_dict, product_name):
    """Generates a downloadable CSV report."""
    df = pd.DataFrame([data_dict])
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"{product_name}_rage_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )


def reset_chat_for_product(product_name):
    if st.session_state.chat_product != product_name:
        st.session_state.chat_product = product_name
        st.session_state.chat_messages = []

def handle_chat(product_name, retrieved_docs):
    reset_chat_for_product(product_name)
    st.markdown(f"### 💬 AI Terminal")
    st.caption(f"Querying `{product_name}` complaints.")
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask a follow-up question..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        context = ""
        # Dynamically retrieve new documents based on the chat query
        with st.spinner("Searching database..."):
            new_docs = retrieve_complaints(prompt, product_name, k=10)
            
        for i, doc in enumerate(new_docs):
            context += f"--- Document {i+1} ---\n{doc.page_content}\n\n"
            
        system_prompt = f"You are a helpful AI assistant answering questions about {product_name} complaints. Base your answers strictly on the context provided below.\n\nContext:\n{context}"
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model='openai/gpt-oss-120b',
                    temperature=0.2,
                )
                response = chat_completion.choices[0].message.content
                message_placeholder.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error querying Groq: {e}")


def render_hero_intro():
    st.markdown('<div class="hero-shell">', unsafe_allow_html=True)
    st.markdown('<div class="hero-kicker">Complaint intelligence</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">See what Reddit really hates</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-copy">Drop in a product name, optionally narrow the subreddit scope, and the app will scrape Reddit, retrieve the loudest complaints, and turn them into a polished executive dashboard.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    chips = [
        "Live Reddit scraping",
        "Semantic retrieval",
        "AI summary and deep dive",
        "Tabbed executive dashboard",
    ]
    st.markdown("<div style='text-align:center;'>" + "".join([f"<span class='soft-chip'>{chip}</span>" for chip in chips]) + "</div>", unsafe_allow_html=True)


def render_search_form(compact=False):
    form_key = "analysis_form_compact" if compact else "analysis_form"
    with st.form(form_key):
        if compact:
            left, middle, right = st.columns([2.2, 2, 1])
            with left:
                product_query = st.text_input(
                    "Product",
                    key="search_product",
                    placeholder="e.g. Instagram, ChatGPT",
                    label_visibility="collapsed",
                )
            with middle:
                custom_subs_input = st.text_input(
                    "Custom subreddits",
                    key="search_subreddits",
                    placeholder="Optional: technology",
                    label_visibility="collapsed",
                )
            with right:
                submitted = st.form_submit_button("Analyze", use_container_width=True)
        else:
            render_hero_intro()
            left, center, right = st.columns([1, 2.6, 1])
            with center:
                product_query = st.text_input(
                    "Product name",
                    key="search_product",
                    placeholder="e.g. Instagram, ChatGPT, OnePlus",
                )
                custom_subs_input = st.text_input(
                    "Custom subreddits (optional)",
                    key="search_subreddits",
                    placeholder="e.g. technology, apps, UXDesign",
                )
                submitted = st.form_submit_button("Analyze Reddit Complaints", use_container_width=True)
        return submitted, product_query, custom_subs_input


def run_analysis(product_name, custom_subs):
    with st.spinner(f"Scraping Reddit for '{product_name}'..."):
        raw_data = scrape_reddit(product_name, limit_per_sub=50, custom_subreddits=custom_subs)
        if not raw_data:
            raise RuntimeError("No data found or scraping failed.")

    with st.spinner("Processing text and updating the vector database..."):
        success = process_product(raw_data, product_name)
        if not success:
            raise RuntimeError("Failed to process embeddings.")

    with st.spinner("Retrieving semantic complaints via RAG..."):
        retrieved_docs = retrieve_complaints("major issues bugs hate worst features", product_name, k=15)
        if not retrieved_docs:
            raise RuntimeError("RAG retrieval failed.")

    with st.spinner("Generating AI analysis using LLaMA 3.3..."):
        analysis_result = analyze_complaints(product_name, retrieved_docs)
        if "error" in analysis_result:
            raise RuntimeError(f"Analysis failed: {analysis_result['error']}")

    return retrieved_docs, analysis_result


def render_metric_column_vertical(analysis_result, retrieved_docs):
    st.metric("Overall Sentiment", analysis_result.get("overall_sentiment", "N/A"))
    st.metric("Emotional Intensity", analysis_result.get("emotional_intensity", "N/A"))
    st.metric("Complaints Reviewed", len(retrieved_docs))


def display_pie_chart(analysis_result):
    sentiment = str(analysis_result.get("overall_sentiment", "Neutral")).lower()
    if "very negative" in sentiment:
        vals = [82, 13, 5]
    elif "negative" in sentiment:
        vals = [64, 26, 10]
    elif "positive" in sentiment:
        vals = [22, 33, 45]
    else:
        vals = [40, 40, 20]

    fig = px.pie(
        names=["Negative", "Neutral", "Positive"],
        values=vals,
        color_discrete_sequence=["#ff00ff", "#cccccc", "#00ff00"],
        hole=0.35,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#000000"),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5),
    )
    fig.update_traces(textinfo="percent+label", textfont_color="#000000", marker=dict(line=dict(color='#000000', width=2)))
    st.plotly_chart(fig, use_container_width=True)

def render_deep_dive(analysis_result):
    with st.container(border=True):
        st.markdown("### Deep Dive Analysis")
        left, middle, right = st.columns(3)
        sections = [
            (left, "Most Hated Features", analysis_result.get("most_hated_features", [])),
            (middle, "Common Bug Patterns", analysis_result.get("common_bug_patterns", [])),
            (right, "Recurring Complaints", analysis_result.get("key_recurring_complaints", [])),
        ]
        for column, title, items in sections:
            with column:
                st.subheader(title)
                if items:
                    for item in items:
                        st.markdown(f"- {item}")
                else:
                    st.info("No items returned.")

def main():
    apply_y2k_theme()
    initialize_state()
    
    from dotenv import load_dotenv
    load_dotenv()
    missing_keys = []
    if not os.getenv("GROQ_API_KEY"):
        missing_keys.append("GROQ_API_KEY")
    if not os.getenv("PINECONE_API_KEY"):
        missing_keys.append("PINECONE_API_KEY")
    if not os.getenv("PINECONE_INDEX_NAME"):
        missing_keys.append("PINECONE_INDEX_NAME")
        
    if missing_keys:
        st.warning(f"⚠️ Warning: Missing API keys in `.env` file: {', '.join(missing_keys)}.")

    if st.session_state.analysis_result is None:
        submitted, product_query, custom_subs_input = render_search_form(compact=False)
        if not submitted:
            st.stop()
    else:
        submitted, product_query, custom_subs_input = render_search_form(compact=True)

    if submitted:
        product_name = (product_query or "").strip()
        if not product_name:
            st.error("Enter a product name before running the analysis.")
            st.stop()

        custom_subs = [s.strip() for s in (custom_subs_input or "").split(",") if s.strip()]

        st.session_state.product_name = product_name
        st.session_state.analysis_result = None
        st.session_state.retrieved_docs = []
        st.session_state.chat_messages = []
        st.session_state.chat_product = product_name

        try:
            retrieved_docs, analysis_result = run_analysis(product_name, custom_subs)
            st.session_state.retrieved_docs = retrieved_docs
            st.session_state.analysis_result = analysis_result
            st.success("Analysis complete.")
            st.rerun()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.stop()

    analysis_result = st.session_state.analysis_result
    product_name = st.session_state.product_name
    retrieved_docs = st.session_state.retrieved_docs

    if not analysis_result:
        st.stop()

    st.markdown(f"## 📊 {product_name} Dashboard")
    st.caption("Executive overview generated from Reddit complaints and AI analysis.")

    # TABS REMOVED. NEW WINDOW-BASED LAYOUT.
    
    # ROW 1: Controls/Metrics on left, Visualizer on right
    top_left, top_right = st.columns([1, 2.5])
    
    with top_left:
        with st.container(border=True):
            st.markdown("### Status Metrics")
            render_metric_column_vertical(analysis_result, retrieved_docs)
            st.markdown("### Export")
            create_download_link(analysis_result, product_name)
            
    with top_right:
        with st.container(border=True):
            st.markdown("### Executive Summary Visualizer")
            st.write(analysis_result.get("summary_paragraph", ""))
            
            viz_left, viz_right = st.columns([1.2, 1])
            with viz_left:
                st.subheader("Top Complaint Keywords")
                keywords = analysis_result.get("top_keywords", [])
                if keywords:
                    display_word_cloud(keywords)
                else:
                    st.info("No keywords were returned.")
            with viz_right:
                st.subheader("Sentiment Distribution")
                display_pie_chart(analysis_result)

    # ROW 2: Deep Dive (Full Width)
    render_deep_dive(analysis_result)

    # ROW 3: Raw Data Stream on left, AI Terminal on right
    bot_left, bot_right = st.columns(2)
    with bot_left:
        with st.container(border=True):
            st.markdown("### Raw Data Stream")
            if retrieved_docs:
                for i, doc in enumerate(retrieved_docs[:8]):
                    with st.expander(f"Complaint #{i + 1} | Upvotes: {doc.metadata.get('upvotes', 'N/A')}"):
                        st.write(doc.page_content)
                        st.caption(
                            f"Subreddit: r/{doc.metadata.get('subreddit', 'N/A')} | URL: {doc.metadata.get('url', 'N/A')}"
                        )
            else:
                st.info("No retrieved documents available.")

    with bot_right:
        with st.container(border=True):
            handle_chat(product_name, retrieved_docs)


if __name__ == "__main__":
    main()
