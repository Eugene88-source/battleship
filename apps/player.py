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
    """Шукає кораблі випадковими пострілами, а влучивши — добиває поранений корабель.

    Кораблів суперника комп'ютер не бачить: SHIP для нього — така сама нестріляна клітинка.
    Усе, що він знає, — позначки пострілів на полі суперника (MISS, HIT, SUNK).
    """

    def choose_target(self, enemy: Board) -> tuple[int, int]:
        candidates = self._finishing_shots(enemy) or self._open_cells(enemy)
        if not candidates:
            # Флот уже потоплено — сюди гра не доходить, але без кандидатів random.choice впав би.
            candidates = [
                (x, y)
                for y in range(enemy.size)
                for x in range(enemy.size)
                if enemy.grid[y][x] in (CellState.EMPTY, CellState.SHIP)
            ]
        return random.choice(candidates)

    def _finishing_shots(self, enemy: Board) -> list[tuple[int, int]]:
        """Клітинки, де може продовжуватися поранений (влучений, але не потоплений) корабель."""
        hits = [
            (x, y)
            for y in range(enemy.size)
            for x in range(enemy.size)
            if enemy.grid[y][x] == CellState.HIT
        ]
        if not hits:
            return []

        xs = {x for x, _ in hits}
        ys = {y for _, y in hits}
        if len(hits) > 1 and len(ys) == 1:
            # Кілька влучань в один рядок — корабель горизонтальний: стріляємо з кінців.
            y = hits[0][1]
            ends = [(min(xs) - 1, y), (max(xs) + 1, y)]
        elif len(hits) > 1 and len(xs) == 1:
            x = hits[0][0]
            ends = [(x, min(ys) - 1), (x, max(ys) + 1)]
        else:
            ends = [
                (x + dx, y + dy)
                for x, y in hits
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            ]
        return [cell for cell in ends if self._is_open(enemy, *cell)]

    def _open_cells(self, enemy: Board) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y in range(enemy.size)
            for x in range(enemy.size)
            if self._is_open(enemy, x, y)
        ]

    @staticmethod
    def _is_open(enemy: Board, x: int, y: int) -> bool:
        """Сюди ще не стріляли і тут може бути корабель: поруч із потопленим кораблів не буває."""
        if not enemy.in_bounds(x, y) or enemy.grid[y][x] not in (CellState.EMPTY, CellState.SHIP):
            return False
        return not any(
            enemy.in_bounds(x + dx, y + dy) and enemy.grid[y + dy][x + dx] == CellState.SUNK
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
        )
