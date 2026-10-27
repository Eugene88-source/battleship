import unittest

from apps.config import ConfigError, validate_config


class ValidateConfigTest(unittest.TestCase):
    def test_default_config_is_valid(self) -> None:
        validate_config()

    def test_board_size_out_of_range(self) -> None:
        for size in (0, 27):
            with self.subTest(size=size), self.assertRaises(ConfigError):
                validate_config(size, {1: 1})

    def test_empty_fleet(self) -> None:
        with self.assertRaisesRegex(ConfigError, "порожній"):
            validate_config(10, {})

    def test_non_positive_length_or_count(self) -> None:
        for fleet in ({0: 1}, {-1: 1}, {1: 0}, {1: -2}):
            with self.subTest(fleet=fleet), self.assertRaises(ConfigError):
                validate_config(10, fleet)

    def test_ship_longer_than_board(self) -> None:
        with self.assertRaisesRegex(ConfigError, "не вміщається"):
            validate_config(3, {4: 1})


if __name__ == "__main__":
    unittest.main()
