import unittest

from apps.config import BOARD_SIZE
from apps.coordinates import format_coordinate, parse_coordinate, parse_ship


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


class ParseShipTest(unittest.TestCase):
    def test_horizontal_and_vertical(self) -> None:
        self.assertEqual(parse_ship("B2 E2", BOARD_SIZE), {(1, 1), (2, 1), (3, 1), (4, 1)})
        self.assertEqual(parse_ship("b2-b4", BOARD_SIZE), {(1, 1), (1, 2), (1, 3)})

    def test_ends_in_any_order(self) -> None:
        self.assertEqual(parse_ship("E2 B2", BOARD_SIZE), parse_ship("B2 E2", BOARD_SIZE))

    def test_single_cell(self) -> None:
        self.assertEqual(parse_ship("C7", BOARD_SIZE), {(2, 6)})
        self.assertEqual(parse_ship("C7 C7", BOARD_SIZE), {(2, 6)})

    def test_invalid(self) -> None:
        for text in ("", "A1 B2", "A1 K1", "A1 A2 A3", "щось"):
            with self.subTest(text=text):
                self.assertIsNone(parse_ship(text, BOARD_SIZE))


if __name__ == "__main__":
    unittest.main()
