import random
import string
from abc import ABC, abstractmethod
from collections.abc import Callable

from apps.board import Board
from apps.models import CellState


LETTERS = string.ascii_uppercase


def parse_coordinate(text: str, size: int) -> tuple[int, int] | None:
    """«B7» → (1, 6): літера — стовпець, число — рядок. None, якщо формат невірний або клітинка поза полем."""
    text = text.strip().upper()
    if len(text) < 2 or text[0] not in LETTERS[:size] or not text[1:].isdigit():
        return None
    x = LETTERS.index(text[0])
    y = int(text[1:]) - 1
    if not 0 <= y < size:
        return None
    return x, y


def format_coordinate(x: int, y: int) -> str:
    return f"{LETTERS[x]}{y + 1}"


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.board = Board()

    @abstractmethod
    def choose_target(self, enemy: Board) -> tuple[int, int]:
        ...


class HumanPlayer(Player):
    def __init__(
        self,
        name: str,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
    ) -> None:
        super().__init__(name)
        self.read = read
        self.write = write

    def choose_target(self, enemy: Board) -> tuple[int, int]:
        while True:
            target = parse_coordinate(self.read("Ваш постріл (напр. B7): "), enemy.size)
            if target is not None:
                return target
            self.write("Невірні координати. Приклад: B7")


class ComputerPlayer(Player):
    def choose_target(self, enemy: Board) -> tuple[int, int]:
        # Кораблів суперника комп'ютер не бачить: SHIP для нього — така сама нестріляна клітинка.
        return random.choice([
            (x, y)
            for y in range(enemy.size)
            for x in range(enemy.size)
            if enemy.grid[y][x] in (CellState.EMPTY, CellState.SHIP)
        ])
