from collections.abc import Callable

from apps.board import fleet_lengths
from apps.coordinates import format_coordinate
from apps.models import ShotResult
from apps.player import HumanPlayer, Player
from apps.renderer import describe, render_boards


class Game:
    def __init__(
        self,
        p1: Player,
        p2: Player,
        write: Callable[[str], None] = print,
        color: bool = False,
    ) -> None:
        self.players = [p1, p2]
        self.current = 0
        self.write = write
        self.color = color
        for player in self.players:
            player.place_fleet()
            # Без повного флоту гра або скінчилася б раніше часу, або не скінчилася б ніколи.
            lengths = sorted((len(ship.cells) for ship in player.board.ships), reverse=True)
            if lengths != fleet_lengths():
                raise ValueError(f"{player.name}: флот {lengths} замість {fleet_lengths()}")

    def play(self) -> Player:
        """Грає партію до кінця і повертає переможця."""
        while True:
            player = self.players[self.current]
            enemy = self.players[1 - self.current]
            human = isinstance(player, HumanPlayer)

            if human:
                self.write("\n" + render_boards(player.board, enemy.board, color=self.color))

            x, y = player.choose_target(enemy.board)
            result = enemy.board.receive_shot(x, y)

            if human:
                self.write(describe(result))
            else:
                self.write(f"{player.name} стріляє: {format_coordinate(x, y)} — {describe(result)}")

            if enemy.board.all_sunk():
                self._finish(player, enemy)
                return player

            # Після влучання чи повторного пострілу той самий гравець стріляє ще раз.
            if result == ShotResult.MISS:
                self.current = 1 - self.current

    def _finish(self, winner: Player, loser: Player) -> None:
        # Поля — з боку людини: її поле ліворуч. Без людини (комп'ютер проти комп'ютера) — з боку переможця.
        own, other = (loser, winner) if isinstance(loser, HumanPlayer) else (winner, loser)
        self.write("\n" + render_boards(own.board, other.board, reveal_enemy=True, color=self.color))
        self.write("\nВи перемогли!" if isinstance(winner, HumanPlayer) else f"\nПереміг: {winner.name}.")
