import unittest

from apps.board import Board
from apps.config import BOARD_SIZE
from apps.models import Ship, ShotResult
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
    RUNS = 200

    def setUp(self) -> None:
        self.player = ComputerPlayer("Комп'ютер")

    def test_sinks_fleet_without_repeating_shots(self) -> None:
        for _ in range(self.RUNS):
            enemy = Board()
            enemy.place_fleet_randomly()

            shots: set[tuple[int, int]] = set()
            while not enemy.all_sunk():
                target = self.player.choose_target(enemy)
                self.assertNotIn(target, shots)
                self.assertNotEqual(enemy.receive_shot(*target), ShotResult.ALREADY_SHOT)
                shots.add(target)

            self.assertLess(len(shots), BOARD_SIZE * BOARD_SIZE)

    def test_shoots_next_to_single_hit(self) -> None:
        enemy = Board()
        enemy.place_ship(Ship({(4, 4), (5, 4), (6, 4)}))
        enemy.receive_shot(4, 4)

        for _ in range(self.RUNS):
            self.assertIn(self.player.choose_target(enemy), {(3, 4), (5, 4), (4, 3), (4, 5)})

    def test_continues_along_ship_line(self) -> None:
        enemy = Board()
        enemy.place_ship(Ship({(4, 4), (5, 4), (6, 4)}))
        enemy.receive_shot(4, 4)
        enemy.receive_shot(5, 4)

        for _ in range(self.RUNS):
            self.assertIn(self.player.choose_target(enemy), {(3, 4), (6, 4)})

    def test_continues_vertical_line_past_miss(self) -> None:
        enemy = Board()
        enemy.place_ship(Ship({(2, 0), (2, 1), (2, 2), (2, 3)}))
        enemy.receive_shot(2, 0)
        enemy.receive_shot(2, 1)

        # Вгорі край поля — лишається тільки низ.
        for _ in range(self.RUNS):
            self.assertEqual(self.player.choose_target(enemy), (2, 2))

    def test_never_shoots_next_to_sunk_ship(self) -> None:
        enemy = Board()
        enemy.place_ship(Ship({(0, 0), (1, 0)}))
        enemy.receive_shot(0, 0)
        enemy.receive_shot(1, 0)
        forbidden = {(x, y) for x in range(3) for y in range(2)}

        for _ in range(self.RUNS):
            self.assertNotIn(self.player.choose_target(enemy), forbidden)

    def test_smarter_than_random(self) -> None:
        # Випадкова стрільба в середньому потребує ~96 пострілів; добивання — значно менше.
        total = 0
        for _ in range(self.RUNS):
            enemy = Board()
            enemy.place_fleet_randomly()
            while not enemy.all_sunk():
                enemy.receive_shot(*self.player.choose_target(enemy))
                total += 1
        self.assertLess(total / self.RUNS, 80)


if __name__ == "__main__":
    unittest.main()
