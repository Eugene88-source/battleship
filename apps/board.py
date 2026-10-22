import random

from apps.config import BOARD_SIZE, FLEET
from apps.models import CellState, Ship, ShotResult


MAX_PLACEMENT_ATTEMPTS = 1000


class Board:
    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size = size
        self.grid: list[list[CellState]] = [
            [CellState.EMPTY] * size for _ in range(size)
        ]
        self.ships: list[Ship] = []

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def can_place(self, cells: set[tuple[int, int]]) -> bool:
        if not cells or not _is_straight_line(cells):
            return False
        for x, y in cells:
            if not self.in_bounds(x, y):
                return False
            for nx, ny in self._area(x, y):
                if self.grid[ny][nx] == CellState.SHIP:
                    return False
        return True

    def place_ship(self, ship: Ship) -> None:
        if not self.can_place(ship.cells):
            raise ValueError(f"Неможливо розмістити корабель у клітинках {sorted(ship.cells)}")
        self.ships.append(ship)
        for x, y in ship.cells:
            self.grid[y][x] = CellState.SHIP

    def place_fleet_randomly(self) -> None:
        lengths = [
            length
            for length, count in sorted(FLEET.items(), reverse=True)
            for _ in range(count)
        ]
        while True:
            self._clear()
            if all(self._place_randomly(length) for length in lengths):
                return

    def receive_shot(self, x: int, y: int) -> ShotResult:
        if not self.in_bounds(x, y):
            raise ValueError(f"Постріл за межами поля: ({x}, {y})")

        state = self.grid[y][x]
        if state in (CellState.MISS, CellState.HIT, CellState.SUNK):
            return ShotResult.ALREADY_SHOT
        if state == CellState.EMPTY:
            self.grid[y][x] = CellState.MISS
            return ShotResult.MISS

        ship = self._ship_at(x, y)
        ship.hits.add((x, y))
        if ship.is_sunk():
            for sx, sy in ship.cells:
                self.grid[sy][sx] = CellState.SUNK
            return ShotResult.SUNK
        self.grid[y][x] = CellState.HIT
        return ShotResult.HIT

    def all_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)

    def _clear(self) -> None:
        self.grid = [[CellState.EMPTY] * self.size for _ in range(self.size)]
        self.ships = []

    def _place_randomly(self, length: int) -> bool:
        for _ in range(MAX_PLACEMENT_ATTEMPTS):
            horizontal = random.choice((True, False))
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if horizontal:
                cells = {(x + i, y) for i in range(length)}
            else:
                cells = {(x, y + i) for i in range(length)}
            if self.can_place(cells):
                self.place_ship(Ship(cells))
                return True
        return False

    def _area(self, x: int, y: int) -> list[tuple[int, int]]:
        """Клітинка разом з усіма сусідами (включно з діагональними), що лежать на полі."""
        return [
            (x + dx, y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if self.in_bounds(x + dx, y + dy)
        ]

    def _ship_at(self, x: int, y: int) -> Ship:
        for ship in self.ships:
            if (x, y) in ship.cells:
                return ship
        raise LookupError(f"На клітинці ({x}, {y}) немає корабля")


def _is_straight_line(cells: set[tuple[int, int]]) -> bool:
    xs = {x for x, _ in cells}
    ys = {y for _, y in cells}
    if len(xs) == 1:
        coords = sorted(ys)
    elif len(ys) == 1:
        coords = sorted(xs)
    else:
        return False
    return coords == list(range(coords[0], coords[0] + len(coords)))
