import argparse
import dataclasses
import heapq
import itertools
import logging
import math
import os
import sys

from typing import (
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)


advent = "Advent of Code 2023"
program_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
if program_name.startswith("solve"):
    day = program_name[5:-1]
    phase = program_name[-1]
else:
    day = "unk"
    phase = "unk"

input_name = f"input{day}.txt"


desc = f"{advent}, day {day}, phase {phase.capitalize()}"
parser = argparse.ArgumentParser(prog=program_name, description=f"{desc}.")
parser.add_argument("input", nargs="?", default=input_name)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-q", "--quiet", action="store_true")
parser.add_argument("-t", "--tests", action="store_true", help="run tests (if any)")

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

    def __init__(
        self,
        data: List[List[T]],
        nrows: Optional[int] = None,
        ncols: Optional[int] = None,
    ):
        self.data = data

        if nrows is not None:
            assert len(data) == nrows
        else:
            nrows = len(data)

        if ncols is not None:
            assert all(len(_) == ncols for _ in data)
        else:
            if len(data) > 0:
                ncols = len(data[0])
                assert all(len(_) == ncols for _ in data[1:])
            else:
                ncols = 0

        self.nrows = nrows
        self.ncols = ncols

    def __repr__(self) -> str:
        s = "Matrix(\n    "
        s += "\n    ".join("".join(str(c) for c in _) for _ in self.data)
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
    ) -> Iterator[T]:
        for row, col in self.iterneighbors(idx0, idx1, diagonals=diagonals):
            yield self.data[row][col]

    def transpose(self) -> "Matrix[T]":
        new_data = []
        for j in range(self.ncols):
            new_row = []
            for i in range(self.nrows):
                new_row.append(self[i, j])

            new_data.append(new_row)

        mt = Matrix(new_data, self.ncols, self.nrows)
        return mt

    def transposed_view(self) -> "View[T]":
        return View(self, [[0, 1], [1, 0]], [0, 0])

    def rotated_view(self, count: int) -> "View[T]":
        """A view rotated `count * 90` degrees clockwise."""
        count = count % 4
        if count == 0:
            A = [[1, 0], [0, 1]]
            b = [0, 0]
        elif count == 1:
            A = [[0, -1], [1, 0]]
            b = [self.nrows - 1, 0]
        elif count == 2:
            A = [[-1, 0], [0, -1]]
            b = [self.nrows - 1, self.ncols - 1]
        elif count == 3:
            A = [[0, 1], [-1, 0]]
            b = [0, self.ncols - 1]
        else:
            assert False

        return View(self, A=A, b=b)

    def get_hash(self) -> int:
        d = {"nrows": self.nrows, "ncols": self.ncols}
        d["data"] = tuple(tuple(_) for _ in self.data)
        return hash(tuple(d.items()))


class View(Generic[T]):
    """Provide a view into a matrix using affinely transformed indices.

    This simply transforms indices before using the underlying matrix's __getitem__
    and __setitem__. Specifically, given a 2x2 matrix `A` and a length-2 sequence `b`,
    we have

    ```
        View[i, j] = mat[
            A[0][0] * i + A[0][1] * j + b[0],
            A[1][0] * i + A[1][1] * j + b[1],
        ]
    ```
    """

    def __init__(self, mat: Matrix[T], A: Sequence[Sequence[int]], b: Sequence[int]):
        self.mat = mat

        assert len(b) == 2
        assert len(A) == 2 and all(len(_) == 2 for _ in A)

        self.A = A
        self.b = b

        self.extents = None
        self.nrows = None
        self.ncols = None
        self._find_extents()

    def transformed_idx(self, i: int, j: int) -> Tuple[int, int]:
        mi = self.A[0][0] * i + self.A[0][1] * j + self.b[0]
        mj = self.A[1][0] * i + self.A[1][1] * j + self.b[1]
        return mi, mj

    def __getitem__(self, idx: Tuple[int, int]) -> T:
        mi, mj = self.transformed_idx(*idx)
        if mi < 0 or mj < 0 or mi >= self.mat.nrows or mj >= self.mat.ncols:
            raise IndexError(f"Maps to invalid index ({mi}, {mj})")
        return self.mat[mi, mj]

    def __setitem__(self, idx: Tuple[int, int], value: T):
        mi, mj = self.transformed_idx(*idx)
        if mi < 0 or mj < 0 or mi >= self.mat.nrows or mj >= self.mat.ncols:
            raise IndexError(f"Maps to invalid index ({mi}, {mj})")
        self.mat[mi, mj] = value

    def __repr__(self):
        s = f"View(A={self.A}, b={self.b}, mat={self.mat!s})"
        return s

    def as_matrix(self) -> Matrix[T]:
        if self.extents is None:
            raise ValueError(
                "Can only convert to matrix if view is trivial, rotated, or transposed"
            )

        i0, i1, j0, j1 = self.extents
        if i0 != 0 or j0 != 0:
            raise ValueError(
                f"Lowest indices in view should be zero, instead they are ({i0}, {j0})"
            )

        new_data = []
        for i in range(i0, i1 + 1):
            row = []
            for j in range(j0, j1 + 1):
                mi, mj = self.transformed_idx(i, j)
                row.append(self.mat[mi, mj])

            new_data.append(row)

        res = Matrix(new_data, self.nrows, self.ncols)
        return res

    def _find_extents(self):
        is_diag = self.A[0][1] == 0 and self.A[1][0] == 0
        is_transp = self.A[0][0] == 0 and self.A[1][1] == 0
        if not is_diag and not is_transp:
            logger.debug(
                f"Cannot assign extents to view because it's not diagonal or transposed"
            )
            self.extents = None
            self.nrows = None
            self.ncols = None
            return

        if is_diag:
            i0 = int(math.ceil(-self.b[0] / self.A[0][0]))
            i1 = int(math.floor((self.mat.nrows - 1 - self.b[0]) / self.A[0][0]))

            j0 = int(math.ceil(-self.b[1] / self.A[1][1]))
            j1 = int(math.floor((self.mat.ncols - 1 - self.b[1]) / self.A[1][1]))
        elif is_transp:
            j0 = int(math.ceil(-self.b[0] / self.A[0][1]))
            j1 = int(math.floor((self.mat.nrows - 1 - self.b[0]) / self.A[0][1]))

            i0 = int(math.ceil(-self.b[1] / self.A[1][0]))
            i1 = int(math.floor((self.mat.ncols - 1 - self.b[1]) / self.A[1][0]))

        if i0 > i1:
            i0, i1 = i1, i0
        if j0 > j1:
            j0, j1 = j1, j0

        self.extents = (i0, i1, j0, j1)

        self.nrows = i1 - i0 + 1
        self.ncols = j1 - j0 + 1


def _matrix_from_data(data: List[List[str]]) -> Matrix[str]:
    nrows = len(data)
    ncols = len(data[0])
    for row in data:
        assert len(row) == ncols

    matrix = Matrix(data, nrows, ncols)
    return matrix


def loadmatrix() -> Matrix[str]:
    data = [list(_) for _ in iterinput()]
    matrix = _matrix_from_data(data)
    logger.info(f"Loaded matrix size {matrix.nrows} x {matrix.ncols}.")
    return matrix


def extended_gcd(a: int, b: int, /) -> Tuple[int, int, int]:
    """Find GCD and Bézout coefficients.

    From https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Pseudocode.

    Parameters
    ----------
    a, b : int
        Integers for which to find the GCD.

    Returns
    -------
    gcd : int
        The GCD between `a` and `b`.
    x, y : int
        The Bézout coefficients, obeying `a * x + b * y = gcd`.
    """
    s = 0
    r = b

    old_s = 1
    old_r = a

    while r != 0:
        q = old_r // r

        old_s, s = s, old_s - q * s
        old_r, r = r, old_r - q * r

    gcd = old_r
    x = old_s
    if b != 0:
        y = (old_r - old_s * a) // b
    else:
        y = 0

    return gcd, x, y


@dataclasses.dataclass
class IntegerLattice:
    """An integer lattice, `base + k * step` for integer `k`.

    `base = None` stands for empty.
    """

    base: Union[int, None]
    step: Union[int, None]

    def intersect(self, other: "IntegerLattice") -> "IntegerLattice":
        """Return a new integer lattice that is the intersection of the two."""
        # The intersection is the lattice of integers n where
        #       n = base1 + step1 * k1 ,                                (1)
        #       n = base2 + step2 * k2 ,
        # for some integers k1 and k2.
        #
        # This implies
        #       base2 - base1 = step1 * k1 - step2 * k2 .              (2)
        # Bézout's identity implies that a solution exists iff
        #       base2 - base1 = delta = m * gcd(step1, step2) ,
        # where m is some integer.
        #
        # In that case, let x, y be Bézout coefficients, i.e.,
        #       gcd = step1 * x + step2 * y .
        # Then
        #       step1 * (x * m) - step2 * (-y * m) = m * gcd = base2 - base1 ,
        # which implies that a solution for equation (2) above is
        #       k1 = x * m ,  k2 = -y * m
        #
        # All pairs of solutions are given by
        #       (k1 + p * step2 / gcd, k2 + p * step1 / gcd)
        # where p is an integer.
        #
        # Plugging this into equation (1) above, we get that the integers n on the
        # intersection lattice obey
        #       n = base1 + x * m * step1 + p * step1 * step2 / gcd
        #         = base1 + x * m * step1 + p * lcm ,
        # where lcm is the least common multiplier, lcm = step1 * step2 / gcd.
        #
        # Similarly,
        #       n = base2 - y * m * step2 + p * step1 * step2 / gcd
        #         = base2 - y * m * step2 + p * lcm
        #         = base1 + (base2 - base1) - y * m * step2 + p * lcm
        #         = base1 + m * (gcd - y * step2) + p * lcm
        #         = base1 + m * x * step1 + p * lcm ,
        # where we used Bézout's identity. This matches the above.

        # In other words, the new lattice is given by
        #       base = base1 + x * m * step1
        #            = base1 + x * (base2 - base1) / gcd * step1
        #       step = lcm = step1 * step2 / gcd .

        if self.empty() or other.empty():
            return IntegerLattice(None, None)

        if self.step == 0 and other.step == 0:
            if self.base == other.base:
                return IntegerLattice(self.base, 0)
            else:
                return IntegerLattice(None, None)

        gcd, x, _ = extended_gcd(self.step, other.step)

        delta = other.base - self.base
        if delta % gcd != 0:
            return IntegerLattice(None, None)

        m = delta // gcd
        new_base = self.base + x * m * self.step
        new_step = self.step // gcd * other.step
        return IntegerLattice(new_base, new_step)

    def __and__(self, other: "IntegerLattice") -> "IntegerLattice":
        return self.intersect(other)

    def empty(self) -> bool:
        """Return true if this lattice is empty."""
        return self.base is None

    def first_after(self, start: int) -> Union[int, None]:
        """Find the smallest entry in the lattice that is larger than or equal to a
        starting point.

        Returns `None` if the lattice is empty or it contains a single element that is
        smaller than `start`.
        """
        # we have
        #       base + k * step >= start
        #   =>  k >= (start - base) / step
        # smallest integer larger than or equal to something is the ceil:
        #       k = ceil((start - base) / step) .

        if self.empty():
            return None
        if self.step == 0:
            if self.base >= start:
                return self.base
            else:
                return None

        # can't use floating point because of overflow
        # instead use:
        #       ceil(n / m) = floor((n - 1) / m) + 1
        # (https://en.wikipedia.org/wiki/Floor_and_ceiling_functions)
        k = (start - self.base - 1) // self.step + 1
        return self.base + k * self.step

    def __repr__(self) -> str:
        if self.empty():
            return "<EMPTY>"
        else:
            return f"<{self.base} + k * {self.step}>"


T = TypeVar("T")


class PriorityQueue(Generic[T]):
    """Priority queue implementation based on Python docs.

    https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes
    """

    _REMOVED = "<removed-task>"

    _heap: List[List[Tuple[int, int, T]]]
    _finder: Dict[T, int]
    _counter: Iterator[int]
    _n_tasks: int

    def __init__(self):
        self._heap = []
        self._finder = {}
        self._counter = itertools.count()
        self._n_tasks = 0

    def add_task(self, task: T, priority: int = 0):
        """Add a new task or update the priority of an existing task."""
        if task in self._finder:
            self.remove_task(task)

        count = next(self._counter)
        entry = [priority, count, task]
        self._finder[task] = entry
        heapq.heappush(self._heap, entry)

        self._n_tasks += 1

    def remove_task(self, task: T):
        """Mark an existing task as removed.

        Raise `KeyError` if not found.
        """
        entry = self._finder[task]
        entry[-1] = self._REMOVED
        self._n_tasks -= 1

    def pop_task(self) -> T:
        """Remove and return the lowest priority task.

        Raise `KeyError` if empty.
        """
        while self._heap:
            _, _, task = heapq.heappop(self._heap)
            if task is not self._REMOVED:
                self._finder.pop(task)
                self._n_tasks -= 1
                return task

        raise KeyError("Pop from empty priority queue")

    def peek(self) -> T:
        """Take a peek at the lowest priority task.

        This also cleans any items tagged with REMOVED that might have had lower
        priority than the currently lowest priority task.

        Raise `KeyError` if empty.
        """
        while self._heap:
            _, _, task = self._heap[0]
            if task is not self._REMOVED:
                return task

            heapq.heappop(self._heap)

        raise KeyError("Peek at empty priority queue")

    def __len__(self) -> int:
        return self._n_tasks

    def __repr__(self) -> str:
        n_tasks = len(self)
        s = f"PriorityQueue(n_tasks={n_tasks}, tasks=["
        if n_tasks != 0:
            s += f"{self.peek()}, ..."

        s += "])"
        return s


def itermatrix() -> Iterator[Matrix[str]]:
    data = []
    for line in iterinput():
        if line:
            data.append(list(line))
        else:
            if data:
                matrix = _matrix_from_data(data)
                logger.debug(f"Loaded matrix size {matrix.nrows} x {matrix.ncols}.")
                data = []
                yield matrix

    if data:
        matrix = _matrix_from_data(data)
        logger.debug(f"Loaded matrix size {matrix.nrows} x {matrix.ncols}.")
        yield matrix
