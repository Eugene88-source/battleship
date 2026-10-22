from dataclasses import dataclass, field
from enum import Enum, auto


class CellState(Enum):
    EMPTY = auto()
    SHIP = auto()
    MISS = auto()
    HIT = auto()
    SUNK = auto()


class ShotResult(Enum):
    MISS = auto()
    HIT = auto()
    SUNK = auto()
    ALREADY_SHOT = auto()


@dataclass
class Ship:
    cells: set[tuple[int, int]]
    hits: set[tuple[int, int]] = field(default_factory=set)

    def is_sunk(self) -> bool:
        return self.hits >= self.cells
