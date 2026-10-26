import unittest

from apps.board import Board
from apps.config import FLEET
from apps.models import CellState, Ship, ShotResult


class CanPlaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board()

    def test_straight_line_in_bounds(self) -> None:
        self.assertTrue(self.board.can_place({(0, 0), (1, 0), (2, 0)}))
        self.assertTrue(self.board.can_place({(4, 4), (4, 5), (4, 6)}))

    def test_line_with_gap(self) -> None:
        self.assertFalse(self.board.can_place({(0, 0), (2, 0)}))

    def test_diagonal(self) -> None:
        self.assertFalse(self.board.can_place({(0, 0), (1, 1)}))

    def test_out_of_bounds(self) -> None:
        self.assertFalse(self.board.can_place({(9, 0), (10, 0)}))
        self.assertFalse(self.board.can_place({(-1, 0)}))

    def test_empty_cells(self) -> None:
        self.assertFalse(self.board.can_place(set()))

    def test_ships_cannot_touch(self) -> None:
        self.board.place_ship(Ship({(0, 0), (1, 0)}))
        self.assertFalse(self.board.can_place({(0, 1)}))  # боком
        self.assertFalse(self.board.can_place({(2, 1)}))  # кутом
        self.assertTrue(self.board.can_place({(3, 0)}))


class PlaceShipTest(unittest.TestCase):
    def test_marks_cells_using_x_as_column(self) -> None:
        board = Board()
        board.place_ship(Ship({(7, 2)}))
        self.assertEqual(board.grid[2][7], CellState.SHIP)
        self.assertEqual(len(board.ships), 1)

    def test_invalid_placement_raises(self) -> None:
        board = Board()
        board.place_ship(Ship({(0, 0), (1, 0)}))
        with self.assertRaises(ValueError):
            board.place_ship(Ship({(1, 1)}))


class ReceiveShotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board()
        self.board.place_ship(Ship({(0, 0), (1, 0)}))

    def test_miss(self) -> None:
        self.assertEqual(self.board.receive_shot(5, 5), ShotResult.MISS)
        self.assertEqual(self.board.grid[5][5], CellState.MISS)

    def test_repeated_miss(self) -> None:
        self.board.receive_shot(5, 5)
        self.assertEqual(self.board.receive_shot(5, 5), ShotResult.ALREADY_SHOT)

    def test_hit(self) -> None:
        self.assertEqual(self.board.receive_shot(0, 0), ShotResult.HIT)
        self.assertEqual(self.board.grid[0][0], CellState.HIT)
        self.assertFalse(self.board.all_sunk())

    def test_repeated_hit(self) -> None:
        self.board.receive_shot(0, 0)
        self.assertEqual(self.board.receive_shot(0, 0), ShotResult.ALREADY_SHOT)

    def test_sunk(self) -> None:
        self.board.receive_shot(0, 0)
        self.assertEqual(self.board.receive_shot(1, 0), ShotResult.SUNK)
        self.assertEqual(self.board.grid[0][0], CellState.SUNK)
        self.assertEqual(self.board.grid[0][1], CellState.SUNK)
        self.assertTrue(self.board.all_sunk())

    def test_repeated_shot_at_sunk_ship(self) -> None:
        self.board.receive_shot(0, 0)
        self.board.receive_shot(1, 0)
        self.assertEqual(self.board.receive_shot(0, 0), ShotResult.ALREADY_SHOT)

    def test_out_of_bounds_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.receive_shot(10, 0)


class PlaceFleetRandomlyTest(unittest.TestCase):
    RUNS = 200

    def test_fleet_is_valid(self) -> None:
        expected_lengths = sorted(
            length for length, count in FLEET.items() for _ in range(count)
        )
        for _ in range(self.RUNS):
            board = Board()
            board.place_fleet_randomly()

            self.assertEqual(
                sorted(len(ship.cells) for ship in board.ships), expected_lengths
            )

            ship_cells = {cell for ship in board.ships for cell in ship.cells}
            grid_cells = {
                (x, y)
                for y in range(board.size)
                for x in range(board.size)
                if board.grid[y][x] == CellState.SHIP
            }
            self.assertEqual(ship_cells, grid_cells)

            for ship in board.ships:
                others = ship_cells - ship.cells
                for x, y in ship.cells:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            self.assertNotIn((x + dx, y + dy), others)

    def test_whole_fleet_can_be_sunk(self) -> None:
        board = Board()
        board.place_fleet_randomly()
        for ship in board.ships:
            for x, y in ship.cells:
                board.receive_shot(x, y)
        self.assertTrue(board.all_sunk())

    def test_fleet_does_not_fit(self) -> None:
        board = Board(3)
        with self.assertRaises(ValueError):
            board.place_fleet_randomly()
        self.assertEqual(board.ships, [])


class BoardSizeTest(unittest.TestCase):
    def test_size_limited_by_letters(self) -> None:
        Board(26)
        for size in (0, 27):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    Board(size)


if __name__ == "__main__":
    unittest.main()
