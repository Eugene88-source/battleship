from apps.game import Game
from apps.player import ComputerPlayer, HumanPlayer
from apps.renderer import supports_color


def main():
    color = supports_color()
    try:
        Game(HumanPlayer("Ви", color=color), ComputerPlayer("Комп'ютер"), color=color).play()
    except (KeyboardInterrupt, EOFError):
        print("\nГру перервано.")


if __name__ == '__main__':
    main()
