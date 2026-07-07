from dataclasses import dataclass
import numpy as np

from services.models.chunk import Chunk


@dataclass
class VectorRecord:

    embedding: np.ndarray

    chunk: Chunk