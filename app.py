import streamlit as st

from services.youtube_service import extract_video_id
from services.transcript_service import (
    get_transcript,
    transcript_to_text,
    transcript_with_timestamps
)

from services.chunk_service import (
    chunk_text,
    chunk_transcript
)

from services.embedding_service import generate_embeddings
from services.vector_store import (
    create_vector_store,
    retrieve_documents
)
from services.llm_service import (
    summarize,
    generate_insights,
    ask_question
)
from services.youtube_metadata import get_video_metadata
from services.export_service import generate_pdf
from services.context_builder import build_context
from services.pdf_service import extract_pdf_text
from services.knowledge_base import KnowledgeBase
from services.memory_service import MemoryService
from services.website_service import (extract_website_text)

#page setup

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon=".assets/lumina logo.png",
    layout="wide"
)

#session state

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "takeaways" not in st.session_state:
    st.session_state.takeaways = []

if "topics" not in st.session_state:
    st.session_state.topics = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []
    

if "knowledge_base" not in st.session_state:

    st.session_state.knowledge_base = KnowledgeBase()   



if "memory" not in st.session_state:

    st.session_state.memory = MemoryService()

if "metadata" not in st.session_state:
    st.session_state.metadata = None

if "metadata_chunks" not in st.session_state:
    st.session_state.metadata_chunks = []

#transcript popup

@st.dialog("📜 Full Transcript", width="large")
def show_transcript():

    st.text_area(
        "",
        st.session_state.transcript,
        height=500
    )

#side bar

with st.sidebar:

    st.title("🎥 AI Knowledge Assistant")

    st.markdown("---")

    st.subheader("About")

    st.write("""
This application uses Retrieval-Augmented Generation (RAG)
to analyze YouTube videos.

Pipeline

• Transcript
• Chunking
• Embeddings
• FAISS
• Qwen
""")

    st.markdown("---")
    st.success("✅ RAG Enabled")

#main app

st.title("🎥 AI Knowledge Assistant")
st.caption("Analyze YouTube videos using AI")
st.divider()

#input of youtube url

video_url = st.text_input("🔗 Paste YouTube URL")

uploaded_pdf = st.file_uploader(
    "📄 Upload PDF",
    type=["pdf"]
)

website_url = st.text_input(
    "🌐 Paste Website URL"
)

if uploaded_pdf:

    pdf_text = extract_pdf_text(
        uploaded_pdf
    )

    st.success("PDF Loaded Successfully")

    st.write(pdf_text[:500])

#extract transcript, summary and build vector database

if st.button("🚀 Analyze", use_container_width=True):

    video_id = extract_video_id(video_url)

    if video_id is None:
        st.error("Invalid YouTube URL")

    else:

        st.session_state.metadata = get_video_metadata(video_url)

        with st.spinner("Fetching Transcript..."):
            raw_transcript = get_transcript(video_id)

        if raw_transcript is None:
            st.error("Couldn't fetch transcript.")

        else:

            plain_text = transcript_to_text(raw_transcript)
            st.session_state.transcript = plain_text
            timestamp_segments = transcript_with_timestamps(
             raw_transcript
            )

            with st.spinner("Generating AI Summary..."):
                summary = summarize(plain_text)

            st.session_state.summary = summary

            #generate insights

            with st.spinner("Generating Key Takeaways..."):
                insights = generate_insights(summary)

            st.session_state.takeaways = insights.get("takeaways", [])
            st.session_state.topics = insights.get("topics", [])

            #build vector database

            with st.spinner("Building Knowledge Base..."):
                metadata_chunks = chunk_transcript(
                timestamp_segments
                )

                chunks = [
                chunk["text"]
                for chunk in metadata_chunks
                ]

                embeddings = generate_embeddings(
                chunks
                )
                vector_store = create_vector_store(embeddings)

            st.session_state.chunks = chunks
            st.session_state.metadata_chunks = metadata_chunks
            st.session_state.vector_store = vector_store

            st.success("✅ Video Analysis Complete!")

#video information

if st.session_state.metadata:

    st.divider()

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(
            st.session_state.metadata["thumbnail"],
            use_container_width=True
        )

    with col2:
        st.subheader(st.session_state.metadata["title"])
        st.write(f"👤 {st.session_state.metadata['channel']}")

#ai summary

if st.session_state.summary:

    st.divider()
    st.subheader("📝 AI Summary")
    st.write(st.session_state.summary)

#key takeaways

if st.session_state.takeaways:

    st.divider()
    st.subheader("💡 Key Takeaways")

    for takeaway in st.session_state.takeaways:
        st.success(takeaway)

#main topics

if st.session_state.topics:

    st.divider()
    st.subheader("🧠 Main Topics")

    cols = st.columns(2)

    for i, topic in enumerate(st.session_state.topics):
        with cols[i % 2]:
            st.info(topic)


#download report

if st.session_state.summary:

    st.divider()

    st.subheader("📄 Export Report")

    pdf = generate_pdf(
         st.session_state.metadata,
         st.session_state.topics[0] if st.session_state.topics else "AI Knowledge Report",
         st.session_state.summary,
         st.session_state.takeaways,
         st.session_state.topics
)

    st.download_button(
        label="⬇ Download PDF Report",
        data=pdf,
        file_name="Lumina_AI_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
#transcript

if st.session_state.transcript:

    st.divider()
    st.subheader("📜 Transcript")

    st.write("The transcript is hidden to keep the interface clean.")

    if st.button("📜 View Full Transcript", use_container_width=True):
        show_transcript()

#ask question

#chat

if st.session_state.vector_store is not None:

    st.divider()

    st.subheader("💬 Chat with Lumina AI")

    #display previous messages

    for message in st.session_state.memory.get_messages():

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask anything about this video..."
    )

    if question:
        st.session_state.memory.add_message(
            "user",
             question
)

        with st.chat_message("user"):

            st.markdown(question)

        with st.spinner(
            "Searching Knowledge Base..."
        ):

            retrieved_chunks = retrieve_documents(
                question,
                st.session_state.vector_store,
                st.session_state.metadata_chunks
            )

            context_data = build_context(retrieved_chunks)

        with st.spinner(
            "Thinking..."
        ):

            answer = ask_question(
    question=question,
    context=context_data["context"],
    messages=st.session_state.memory.get_recent_messages()
)

        st.session_state.memory.add_message(
    "assistant",
    answer
)

        with st.chat_message("assistant"):

            st.markdown(answer)

        st.caption("📚 Sources")

        for source in context_data["sources"]:
            st.write(source)

        st.caption("📍 Mentioned in video")

        for chunk in retrieved_chunks:
            start = int(chunk["start"])
            minutes = start // 60
            seconds = start % 60
            st.write(f"• {minutes:02}:{seconds:02}")
            

            