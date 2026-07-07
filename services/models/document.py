from dataclasses import dataclass, field
from typing import Dict
import uuid


@dataclass
class Document:

    id: str

    source: str

    title: str

    content: str

    metadata: Dict = field(default_factory=dict)

    @staticmethod
    def create(

        source,

        title,

        content,

        metadata=None

    ):

        if metadata is None:

            metadata = {}

        return Document(

            id=str(uuid.uuid4()),

            source=source,

            title=title,

            content=content,

            metadata=metadata

        )