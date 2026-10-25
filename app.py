import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Codebase Chat — talk to any GitHub repo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global styles — shared design system for landing / auth / chat views
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden; }
    .stApp {
        background: #07070f;
        color: #e7e7f2;
    }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; }

    /* ---------- animated background blobs ---------- */
    .blob {
        position: fixed;
        border-radius: 50%;
        filter: blur(110px);
        opacity: 0.4;
        z-index: 0;
        pointer-events: none;
        animation: float 16s ease-in-out infinite;
    }
    .blob1 { width: 460px; height: 460px; background: #6366f1; top: -140px; left: -120px; }
    .blob2 { width: 400px; height: 400px; background: #a855f7; bottom: -140px; right: -100px; animation-delay: 5s; }
    .blob3 { width: 320px; height: 320px; background: #ec4899; top: 45%; left: 62%; animation-delay: 9s; }
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(40px, -30px) scale(1.1); }
        66% { transform: translate(-30px, 30px) scale(0.95); }
    }

    /* ---------- glass cards ---------- */
    .glass-card {
        position: relative;
        z-index: 1;
        background: rgba(18, 18, 32, 0.6);
        backdrop-filter: blur(22px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 34px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .soft-card {
        position: relative;
        z-index: 1;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }
    .soft-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.45);
        box-shadow: 0 12px 34px rgba(99, 102, 241, 0.18);
    }
    .soft-card h3 { margin: 6px 0 8px; font-size: 17px; color: #d6d6ea; }
    .soft-card p { color: #9a9ab5; font-size: 14px; line-height: 1.55; margin: 0; }
    .card-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 44px; height: 44px; border-radius: 12px; font-size: 20px;
        background: linear-gradient(135deg, rgba(99,102,241,.25), rgba(168,85,247,.25));
        border: 1px solid rgba(139,92,246,.35);
    }

    /* ---------- navbar ---------- */
    .navbar {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 18, 32, 0.65);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px 20px;
        margin-bottom: 18px;
    }
    .navbar-brand { font-weight: 800; font-size: 16px; letter-spacing: .2px; }
    .navbar-brand span {
        background: linear-gradient(90deg, #818cf8, #c084fc, #f0abfc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .navbar-meta { color: #8f8fae; font-size: 13px; }
    .navbar-user {
        color: #c4b5fd; font-weight: 600; font-size: 13px;
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(139, 92, 246, 0.35);
        padding: 4px 12px; border-radius: 999px;
    }

    /* ---------- hero / landing ---------- */
    .hero-badge {
        display: inline-block;
        font-size: 12px; font-weight: 600; letter-spacing: .6px;
        color: #a5b4fc;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 999px;
        padding: 5px 14px;
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 46px;
        font-weight: 900;
        line-height: 1.12;
        margin: 0 0 14px;
        background: linear-gradient(92deg, #a5b4fc 0%, #c084fc 55%, #f0abfc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { color: #a2a2bd; font-size: 17px; line-height: 1.6; margin: 0; max-width: 560px; }
    .section-label {
        text-transform: uppercase; letter-spacing: 2px;
        font-size: 11px; font-weight: 700; color: #7c7c9c; margin: 8px 0 14px;
    }
    .step-num {
        font-size: 13px; font-weight: 800; color: #0b0b14;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        width: 26px; height: 26px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        margin-bottom: 8px;
    }
    .footer-note { text-align: center; color: #5d5d78; font-size: 12px; margin-top: 26px; position: relative; z-index: 1; }

    h1 {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
    }
    .subtitle { text-align: center; color: #9999b0; margin-bottom: 24px; }

    /* ---------- form controls ---------- */
    .stTextInput input, .stPassword input {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 10px 14px !important;
        transition: border-color .15s ease, box-shadow .15s ease;
    }
    .stTextInput input:focus, .stPassword input:focus {
        border-color: rgba(139, 92, 246, 0.7) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.18) !important;
    }
    .stButton > button, .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 11px;
        font-weight: 700;
        font-size: 14px;
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.45);
        filter: brightness(1.06);
    }
    /* secondary buttons (inside popovers / small actions) */
    div[data-testid="stPopover"] button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }

    /* ---------- chat ---------- */
    .stChatMessage {
        background-color: rgba(255,255,255,0.05);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px 18px !important;
    }
    div[data-testid="stExpander"] {
        background-color: rgba(255,255,255,0.04);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.09);
    }
    div[data-testid="stChatInput"] {
        position: relative;
        z-index: 1;
    }
    div[data-testid="stChatInput"] textarea {
        background: rgba(18, 18, 32, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 14px !important;
        color: white !important;
    }
    pre, code {
        background: rgba(10, 10, 20, 0.85) !important;
        border-radius: 10px !important;
    }
    hr { border-color: rgba(255,255,255,0.08); }
    a { color: #a5b4fc; }
    .stAlert, div[data-testid="stAlert"] { border-radius: 12px; }
</style>

<div class="blob blob1"></div>
<div class="blob blob2"></div>
<div class="blob blob3"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
defaults = {
    "logged_in": False,
    "token": None,
    "username": None,
    "view": "landing",          # landing | login | register | app
    "repo_loaded": False,
    "messages": [],
    "question_history": [],
    "pending_question": None,
    "chunk_count": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def reset_chat():
    st.session_state.repo_loaded = False
    st.session_state.messages = []
    st.session_state.question_history = []
    st.session_state.chunk_count = 0


def logout():
    for key in ("logged_in", "token", "username"):
        st.session_state[key] = defaults[key]
    reset_chat()
    st.session_state.view = "landing"
    st.rerun()


def ask_question(question):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.question_history.append(question)
    response = requests.post(f"{API_URL}/chat", json={"question": question}, headers=api_headers())
    result = response.json()
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })


# ===========================================================================
# LANDING PAGE
# ===========================================================================
def render_landing():
    st.markdown(
        """
        <div style="position:relative; z-index:1; max-width: 980px; margin: 0 auto; padding-top: 26px;">
            <div style="text-align:center;">
                <span class="hero-badge">⚡ AI-powered codebase Q&amp;A</span>
                <h1 class="hero-title">Chat with any GitHub repo<br>in plain English</h1>
                <p class="hero-subtitle" style="margin-left:auto; margin-right:auto;">
                    Paste a repository URL and Codebase Chat clones it, indexes every function
                    with semantic search, and answers your questions with real source snippets
                    as citations. No cloning, no setup, no reading other people's code blind.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label" style="text-align:center; margin-top:34px;">Why Codebase Chat</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
            <div class="soft-card">
                <span class="card-icon">🧠</span>
                <h3>Semantic search</h3>
                <p>Ask about behaviour, not syntax. Find the code that <em>does</em> what you mean, even without exact keywords.</p>
            </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class="soft-card">
                <span class="card-icon">🔌</span>
                <h3>Instant indexing</h3>
                <p>Drop a GitHub URL — the repo is cloned, parsed and embedded into a vector store automatically.</p>
            </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class="soft-card">
                <span class="card-icon">📎</span>
                <h3>Cited answers</h3>
                <p>Every answer comes with the exact files, functions and similarity scores it was built from.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="text-align:center; margin-top:34px;">How it works</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    steps = [
        ("1", "Paste a repo URL", "Any public GitHub repository works — just drop the link on the next screen."),
        ("2", "We index the code", "Functions are extracted and embedded with a sentence-transformer model."),
        ("3", "Ask anything", "Get precise answers grounded in the repo's actual source, with citations."),
    ]
    for col, (num, title, body) in zip([s1, s2, s3], steps):
        with col:
            st.markdown(f"""
                <div class="soft-card" style="text-align:center;">
                    <span class="step-num">{num}</span>
                    <h3>{title}</h3>
                    <p>{body}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    a1, a2, a3 = st.columns([1, 1.2, 1])
    with a2:
        if st.button("🚀 Get started — it's free", key="cta_start"):
            st.session_state.view = "login"
            st.rerun()
    with a3:
        if st.button("Sign up", key="cta_signup"):
            st.session_state.view = "register"
            st.rerun()

    st.markdown(
        '<p class="footer-note">Built with FastAPI · Streamlit · Qdrant · Gemini</p>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# AUTH PAGES (login / register)
# ===========================================================================
def render_auth(mode: str):
    is_login = mode == "login"

    # back link
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("← Back", key="auth_back", use_container_width=True):
            st.session_state.view = "landing"
            st.rerun()

    with nav2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            f"<h1>🔐 {'Welcome back' if is_login else 'Create account'}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="subtitle">{"Sign in to continue chatting with your codebases" if is_login else "One step away from chatting with any repo"}</p>',
            unsafe_allow_html=True,
        )

        username = st.text_input("Username", key=f"{mode}_username", placeholder="yourname")
        password = st.text_input("Password", type="password", key=f"{mode}_password", placeholder="••••••••")

        if st.button("Sign in" if is_login else "Create account", key=f"{mode}_submit"):
            if not username.strip() or not password:
                st.error("Please fill in both fields.")
            else:
                try:
                    if is_login:
                        resp = requests.post(
                            f"{API_URL}/auth/login",
                            json={"username": username, "password": password},
                            timeout=15,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.logged_in = True
                            st.session_state.token = data["token"]
                            st.session_state.username = username.strip()
                            st.session_state.view = "app"
                            reset_chat()
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Login failed"))
                    else:
                        resp = requests.post(
                            f"{API_URL}/auth/register",
                            json={"username": username, "password": password},
                            timeout=15,
                        )
                        if resp.status_code == 200:
                            st.success("Account created! You can sign in now.")
                            st.session_state.view = "login"
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Registration failed"))
                except requests.exceptions.ConnectionError:
                    st.error("Can't reach the API server. Start it with: uvicorn main:app --port 8000")

        st.markdown("---")
        switch_label = "New here? Create an account" if is_login else "Already have an account? Sign in"
        switch_to = "register" if is_login else "login"
        if st.button(switch_label, key=f"{mode}_switch"):
            st.session_state.view = switch_to
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ===========================================================================
# MAIN APP (unchanged functionality, upgraded chrome)
# ===========================================================================
def render_app():
    if not st.session_state.repo_loaded:
        st.markdown(
            f"""
            <div class="navbar">
                <span class="navbar-brand"><span>🤖 Codebase Chat</span></span>
                <span class="navbar-user">👤 {st.session_state.username}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.15, 1])
        with left:
            st.markdown('<div class="glass-card" style="margin-top: 10px;">', unsafe_allow_html=True)
            st.markdown("<h1>🤖 Chat with your codebase</h1>", unsafe_allow_html=True)
            st.markdown(
                '<p class="subtitle">Paste a GitHub repo and ask questions in plain English</p>',
                unsafe_allow_html=True,
            )

            github_url = st.text_input(
                "GitHub URL", label_visibility="collapsed", placeholder="https://github.com/user/repo"
            )

            if st.button("Load repo"):
                if github_url.strip():
                    with st.spinner("Cloning and indexing... this may take a minute"):
                        response = requests.post(
                            f"{API_URL}/load",
                            json={"github_url": github_url},
                            headers=api_headers(),
                        )
                        result = response.json()
                        st.session_state.repo_loaded = True
                        st.session_state.chunk_count = result["chunks"]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown(
                """
                <div class="soft-card" style="margin-top: 10px;">
                    <span class="card-icon">💡</span>
                    <h3>Try asking things like…</h3>
                    <p>“Where is user authentication handled?”<br>
                       “What happens when the API returns an error?”<br>
                       “Which function computes the total price?”</p>
                    <p style="margin-top:10px; color:#6f6f8c; font-size:12px;">
                        Repos are indexed once, then you can ask unlimited follow-up questions.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Sign out", key="signout_load"):
                logout()

    else:
        # ---- Top navbar ----
        st.markdown(
            f"""
            <div class="navbar">
                <span class="navbar-brand"><span>🤖 Codebase Chat</span></span>
                <span class="navbar-meta">📦 {st.session_state.chunk_count} chunks indexed</span>
                <span class="navbar-user">👤 {st.session_state.username}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_col1, nav_col2, nav_col3 = st.columns([3, 1, 1])
        with nav_col1:
            pass
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

        if not st.session_state.messages:
            st.markdown(
                '<p class="subtitle" style="margin-bottom: 8px;">Ask your first question about this repo 👇</p>',
                unsafe_allow_html=True,
            )

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

        side = st.sidebar
        side.markdown(f"**Signed in as** 👤 {st.session_state.username}")
        if side.button("Sign out"):
            logout()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if st.session_state.logged_in:
    st.session_state.view = "app"

if st.session_state.view == "landing":
    render_landing()
elif st.session_state.view in ("login", "register"):
    render_auth(st.session_state.view)
else:
    render_app()
