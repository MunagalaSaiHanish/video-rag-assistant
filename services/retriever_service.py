import numpy as np

from services.embedding_service import model


def retrieve_chunks(question, index, chunks, top_k=3):

    question_embedding = model.encode([question])

    question_embedding = np.array(question_embedding).astype("float32")

    distances, indices = index.search(question_embedding, top_k)

    retrieved_chunks = []

    for idx in indices[0]:
        retrieved_chunks.append(chunks[idx])

    return retrieved_chunks