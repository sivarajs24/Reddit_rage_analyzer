import streamlit as st


def apply_glassmorphism():
    """Injects the premium visual system used by the dashboard."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

        :root {
            --page-bg: #020617;
            --page-bg-2: #0f172a;
            --glass-bg: rgba(15, 23, 42, 0.68);
            --glass-border: rgba(148, 163, 184, 0.18);
            --glass-shadow: 0 24px 80px rgba(2, 6, 23, 0.42);
            --accent: #38bdf8;
            --accent-strong: #0ea5e9;
            --accent-soft: rgba(56, 189, 248, 0.16);
            --text-main: #e2e8f0;
            --text-soft: #94a3b8;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(99, 102, 241, 0.16), transparent 28%),
                linear-gradient(180deg, #020617 0%, #081120 55%, #020617 100%);
            color: var(--text-main);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        #MainMenu,
        footer,
        header {
            visibility: hidden;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', 'Inter', sans-serif;
            letter-spacing: -0.03em;
            color: var(--text-main);
        }

        p, li, label, span, div {
            color: var(--text-main);
        }

        .hero-shell {
            text-align: center;
            margin-bottom: 1.25rem;
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
            border: 1px solid rgba(56, 189, 248, 0.24);
            background: rgba(15, 23, 42, 0.55);
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: clamp(2.6rem, 5vw, 4.9rem);
            line-height: 0.96;
            margin: 0;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 35%, #38bdf8 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .hero-copy {
            max-width: 760px;
            margin: 0 auto 1.5rem auto;
            color: var(--text-soft);
            font-size: 1.03rem;
            line-height: 1.7;
        }

        .soft-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.8rem;
            margin: 0.25rem 0.35rem 0 0;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.16);
            color: var(--text-soft);
            font-size: 0.84rem;
        }

        [data-testid="stForm"] {
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 28px;
            padding: 1.15rem 1.15rem 0.9rem 1.15rem;
            box-shadow: var(--glass-shadow);
            backdrop-filter: blur(16px);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            box-shadow: var(--glass-shadow);
            backdrop-filter: blur(18px);
        }

        [data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 20px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 16px 40px rgba(2, 6, 23, 0.26);
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-soft) !important;
            font-size: 0.85rem;
        }

        [data-testid="stMetricValue"] {
            color: var(--text-main) !important;
            font-family: 'Outfit', sans-serif;
        }

        [data-baseweb="input"] {
            background: rgba(2, 6, 23, 0.42) !important;
            border-radius: 16px !important;
        }

        input, textarea {
            background: rgba(2, 6, 23, 0.42) !important;
            color: var(--text-main) !important;
            border-color: rgba(148, 163, 184, 0.2) !important;
        }

        input:focus, textarea:focus {
            border-color: rgba(56, 189, 248, 0.55) !important;
            box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.4) !important;
        }

        button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
            color: #020617 !important;
            border: 0 !important;
            border-radius: 999px !important;
            font-weight: 700 !important;
            box-shadow: 0 18px 40px rgba(14, 165, 233, 0.32) !important;
        }

        button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 22px 44px rgba(14, 165, 233, 0.42) !important;
        }

        button[kind="secondary"] {
            background: rgba(15, 23, 42, 0.85) !important;
            color: var(--text-main) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 999px !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.6rem;
            background: rgba(15, 23, 42, 0.42);
            padding: 0.35rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.14);
        }

        button[data-baseweb="tab"] {
            border-radius: 999px !important;
            color: var(--text-soft) !important;
            background: transparent !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: rgba(56, 189, 248, 0.18) !important;
            color: var(--text-main) !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid rgba(148, 163, 184, 0.14) !important;
            border-radius: 18px !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatMessage"] {
            background: rgba(15, 23, 42, 0.56);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 20px;
            padding: 0.25rem 0.25rem 0.25rem 0.25rem;
        }

        div[data-testid="stDownloadButton"] button {
            width: 100%;
        }

        hr {
            border-color: rgba(148, 163, 184, 0.16);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
