import time
import uuid

import streamlit as st
from services.youtube_service import extract_video_id
from services.transcript_service import (
    get_transcript,
    transcript_to_text,
    transcript_with_timestamps
)

from services.chunk_service import (
    chunk_transcript
)
from services.llm_service import (
    summarize,
    generate_insights,
    ask_question
)
from services.youtube_metadata import (
    get_video_metadata
)
from services.export_service import (
    generate_pdf
)

from services.context_builder import (
    build_context
)

from services.pdf_service import (
    extract_pdf_text
)

from services.website_service import (
    extract_website_text
)

from services.knowledge_base import (
    KnowledgeBase
)

from services.memory_service import (
    MemoryService
)

# -------------------------------------------------------
# Page config & session state
# -------------------------------------------------------

st.set_page_config(
    page_icon="assets/pdf lumina logo.png",
    layout="wide"
)

DEFAULT_STATE = {
    "knowledge_base": KnowledgeBase(),
    "memory": MemoryService(),
    "metadata": None,
    "summary": "",
    "takeaways": [],
    "topics": [],
    "transcript": "",
    "left_panel_open": True,
    "processing": False,
    "knowledge_sources": [],
    "source_data": {},
    "pending_analyze": False,
    "pending_question": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------------------
# UI helpers
# -------------------------------------------------------

def inject_global_css():
    collapsed_css = ""
    if not st.session_state.left_panel_open:
        collapsed_css = """
        .st-key-lumina_left_history,
        .st-key-lumina_left_panel .btn-danger,
        .st-key-lumina_left_panel .panel-section-title {
            display: none !important;
        }
        .st-key-lumina_left_panel {
            padding: 0.35rem !important;
        }
        """
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --bg-deep: #0f1117;
            --bg-panel: rgba(26, 27, 46, 0.72);
            --bg-card: rgba(30, 32, 52, 0.85);
            --accent: #7c6af7;
            --accent-glow: rgba(124, 106, 247, 0.45);
            --text-primary: #e8eaed;
            --text-muted: #9aa0b4;
            --border: rgba(255, 255, 255, 0.08);
            --radius: 14px;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            --logo-offset: 2.5rem;
            --chat-dock-h: auto;
        }}

        html, body {{
            overflow: hidden !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* Hide Streamlit's default bottom block — prevents blank bar */
        [data-testid="stBottomBlockContainer"],
        [data-testid="stBottom"] {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }}

        #MainMenu, footer, header, .stDeployButton {{
            visibility: hidden !important;
            display: none !important;
        }}

        .stApp {{
            background: var(--bg-deep);
            font-family: 'Inter', sans-serif !important;
            overflow: hidden !important;
            height: 100vh !important;
        }}

        [data-testid="stAppViewContainer"] {{
            overflow: hidden !important;
            height: 100vh !important;
        }}

        [data-testid="stAppViewContainer"] > section.main {{
            background: var(--bg-deep);
            overflow: hidden !important;
            height: 100vh !important;
        }}

        .block-container {{
            padding: var(--logo-offset) 0.5rem 0.5rem 0.5rem !important;
            max-width: 100% !important;
            height: var(--panel-h) !important;
            max-height: var(--panel-h) !important;
            overflow: hidden !important;
        }}

        .block-container > div {{
            height: 100% !important;
            max-height: 100% !important;
            overflow: hidden !important;
        }}

        /* ---- Fixed brand logo (outside panels) ---- */
        .lumina-brand {{
            position: fixed;
            top: 10px;
            left: 14px;
            z-index: 1000;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            line-height: 1;
            max-height: 32px;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            pointer-events: none;
        }}

        .lumina-brand .accent {{
            color: var(--accent);
            font-size: 1rem;
        }}

        /* ---- Main 3-column row — locked to viewport ---- */
        .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            align-items: stretch !important;
            overflow: hidden !important;
        }}

        .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="column"] {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        .block-container > div > div > [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="column"] > div {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow: hidden !important;
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        h1, h2, h3, h4, h5, h6, p, label, span, div {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* ---- Shell panels (Streamlit keyed containers) ---- */
        div[data-testid="column"] {{
            padding: 0 4px !important;
            align-self: stretch !important;
        }}

        .st-key-lumina_left_panel,
        .st-key-lumina_center_panel,
        .st-key-lumina_right_panel {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow: hidden !important;
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        .st-key-lumina_left_panel,
        .st-key-lumina_center_panel,
        .st-key-lumina_right_panel,
        .st-key-lumina_left_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-lumina_center_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-lumina_right_panel [data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--bg-panel) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            box-shadow: var(--shadow) !important;
        }}

        .st-key-lumina_left_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-lumina_center_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-lumina_right_panel [data-testid="stVerticalBlockBorderWrapper"] {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        .st-key-lumina_left_panel [data-testid="stVerticalBlockBorderWrapper"] {{
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }}

        .st-key-lumina_left_panel {{
            padding: 0.55rem 0.5rem !important;
        }}

        .st-key-lumina_right_panel {{
            padding: 0.75rem 0.65rem !important;
        }}

        .st-key-lumina_right_panel [data-testid="stVerticalBlockBorderWrapper"] {{
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }}

        .st-key-lumina_center_panel {{
            padding: 0 !important;
            position: relative !important;
        }}

        /* ---- Center scroll feed ---- */
        .st-key-lumina_center_scroll {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: auto !important;
            max-height: none !important;
            overflow: hidden !important;
            padding: 0 !important;
        }}

        .st-key-lumina_center_scroll [data-testid="stVerticalBlockBorderWrapper"] {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0.85rem 1rem 1rem 1rem !important;
        }}

        .st-key-lumina_left_history {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            overflow: hidden !important;
            margin-bottom: 0.35rem !important;
        }}

        .st-key-lumina_left_history [data-testid="stVerticalBlockBorderWrapper"] {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* ---- Chat dock — pinned bottom of center panel ---- */
        .st-key-lumina_chat_dock {{
            flex: 0 0 var(--chat-dock-h) !important;
            height: var(--chat-dock-h) !important;
            min-height: var(--chat-dock-h) !important;
            max-height: var(--chat-dock-h) !important;
            overflow: hidden !important;
            background: linear-gradient(to top, rgba(15,17,23,0.99) 80%, rgba(15,17,23,0.85)) !important;
            border-top: 1px solid var(--border) !important;
            padding: 0.4rem 1rem 0.55rem 1rem !important;
            z-index: 200 !important;
            position: relative !important;
        }}

        .st-key-lumina_chat_dock [data-testid="stVerticalBlockBorderWrapper"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            height: 100% !important;
            overflow: hidden !important;
        }}

        .st-key-lumina_chat_dock [data-testid="stChatInput"] {{
            position: relative !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }}

        .st-key-lumina_chat_dock [data-testid="stChatInput"] textarea {{
            background: rgba(26, 27, 46, 0.95) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            backdrop-filter: blur(12px) !important;
        }}

        .st-key-lumina_chat_dock [data-testid="stChatInput"] textarea:focus {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent-glow) !important;
        }}

        .left-panel-header {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            margin-bottom: 0.35rem;
        }}

        .left-panel-header .panel-section-title {{
            margin: 0 !important;
            flex: 1;
        }}

        {collapsed_css}

        .lumina-logo-icon {{
            display: none;
        }}

        .lumina-logo-full {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            line-height: 1;
            max-height: 32px;
            margin: 0 0 0.5rem 0.15rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}

        .lumina-logo-full .accent {{
            color: var(--accent);
            font-size: 1rem;
        }}

        .lumina-logo-icon {{
            font-size: 1rem;
            color: var(--accent);
            font-weight: 700;
            justify-content: center;
            margin-bottom: 0.5rem;
        }}

        .panel-section-title {{
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin: 0.35rem 0 0.5rem 0.15rem;
        }}

        .history-scroll {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 0.5rem;
            padding-right: 2px;
        }}

        .history-item {{
            padding: 0.45rem 0.55rem;
            border-radius: 10px;
            font-size: 0.82rem;
            color: var(--text-muted);
            cursor: default;
            transition: all 0.2s ease;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .history-item:hover {{
            background: rgba(124, 106, 247, 0.12);
            color: var(--text-primary);
        }}

        .history-empty {{
            font-size: 0.78rem;
            color: var(--text-muted);
            padding: 0.4rem 0.55rem;
        }}

        .fade-in {{
            animation: fadeIn 0.45s ease forwards;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .content-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1rem 1.1rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }}

        .content-card h3 {{
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin: 0 0 0.65rem 0 !important;
        }}

        .takeaway-pill {{
            background: rgba(124, 106, 247, 0.15);
            border: 1px solid rgba(124, 106, 247, 0.3);
            border-radius: 10px;
            padding: 0.5rem 0.75rem;
            margin-bottom: 0.4rem;
            font-size: 0.85rem;
            color: var(--text-primary);
        }}

        .topic-pill {{
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 10px;
            padding: 0.45rem 0.7rem;
            font-size: 0.82rem;
            color: var(--text-primary);
            text-align: center;
        }}

        /* ---- Chat bubbles ---- */
        .chat-user-wrap {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 0.75rem;
        }}

        .chat-user {{
            background: linear-gradient(135deg, #7c6af7, #6366f1);
            color: #fff;
            padding: 0.65rem 0.9rem;
            border-radius: 16px 16px 4px 16px;
            max-width: 78%;
            font-size: 0.88rem;
            line-height: 1.5;
            box-shadow: 0 4px 12px rgba(124, 106, 247, 0.3);
        }}

        .chat-assistant-wrap {{
            display: flex;
            justify-content: flex-start;
            margin-bottom: 0.75rem;
        }}

        .chat-assistant {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.65rem 0.9rem;
            border-radius: 16px 16px 16px 4px;
            max-width: 85%;
            font-size: 0.88rem;
            line-height: 1.55;
        }}

        .chat-meta {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin: 0.25rem 0 0.75rem 0.5rem;
        }}

        /* ---- Loading indicators ---- */
        .thinking-loader {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            padding: 0.5rem 0;
        }}

        .thinking-dots span {{
            animation: pulseDot 1.4s infinite ease-in-out both;
            display: inline-block;
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: var(--accent);
            margin: 0 1px;
        }}

        .thinking-dots span:nth-child(1) {{ animation-delay: 0s; }}
        .thinking-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
        .thinking-dots span:nth-child(3) {{ animation-delay: 0.4s; }}

        @keyframes pulseDot {{
            0%, 80%, 100% {{ transform: scale(0.6); opacity: 0.4; }}
            40% {{ transform: scale(1); opacity: 1; }}
        }}

        .skeleton-pulse {{
            background: linear-gradient(90deg,
                rgba(124,106,247,0.08) 25%,
                rgba(124,106,247,0.18) 50%,
                rgba(124,106,247,0.08) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 10px;
            height: 14px;
            margin-bottom: 8px;
        }}

        @keyframes shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}

        /* ---- Knowledge base list ---- */
        .kb-item {{
            display: flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.4rem 0.5rem;
            border-radius: 10px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            margin-bottom: 4px;
            font-size: 0.78rem;
            color: var(--text-primary);
        }}

        .kb-item-icon {{
            flex-shrink: 0;
            font-size: 0.85rem;
        }}

        .kb-item-label {{
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* ---- Widget overrides ---- */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: rgba(15, 17, 23, 0.8) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.84rem !important;
            transition: all 0.2s ease !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent-glow) !important;
        }}

        .stTextInput label, .stTextArea label,
        .stFileUploader label {{
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            color: var(--text-muted) !important;
            margin-bottom: 2px !important;
        }}

        div[data-testid="stFileUploader"] {{
            background: transparent !important;
        }}

        div[data-testid="stFileUploader"] section {{
            background: rgba(15, 17, 23, 0.6) !important;
            border: 1px dashed rgba(124, 106, 247, 0.35) !important;
            border-radius: 12px !important;
            padding: 0.5rem !important;
        }}

        div[data-testid="stFileUploader"] section small {{
            color: var(--text-muted) !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #7c6af7, #6366f1) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 14px rgba(124, 106, 247, 0.35) !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(124, 106, 247, 0.5) !important;
        }}

        .stButton > button:disabled {{
            opacity: 0.45 !important;
            transform: none !important;
            cursor: not-allowed !important;
        }}

        .btn-ghost > button {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
            color: var(--text-muted) !important;
            font-weight: 500 !important;
        }}

        .btn-ghost > button:hover {{
            background: rgba(124, 106, 247, 0.12) !important;
            color: var(--text-primary) !important;
            box-shadow: none !important;
        }}

        .btn-danger > button {{
            background: rgba(239, 68, 68, 0.15) !important;
            border: 1px solid rgba(239, 68, 68, 0.35) !important;
            color: #fca5a5 !important;
            box-shadow: none !important;
        }}

        .btn-danger > button:hover {{
            background: rgba(239, 68, 68, 0.25) !important;
            box-shadow: none !important;
        }}

        .btn-toggle > button {{
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
            color: var(--text-primary) !important;
            min-width: 32px !important;
            width: 32px !important;
            height: 32px !important;
            padding: 0 !important;
            font-size: 0.9rem !important;
        }}

        .btn-toggle > button:hover {{
            background: rgba(124, 106, 247, 0.15) !important;
        }}

        .btn-kb-remove > button {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: var(--text-muted) !important;
            font-size: 0.72rem !important;
            padding: 0.15rem 0.35rem !important;
            min-height: 0 !important;
        }}

        .btn-kb-remove > button:hover {{
            color: #fca5a5 !important;
            background: rgba(239,68,68,0.1) !important;
        }}

        /* Hide default chat message chrome */
        [data-testid="stChatMessage"] {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }}

        .stAlert {{
            border-radius: 12px !important;
            font-size: 0.84rem !important;
        }}

        div[data-testid="stDownloadButton"] > button {{
            width: 100%;
        }}

        .resources-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0 0 0.65rem 0;
            letter-spacing: -0.02em;
        }}

        .right-spacer {{
            flex: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def loading_indicator_html(text="Thinking"):
    return (
        f'<div class="thinking-loader fade-in">'
        f'{text}<span class="thinking-dots">'
        f'<span></span><span></span><span></span>'
        f'</span></div>'
    )


def stream_text_word_by_word(text, placeholder, css_class="chat-assistant"):
    words = text.split(" ")
    displayed = ""
    for i, word in enumerate(words):
        displayed += (" " if i > 0 else "") + word
        placeholder.markdown(
            f'<div class="chat-assistant-wrap fade-in">'
            f'<div class="{css_class}">{displayed}</div></div>',
            unsafe_allow_html=True
        )
        time.sleep(0.03)


def stream_summary_word_by_word(text, placeholder):
    words = text.split(" ")
    displayed = ""
    for i, word in enumerate(words):
        displayed += (" " if i > 0 else "") + word
        placeholder.markdown(
            f'<div class="content-card fade-in">'
            f'<h3>Summary</h3>'
            f'<p style="margin:0;color:#e8eaed;font-size:0.88rem;line-height:1.6;">'
            f'{displayed}</p></div>',
            unsafe_allow_html=True
        )
        time.sleep(0.025)


def clear_workspace():
    st.session_state.knowledge_base.clear()
    st.session_state.memory.clear()
    st.session_state.summary = ""
    st.session_state.takeaways = []
    st.session_state.topics = []
    st.session_state.transcript = ""
    st.session_state.metadata = None
    st.session_state.knowledge_sources = []
    st.session_state.source_data = {}
    st.session_state.processing = False
    st.session_state.pending_analyze = False
    st.session_state.pending_question = None
    for key in ("input_youtube", "input_website", "input_notes", "input_pdf"):
        if key in st.session_state:
            del st.session_state[key]


def rebuild_knowledge_base():
    kb = st.session_state.knowledge_base
    kb.clear()
    for data in st.session_state.source_data.values():
        if data["kind"] == "chunks":
            kb.add_chunks(data["chunks"])
        elif data["kind"] == "document":
            kb.add_document(
                text=data["text"],
                metadata=data["metadata"]
            )


def remove_knowledge_source(source_id):
    if source_id in st.session_state.source_data:
        del st.session_state.source_data[source_id]
    st.session_state.knowledge_sources = [
        s for s in st.session_state.knowledge_sources
        if s["id"] != source_id
    ]
    rebuild_knowledge_base()
    if not st.session_state.source_data:
        st.session_state.summary = ""
        st.session_state.takeaways = []
        st.session_state.topics = []
        st.session_state.transcript = ""
        st.session_state.metadata = None


def add_source_entry(source_id, source_type, label, icon, data):
    st.session_state.source_data[source_id] = data
    st.session_state.knowledge_sources.append({
        "id": source_id,
        "type": source_type,
        "label": label[:48],
        "icon": icon
    })


def source_icon(source_type):
    icons = {
        "youtube": "▶",
        "pdf": "📄",
        "website": "🌐",
        "notes": "📝"
    }
    return icons.get(source_type, "📎")


def run_analyze(video_url, uploaded_pdf, website_url, notes_text, status_slot=None):
    """Run full analyze pipeline. Returns True on success, False on failure."""
    kb = st.session_state.knowledge_base
    kb.clear()
    st.session_state.memory.clear()
    st.session_state.metadata = None
    st.session_state.summary = ""
    st.session_state.takeaways = []
    st.session_state.topics = []
    st.session_state.transcript = ""
    st.session_state.knowledge_sources = []
    st.session_state.source_data = {}
    source_loaded = False
    combined_text = ""

    def show_status(text):
        if status_slot is not None:
            status_slot.markdown(
                loading_indicator_html(text),
                unsafe_allow_html=True
            )

    def clear_status():
        if status_slot is not None:
            status_slot.empty()

    # youtube
    if video_url.strip():
        video_id = extract_video_id(video_url)

        if video_id is None:
            st.error("Invalid YouTube URL.")
        else:
            metadata = get_video_metadata(video_url)
            show_status("Fetching transcript")
            transcript = get_transcript(video_id)
            clear_status()
            if transcript is None:
                st.error("Unable to fetch transcript.")
            else:
                transcript_text = transcript_to_text(transcript)
                st.session_state.transcript = transcript_text
                transcript_chunks = chunk_transcript(
                    transcript_with_timestamps(transcript)
                )

                for chunk in transcript_chunks:
                    chunk["metadata"] = metadata
                kb.add_chunks(transcript_chunks)

                st.session_state.metadata = metadata
                combined_text += transcript_text + "\n\n"
                source_loaded = True
                add_source_entry(
                    source_id=f"yt_{video_id}",
                    source_type="youtube",
                    label=metadata.get("title", video_url),
                    icon="▶",
                    data={
                        "kind": "chunks",
                        "chunks": transcript_chunks
                    }
                )

    # pdf
    if uploaded_pdf is not None:
        show_status("Reading PDF")
        pdf_text = extract_pdf_text(uploaded_pdf)
        clear_status()
        if pdf_text:
            kb.add_document(
                text=pdf_text,
                metadata={
                    "source": "pdf",
                    "title": uploaded_pdf.name,
                    "file": uploaded_pdf.name
                }
            )
            combined_text += pdf_text + "\n\n"
            source_loaded = True
            add_source_entry(
                source_id=f"pdf_{uploaded_pdf.name}_{uuid.uuid4().hex[:6]}",
                source_type="pdf",
                label=uploaded_pdf.name,
                icon="📄",
                data={
                    "kind": "document",
                    "text": pdf_text,
                    "metadata": {
                        "source": "pdf",
                        "title": uploaded_pdf.name,
                        "file": uploaded_pdf.name
                    }
                }
            )

    # website urls
    if website_url.strip():
        show_status("Reading website")
        website_text = extract_website_text(website_url)
        clear_status()
        if website_text:
            kb.add_document(
                text=website_text,
                metadata={
                    "source": "website",
                    "title": website_url,
                    "url": website_url
                }
            )
            combined_text += website_text + "\n\n"
            source_loaded = True
            add_source_entry(
                source_id=f"web_{uuid.uuid4().hex[:8]}",
                source_type="website",
                label=website_url,
                icon="🌐",
                data={
                    "kind": "document",
                    "text": website_text,
                    "metadata": {
                        "source": "website",
                        "title": website_url,
                        "url": website_url
                    }
                }
            )

    # text
    if notes_text.strip():
        kb.add_document(
            text=notes_text,
            metadata={
                "source": "notes",
                "title": "Notes"
            }
        )
        combined_text += notes_text + "\n\n"
        source_loaded = True
        add_source_entry(
            source_id=f"notes_{uuid.uuid4().hex[:8]}",
            source_type="notes",
            label="Plain text notes",
            icon="📝",
            data={
                "kind": "document",
                "text": notes_text,
                "metadata": {
                    "source": "notes",
                    "title": "Notes"
                }
            }
        )

    if not source_loaded:
        st.session_state.processing = False
        st.warning("Please provide at least one Resource.")
        return False

    # summary
    show_status("Generating summary")
    summary = summarize(combined_text)
    st.session_state.summary = summary
    clear_status()
    summary_stream_slot = st.empty()
    stream_summary_word_by_word(summary, summary_stream_slot)

    # insights
    show_status("Generating insights")
    insights = generate_insights(summary)
    st.session_state.takeaways = insights.get("takeaways", [])
    st.session_state.topics = insights.get("topics", [])
    clear_status()

    st.session_state.processing = False
    return True


@st.dialog(
    "📜 Transcript",
    width="large"
)
def show_transcript():
    st.text_area(
        "",
        st.session_state.transcript,
        height=500
    )


# -------------------------------------------------------
# Global CSS
# -------------------------------------------------------

inject_global_css()

# Fixed logo — outside all panels, top-left corner
st.markdown(
    '<div class="lumina-brand"><span class="accent">✦</span> Lumina</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------------
# Three-panel layout
# -------------------------------------------------------

left_width = 2.1 if st.session_state.left_panel_open else 0.42
center_width = 5.8 if st.session_state.left_panel_open else 7.0
right_width = 2.1

left_col, center_col, right_col = st.columns(
    [left_width, center_width, right_width],
    gap="small"
)

# -------------------------------------------------------
# Right Panel — Resources (inputs first, collected before analyze)
# -------------------------------------------------------

with right_col:
    with st.container(border=True, height="stretch", key="lumina_right_panel"):
        st.markdown(
            '<p class="resources-title">Resources</p>',
            unsafe_allow_html=True
        )

        video_url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/...",
            key="input_youtube",
            label_visibility="visible"
        )

        uploaded_pdf = st.file_uploader(
            "PDF file upload",
            type=["pdf"],
            key="input_pdf",
            label_visibility="visible"
        )

        website_url = st.text_input(
            "Website URL",
            placeholder="https://...",
            key="input_website",
            label_visibility="visible"
        )

        notes_text = st.text_area(
            "Plain text",
            height=120,
            placeholder="Paste notes, documentation or articles...",
            key="input_notes",
            label_visibility="visible"
        )

        if st.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            key="analyze_btn",
            disabled=st.session_state.processing
        ):
            st.session_state.pending_analyze = True
            st.rerun()

        st.markdown(
            '<p class="panel-section-title">Knowledge Base</p>',
            unsafe_allow_html=True
        )

        if not st.session_state.knowledge_sources:
            st.markdown(
                '<p class="history-empty">No sources loaded.</p>',
                unsafe_allow_html=True
            )
        else:
            for source in st.session_state.knowledge_sources:
                icon = source.get("icon", source_icon(source["type"]))
                label = source.get("label", "Source")
                col_icon, col_label, col_remove = st.columns([0.15, 0.65, 0.2])
                with col_icon:
                    st.markdown(
                        f'<span class="kb-item-icon">{icon}</span>',
                        unsafe_allow_html=True
                    )
                with col_label:
                    st.markdown(
                        f'<span class="kb-item-label" title="{label}">{label}</span>',
                        unsafe_allow_html=True
                    )
                with col_remove:
                    st.markdown('<div class="btn-kb-remove">', unsafe_allow_html=True)
                    if st.button(
                        "Remove",
                        key=f"remove_{source['id']}",
                        disabled=st.session_state.processing
                    ):
                        remove_knowledge_source(source["id"])
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Read input values from session state for reliable analyze
video_url = st.session_state.get("input_youtube", "") or ""
website_url = st.session_state.get("input_website", "") or ""
notes_text = st.session_state.get("input_notes", "") or ""
uploaded_pdf = st.session_state.get("input_pdf")

# -------------------------------------------------------
# Left Panel — History & Navigation
# -------------------------------------------------------

with left_col:
    with st.container(border=True, height="stretch", key="lumina_left_panel"):
        hdr_toggle, hdr_title = st.columns([0.14, 0.86], gap="small")
        with hdr_toggle:
            st.markdown('<div class="btn-toggle">', unsafe_allow_html=True)
            toggle_icon = "←" if st.session_state.left_panel_open else "☰"
            if st.button(toggle_icon, key="sidebar_toggle", help="Toggle sidebar"):
                st.session_state.left_panel_open = not st.session_state.left_panel_open
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with hdr_title:
            st.markdown(
                '<p class="panel-section-title">History</p>',
                unsafe_allow_html=True
            )

        with st.container(height="stretch", key="lumina_left_history"):
            messages = st.session_state.memory.get_messages()
            if not messages:
                st.markdown(
                    '<p class="history-empty">No conversations yet.</p>',
                    unsafe_allow_html=True
                )
            else:
                user_msgs = [
                    m for m in messages if m["role"] == "user"
                ]
                for i, msg in enumerate(user_msgs):
                    title = msg["content"][:42]
                    if len(msg["content"]) > 42:
                        title += "…"
                    css = " fade-in" if i == 0 else ""
                    prefix = "💬 " if i == 0 else ""
                    st.markdown(
                        f'<div class="history-item{css}">{prefix}{title}</div>',
                        unsafe_allow_html=True
                    )

        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button(
            "Clear Workspace",
            use_container_width=True,
            key="clear_workspace"
        ):
            clear_workspace()
            st.session_state.pending_analyze = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Center Panel — Main Workspace
# -------------------------------------------------------

kb = st.session_state.knowledge_base
memory = st.session_state.memory

with center_col:
    with st.container(border=True, height="stretch", key="lumina_center_panel"):
        with st.container(height="stretch", key="lumina_center_scroll"):

            if st.session_state.pending_analyze:
                st.session_state.pending_analyze = False
                st.session_state.processing = True
                status_slot = st.empty()
                success = run_analyze(
                    video_url=video_url,
                    uploaded_pdf=uploaded_pdf,
                    website_url=website_url,
                    notes_text=notes_text,
                    status_slot=status_slot
                )
                if success:
                    st.rerun()

            # Process chat question in scrollable feed
            if st.session_state.pending_question:
                question = st.session_state.pending_question
                st.session_state.pending_question = None

                search_slot = st.empty()
                search_slot.markdown(
                    loading_indicator_html("Searching knowledge base"),
                    unsafe_allow_html=True
                )
                retrieved_documents = kb.retrieve(
                    question=question,
                    top_k=5
                )
                context_data = build_context(retrieved_documents)
                search_slot.empty()

                think_slot = st.empty()
                think_slot.markdown(
                    loading_indicator_html("Thinking"),
                    unsafe_allow_html=True
                )
                answer = ask_question(
                    question=question,
                    context=context_data["context"],
                    messages=memory.get_recent_messages()
                )
                think_slot.empty()

                memory.add_message("assistant", answer)

                response_slot = st.empty()
                stream_text_word_by_word(answer, response_slot)

                if context_data["sources"]:
                    sources_html = "📚 " + " · ".join(context_data["sources"])
                    st.markdown(
                        f'<p class="chat-meta">{sources_html}</p>',
                        unsafe_allow_html=True
                    )

                youtube_chunks = []
                for document in retrieved_documents:
                    if "start" in document:
                        youtube_chunks.append(document)
                if youtube_chunks:
                    displayed = set()
                    timestamps = []
                    for chunk in youtube_chunks:
                        timestamp = int(chunk["start"])
                        if timestamp in displayed:
                            continue
                        displayed.add(timestamp)
                        minutes = timestamp // 60
                        seconds = timestamp % 60
                        timestamps.append(f"{minutes:02}:{seconds:02}")
                    ts_html = "📍 " + " · ".join(timestamps)
                    st.markdown(
                        f'<p class="chat-meta">{ts_html}</p>',
                        unsafe_allow_html=True
                    )

                st.session_state.processing = False

            # metadata
            if st.session_state.metadata:
                metadata = st.session_state.metadata
                st.markdown('<div class="content-card fade-in">', unsafe_allow_html=True)
                meta_col1, meta_col2 = st.columns([1, 3])
                with meta_col1:
                    thumbnail = metadata.get("thumbnail", "")
                    if thumbnail:
                        st.image(thumbnail, use_container_width=True)
                with meta_col2:
                    st.markdown(
                        f'<h3>{metadata.get("title", "Knowledge Source")}</h3>',
                        unsafe_allow_html=True
                    )
                    if metadata.get("channel"):
                        st.markdown(
                            f'<p style="color:#9aa0b4;font-size:0.84rem;margin:0;">'
                            f'👤 {metadata["channel"]}</p>',
                            unsafe_allow_html=True
                        )
                    if metadata.get("url"):
                        st.markdown(
                            f'<p style="color:#7c6af7;font-size:0.82rem;margin:0.25rem 0 0 0;">'
                            f'{metadata["url"]}</p>',
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            # summary
            if st.session_state.summary:
                st.markdown(
                    f'<div class="content-card fade-in">'
                    f'<h3>Summary</h3>'
                    f'<p style="margin:0;color:#e8eaed;font-size:0.88rem;line-height:1.6;">'
                    f'{st.session_state.summary}</p></div>',
                    unsafe_allow_html=True
                )

            # takeaways
            if st.session_state.takeaways:
                st.markdown(
                    '<div class="content-card fade-in"><h3>Key Takeaways</h3>',
                    unsafe_allow_html=True
                )
                for takeaway in st.session_state.takeaways:
                    st.markdown(
                        f'<div class="takeaway-pill">{takeaway}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            # topics
            if st.session_state.topics:
                st.markdown(
                    '<div class="content-card fade-in"><h3>Main Topics</h3>',
                    unsafe_allow_html=True
                )
                topic_cols = st.columns(2)
                for index, topic in enumerate(st.session_state.topics):
                    with topic_cols[index % 2]:
                        st.markdown(
                            f'<div class="topic-pill">{topic}</div>',
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            # export
            if st.session_state.summary:
                st.markdown(
                    '<div class="content-card fade-in"><h3>Export Report</h3>',
                    unsafe_allow_html=True
                )
                report_title = (
                    st.session_state.topics[0]
                    if st.session_state.topics
                    else "Lumina AI Report"
                )
                pdf = generate_pdf(
                    metadata=st.session_state.metadata,
                    topic=report_title,
                    summary=st.session_state.summary,
                    takeaways=st.session_state.takeaways,
                    topics=st.session_state.topics
                )
                st.download_button(
                    label="Download PDF Report",
                    data=pdf,
                    file_name=f"{report_title}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # transcript
            if st.session_state.transcript:
                st.markdown(
                    '<div class="content-card fade-in">'
                    '<h3>Transcript</h3>'
                    '<p style="color:#9aa0b4;font-size:0.84rem;margin:0 0 0.65rem 0;">'
                    'Transcript hidden for a cleaner interface.</p>',
                    unsafe_allow_html=True
                )
                if st.button("View Transcript", use_container_width=True):
                    show_transcript()
                st.markdown('</div>', unsafe_allow_html=True)

            # chat messages
            if kb.index is not None:
                st.markdown(
                    '<div class="content-card fade-in" '
                    'style="background:transparent;border:none;box-shadow:none;padding:0;">'
                    '<h3 style="margin-bottom:0.75rem;">Ask Lumina</h3>',
                    unsafe_allow_html=True
                )

                for message in memory.get_messages():
                    role = message["role"]
                    content = message["content"]
                    if role == "user":
                        st.markdown(
                            f'<div class="chat-user-wrap fade-in">'
                            f'<div class="chat-user">{content}</div></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="chat-assistant-wrap fade-in">'
                            f'<div class="chat-assistant">{content}</div></div>',
                            unsafe_allow_html=True
                        )

                st.markdown('</div>', unsafe_allow_html=True)

        # Floating chat input dock — fixed at bottom of center panel
        if kb.index is not None:
            with st.container(height=68, key="lumina_chat_dock"):
                question = st.chat_input(
                    "Ask anything about your knowledge..."
                )

                if question:
                    memory.add_message("user", question)
                    st.session_state.pending_question = question
                    st.session_state.processing = True
                    st.rerun()
