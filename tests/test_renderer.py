import unittest

from apps.board import Board
from apps.models import Ship
from apps.renderer import render_board, render_boards


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
        self.assertEqual(lines[6], " 6 . . . . . # . . . .")
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


if __name__ == "__main__":
    unittest.main()
