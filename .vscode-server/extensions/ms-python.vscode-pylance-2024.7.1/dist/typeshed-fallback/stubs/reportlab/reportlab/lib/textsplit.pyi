from _typeshed import Incomplete
from collections.abc import Sequence
from typing import Final

__version__: Final[str]
CANNOT_START_LINE: Final[Sequence[str]]
ALL_CANNOT_START: Final[str]
CANNOT_END_LINE: Final[Sequence[str]]
ALL_CANNOT_END: Final[str]

def is_multi_byte(ch): ...
def getCharWidths(word, fontName, fontSize): ...
def wordSplit(word, maxWidths, fontName, fontSize, encoding: str = "utf8"): ...
def dumbSplit(word, widths, maxWidths): ...
def kinsokuShoriSplit(word, widths, availWidth) -> None: ...

rx: Incomplete

def cjkwrap(text, width, encoding: str = "utf8"): ...
