# knowledge base builder


class KnowledgeBase:

    def __init__(self):

        self.documents = []

    # add document

    def add_document(
        self,
        text,
        metadata
    ):

        self.documents.append(
            {
                "text": text,
                "metadata": metadata
            }
        )

    # return all documents

    def get_documents(self):

        return self.documents

    # clear knowledge base

    def clear(self):

        self.documents = []