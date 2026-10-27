import os
import re
import unittest
from unittest import mock

from apps.board import Board
from apps.models import Ship
from apps.renderer import render_board, render_boards, supports_color


ANSI = re.compile(r"\033\[[0-9;]*m")


class RenderBoardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board()
        self.board.place_ship(Ship({(0, 0), (1, 0)}))
        self.board.place_ship(Ship({(5, 5)}))
        self.board.receive_shot(0, 0)  # влучання
        self.board.receive_shot(9, 9)  # промах
        self.board.receive_shot(5, 5)  # потоплено

    def test_header_and_rows(self) -> None:
        lines = render_board(self.board, reveal=True)
        self.assertEqual(lines[0], "   A B C D E F G H I J")
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines[1], " 1 x ■ . . . . . . . .")
        self.assertEqual(lines[5], " 5 . . . . o o o . . .")
        self.assertEqual(lines[6], " 6 . . . . o # o . . .")
        self.assertEqual(lines[7], " 7 . . . . o o o . . .")
        self.assertEqual(lines[10], "10 . . . . . . . . . o")

    def test_hidden_ships(self) -> None:
        lines = render_board(self.board, reveal=False)
        self.assertEqual(lines[1], " 1 x . . . . . . . . .")
        self.assertNotIn("■", "".join(lines))

    def test_enemy_ships_hidden_side_by_side(self) -> None:
        own = Board()
        own.place_ship(Ship({(3, 3)}))
        text = render_boards(own, self.board)

        self.assertIn("Ваше поле", text)
        self.assertIn("Поле суперника", text)
        self.assertEqual(text.count("■"), 1)  # лише свій корабель


class ColorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board()
        self.board.place_ship(Ship({(0, 0), (1, 0)}))
        self.board.receive_shot(0, 0)  # влучання
        self.board.receive_shot(9, 9)  # промах

    def test_cells_are_colored(self) -> None:
        lines = render_board(self.board, reveal=True, color=True)
        self.assertIn("\033[31mx\033[0m", lines[1])
        self.assertIn("\033[34m■\033[0m", lines[1])
        self.assertIn("\033[90mo\033[0m", lines[10])

    def test_same_text_without_codes(self) -> None:
        for reveal in (True, False):
            plain = render_board(self.board, reveal=reveal)
            colored = render_board(self.board, reveal=reveal, color=True)
            self.assertEqual([ANSI.sub("", line) for line in colored], plain)

    def test_hidden_ship_not_colored(self) -> None:
        lines = render_board(self.board, reveal=False, color=True)
        self.assertNotIn("\033[34m", "".join(lines))

    def test_side_by_side_alignment_kept(self) -> None:
        own = Board()
        own.place_ship(Ship({(3, 3)}))
        colored = render_boards(own, self.board, color=True)
        self.assertEqual(ANSI.sub("", colored), render_boards(own, self.board))

    def test_no_color_env_disables_colors(self) -> None:
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            self.assertFalse(supports_color())


if __name__ == "__main__":
    unittest.main()
