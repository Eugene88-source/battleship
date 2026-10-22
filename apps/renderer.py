from apps.board import Board
from apps.models import CellState, ShotResult
from apps.player import LETTERS


SYMBOLS = {
    CellState.EMPTY: ".",
    CellState.SHIP: "■",
    CellState.MISS: "o",
    CellState.HIT: "x",
    CellState.SUNK: "#",
}

GAP = "     "


def render_board(board: Board, reveal: bool) -> list[str]:
    """Поле рядками: заголовок зі стовпцями і рядок на кожен ряд. Без reveal кораблі приховано."""
    lines = ["   " + " ".join(LETTERS[: board.size])]
    for y, row in enumerate(board.grid):
        cells = [
            SYMBOLS[CellState.EMPTY] if state == CellState.SHIP and not reveal else SYMBOLS[state]
            for state in row
        ]
        lines.append(f"{y + 1:>2} " + " ".join(cells))
    return lines


def render_boards(own: Board, enemy: Board, reveal_enemy: bool = False) -> str:
    left = render_board(own, reveal=True)
    right = render_board(enemy, reveal=reveal_enemy)
    width = len(left[0])
    lines = [f"{'Ваше поле':<{width}}{GAP}Поле суперника"]
    lines += [f"{a:<{width}}{GAP}{b}" for a, b in zip(left, right)]
    return "\n".join(lines)


def describe(result: ShotResult) -> str:
    return {
        ShotResult.MISS: "Промах",
        ShotResult.HIT: "Влучання!",
        ShotResult.SUNK: "Корабель потоплено!",
        ShotResult.ALREADY_SHOT: "Сюди вже стріляли",
    }[result]
