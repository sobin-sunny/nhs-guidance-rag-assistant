"""
WEB INTERFACE (styled to the NHS Design System)
================================================

A clean browser chat window that follows the official NHS design language:
the NHS blue header bar with the NHS logo, NHS colours, and the NHS typeface
(with a web-safe fallback, since the real Frutiger font is licensed).

Run it with:

    streamlit run app/streamlit_app.py

Every answer shows the exact source passages underneath, so the audience can
see the assistant is grounded in real documents and not inventing anything.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st                 # noqa: E402
from app.rag_engine import RagEngine   # noqa: E402

# --- Official NHS Design System colours (service-manual.nhs.uk) ---------------
NHS_BLUE = "#005eb8"
NHS_DARK_BLUE = "#003087"
NHS_GREEN = "#007f3b"
NHS_BLACK = "#212b32"
NHS_GREY_1 = "#4c6272"
NHS_GREY_4 = "#d8dde0"
NHS_GREY_5 = "#f0f4f5"
NHS_LINK_HOVER = "#7c2855"

st.set_page_config(page_title="Guidance Assistant", layout="centered")

# --- NHS-style styling --------------------------------------------------------
# This app is an independent portfolio prototype. Following NHS England's
# identity guidelines (england.nhs.uk/nhsidentity), it does NOT use the NHS
# logo and does not imply NHS endorsement. What it DOES adopt is the NHS's
# freely-usable design craft: the NHS secondary typeface (Arial) with the
# NHS weight hierarchy (Bold titles, Regular body, Light supporting text),
# generous white space, and a calm, clear, accessible layout.
st.markdown(f"""
<style>
  /* NHS secondary typeface (Arial), used as the NHS specifies for digital docs.
     Frutiger is the NHS primary font but is licensed, so Arial is the correct
     free fallback the NHS itself uses for internally produced material. */
  html, body, [class*="css"], .stMarkdown, .stChatMessage, input, button, textarea {{
      font-family: Arial, Helvetica, sans-serif !important;
      color: {NHS_BLACK};
      font-size: 16px;              /* NHS standard body size */
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
  }}

  /* Hide Streamlit's default chrome for a clean, calm NHS-style canvas */
  #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; }}

  /* NHS-style generous white space and a comfortable reading measure */
  .block-container {{ padding-top: 0; max-width: 760px; }}
  .stApp {{ background: #ffffff; }}

  /* Header band. NHS blue used as a plain accent; original wordmark, no logo. */
  .app-header {{
      background-color: {NHS_BLUE};
      padding: 20px 28px;
      margin: 0 -1rem 28px -1rem;
  }}
  .app-header .wordmark {{
      color: #fff; font-size: 22px; font-weight: 700;
  }}
  .app-header .sub {{
      color: #ffffff; font-size: 14px; font-weight: 400; margin-top: 4px;
  }}

  /* One consistent, formal type style throughout (Arial). Headings simply
     use a larger, bold weight of the same font. */
  h1, h2, h3 {{ color: {NHS_DARK_BLUE}; font-weight: 700; }}
  h3 {{ font-size: 24px; margin-bottom: 4px; }}
  .lede {{ color: {NHS_BLACK}; font-weight: 400; font-size: 16px; line-height: 1.5; }}
  a {{ color: {NHS_BLUE}; }}
  a:hover {{ color: {NHS_LINK_HOVER}; }}

  /* NHS-style information panel with the signature 4px left keyline */
  .nhs-panel {{
      border-left: 4px solid {NHS_BLUE};
      background: {NHS_GREY_5};
      padding: 14px 18px;
      margin-bottom: 20px;
      border-radius: 0 4px 4px 0;
      font-size: 15px;
      line-height: 1.5;
  }}
  .nhs-panel.privacy {{ border-left-color: {NHS_GREEN}; }}

  /* Source card, styled like an NHS 'expander' detail */
  .streamlit-expanderHeader {{ color: {NHS_BLUE} !important; font-weight: 700; }}
  div[data-testid="stExpander"] {{
      border: 1px solid {NHS_GREY_4};
      border-radius: 4px;
      background: {NHS_GREY_5};
  }}

  /* Chat rows. Hide the default round avatar icon and replace it with a plain
     'User' / 'Agent' text label, so nothing looks auto-generated. */
  .stChatMessage {{ border-radius: 4px; }}
  .stChatMessage img, .stChatMessage svg,
  div[data-testid="stChatMessageAvatarUser"],
  div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
  .role-label {{
      font-weight: 700; font-size: 13px; color: {NHS_GREY_1};
      text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;
  }}

  /* Input focus ring in NHS blue, with the NHS 4px focus emphasis */
  div[data-testid="stChatInput"] textarea:focus {{
      border-color: {NHS_BLUE} !important;
      box-shadow: 0 0 0 3px {NHS_BLUE}40 !important;
  }}

  /* Example-question chips: NHS-style secondary buttons */
  div[data-testid="stButton"] > button {{
      border: 2px solid {NHS_BLUE};
      color: {NHS_BLUE};
      background: #fff;
      border-radius: 4px;
      font-size: 15px;
      font-weight: 700;
      padding: 12px 16px;
      text-align: left;
      white-space: normal;
      line-height: 1.4;
      height: 100%;
      transition: background 0.1s ease;
  }}
  div[data-testid="stButton"] > button:hover {{
      background: {NHS_GREY_5};
      border-color: {NHS_DARK_BLUE};
      color: {NHS_DARK_BLUE};
  }}
  div[data-testid="stButton"] > button:focus {{
      box-shadow: 0 0 0 3px {NHS_BLUE}40 !important;
  }}
</style>
""", unsafe_allow_html=True)

# --- Header band (original wordmark, no NHS logo) -----------------------------
st.markdown(f"""
<div class="app-header">
  <div class="wordmark">Guidance Assistant</div>
  <div class="sub">Answers from published NHS guidance documents</div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Ask about NHS guidance")
st.markdown(
    '<p class="lede">Ask a question and get an answer based only on the source '
    'guidance documents. The exact source is shown for every reply.</p>',
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading...")
def get_engine():
    return RagEngine()


try:
    engine = get_engine()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# Status panel, styled as an NHS information box.
if engine.llm_available:
    st.markdown(
        '<div class="nhs-panel privacy"><b>Running locally.</b> Answers are '
        'produced on this machine. No data leaves this computer.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="nhs-panel"><b>Running in search-only mode.</b> The most '
        'relevant passages are shown below. Start the local service to receive '
        'full written answers.</div>',
        unsafe_allow_html=True,
    )


def render_sources(sources):
    with st.expander("Show sources"):
        for i, doc in enumerate(sources, 1):
            src = doc.metadata.get("source_file", "?")
            page = doc.metadata.get("page", "?")
            st.markdown(f"**{i}. {src} — page {page}**")
            st.caption(doc.page_content[:400] + "...")


def role_label(role):
    """Return the plain text label shown above each message."""
    return "User" if role == "user" else "Agent"


def show_message(role, content, sources=None):
    """Render one chat row with a plain 'User' / 'Agent' label (no icons)."""
    with st.chat_message(role):
        st.markdown(f'<div class="role-label">{role_label(role)}</div>',
                    unsafe_allow_html=True)
        st.markdown(content)
        if sources:
            render_sources(sources)


if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None   # a question waiting to be answered


def submit_question(q):
    """Record the question and trigger an immediate redraw.

    We only store the question here — we do NOT compute the answer yet. This
    lets the screen redraw straight away so the user sees their question (and a
    'Searching...' spinner) instantly, instead of the UI freezing until the
    answer is ready.
    """
    st.session_state.pending = q
    st.rerun()


# --- Clickable example questions (FAQ) ----------------------------------------
# These map to the sample guidance documents, so a click always returns a good
# answer. Handy for a live demo: the panel can click instead of typing.
FAQ = [
    "How much does an HRT prescription prepayment certificate cost and what does it cover?",
    "Who is entitled to a maternity exemption certificate?",
    "How do I apply for a maternity exemption certificate?",
    "Which HRT medicines are covered by the HRT PPC?",
]

# Show the example questions at all times, so the user can click another one
# at any point in the conversation.
st.markdown("**Example questions**")
cols = st.columns(2)
for i, q in enumerate(FAQ):
    if cols[i % 2].button(q, key=f"faq_{i}", use_container_width=True):
        submit_question(q)

# --- Replay the conversation so far -------------------------------------------
for turn in st.session_state.history:
    show_message(turn["role"], turn["content"], turn.get("sources"))

# --- If a question is waiting, show it immediately, then answer it ------------
# This block runs on the redraw triggered by submit_question(), so the user's
# question and the progress note appear at once and the answer follows.
if st.session_state.pending is not None:
    q = st.session_state.pending
    show_message("user", q)
    with st.chat_message("assistant"):
        st.markdown('<div class="role-label">Agent</div>', unsafe_allow_html=True)
        with st.spinner("Searching the guidance..."):
            result = engine.answer(q)
        st.markdown(result["answer"])
        render_sources(result["sources"])
    # Commit both sides to history and clear the pending slot.
    st.session_state.history.append({"role": "user", "content": q})
    st.session_state.history.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
    st.session_state.pending = None

question = st.chat_input("Ask a question")
if question:
    submit_question(question)

# --- Footer: plain, descriptive text, as NHS identity guidelines require ------
LINKEDIN_URL = "https://www.linkedin.com/in/sobin-sunny"
st.markdown(
    f"<hr style='border:none;border-top:1px solid {NHS_GREY_4};margin-top:2.5rem'>"
    f"<p style='color:{NHS_GREY_1};font-size:14px;line-height:1.6;margin-bottom:6px'>"
    f"Developed by <b>Sobin Sunny</b> · "
    f"<a href='{LINKEDIN_URL}' target='_blank' style='color:{NHS_BLUE};text-decoration:none'>LinkedIn</a></p>"
    f"<p style='color:{NHS_GREY_1};font-size:13px;line-height:1.5'>Independent "
    "portfolio prototype demonstrating retrieval-augmented generation over "
    "publicly available NHS guidance. Not produced, affiliated with, or endorsed "
    "by the NHS or the NHS Business Services Authority. The NHS logo is not used.</p>",
    unsafe_allow_html=True,
)
