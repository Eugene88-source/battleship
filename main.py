from apps.game import Game
from apps.player import ComputerPlayer, HumanPlayer


def main():
    try:
        Game(HumanPlayer("Ви"), ComputerPlayer("Комп'ютер")).play()
    except (KeyboardInterrupt, EOFError):
        print("\nГру перервано.")


if __name__ == '__main__':
    main()
