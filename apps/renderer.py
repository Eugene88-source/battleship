import os
import sys

from apps.board import Board
from apps.models import CellState, ShotResult
from apps.coordinates import LETTERS


SYMBOLS = {
    CellState.EMPTY: ".",
    CellState.SHIP: "■",
    CellState.MISS: "o",
    CellState.HIT: "x",
    CellState.SUNK: "#",
}

# ANSI-коди кольорів; порожня клітинка — без кольору.
COLORS = {
    CellState.SHIP: "34",    # синій
    CellState.MISS: "90",    # сірий
    CellState.HIT: "31",     # червоний
    CellState.SUNK: "1;31",  # жирний червоний
}

GAP = "     "


def supports_color() -> bool:
    """Кольори — лише в терміналі і якщо їх не вимкнено змінною NO_COLOR."""
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # вмикає обробку ANSI-кодів у консолі Windows
    return True


def _cell(state: CellState, color: bool) -> str:
    symbol = SYMBOLS[state]
    code = COLORS.get(state)
    return f"\033[{code}m{symbol}\033[0m" if color and code else symbol


def render_board(board: Board, reveal: bool, color: bool = False) -> list[str]:
    """Поле рядками: заголовок зі стовпцями і рядок на кожен ряд. Без reveal кораблі приховано."""
    lines = ["   " + " ".join(LETTERS[: board.size])]
    for y, row in enumerate(board.grid):
        cells = [
            _cell(CellState.EMPTY if state == CellState.SHIP and not reveal else state, color)
            for state in row
        ]
        lines.append(f"{y + 1:>2} " + " ".join(cells))
    return lines


def render_boards(own: Board, enemy: Board, reveal_enemy: bool = False, color: bool = False) -> str:
    left = render_board(own, reveal=True, color=color)
    right = render_board(enemy, reveal=reveal_enemy, color=color)
    # Заголовок і рядки поля однакової видимої ширини, тож склеюємо без вирівнювання:
    # з ANSI-кодами f"{a:<{width}}" рахував би й невидимі символи.
    width = len(left[0])
    lines = [f"{'Ваше поле':<{width}}{GAP}Поле суперника"]
    lines += [a + GAP + b for a, b in zip(left, right)]
    return "\n".join(lines)


def describe(result: ShotResult) -> str:
    return {
        ShotResult.MISS: "Промах",
        ShotResult.HIT: "Влучання!",
        ShotResult.SUNK: "Корабель потоплено!",
        ShotResult.ALREADY_SHOT: "Сюди вже стріляли",
    }[result]
