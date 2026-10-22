from abc import ABC, abstractmethod

from apps.board import Board


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.board = Board()
        self.tracking = Board()

    @abstractmethod
    def choose_target(self) -> tuple[int, int]:
        ...


class HumanPlayer(Player):
    def choose_target(self) -> tuple[int, int]:
        ...


class ComputerPlayer(Player):
    def choose_target(self) -> tuple[int, int]:
        ...
