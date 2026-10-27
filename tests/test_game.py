import unittest

from apps.game import Game
from apps.models import Ship
from apps.player import ComputerPlayer


class GameTest(unittest.TestCase):
    RUNS = 20

    def test_game_ends_with_winner(self) -> None:
        for _ in range(self.RUNS):
            p1 = ComputerPlayer("Перший")
            p2 = ComputerPlayer("Другий")
            messages: list[str] = []

            winner = Game(p1, p2, write=messages.append).play()
            loser = p2 if winner is p1 else p1

            self.assertTrue(loser.board.all_sunk())
            self.assertFalse(winner.board.all_sunk())
            self.assertEqual(messages[-1], f"\nПереміг: {winner.name}.")

    def test_player_without_full_fleet_raises(self) -> None:
        class NoFleetPlayer(ComputerPlayer):
            def place_fleet(self) -> None:
                self.board.place_ship(Ship({(0, 0)}))

        with self.assertRaisesRegex(ValueError, r"Без флоту: флот \[1\] замість \[4, 3, 3"):
            Game(ComputerPlayer("Перший"), NoFleetPlayer("Без флоту"), write=lambda _: None)


if __name__ == "__main__":
    unittest.main()
