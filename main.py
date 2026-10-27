from apps.game import Game
from apps.player import ComputerPlayer, HumanPlayer, QuitGame
from apps.renderer import supports_color


def main():
    color = supports_color()
    try:
        # ValueError ловимо лише під час підготовки: це невдалий конфіг, а не помилка посеред гри.
        try:
            game = Game(HumanPlayer("Ви", color=color), ComputerPlayer("Комп'ютер"), color=color)
        except ValueError as error:
            print(f"Не вдалося почати гру: {error}")
            return
        game.play()
    except QuitGame:
        print("\nВи вийшли з гри.")
    except (KeyboardInterrupt, EOFError):
        print("\nГру перервано.")


if __name__ == '__main__':
    main()
