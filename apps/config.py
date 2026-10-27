from apps.coordinates import LETTERS


BOARD_SIZE = 10
FLEET = {4: 1, 3: 2, 2: 3, 1: 4}


class ConfigError(ValueError):
    """Розмір поля чи склад флоту такі, що з ними не зіграти."""


def validate_config(size: int | None = None, fleet: dict[int, int] | None = None) -> None:
    """Перевіряє конфіг до початку гри, щоб гравець не розставляв кораблі даремно.

    Без аргументів бере BOARD_SIZE і FLEET у момент виклику, а не під час імпорту.
    """
    size = BOARD_SIZE if size is None else size
    fleet = FLEET if fleet is None else fleet
    if not 1 <= size <= len(LETTERS):
        raise ConfigError(f"Розмір поля має бути від 1 до {len(LETTERS)}, а не {size}")
    if not fleet:
        raise ConfigError("Флот порожній: потрібен хоча б один корабель")
    for length, count in fleet.items():
        if length < 1 or count < 1:
            raise ConfigError(f"Неправильний запис флоту {length}: {count} — довжина й кількість мають бути від 1")
        if length > size:
            raise ConfigError(f"Корабель на {length} кл. не вміщається на поле {size}×{size}")
