import faiss
import numpy as np

from services.embedding_service import model


#create faiss vector store

def create_vector_store(embeddings):

    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


#retrieve plain text chunks

def retrieve_chunks(question, index, chunks, top_k=3):

    question_embedding = model.encode([question])

    question_embedding = np.array(question_embedding).astype("float32")

    distances, indices = index.search(
        question_embedding,
        top_k
    )

    retrieved_chunks = []

    for idx in indices[0]:

        retrieved_chunks.append(
            chunks[idx]
        )

    return retrieved_chunks


#retrieve chunks with metadata

def retrieve_chunks_with_metadata(
    question,
    index,
    chunks,
    top_k=3
):

    question_embedding = model.encode([question])

    question_embedding = np.array(
        question_embedding
    ).astype("float32")

    distances, indices = index.search(
        question_embedding,
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append(
            {
                "text": chunks[idx]["text"],
                "start": chunks[idx]["start"],
                "end": chunks[idx]["end"]
            }
        )

    return results