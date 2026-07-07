from services.models.workspace import Workspace
from services.knowledge_base import KnowledgeBase


class WorkspaceManager:

    def __init__(self):

        self.workspace = Workspace.create()

        self.knowledge_base = KnowledgeBase()

    def add_document(self, document):

        self.workspace.documents.append(
            document
        )

        self.knowledge_base.add_document(
            document
        )

    def search(self, question):

        return self.knowledge_base.retrieve(
            question
        )

    def clear(self):

        self.workspace.documents.clear()

        self.knowledge_base.clear()