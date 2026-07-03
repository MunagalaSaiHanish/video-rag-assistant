import streamlit as st

from services.youtube_service import extract_video_id
from services.transcript_service import (
    get_transcript,
    transcript_to_text
)
from services.chunk_service import chunk_text
from services.embedding_service import generate_embeddings
from services.vector_store import (
    create_vector_store,
    retrieve_chunks
)
from services.llm_service import (
    analyze_video,
    ask_question
)

#page setup

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🎥",
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

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

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

#Main app

#header

st.title("🎥 AI Knowledge Assistant")

st.caption(
    "Analyze YouTube videos using AI"
)

st.divider()

#input of YT url

video_url = st.text_input(
    "🔗 Paste YouTube URL"
)

#extract video id, transcript, ai analysis, chunks and embeddings

if st.button(
    "🚀 Analyze Video",
    use_container_width=True
):

    video_id = extract_video_id(video_url)

    if video_id is None:

        st.error("Invalid YouTube URL")

    else:

        with st.spinner("Fetching Transcript..."):

            raw_transcript = get_transcript(video_id)

        if raw_transcript is None:

            st.error(
                "Couldn't fetch transcript."
            )

        else:

            plain_text = transcript_to_text(raw_transcript)

            st.session_state.transcript = plain_text

            #generate ai analysis

            with st.spinner("Analyzing Video..."):

                analysis = analyze_video(plain_text)

            st.session_state.summary = analysis["summary"]
            st.session_state.takeaways = analysis["takeaways"]
            st.session_state.topics = analysis["topics"]

            #build vector database

            with st.spinner("Building Knowledge Base..."):

                chunks = chunk_text(plain_text)

                embeddings = generate_embeddings(chunks)

                vector_store = create_vector_store(
                    embeddings
                )

            st.session_state.chunks = chunks

            st.session_state.vector_store = vector_store

            st.success(
                "✅ Video Analysis Complete!"
            )

#ai summary

if st.session_state.summary:

    st.divider()

    st.subheader("📝 AI Summary")

    st.write(
        st.session_state.summary
    )

#key takeaways

if st.session_state.takeaways:

    st.divider()

    st.subheader("💡 Key Takeaways")

    for takeaway in st.session_state.takeaways:

        st.success(
            takeaway
        )

#main topics

if st.session_state.topics:

    st.divider()

    st.subheader("🧠 Main Topics")

    cols = st.columns(2)

    for i, topic in enumerate(
        st.session_state.topics
    ):

        with cols[i % 2]:

            st.info(
                topic
            )

#transcript

if st.session_state.transcript:

    st.divider()

    st.subheader("📜 Transcript")

    st.write(
        "The full transcript is hidden to keep the interface clean."
    )

    if st.button(
        "📜 View Full Transcript",
        use_container_width=True
    ):

        show_transcript()

#ask question

if st.session_state.vector_store is not None:

    st.divider()

    st.subheader("💬 Ask Anything About This Video")

    question = st.text_input(
        "Your Question"
    )

    if st.button(
        "Ask AI",
        use_container_width=True
    ):

        if question.strip() == "":

            st.warning(
                "Please enter a question."
            )

        else:

            #retrieve relevant chunks

            with st.spinner(
                "Searching Knowledge Base..."
            ):

                retrieved_chunks = retrieve_chunks(
                    question,
                    st.session_state.vector_store,
                    st.session_state.chunks
                )

                context = "\n\n".join(
                    retrieved_chunks
                )

            #generate answer

            with st.spinner(
                "Generating Answer..."
            ):

                answer = ask_question(
                    question,
                    context
                )

            st.subheader("🤖 AI Answer")

            st.write(
                answer
            )
            