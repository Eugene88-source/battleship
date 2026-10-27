from apps.config import ConfigError, validate_config
from apps.game import Game
from apps.player import ComputerPlayer, HumanPlayer, QuitGame
from apps.renderer import supports_color


def main():
    color = supports_color()
    try:
        # Конфіг перевіряємо до першого запитання, щоб не розставляти кораблі даремно.
        validate_config()
        Game(HumanPlayer("Ви", color=color), ComputerPlayer("Комп'ютер"), color=color).play()
    except ConfigError as error:
        # Лише помилки конфігу: решта ValueError — це баги, і traceback тут доречний.
        print(f"\nНе вдалося почати гру: {error}")
    except QuitGame:
        print("\nВи вийшли з гри.")
    except (KeyboardInterrupt, EOFError):
        print("\nГру перервано.")


if __name__ == '__main__':
    main()
