import warnings
from collections import defaultdict
from typing import Iterator, List, Tuple

from utils import logger


class Multigraph:
    def __init__(self):
        self.children_map = defaultdict(list)

    def add_node(self, name: str):
        if name not in self.children_map:
            logger.debug(f"Adding node {name}")
            self.children_map[name] = []
        else:
            warnings.warn(f"Trying to add existing node {name}")

    def add_edge(self, origin: str, target: str):
        self.children_map[origin].append(target)

    def __repr__(self) -> str:
        s = "Multigraph(\n"

        origins = sorted(self.children_map.keys())
        for origin in origins:
            s += f"    {origin} -> {', '.join(self.children_map[origin])}\n"

        s += ")"

        return s

    def __getitem__(self, name: str) -> List[str]:
        return self.children_map[name]

    def parse_row(self, s: str) -> Tuple[str, str]:
        parts = s.split("=")
        assert len(parts) == 2

        origin = parts[0].strip()
        assert "," not in origin
        assert " " not in origin

        targets_list = parts[1].strip()
        assert targets_list.startswith("(")
        assert targets_list.endswith(")")

        targets = [_.strip() for _ in targets_list[1:-1].split(",")]
        for target in targets:
            assert " " not in target
            self.add_edge(origin, target)

    @staticmethod
    def from_iterator(it: Iterator[str]) -> "Multigraph":
        g = Multigraph()
        for line in it:
            line = line.strip()
            if not line:
                continue

            g.parse_row(line)

        return g

    def get_left_child(self, name: str) -> str:
        children = self.children_map[name]
        assert len(children) == 2
        return children[0]

    def get_right_child(self, name: str) -> str:
        children = self.children_map[name]
        assert len(children) == 2
        return children[1]


def check_degrees(g: Multigraph):
    for children in g.children_map.values():
        assert len(children) == 2
