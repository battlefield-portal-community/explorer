import asyncio

import aiohttp


class ExperienceCode:
    symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    symbols_to_value_table = {
        i: index - 1
        for index, i in enumerate(symbols, 1)
    }
    value_to_symbols_table = {v: k for k, v in symbols_to_value_table.items()}

    def __init__(self, experience_code: str) -> None:
        experience_code = experience_code.upper()
        self.experience_code = self.is_valid_experience_code(experience_code) and experience_code

    def __str__(self) -> str:
        return self.experience_code

    def __int__(self) -> int:
        return self.to_int(self.experience_code)

    def __add__(self, other: int) -> 'ExperienceCode':
        return self.to_str(int(self) + other)

    def __radd__(self, other: int) -> 'ExperienceCode':
        return self + other

    def __sub__(self, other: int) -> 'ExperienceCode':
        return self.to_str(int(self) - other)

    def __eq__(self, __value: 'ExperienceCode') -> bool:
        return int(self) == int(__value)

    def __lt__(self, __value: 'ExperienceCode') -> bool:
        return int(self) < int(__value)

    def __gt__(self, __value: 'ExperienceCode') -> bool:
        return int(self) > int(__value)

    def __getitem__(self, index: int) -> str:
        return self.experience_code[index]

    def __hash__(self):
        return int(self)

    @staticmethod
    def to_int(experience_code) -> int:
        integer = 0
        base = len(ExperienceCode.symbols_to_value_table)
        for character in experience_code.upper().lstrip('A'):
            assert character in ExperienceCode.symbols_to_value_table, f"Invalid character: {character}"
            integer *= base
            integer += ExperienceCode.symbols_to_value_table[character]
        return integer

    @staticmethod
    def to_str(int_repr: int, base: int = 35) -> 'ExperienceCode':
        if int_repr < 0:
            raise ValueError("Integer representation must be positive.")
        array = []
        while int_repr:
            int_repr, value = divmod(int_repr, base)
            array.append(ExperienceCode.value_to_symbols_table[value])
        str_repr = ''.join(reversed(array)).rjust(len(array) + 2, 'A')
        if str_repr == 'AA':
            str_repr = 'AAA'
        return ExperienceCode(str_repr)

    @staticmethod
    def is_valid_experience_code(experience_code: str) -> bool:
        """
        Check if the experience code is valid.

        Returns:
        bool: True if the experience code is valid, False otherwise.
        """

        # Check if the experience code is a string
        if not isinstance(experience_code, str):
            raise TypeError(f"Experience code must be a string, not {type(experience_code)}")

        # Check if the experience code is in the correct format
        if len(experience_code) < 3:
            raise ValueError(
                f"Experience code must be at least 3 characters long, not {len(experience_code)}, {experience_code}")

        # Check if the experience code contains only valid characters
        if any(character not in ExperienceCode.symbols_to_value_table for character in experience_code):
            raise ValueError(f"Experience code contains invalid characters: {experience_code}")

        if ExperienceCode.to_int(experience_code) < 0:
            raise ValueError(
                f"Experience code must be positive and non-zero: {experience_code}, \nExperience codes start at AAA.")

        return True


if __name__ == "__main__":
    assert ExperienceCode.to_str(42069) == ExperienceCode("AA9L9")
