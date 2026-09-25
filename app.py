import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Chat with your codebase", layout="centered")

st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden; }
    .stApp {
        background: #08080f;
        overflow: hidden;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 720px;
    }

    .blob {
        position: fixed;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.45;
        z-index: 0;
        animation: float 14s ease-in-out infinite;
    }
    .blob1 { width: 400px; height: 400px; background: #6366f1; top: -100px; left: -100px; animation-delay: 0s; }
    .blob2 { width: 350px; height: 350px; background: #a855f7; bottom: -100px; right: -80px; animation-delay: 4s; }
    .blob3 { width: 300px; height: 300px; background: #ec4899; top: 40%; left: 60%; animation-delay: 8s; }
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(40px, -30px) scale(1.1); }
        66% { transform: translate(-30px, 30px) scale(0.95); }
    }

    .glass-card {
        position: relative;
        z-index: 1;
        background: rgba(20, 20, 35, 0.55);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }

    .navbar {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(20, 20, 35, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 10px 18px;
        margin-bottom: 16px;
    }
    .navbar-title { font-weight: 700; color: #c4b5fd; font-size: 15px; }

    h1 {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
    }
    .subtitle { text-align: center; color: #9999b0; margin-bottom: 24px; }

    .stTextInput input {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stButton button {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px;
        font-weight: 600;
        font-size: 13px;
        transition: transform 0.15s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.4);
    }
    .stChatMessage {
        background-color: rgba(255,255,255,0.05);
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    div[data-testid="stExpander"] {
        background-color: rgba(255,255,255,0.04);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    div[data-testid="stPopover"] button {
        background: rgba(255,255,255,0.06) !important;
    }
</style>

<div class="blob blob1"></div>
<div class="blob blob2"></div>
<div class="blob blob3"></div>
""", unsafe_allow_html=True)

if "repo_loaded" not in st.session_state:
    st.session_state.repo_loaded = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

def reset_chat():
    st.session_state.repo_loaded = False
    st.session_state.messages = []
    st.session_state.question_history = []
    st.session_state.chunk_count = 0

def ask_question(question):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.question_history.append(question)
    response = requests.post(f"{API_URL}/chat", json={"question": question})
    result = response.json()
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })

if not st.session_state.repo_loaded:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h1>🤖 Chat with your codebase</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Paste a GitHub repo and ask questions in plain English</p>', unsafe_allow_html=True)

    github_url = st.text_input("GitHub URL", label_visibility="collapsed", placeholder="https://github.com/user/repo")

    if st.button("Load repo"):
        if github_url.strip():
            with st.spinner("Cloning and indexing... this may take a minute"):
                response = requests.post(f"{API_URL}/load", json={"github_url": github_url})
                result = response.json()
                st.session_state.repo_loaded = True
                st.session_state.chunk_count = result["chunks"]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ---- Top navbar ----
    nav_col1, nav_col2, nav_col3 = st.columns([3, 1, 1])
    with nav_col1:
        st.markdown(f'<div class="navbar"><span class="navbar-title">💬 {st.session_state.chunk_count} chunks indexed</span></div>', unsafe_allow_html=True)
    with nav_col2:
        with st.popover("🕘 History"):
            if not st.session_state.question_history:
                st.caption("No questions yet")
            else:
                for i, q in enumerate(reversed(st.session_state.question_history)):
                    if st.button(q, key=f"hist_{i}"):
                        st.session_state.pending_question = q
                        st.rerun()
    with nav_col3:
        if st.button("🔄 New chat"):
            reset_chat()
            st.rerun()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("View source code used"):
                    for c in msg["sources"]:
                        label = f"{c['class']}.{c['function']}" if c['class'] else c['function']
                        st.markdown(f"**{label}** — `{c['file']}` — similarity: `{c['score']:.2f}`")
                        st.code(c['code'], language="python")

    user_question = st.chat_input("Ask something about the code")

    # handle a question re-asked from history
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        with st.spinner("Searching and thinking..."):
            ask_question(q)
        st.rerun()

    if user_question:
        with st.spinner("Searching and thinking..."):
            ask_question(user_question)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)