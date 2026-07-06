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


# retrieve document chunks

def retrieve_documents(
    question,
    index,
    vector_records,
    top_k=3
):

    question_embedding = model.encode(
        [question]
    )

    question_embedding = np.array(
        question_embedding
    ).astype("float32")

    distances, indices = index.search(
        question_embedding,
        top_k
    )

    results = []

    for idx in indices[0]:

        if idx == -1:
            continue

        results.append(
            vector_records[idx]
        )

    return results

