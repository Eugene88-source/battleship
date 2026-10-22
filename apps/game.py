from apps.player import Player


class Game:
    def __init__(self, p1: Player, p2: Player) -> None:
        self.players = [p1, p2]
        self.current = 0

    def play(self) -> None:
        ...
