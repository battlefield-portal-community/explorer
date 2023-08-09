import asyncio
import random

from rich.text import Text
from rich.live import Live
from rich.table import Table
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
                f"Experience code must be positive and non-zero: {experience_code},\nExperience codes start at AAA.")

        return True


class ExperienceCodeBaseIterator:
    def __init__(self, start: str, end: str | int = None, step: int = 1) -> None:
        if end is None:
            start, end = "AAA", start
        start_code = ExperienceCode(start)
        if isinstance(end, int):
            if step > 0:
                end_code = ExperienceCode.to_str(int(start_code + end))
            else:
                # rich.print(f"calc {max(int(start_code) - end, 0)}, {start_code}")
                end_code = ExperienceCode.to_str(max(int(start_code) - end, 0))
        else:
            end_code = ExperienceCode(end)

        if step > 0 and start_code > end_code:
            raise ValueError(f"Start code must be less than end code: {start_code} > {end_code}")
        elif step < 0 and start_code < end_code:
            raise ValueError(f"Start code must be greater than end code: {start_code} < {end_code}")

        self.start_code = start_code
        self.end_code = end_code
        self.current_code = self.start_code
        self.step = step


class ExperienceCodeIterator(ExperienceCodeBaseIterator):
    def __iter__(self) -> 'ExperienceCodeIterator':
        return self

    def __next__(self):
        if self.step < 0 and self.current_code < self.end_code:
            raise StopIteration
        if self.current_code == self.end_code:
            raise StopIteration
        _ = self.current_code
        try:
            self.current_code += self.step
        except ValueError:
            raise StopIteration
        return _


class AsyncExperienceCodeIterator(ExperienceCodeIterator):
    def __aiter__(self) -> 'AsyncExperienceCodeIterator':
        return self

    async def __anext__(self):
        if self.step < 0 and self.current_code < self.end_code:
            raise StopAsyncIteration
        if self.current_code == self.end_code:
            raise StopAsyncIteration
        _ = self.current_code
        try:
            self.current_code += self.step
        except ValueError:
            raise StopAsyncIteration
        return _


class Worker:
    def __init__(self, start_code, end_code: str = None, chunk_size: int = 10) -> None:
        if end_code is None:
            end_code = "AAA"

        self.start_code = ExperienceCode(start_code)
        self.end_code = ExperienceCode(end_code)

        self.mid_code = self.end_code

        if self.end_code > self.start_code:
            raise ValueError(f"Start code must be greater than end code: {start_code}, {end_code}")

        self.current_code = self.start_code
        self.base_api_url = "https://api.gametools.network/bf2042/playground/"
        self.session = None
        self.current_status = {}
        self.live_display = None
        self.chunk_size = min(
            int(self.start_code) - int(self.end_code),
            chunk_size
        )

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_all_playgrounds())

    async def fetch_all_playgrounds(self):
        # print(f"Fetching {[str(code) for code in codes]} playgrounds")
        async with aiohttp.ClientSession() as session:
            self.set_current_status()
            with Live(self.gen_table(), refresh_per_second=10, vertical_overflow='visible') as live_display:
                live_display.console.print(f"Fetching playgrounds from {self.current_code} to {self.end_code}")
                while self.chunk_size > 0:
                    tasks = [self.get_playground(code, session) for code in self.current_status]
                    for task in asyncio.as_completed(tasks):
                        self.update_table(live_display, *(await task))

                    delta = int(self.current_code) - self.chunk_size
                    if delta <= int(self.end_code):
                        live_display.update(self.gen_table())
                        break

                    self.current_code = ExperienceCode.to_str(delta)

                    self.chunk_size = min(
                        (int(self.current_code) - int(self.end_code)),
                        int(self.current_code),
                        self.chunk_size,
                    )

                    self.set_current_status()

    def set_current_status(self):
        # rich.print(f"Current Code: {self.current_code}, range {self.range}")
        self.current_status = {
            code: Text.assemble(("pending", "brown")) for code in
            AsyncExperienceCodeIterator(
                str(self.current_code),
                self.chunk_size,
                -1
            )
        }

    def gen_table(self):
        table = Table(show_header=False)
        [table.add_row(str(code), status) for code, status in self.current_status.items()]
        return table

    def update_table(self, display, code, errors=False):
        status = Text("Completed")
        status.stylize("green")
        if errors:
            status += Text.assemble((" (Not Found)", "red"))
        self.current_status[code] = status
        display.update(self.gen_table())

    async def get_playground(self, code: ExperienceCode, session):
        # await asyncio.sleep(random.randint(1,2))
        # return code, False
        url = f"{self.base_api_url}?experiencecode={code}"
        resp = await session.get(url)
        json_data = await resp.json()
        if json_data.get("errors", False):
            return code, True
        elif playground := json_data.get("originalPlayground", None):
            return code, False


if __name__ == "__main__":
    worker = Worker("AA9", chunk_size=9)
    worker.start()

    # print(int(ExperienceCode("AA9")), int(ExperienceCode("AAP")))
