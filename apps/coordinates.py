import string


LETTERS = string.ascii_uppercase


def parse_coordinate(text: str, size: int) -> tuple[int, int] | None:
    """«B7» → (1, 6): літера — стовпець, число — рядок. None, якщо формат невірний або клітинка поза полем."""
    text = text.strip().upper()
    if len(text) < 2 or text[0] not in LETTERS[:size] or not (text[1:].isascii() and text[1:].isdecimal()):
        return None
    x = LETTERS.index(text[0])
    y = int(text[1:]) - 1
    if not 0 <= y < size:
        return None
    return x, y


def format_coordinate(x: int, y: int) -> str:
    return f"{LETTERS[x]}{y + 1}"


def parse_ship(text: str, size: int) -> set[tuple[int, int]] | None:
    """«B2 B5» або «B2-B5» → клітинки від B2 до B5; «C7» → одна клітинка.

    None, якщо формат невірний, клітинка поза полем або кінці не в одному рядку чи стовпці.
    """
    parts = text.replace("-", " ").split()
    if not 1 <= len(parts) <= 2:
        return None

    ends = [parse_coordinate(part, size) for part in parts]
    if None in ends:
        return None

    (x1, y1), (x2, y2) = ends[0], ends[-1]
    if x1 != x2 and y1 != y2:
        return None

    return {
        (x, y)
        for x in range(min(x1, x2), max(x1, x2) + 1)
        for y in range(min(y1, y2), max(y1, y2) + 1)
    }
