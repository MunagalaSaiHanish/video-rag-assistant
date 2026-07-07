from dataclasses import dataclass, field
from typing import List

from services.models.document import Document


@dataclass
class Workspace:

    id: str
