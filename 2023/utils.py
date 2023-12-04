import argparse
import dataclasses
import logging
import os
import sys

from typing import Generic, Iterator, List, Tuple, TypeVar, Union


advent = "Advent of Code 2023"
program_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
if program_name.startswith("solve"):
    splits = program_name[5:].split("_")
    day = splits[0]
    if len(splits) > 1:
        phase = splits[1]
    else:
        phase = "unk"
else:
    day = "unk"
    phase = "unk"

input_name = f"input{day}.txt"


desc = f"{advent}, day {day}, phase {phase.capitalize()}"
parser = argparse.ArgumentParser(prog=program_name, description=f"{desc}.")
parser.add_argument("input", nargs="?", default=input_name)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-q", "--quiet", action="store_true")

args = parser.parse_args()

verbosity = args.verbose - args.quiet

logging_format = "%(levelname)-8s : %(asctime)-15s : %(message)s"
logger = logging.getLogger(program_name)
if len(logger.handlers) == 0:
    logging.basicConfig(format=logging_format)
else:
    logging.handlers[0].setFormatter(logging.Formatter(logging_format))

loglevel = {1: logging.DEBUG, 0: logging.INFO, -1: logging.ERROR}[verbosity]
logger.setLevel(loglevel)
logging.captureWarnings(True)


def log_exception(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = log_exception


logger.info(f"Solving {desc}.")


def iterinput(strip: bool = True) -> Iterator[str]:
    logger.info(f"Loading data from {args.input}.")
    with open(args.input, "rt") as f:
        if strip:
            for line in f:
                yield line.strip()
        else:
            yield from f


T = TypeVar("T")


@dataclasses.dataclass
class Matrix(Generic[T]):
    data: List[List[T]]
    nrows: int
    ncols: int

    def __str__(self) -> str:
        s = "Matrix(\n    "
        s += "\n    ".join("".join(_) for _ in self.data)
        s += "\n)"
        return s

    def __getitem__(self, idx: Union[int, Tuple[int, int]]) -> Union[T, List[T]]:
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, (tuple, list)):
            assert len(idx) == 2
            return self.data[idx[0]][idx[1]]
        else:
            raise ValueError("Index should be an integer or a pair of ints.")

    def __setitem__(self, idx: Tuple[int, int], value: T):
        self.data[idx[0]][idx[1]] = value

    def iterneighbors(
        self, row: int, col: int, /, *, diagonals: bool = True
    ) -> Iterator[Tuple[int, int]]:
        if row > 0:
            yield (row - 1, col)
        if row + 1 < self.nrows:
            yield (row + 1, col)
        if col > 0:
            yield (row, col - 1)
        if col + 1 < self.ncols:
            yield (row, col + 1)

        if diagonals:
            if row > 0:
                if col > 0:
                    yield (row - 1, col - 1)
                if col + 1 < self.ncols:
                    yield (row - 1, col + 1)
            if row + 1 < self.nrows:
                if col > 0:
                    yield (row + 1, col - 1)
                if col + 1 < self.ncols:
                    yield (row + 1, col + 1)

    def iterneighborvalues(
        self, idx0: int, idx1: int, /, *, diagonals: bool = True
    ) -> T:
        for row, col in self.iterneighbors(idx0, idx1, diagonals=diagonals):
            yield self.data[row][col]


def loadmatrix() -> Matrix[str]:
    data = [list(_) for _ in iterinput()]

    nrows = len(data)
    ncols = len(data[0])
    for row in data:
        assert len(row) == ncols

    matrix = Matrix(data, nrows, ncols)
    logger.info(f"Loaded matrix size {matrix.nrows} x {matrix.ncols}.")

    return matrix
