import streamlit as st

from services.youtube_service import extract_video_id
from services.transcript_service import (
    get_transcript,
    transcript_to_text
)
from services.chunk_service import chunk_text
from services.embedding_service import generate_embeddings
from services.vector_store import create_vector_store
from services.retriever_service import retrieve_chunks
from services.llm_service import summarize, ask_question


st.set_page_config(
    page_title="AI Video Analyzer",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 AI Video Analyzer")

# -----------------------------
# Initialize Session State
# -----------------------------
if "knowledge_ready" not in st.session_state:
    st.session_state.knowledge_ready = False

if "plain_text" not in st.session_state:
    st.session_state.plain_text = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "index" not in st.session_state:
    st.session_state.index = None

# -----------------------------
# Analyze Section
# -----------------------------

video_url = st.text_input("Paste YouTube URL")

if st.button("Analyze Video"):

    video_id = extract_video_id(video_url)

    if video_id is None:
        st.error("Invalid YouTube URL")

    else:

        raw_transcript = get_transcript(video_id)

        if raw_transcript is None:

            st.warning(
                "Transcript couldn't be fetched.\n"
                "YouTube may have blocked the request."
            )

        else:

            # Transcript
            plain_text = transcript_to_text(raw_transcript)

            # Chunking
            chunks = chunk_text(plain_text)

            # Embeddings
            embeddings = generate_embeddings(chunks)

            # Vector Store
            index = create_vector_store(embeddings)

            # Summary
            with st.spinner("Generating Summary..."):
                summary = summarize(plain_text)

            # Save in Session
            st.session_state.plain_text = plain_text
            st.session_state.summary = summary
            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.knowledge_ready = True

            st.success("✅ Knowledge Base Created Successfully!")

# -----------------------------
# Display Stored Results
# -----------------------------

if st.session_state.knowledge_ready:

    st.subheader("📄 Transcript")

    st.text_area(
        "Transcript",
        st.session_state.plain_text,
        height=250
    )

    st.subheader("📦 Chunks")

    st.write(f"Total Chunks : {len(st.session_state.chunks)}")

    for i, chunk in enumerate(st.session_state.chunks):

        with st.expander(f"Chunk {i+1}"):

            st.write(chunk)

    st.subheader("📝 Summary")

    st.write(st.session_state.summary)

    st.divider()

    st.subheader("💬 Chat with the Video")

    question = st.text_input("Ask a Question")

    if st.button("Ask"):

        retrieved_chunks = retrieve_chunks(
            question,
            st.session_state.index,
            st.session_state.chunks
        )

        context = "\n\n".join(retrieved_chunks)

        answer = ask_question(
            question,
            context
        )

        st.subheader("📚 Retrieved Chunks")

        for i, chunk in enumerate(retrieved_chunks):

            with st.expander(f"Retrieved Chunk {i+1}"):

                st.write(chunk)

        st.subheader("🤖 Answer")

        st.write(answer)