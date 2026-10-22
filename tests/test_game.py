import unittest

from apps.game import Game
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


if __name__ == "__main__":
    unittest.main()
