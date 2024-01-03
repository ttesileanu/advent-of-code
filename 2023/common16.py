from enum import auto, Flag
from typing import List, Literal, Optional, Tuple

from utils import logger, Matrix


try:
    import matplotlib.pyplot as plt

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


class LightStatus(Flag):
    EMPTY = 0

    # input *from* the North, East, South, West
    IN_N = auto()
    IN_E = auto()
    IN_S = auto()
    IN_W = auto()

    # output *to* North, East, South, West
    OUT_N = auto()
    OUT_E = auto()
    OUT_S = auto()
    OUT_W = auto()

    @staticmethod
    def from_str(
        direction: Literal["N", "S", "E", "W"], orientation: Literal["in", "out"] = "in"
    ) -> "LightStatus":
        if orientation == "in":
            return IN_MAP[direction]
        elif orientation == "out":
            return OUT_MAP[direction]
        else:
            raise ValueError(f"Unknown orientation {orientation}")


IN_MAP = {
    "N": LightStatus.IN_N,
    "E": LightStatus.IN_E,
    "W": LightStatus.IN_W,
    "S": LightStatus.IN_S,
}
OUT_MAP = {
    "N": LightStatus.OUT_N,
    "E": LightStatus.OUT_E,
    "W": LightStatus.OUT_W,
    "S": LightStatus.OUT_S,
}


class OpticalSystem:
    elements_map: Matrix[str]
    light_map: Matrix[LightStatus]

    def __init__(self, mat: Matrix[str]):
        self.elements_map = mat
        self.light_map = Matrix(
            [mat.ncols * [LightStatus.EMPTY] for _ in range(mat.nrows)]
        )

    def insert_ray(self, i: int, j: int, port: str):
        assert port in "EWNS"
        port_enum = LightStatus.from_str(port)
        if port_enum in self.light_map[i, j]:
            # this was already inserted, nothing to do
            return

        stack = [(i, j, port)]
        while stack:
            i, j, port = stack.pop()
            logger.debug(f"Entering cell ({i}, {j}) thruogh port {port}")
            candidates = self._propagate(i, j, port)
            for ni, nj, nport in candidates:
                nport_enum = LightStatus.from_str(nport)
                if nport_enum not in self.light_map[ni, nj]:
                    stack.append((ni, nj, nport))

    def _propagate(self, i: int, j: int, port: str) -> List[Tuple[int, int, str]]:
        """Propagate the light through one cell.

        Assumes light enters cell `(i, j)` through the input `port`, propagates the
        light according to the optical element at that location (activating the
        necessary output ports, if any), and generates a list of side effects.

        Specifically, the side effect `(ni, nj, nport)` means that light enters cell
        `(ni, nj)` through input port `nport`.
        """
        port_enum = LightStatus.from_str(port)
        self.light_map[i, j] = self.light_map[i, j] | port_enum

        elem = self.elements_map[i, j]
        neighbors = list(self.elements_map.iterneighbors(i, j, diagonals=False))
        candidates = []
        if (
            elem in ".\\/"
            or (elem == "-" and port in "EW")  # behaves like empty cell
            or (elem == "|" and port in "NS")  # behaves like empty cell
        ):
            effective_elem = elem if elem in ".\\/" else "."

            if effective_elem == ".":
                out_map = {"W": "E", "E": "W", "N": "S", "S": "N"}
                pos_map = {"W": (0, 1), "E": (0, -1), "N": (1, 0), "S": (-1, 0)}
                newport_map = {"W": "W", "E": "E", "N": "N", "S": "S"}
            elif effective_elem == "\\":
                out_map = {"W": "S", "E": "N", "N": "E", "S": "W"}
                pos_map = {"W": (1, 0), "E": (-1, 0), "N": (0, 1), "S": (0, -1)}
                newport_map = {"W": "N", "E": "S", "N": "W", "S": "E"}
            elif effective_elem == "/":
                out_map = {"W": "N", "E": "S", "N": "W", "S": "E"}
                pos_map = {"W": (-1, 0), "E": (1, 0), "N": (0, -1), "S": (0, 1)}
                newport_map = {"W": "S", "E": "N", "N": "E", "S": "W"}
            else:
                raise RuntimeError("Should not happen: effective_elem not in ., \\, /")

            out_port = out_map[port]
            out_port_enum = LightStatus.from_str(out_port, orientation="out")
            self.light_map[i, j] = self.light_map[i, j] | out_port_enum

            di, dj = pos_map[port]
            ni = i + di
            nj = j + dj

            nport = newport_map[port]
            if (ni, nj) in neighbors:
                candidates.append((ni, nj, nport))
        elif elem in "-|":
            # we already ruled out coming in parallel to the splitters
            if port in "EW":
                self.light_map[i, j] = (
                    self.light_map[i, j] | LightStatus.OUT_N | LightStatus.OUT_S
                )

                if (i - 1, j) in neighbors:
                    candidates.append((i - 1, j, "S"))
                if (i + 1, j) in neighbors:
                    candidates.append((i + 1, j, "N"))
            elif port in "NS":
                self.light_map[i, j] = (
                    self.light_map[i, j] | LightStatus.OUT_E | LightStatus.OUT_W
                )

                if (i, j - 1) in neighbors:
                    candidates.append((i, j - 1, "E"))
                if (i, j + 1) in neighbors:
                    candidates.append((i, j + 1, "W"))
            else:
                raise ValueError(f"Unknown port {port}")
        else:
            raise ValueError(f"Unknown elem {elem}")

        return candidates

    def show(self) -> str:
        res_l = []
        for i in range(self.nrows):
            row_l = []
            for j in range(self.ncols):
                elem = self.elements_map[i, j]
                if elem != ".":
                    row_l.append(elem)
                else:
                    light = self.light_map[i, j]
                    if light == LightStatus.EMPTY:
                        ch = "."
                    elif light == LightStatus.IN_W | LightStatus.OUT_E:
                        ch = ">"
                    elif light == LightStatus.IN_E | LightStatus.OUT_W:
                        ch = "<"
                    elif light == LightStatus.IN_N | LightStatus.OUT_S:
                        ch = "v"
                    elif light == LightStatus.IN_S | LightStatus.OUT_N:
                        ch = "^"
                    else:
                        ch = "2"
                    row_l.append(ch)

            row = "".join(row_l)
            res_l.append(row)

        return "\n".join(res_l)

    if FANCY_PLOTTING:

        def show_mpl(self, ax: Optional[plt.Axes] = None):
            B = 0.4
            BW = 3
            LW = 1
            A = 1.0

            if ax is None:
                _, ax = plt.subplots(figsize=(4, 4))

            color = [0.7, 0.0, 0.0]
            for i in range(self.nrows):
                for j in range(self.ncols):
                    elem = self.elements_map[i, j]
                    if elem == "/":
                        ax.plot([j - B, j + B], [i + B, i - B], lw=BW, c="k")
                    elif elem == "\\":
                        ax.plot([j - B, j + B], [i - B, i + B], lw=BW, c="k")
                    elif elem == "-":
                        ax.plot([j - B, j + B], [i, i], lw=BW, c="k")
                    elif elem == "|":
                        ax.plot([j, j], [i - B, i + B], lw=BW, c="k")
                    elif elem != ".":
                        raise ValueError(f"Unknown elem {elem}")

                    light = self.light_map[i, j]
                    if LightStatus.IN_W in light:
                        ax.plot([j - 0.5, j], [i, i], lw=LW, c=color, alpha=A)
                    if LightStatus.OUT_E in light:
                        ax.plot([j, j + 0.5], [i, i], lw=LW, c=color, alpha=A)
                    if LightStatus.IN_E in light:
                        ax.plot([j + 0.5, j], [i, i], lw=LW, c=color, alpha=A)
                    if LightStatus.OUT_W in light:
                        ax.plot([j, j - 0.5], [i, i], lw=LW, c=color, alpha=A)

                    if LightStatus.IN_N in light:
                        ax.plot([j, j], [i - 0.5, i], lw=LW, c=color, alpha=A)
                    if LightStatus.OUT_S in light:
                        ax.plot([j, j], [i, i + 0.5], lw=LW, c=color, alpha=A)
                    if LightStatus.IN_S in light:
                        ax.plot([j, j], [i + 0.5, i], lw=LW, c=color, alpha=A)
                    if LightStatus.OUT_N in light:
                        ax.plot([j, j], [i, i - 0.5], lw=LW, c=color, alpha=A)

            ax.set_aspect(1.0)
            ax.invert_yaxis()
            plt.show()

    if not FANCY_PLOTTING:

        def show_mpl():
            pass

    @property
    def nrows(self) -> int:
        assert self.elements_map.nrows == self.light_map.nrows
        return self.elements_map.nrows

    @property
    def ncols(self) -> int:
        assert self.elements_map.ncols == self.light_map.ncols
        return self.elements_map.ncols

    def count_energized(self) -> int:
        n_energized = 0
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.light_map[i, j] != LightStatus.EMPTY:
                    n_energized += 1

        return n_energized
