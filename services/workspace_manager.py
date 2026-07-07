from services.models.workspace import Workspace


class WorkspaceManager:

    def __init__(self):

        self.workspace = Workspace.create()

    def add_document(
        self,
        text,
        metadata
    ):

        self.workspace.documents.append(
            metadata
        )

        self.workspace.knowledge_base.add_document(
            text,
            metadata
        )

    def ask(
        self,
        question
    ):

        retrieved_documents = (
            self.workspace
            .knowledge_base
            .retrieve(question)
        )

        return retrieved_documents

    def memory(self):

        return self.workspace.memory

    def clear(self):

        self.workspace.documents.clear()

        self.workspace.memory.clear()

        self.workspace.knowledge_base.clear()