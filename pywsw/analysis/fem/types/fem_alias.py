__all__ = (
    "Arr",
    "IDs",
    "IndexType",
    "Mat",
    "TagType",
    "Vec",
)

from collections.abc import Hashable
from typing import Any

import numpy as np

type TagType = Hashable
type IndexType = int

type IDs = np.ndarray[tuple[int], IndexType]
type Vec = np.ndarray[tuple[int], float]
type Mat = np.ndarray[tuple[int, int], float]
type Arr = np.ndarray[tuple[Any], float]
