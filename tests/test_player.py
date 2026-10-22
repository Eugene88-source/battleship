import unittest

from apps.board import Board
from apps.config import BOARD_SIZE
from apps.player import ComputerPlayer, HumanPlayer, format_coordinate, parse_coordinate


class ParseCoordinateTest(unittest.TestCase):
    def test_valid(self) -> None:
        self.assertEqual(parse_coordinate("B7", BOARD_SIZE), (1, 6))
        self.assertEqual(parse_coordinate("b7", BOARD_SIZE), (1, 6))
        self.assertEqual(parse_coordinate(" a1 ", BOARD_SIZE), (0, 0))
        self.assertEqual(parse_coordinate("J10", BOARD_SIZE), (9, 9))

    def test_invalid(self) -> None:
        for text in ("K1", "A0", "A11", "7B", "", "B", "B7x", "Б7"):
            with self.subTest(text=text):
                self.assertIsNone(parse_coordinate(text, BOARD_SIZE))

    def test_format_is_inverse_of_parse(self) -> None:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                self.assertEqual(parse_coordinate(format_coordinate(x, y), BOARD_SIZE), (x, y))


class HumanPlayerTest(unittest.TestCase):
    def test_asks_again_until_valid(self) -> None:
        answers = iter(["zz", "C3"])
        messages: list[str] = []
        player = HumanPlayer("Ви", read=lambda prompt: next(answers), write=messages.append)

        self.assertEqual(player.choose_target(Board()), (2, 2))
        self.assertEqual(len(messages), 1)


class ComputerPlayerTest(unittest.TestCase):
    def test_never_shoots_same_cell_twice(self) -> None:
        enemy = Board()
        enemy.place_fleet_randomly()
        player = ComputerPlayer("Комп'ютер")

        shots = set()
        for _ in range(BOARD_SIZE * BOARD_SIZE):
            x, y = player.choose_target(enemy)
            enemy.receive_shot(x, y)
            shots.add((x, y))

        self.assertEqual(len(shots), BOARD_SIZE * BOARD_SIZE)
        self.assertTrue(enemy.all_sunk())


if __name__ == "__main__":
    unittest.main()
