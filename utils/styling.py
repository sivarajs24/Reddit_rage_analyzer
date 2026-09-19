import streamlit as st

def apply_y2k_theme():
    """Injects the Y2K / Retro Pixel Art visual system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=VT323&display=swap');

        :root {
            --bg-color: #d1d5db; /* Light grey retro OS background */
            --window-bg: #f3f4f6; /* White/grey window background */
            --border-color: #000000;
            --text-primary: #000000;
            --text-secondary: #333333;
            --hot-pink: #ff00ff;
            --neon-cyan: #00ffff;
            --lime-green: #00ff00;
            --box-shadow: 4px 4px 0px #000000;
        }

        html, body, [class*="css"] {
            font-family: 'Space Mono', monospace;
            background-color: var(--bg-color);
            color: var(--text-primary);
        }

        .stApp {
            background-color: var(--bg-color);
            background-image: 
                linear-gradient(45deg, #cbd5e1 25%, transparent 25%, transparent 75%, #cbd5e1 75%, #cbd5e1),
                linear-gradient(45deg, #cbd5e1 25%, transparent 25%, transparent 75%, #cbd5e1 75%, #cbd5e1);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'VT323', monospace;
            text-transform: uppercase;
            color: var(--text-primary);
            text-shadow: 2px 2px 0px var(--hot-pink);
            letter-spacing: 2px;
        }

        p, li, label, span, div {
            color: var(--text-primary);
        }

        /* Hero Section */
        .hero-shell {
            text-align: center;
            margin-bottom: 4rem;
            background: var(--window-bg);
            border: 3px solid var(--border-color);
            box-shadow: var(--box-shadow);
            padding: 3rem 2rem;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.2rem 0.8rem;
            background: var(--hot-pink);
            color: #fff;
            border: 2px solid var(--border-color);
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
            box-shadow: 2px 2px 0px #000;
        }

        .hero-title {
            font-size: clamp(3rem, 7vw, 6rem);
            line-height: 1;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            font-family: 'VT323', monospace;
            text-shadow: 4px 4px 0px var(--neon-cyan);
            letter-spacing: 2px;
        }

        .hero-copy {
            max-width: 680px;
            margin: 0 auto 2rem auto;
            color: var(--text-secondary);
            font-size: 1.1rem;
            line-height: 1.5;
            font-weight: 700;
        }

        .soft-chip {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            margin: 0.25rem;
            background: var(--lime-green);
            border: 2px solid var(--border-color);
            color: #000;
            font-size: 0.85rem;
            font-weight: 700;
            box-shadow: 2px 2px 0px #000;
        }

        /* Forms & Containers */
        [data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--window-bg) !important;
            border: 3px solid var(--border-color) !important;
            border-radius: 0px !important;
            padding: 2rem;
            box-shadow: var(--box-shadow) !important;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 3px solid var(--border-color);
            border-radius: 0px;
            padding: 1rem;
            box-shadow: var(--box-shadow);
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-primary) !important;
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.2rem;
            margin-bottom: 0.5rem;
        }

        [data-testid="stMetricValue"] {
            color: var(--hot-pink) !important;
            font-family: 'VT323', monospace;
            font-size: 3rem;
            text-shadow: 2px 2px 0px var(--neon-cyan);
        }

        /* Inputs */
        input, textarea, [data-baseweb="input"] {
            background: #ffffff !important;
            color: var(--text-primary) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 0px !important;
            font-family: 'Space Mono', monospace !important;
            font-weight: 700 !important;
        }

        input:focus, textarea:focus {
            outline: none !important;
            background: var(--neon-cyan) !important;
        }

        /* Buttons */
        button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: var(--hot-pink) !important;
            color: #ffffff !important;
            border: 3px solid var(--border-color) !important;
            border-radius: 0px !important;
            font-family: 'VT323', monospace !important;
            font-size: 1.5rem !important;
            padding: 0.2rem 1.5rem !important;
            box-shadow: var(--box-shadow) !important;
            transition: all 0.1s;
        }

        button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            transform: translate(2px, 2px);
            box-shadow: 2px 2px 0px #000000 !important;
            background: var(--neon-cyan) !important;
            color: #000 !important;
        }

        button[kind="secondary"] {
            background: #ffffff !important;
            color: var(--text-primary) !important;
            border: 3px solid var(--border-color) !important;
            border-radius: 0px !important;
            font-family: 'Space Mono', monospace !important;
            font-weight: 700 !important;
            box-shadow: var(--box-shadow) !important;
            transition: all 0.1s;
        }

        button[kind="secondary"]:hover {
            transform: translate(2px, 2px);
            box-shadow: 2px 2px 0px #000000 !important;
            background: var(--lime-green) !important;
        }

        /* Tabs */
        div[data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: transparent;
            border-bottom: 3px solid var(--border-color);
        }

        button[data-baseweb="tab"] {
            border: 3px solid var(--border-color) !important;
            border-bottom: 0 !important;
            border-radius: 0px !important;
            background: #cbd5e1 !important;
            color: #000 !important;
            font-family: 'VT323', monospace;
            font-size: 1.5rem !important;
            padding: 0.2rem 1rem !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: var(--window-bg) !important;
            margin-bottom: -3px !important;
            border-bottom: 3px solid var(--window-bg) !important;
        }

        /* Expanders & Chat */
        div[data-testid="stExpander"] {
            background: #ffffff !important;
            border: 3px solid var(--border-color) !important;
            border-radius: 0px !important;
            box-shadow: var(--box-shadow) !important;
            margin-bottom: 1rem !important;
        }

        div[data-testid="stChatMessage"] {
            background: #ffffff;
            border: 3px solid var(--border-color);
            border-radius: 0px;
            padding: 1rem;
            box-shadow: 3px 3px 0px #000;
        }

        div[data-testid="stDownloadButton"] button {
            width: 100%;
        }

        hr {
            border-color: var(--border-color);
            border-width: 3px;
            border-style: dashed;
            margin: 3rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
