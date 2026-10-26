from apps.game import Game
from apps.player import ComputerPlayer, HumanPlayer, QuitGame
from apps.renderer import supports_color


def main():
    color = supports_color()
    try:
        Game(HumanPlayer("Ви", color=color), ComputerPlayer("Комп'ютер"), color=color).play()
    except QuitGame:
        print("\nВи вийшли з гри.")
    except (KeyboardInterrupt, EOFError):
        print("\nГру перервано.")


if __name__ == '__main__':
    main()
