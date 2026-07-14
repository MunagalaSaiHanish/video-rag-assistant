from dataclasses import dataclass
from typing import Dict
import uuid


@dataclass
class Chunk:

    id: str

    document_id: str

    text: str

    metadata: Dict