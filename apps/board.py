import random

from apps.config import BOARD_SIZE, FLEET, ConfigError
from apps.coordinates import LETTERS
from apps.models import CellState, Ship, ShotResult


MAX_PLACEMENT_ATTEMPTS = 1000
MAX_FLEET_ATTEMPTS = 100


class Board:
    def __init__(self, size: int = BOARD_SIZE) -> None:
        if not 1 <= size <= len(LETTERS):
            raise ValueError(f"Розмір поля має бути від 1 до {len(LETTERS)}, а не {size}")
        self.size = size
        self.grid: list[list[CellState]]
        self.ships: list[Ship]
        self.clear()

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def can_place(self, cells: set[tuple[int, int]]) -> bool:
        if not cells or not _is_straight_line(cells):
            return False
        for x, y in cells:
            if not self.in_bounds(x, y) or self.grid[y][x] != CellState.EMPTY:
                return False
            # Поруч не має бути жодного корабля — ні цілого, ні підбитого, ні потопленого.
            for nx, ny in self._area(x, y):
                if self.grid[ny][nx] in (CellState.SHIP, CellState.HIT, CellState.SUNK):
                    return False
        return True

    def place_ship(self, ship: Ship) -> None:
        # Спершу дешеві перевірки самого корабля, потім — сканування поля.
        if not ship.cells:
            raise ValueError("Корабель без жодної клітинки")
        if ship.hits:
            raise ValueError(f"Корабель уже має влучання {sorted(ship.hits)}: ставити можна лише цілий")
        length = len(ship.cells)
        placed = sum(1 for other in self.ships if len(other.cells) == length)
        if placed >= FLEET.get(length, 0):
            raise ValueError(f"У флоті немає місця для ще одного корабля на {length} кл.: {fleet_lengths()}")
        if not self.can_place(ship.cells):
            raise ValueError(f"Неможливо розмістити корабель у клітинках {sorted(ship.cells)}")
        self.ships.append(ship)
        for x, y in ship.cells:
            self.grid[y][x] = CellState.SHIP

    def place_fleet_randomly(self) -> None:
        for _ in range(MAX_FLEET_ATTEMPTS):
            self.clear()
            if all(self._place_randomly(length) for length in fleet_lengths()):
                return
        self.clear()
        raise ConfigError(f"Флот {fleet_lengths()} не вміщається на поле {self.size}×{self.size}")

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
                # За класичними правилами клітинки навколо потопленого корабля відкриваються як промахи.
                for nx, ny in self._area(sx, sy):
                    if self.grid[ny][nx] == CellState.EMPTY:
                        self.grid[ny][nx] = CellState.MISS
                self.grid[sy][sx] = CellState.SUNK
            return ShotResult.SUNK
        self.grid[y][x] = CellState.HIT
        return ShotResult.HIT

    def has_full_fleet(self) -> bool:
        """На полі рівно той флот, що заданий у FLEET: ні кораблем більше, ні менше."""
        return bool(self.ships) and self.ship_lengths() == fleet_lengths()

    def ship_lengths(self) -> list[int]:
        """Довжини розставлених кораблів, від найбільшого — у тому ж порядку, що й fleet_lengths()."""
        return sorted((len(ship.cells) for ship in self.ships), reverse=True)

    def all_sunk(self) -> bool:
        return bool(self.ships) and all(ship.is_sunk() for ship in self.ships)

    def clear(self) -> None:
        self.grid = [[CellState.EMPTY] * self.size for _ in range(self.size)]
        self.ships = []

    def _place_randomly(self, length: int) -> bool:
        if length > self.size:
            return False
        for _ in range(MAX_PLACEMENT_ATTEMPTS):
            horizontal = random.choice((True, False))
            # Початок обираємо так, щоб корабель не виходив за край поля.
            x = random.randrange(self.size - length + 1 if horizontal else self.size)
            y = random.randrange(self.size if horizontal else self.size - length + 1)
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


def fleet_lengths() -> list[int]:
    """Довжини кораблів флоту, від найбільшого: [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]."""
    return [
        length
        for length, count in sorted(FLEET.items(), reverse=True)
        for _ in range(count)
    ]
