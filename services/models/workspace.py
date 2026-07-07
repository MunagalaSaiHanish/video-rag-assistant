from dataclasses import dataclass, field
from typing import List
import uuid

from services.memory_service import MemoryService
from services.knowledge_base import KnowledgeBase


@dataclass
class Workspace:

    id: str

    name: str

    documents: List = field(default_factory=list)

    knowledge_base: KnowledgeBase = field(
        default_factory=KnowledgeBase
    )

    memory: MemoryService = field(
        default_factory=MemoryService
    )

    @staticmethod
    def create(
        name="Untitled Workspace"
    ):

        return Workspace(

            id=str(uuid.uuid4()),

            name=name
        )