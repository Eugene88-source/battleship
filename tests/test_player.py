import unittest

from apps.board import Board, fleet_lengths
from apps.config import BOARD_SIZE
from apps.models import Ship, ShotResult
from apps.player import ComputerPlayer, HumanPlayer, QuitGame


# Правильна розстановка всього флоту, від найбільшого корабля.
MANUAL_FLEET = ["A1 D1", "A3 C3", "E3 G3", "A5 B5", "D5 E5", "G5 H5", "A7", "C7", "E7", "G7"]


def scripted_player(answers: list[str]) -> tuple[HumanPlayer, list[str]]:
    replies = iter(answers)
    messages: list[str] = []
    return HumanPlayer("Ви", read=lambda prompt: next(replies), write=messages.append), messages


class HumanPlayerTest(unittest.TestCase):
    def test_asks_again_until_valid(self) -> None:
        player, messages = scripted_player(["zz", "C3"])

        self.assertEqual(player.choose_target(Board()), (2, 2))
        self.assertEqual(len(messages), 1)

    def test_quit_when_shooting(self) -> None:
        for word in ("вихід", " Q ", "exit"):
            with self.subTest(word=word):
                player, _ = scripted_player([word])
                with self.assertRaises(QuitGame):
                    player.choose_target(Board())


class HumanPlacementTest(unittest.TestCase):
    def test_random_by_default(self) -> None:
        player, _ = scripted_player([""])
        player.place_fleet()

        self.assertEqual(sorted(len(s.cells) for s in player.board.ships), sorted(fleet_lengths()))

    def test_manual_placement(self) -> None:
        player, _ = scripted_player(["т", *MANUAL_FLEET])
        player.place_fleet()

        self.assertEqual([len(s.cells) for s in player.board.ships], fleet_lengths())
        self.assertEqual(player.board.ships[0].cells, {(0, 0), (1, 0), (2, 0), (3, 0)})
        self.assertEqual(player.board.ships[-1].cells, {(6, 6)})

    def test_rejects_invalid_ships_and_asks_again(self) -> None:
        player, messages = scripted_player([
            "так",
            "A1 A2",   # не та довжина
            "A1 D2",   # не по прямій
            "щось",    # не координати
            MANUAL_FLEET[0],
            "A2 C2",   # торкається першого корабля
            *MANUAL_FLEET[1:],
        ])
        player.place_fleet()

        self.assertEqual(len(player.board.ships), len(fleet_lengths()))
        errors = [m for m in messages if not m.startswith("\n") and "Введіть" not in m]
        self.assertEqual(len(errors), 4)
        self.assertIn("Потрібен корабель на 4 кл., а введено 2.", errors)

    def test_restart(self) -> None:
        player, _ = scripted_player(["т", "F10 I10", "A3 C3", "заново", *MANUAL_FLEET])
        player.place_fleet()

        self.assertEqual(player.board.ships[0].cells, {(0, 0), (1, 0), (2, 0), (3, 0)})
        self.assertEqual(len(player.board.ships), len(fleet_lengths()))

    def test_quit_during_placement(self) -> None:
        for answers in (["вихід"], ["т", MANUAL_FLEET[0], "вихід"]):
            with self.subTest(answers=answers):
                player, _ = scripted_player(answers)
                with self.assertRaises(QuitGame):
                    player.place_fleet()


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

    def test_first_shot_away_from_edges(self) -> None:
        # Через клітинки біля центру проходить більше можливих положень кораблів, ніж через краї.
        for _ in range(self.RUNS):
            x, y = self.player.choose_target(Board())
            self.assertTrue(0 < x < BOARD_SIZE - 1 and 0 < y < BOARD_SIZE - 1)

    def test_remaining_ships_exclude_sunk(self) -> None:
        enemy = Board()
        enemy.place_ship(Ship({(0, 0), (1, 0)}))
        enemy.place_ship(Ship({(5, 5)}))
        enemy.receive_shot(0, 0)
        enemy.receive_shot(1, 0)
        enemy.receive_shot(5, 5)

        remaining = ComputerPlayer._remaining_ships(enemy)
        self.assertEqual(remaining, {4: 1, 3: 2, 2: 2, 1: 3})

    def test_smarter_than_random(self) -> None:
        # Випадкова стрільба в середньому потребує ~96 пострілів, випадковий пошук із добиванням — ~58,
        # пошук за ймовірністю — ~55.
        total = 0
        for _ in range(self.RUNS):
            enemy = Board()
            enemy.place_fleet_randomly()
            while not enemy.all_sunk():
                enemy.receive_shot(*self.player.choose_target(enemy))
                total += 1
        self.assertLess(total / self.RUNS, 57)


if __name__ == "__main__":
    unittest.main()
