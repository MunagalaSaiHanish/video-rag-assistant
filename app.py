import streamlit as st

from services.youtube_service import (
    extract_video_id
)

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

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(


    page_icon="asset/pdf lumina logo.png",

    layout="wide"

)

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

DEFAULT_STATE = {

    "knowledge_base": KnowledgeBase(),

    "memory": MemoryService(),

    "metadata": None,

    "summary": "",

    "takeaways": [],

    "topics": [],

    "transcript": ""

}

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ---------------------------------------------------------
# Transcript Dialog
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

logo_col, title_col = st.columns([1,10])

with logo_col:

    st.image(

        "assets/pdf lumina logo.png",

        width=100

    )

st.divider()

# ---------------------------------------------------------
# Main Layout
# ---------------------------------------------------------

center_panel, source_panel = st.columns(

    [5.5, 2]

)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.title("☰ Workspace")

    st.divider()

    st.subheader("Conversation")

    if len(

        st.session_state.memory.get_messages()

    ) == 0:

        st.caption(

            "No conversation yet."

        )

    else:

        st.success(

            "Conversation Active"

        )

    st.divider()

    if st.button(

        "🗑 Clear Workspace",

        use_container_width=True

    ):

        st.session_state.knowledge_base.clear()

        st.session_state.memory.clear()

        st.session_state.metadata = None

        st.session_state.summary = ""

        st.session_state.takeaways = []

        st.session_state.topics = []

        st.session_state.transcript = ""

        st.rerun()

# ---------------------------------------------------------
# Knowledge Sources
# ---------------------------------------------------------

with source_panel:

    st.subheader(

        "Knowledge Sources"

    )

    st.markdown("---")

    video_url = st.text_input(

        "🎥 YouTube URL",

        placeholder="https://youtube.com/..."

    )

    uploaded_pdf = st.file_uploader(

        "📄 Upload PDF",

        type=["pdf"]

    )

    website_url = st.text_input(

        "🌐 Website URL",

        placeholder="https://..."

    )

    notes_text = st.text_area(

        "📝 Plain Text",

        height=180,

        placeholder="Paste notes, documentation or articles..."

    )

    st.markdown("")

    analyze_clicked = st.button(

        "🚀 Analyze",

        use_container_width=True,

        type="primary"

    )

    st.markdown("---")

    st.subheader(

        "Knowledge Base"

    )

    if st.session_state.knowledge_base.index is None:

        st.warning(

            "No Knowledge Loaded"

        )

    else:

        st.success(

            "Knowledge Base Ready"

        )
if analyze_clicked:

    kb = st.session_state.knowledge_base

    kb.clear()

    st.session_state.memory.clear()

    st.session_state.metadata = None

    st.session_state.summary = ""

    st.session_state.takeaways = []

    st.session_state.topics = []

    st.session_state.transcript = ""

    source_loaded = False

    combined_text = ""

    # ---------------------------------------------------------
    # YouTube
    # ---------------------------------------------------------

    if video_url.strip():

        video_id = extract_video_id(
            video_url
        )

        if video_id is None:

            st.error(
                "Invalid YouTube URL."
            )

        else:

            metadata = get_video_metadata(
                video_url
            )

            with st.spinner(
                "Fetching Transcript..."
            ):

                transcript = get_transcript(
                    video_id
                )

            if transcript is None:

                st.error(
                    "Unable to fetch transcript."
                )

            else:

                transcript_text = transcript_to_text(
                    transcript
                )

                st.session_state.transcript = (
                    transcript_text
                )

                transcript_chunks = chunk_transcript(

                    transcript_with_timestamps(
                        transcript
                    )

                )

                for chunk in transcript_chunks:

                    chunk["metadata"] = metadata

                kb.add_chunks(
                    transcript_chunks
                )

                st.session_state.metadata = metadata

                combined_text += (
                    transcript_text + "\n\n"
                )

                source_loaded = True

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    if uploaded_pdf is not None:

        with st.spinner(
            "Reading PDF..."
        ):

            pdf_text = extract_pdf_text(
                uploaded_pdf
            )

        if pdf_text:

            kb.add_document(

                text=pdf_text,

                metadata={

                    "source": "pdf",

                    "title": uploaded_pdf.name,

                    "file": uploaded_pdf.name

                }

            )

            combined_text += (

                pdf_text + "\n\n"

            )

            source_loaded = True

    # ---------------------------------------------------------
    # Website
    # ---------------------------------------------------------

    if website_url.strip():

        with st.spinner(
            "Reading Website..."
        ):

            website_text = extract_website_text(
                website_url
            )

        if website_text:

            kb.add_document(

                text=website_text,

                metadata={

                    "source": "website",

                    "title": website_url,

                    "url": website_url

                }

            )

            combined_text += (

                website_text + "\n\n"

            )

            source_loaded = True

    # ---------------------------------------------------------
    # Plain Text
    # ---------------------------------------------------------

    if notes_text.strip():

        kb.add_document(

            text=notes_text,

            metadata={

                "source": "notes",

                "title": "Notes"

            }

        )

        combined_text += (

            notes_text + "\n\n"

        )

        source_loaded = True

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    if not source_loaded:

        st.warning(

            "Please provide at least one knowledge source."

        )

        st.stop()
    # ---------------------------------------------------------
    # Default Metadata
    # ---------------------------------------------------------

    if st.session_state.metadata is None:

        st.session_state.metadata = {

            "source": "knowledge",

            "title": "Knowledge Base",

            "channel": "",

            "thumbnail": "",

            "url": ""

        }

    # ---------------------------------------------------------
    # Generate Summary
    # ---------------------------------------------------------

    with st.spinner(

        "Generating Summary..."

    ):

        summary = summarize(

            combined_text

        )

    st.session_state.summary = summary

    # ---------------------------------------------------------
    # Generate Insights
    # ---------------------------------------------------------

    with st.spinner(

        "Generating Insights..."

    ):

        insights = generate_insights(

            summary

        )

    st.session_state.takeaways = insights.get(

        "takeaways",

        []

    )

    st.session_state.topics = insights.get(

        "topics",

        []

    )

    st.success(

        "✅ Knowledge Base Ready"

    )
with center_panel:

    # ---------------------------------------------------------
    # Knowledge Information
    # ---------------------------------------------------------

    if st.session_state.metadata:

        metadata = st.session_state.metadata

        st.divider()

        col1, col2 = st.columns([1, 3])

        with col1:

            thumbnail = metadata.get(
                "thumbnail",
                ""
            )

            if thumbnail:

                st.image(
                    thumbnail,
                    use_container_width=True
                )

        with col2:

            st.subheader(

                metadata.get(
                    "title",
                    "Knowledge Base"
                )

            )

            if metadata.get("channel"):

                st.write(

                    f"👤 {metadata['channel']}"

                )

            if metadata.get("url"):

                st.write(

                    metadata["url"]

                )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    if st.session_state.summary:

        st.divider()

        st.subheader(

            "📝 Executive Summary"

        )

        st.write(

            st.session_state.summary

        )

    # ---------------------------------------------------------
    # Key Takeaways
    # ---------------------------------------------------------

    if st.session_state.takeaways:

        st.divider()

        st.subheader(

            "💡 Key Takeaways"

        )

        for takeaway in st.session_state.takeaways:

            st.success(

                takeaway

            )

    # ---------------------------------------------------------
    # Main Topics
    # ---------------------------------------------------------

    if st.session_state.topics:

        st.divider()

        st.subheader(

            "🧠 Main Topics"

        )

        cols = st.columns(2)

        for index, topic in enumerate(

            st.session_state.topics

        ):

            with cols[index % 2]:

                st.info(

                    topic

                )

    # ---------------------------------------------------------
    # Export Report
    # ---------------------------------------------------------

    if st.session_state.summary:

        st.divider()

        st.subheader(

            "📄 Export Report"

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

            "⬇ Download PDF Report",

            data=pdf,

            file_name="Lumina_AI_Report.pdf",

            mime="application/pdf",

            use_container_width=True

        )

    # ---------------------------------------------------------
    # Transcript
    # ---------------------------------------------------------

    if st.session_state.transcript:

        st.divider()

        st.subheader(

            "📜 Transcript"

        )

        st.write(

            "Transcript hidden for a cleaner interface."

        )

        if st.button(

            "View Transcript",

            use_container_width=True

        ):

            show_transcript()

    # ---------------------------------------------------------
    # Chat with Lumina
    # ---------------------------------------------------------

    if st.session_state.knowledge_base.index is not None:

        st.divider()

        st.subheader(

            "💬 Ask Lumina"

        )

        kb = st.session_state.knowledge_base

        memory = st.session_state.memory

        # -----------------------------------------------------
        # Previous Conversation
        # -----------------------------------------------------

        for message in memory.get_messages():

            with st.chat_message(

                message["role"]

            ):

                st.markdown(

                    message["content"]

                )

        # -----------------------------------------------------
        # User Question
        # -----------------------------------------------------

        question = st.chat_input(

            "Ask anything about your knowledge..."

        )

        if question:

            memory.add_message(

                "user",

                question

            )

            with st.chat_message(

                "user"

            ):

                st.markdown(

                    question

                )

            # -------------------------------------------------
            # Retrieve Context
            # -------------------------------------------------

            with st.spinner(

                "Searching Knowledge Base..."

            ):

                retrieved_documents = kb.retrieve(

                    question=question,

                    top_k=5

                )

                context_data = build_context(

                    retrieved_documents

                )

            # -------------------------------------------------
            # LLM Response
            # -------------------------------------------------

            with st.spinner(

                "Thinking..."

            ):

                answer = ask_question(

                    question=question,

                    context=context_data["context"],

                    messages=memory.get_recent_messages()

                )

            memory.add_message(

                "assistant",

                answer

            )

            with st.chat_message(

                "assistant"

            ):

                st.markdown(

                    answer

                )

            # -------------------------------------------------
            # Sources
            # -------------------------------------------------

            if context_data["sources"]:

                st.caption(

                    "📚 Sources"

                )

                for source in context_data["sources"]:

                    st.write(

                        f"• {source}"

                    )

            # -------------------------------------------------
            # Video Timestamps
            # -------------------------------------------------

            timestamps = []

            for document in retrieved_documents:

                if "start" in document:

                    timestamps.append(

                        document

                    )

            if timestamps:

                st.caption(

                    "📍 Mentioned in Video"

                )

                shown = set()

                for chunk in timestamps:

                    start = int(

                        chunk["start"]

                    )

                    if start in shown:

                        continue

                    shown.add(

                        start

                    )

                    minutes = start // 60

                    seconds = start % 60

                    st.write(

                        f"• {minutes:02}:{seconds:02}"

                    )