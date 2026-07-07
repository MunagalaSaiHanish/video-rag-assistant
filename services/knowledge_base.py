import numpy as np

from services.chunk_service import chunk_text
from services.embedding_service import generate_embeddings
from services.vector_store import create_vector_store
from services.retriever import Retriever


class KnowledgeBase:

    def __init__(self):

        self.vector_records = []
        self.index = None

    def add_document(
        self,
        text,
        metadata
    ):

        chunks = chunk_text(text)

        embeddings = generate_embeddings(chunks)
        embeddings = np.array(
            embeddings
        ).astype("float32")

        new_records = []

        for chunk in chunks:

            new_records.append(
                {
                    "text": chunk,
                    "metadata": metadata
                }
            )

        self.vector_records.extend(
            new_records
        )

        if self.index is None:

            self.index = create_vector_store(
                embeddings
            )

        else:

            self.index.add(
                embeddings
            )

    def retrieve(
        self,
        question,
        top_k=3
    ):

        if self.index is None:

            return []

        retriever = Retriever(
            self.index,
            self.vector_records
        )

        return retriever.search(
            question,
            top_k
        )

    def clear(self):

        self.vector_records.clear()

        self.index = None