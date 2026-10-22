import random
from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Callable
from functools import cache

from apps.board import Board, fleet_lengths
from apps.coordinates import parse_coordinate, parse_ship
from apps.models import CellState, Ship
from apps.renderer import render_board


RESTART = "заново"


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.board = Board()

    def place_fleet(self) -> None:
        self.board.place_fleet_randomly()

    @abstractmethod
    def choose_target(self, enemy: Board) -> tuple[int, int]:
        ...


class HumanPlayer(Player):
    def __init__(
        self,
        name: str,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
        color: bool = False,
    ) -> None:
        super().__init__(name)
        self.read = read
        self.write = write
        self.color = color

    def place_fleet(self) -> None:
        answer = self.read("Розставити кораблі вручну? (т — так, Enter — випадково): ")
        if answer.strip().lower() in ("т", "так", "y", "yes"):
            self._place_fleet_manually()
        else:
            super().place_fleet()

    def _place_fleet_manually(self) -> None:
        self.write(
            "Введіть початок і кінець корабля, напр. B2 B5; однопалубний — одна клітинка, напр. C7.\n"
            "Кораблі стоять прямо й не торкаються один одного навіть кутом. "
            f"Почати розстановку спочатку — «{RESTART}»."
        )
        self.board.clear()
        lengths = fleet_lengths()
        while len(self.board.ships) < len(lengths):
            length = lengths[len(self.board.ships)]
            self.write("\n" + "\n".join(render_board(self.board, reveal=True, color=self.color)))
            answer = self.read(f"Корабель на {length} кл.: ")

            if answer.strip().lower() == RESTART:
                self.board.clear()
                continue

            cells = parse_ship(answer, self.board.size)
            if cells is None:
                self.write("Невірний формат. Приклад: B2 B5")
            elif len(cells) != length:
                self.write(f"Потрібен корабель на {length} кл., а введено {len(cells)}.")
            elif not self.board.can_place(cells):
                self.write("Сюди не можна: корабель торкається іншого.")
            else:
                self.board.place_ship(Ship(cells))

    def choose_target(self, enemy: Board) -> tuple[int, int]:
        while True:
            target = parse_coordinate(self.read("Ваш постріл (напр. B7): "), enemy.size)
            if target is not None:
                return target
            self.write("Невірні координати. Приклад: B7")


class ComputerPlayer(Player):
    """Стріляє туди, де корабель найімовірніший, а влучивши — добиває поранений корабель.

    Кораблів суперника комп'ютер не бачить: SHIP для нього — така сама нестріляна клітинка.
    Усе, що він знає, — склад флоту і позначки пострілів на полі суперника (MISS, HIT, SUNK).
    """

    def choose_target(self, enemy: Board) -> tuple[int, int]:
        weights = self._weights(enemy)
        if weights:
            best = max(weights.values())
            candidates = [cell for cell, weight in weights.items() if weight == best]
        else:
            # Флот уже потоплено — сюди гра не доходить, але без кандидатів random.choice впав би.
            candidates = [
                (x, y)
                for y in range(enemy.size)
                for x in range(enemy.size)
                if enemy.grid[y][x] in (CellState.EMPTY, CellState.SHIP)
            ]
        return random.choice(candidates)

    def _weights(self, enemy: Board) -> Counter[tuple[int, int]]:
        """Скільки можливих положень кораблів, що лишилися, проходить через кожну клітинку.

        Якщо є влучання, рахуються лише положення, що накривають усі влучання: вони завжди
        належать одному кораблю, бо комп'ютер добиває корабель до кінця, перш ніж шукати інший.
        """
        hits = {
            (x, y)
            for y in range(enemy.size)
            for x in range(enemy.size)
            if enemy.grid[y][x] == CellState.HIT
        }
        allowed = hits | {
            (x, y)
            for y in range(enemy.size)
            for x in range(enemy.size)
            if self._is_open(enemy, x, y)
        }

        weights: Counter[tuple[int, int]] = Counter()
        for length, count in self._remaining_ships(enemy).items():
            for line in _lines(enemy.size, length):
                if hits.issubset(line) and allowed.issuperset(line):
                    for cell in line:
                        if cell not in hits:
                            weights[cell] += count
        return weights

    @staticmethod
    def _remaining_ships(enemy: Board) -> Counter[int]:
        """Довжини ще не потоплених кораблів: увесь флот мінус потоплені кораблі на полі."""
        remaining = Counter(fleet_lengths())
        seen: set[tuple[int, int]] = set()
        for y in range(enemy.size):
            for x in range(enemy.size):
                if enemy.grid[y][x] != CellState.SUNK or (x, y) in seen:
                    continue
                # Обходимо потоплений корабель: кораблі не торкаються, тож сусідні SUNK — це він сам.
                stack, length = [(x, y)], 0
                seen.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    length += 1
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if (nx, ny) not in seen and enemy.in_bounds(nx, ny) and enemy.grid[ny][nx] == CellState.SUNK:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
                remaining[length] -= 1
        return +remaining

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


@cache
def _lines(size: int, length: int) -> list[tuple[tuple[int, int], ...]]:
    """Усі положення корабля довжини length на полі size×size: горизонтальні й вертикальні."""
    horizontal = [
        tuple((x + i, y) for i in range(length))
        for y in range(size)
        for x in range(size - length + 1)
    ]
    if length == 1:
        return horizontal
    vertical = [
        tuple((x, y + i) for i in range(length))
        for x in range(size)
        for y in range(size - length + 1)
    ]
    return horizontal + vertical
