from dataclasses import dataclass, replace
from typing import Dict, List, Literal, Tuple, Union


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int


VarInterval = Tuple[int, int]


@dataclass
class PartInterval:
    x: VarInterval
    m: VarInterval
    a: VarInterval
    s: VarInterval

    def empty(self) -> bool:
        empty_x = self.x[1] <= self.x[0]
        empty_m = self.m[1] <= self.m[0]
        empty_a = self.a[1] <= self.a[0]
        empty_s = self.s[1] <= self.s[0]
        return empty_x or empty_m or empty_a or empty_s

    def count(self) -> int:
        n_x = max(0, self.x[1] - self.x[0])
        n_m = max(0, self.m[1] - self.m[0])
        n_a = max(0, self.a[1] - self.a[0])
        n_s = max(0, self.s[1] - self.s[0])
        return n_x * n_m * n_a * n_s


@dataclass
class BaseNode:
    def run(
        self, _: Union[Part, PartInterval]
    ) -> Union["BaseNode", List[Tuple[PartInterval, "BaseNode"]]]:
        raise NotImplementedError("This should only be called on descendants")


@dataclass
class IfNode(BaseNode):
    kind: Literal["<", ">"]
    var: str
    threshold: int
    left: BaseNode  # this is the "then" branch
    right: BaseNode  # this is the "else" branch

    def __post_init__(self):
        assert self.kind in "<>"

    def run(
        self, part: Union[Part, PartInterval]
    ) -> Union[BaseNode, List[Tuple[PartInterval, BaseNode]]]:
        value = getattr(part, self.var)
        if isinstance(part, Part):
            flag = (
                value < self.threshold if self.kind == "<" else value > self.threshold
            )
            return [self.right, self.left][flag].run(part)
        elif isinstance(part, PartInterval):
            res = []

            part_left = replace(part)
            if self.kind == "<":
                new_value = (value[0], min(value[1], self.threshold))
                setattr(part_left, self.var, new_value)
            elif self.kind == ">":
                new_value = (max(value[0], self.threshold + 1), value[1])
                setattr(part_left, self.var, new_value)
            if not part_left.empty():
                res.extend(self.left.run(part_left))

            part_right = replace(part)
            if self.kind == ">":
                new_value = (value[0], min(value[1], self.threshold + 1))
                setattr(part_right, self.var, new_value)
            elif self.kind == "<":
                new_value = (max(value[0], self.threshold), value[1])
                setattr(part_right, self.var, new_value)
            if not part_right.empty():
                res.extend(self.right.run(part_right))

            return res


@dataclass
class MoveNode(BaseNode):
    workflow: str = ""

    def __post_init__(self):
        assert len(self.workflow) > 1

    def run(
        self, part: Union[Part, PartInterval]
    ) -> Union["MoveNode", List[Tuple[PartInterval, "MoveNode"]]]:
        if isinstance(part, Part):
            return self
        elif isinstance(part, PartInterval):
            return [(part, self)]


@dataclass
class EndNode(BaseNode):
    kind: Literal["A", "R"]

    def __post_init__(self):
        assert self.kind in "AR"

    def run(
        self, part: Union[Part, PartInterval]
    ) -> Union["EndNode", List[Tuple[PartInterval, "EndNode"]]]:
        if isinstance(part, Part):
            return self
        elif isinstance(part, PartInterval):
            return [(part, self)]


class Parser:
    sentence: str
    ip: int

    def __init__(self, sentence: str):
        self.sentence = sentence
        self.ip = 0

    def expr(self) -> BaseNode:
        """Parse an expression.

        An expression is either an if with a "then" and an "else" option, or an Accept
        or Reject.
        """
        ch = self.feed()
        if ch in "AR":
            return EndNode(ch)

        if self.peek().isalpha():
            # this is a workflow
            return self.workflow(prefix=ch)
        else:
            var = ch
            assert var in "xmas"

        kind = self.feed()
        assert kind in "<>"

        threshold = self.number()
        assert self.feed() == ":"

        if_true = self.workflow()
        assert self.feed() == ","

        if_false = self.expr()
        return IfNode(kind, var=var, threshold=threshold, left=if_true, right=if_false)

    def number(self) -> int:
        s = ""
        ch = self.peek()
        while ch.isdigit():
            s += ch
            self.ip += 1
            if self.ip >= len(self.sentence):
                break
            ch = self.peek()

        return int(s)

    def workflow(self, prefix: str = "") -> Union[EndNode, MoveNode]:
        s = prefix
        ch = self.peek()
        if len(prefix) == 0 and ch in "AR":
            self.ip += 1
            return EndNode(ch)
        while ch.isalpha():
            s += ch
            self.ip += 1
            if self.ip >= len(self.sentence):
                break
            ch = self.peek()

        return MoveNode(s)

    def feed(self) -> str:
        """Return the following character in the sentence, and advance `ip`."""
        assert self.ip < len(self.sentence)
        ch = self.sentence[self.ip]
        self.ip += 1
        return ch

    def peek(self) -> str:
        """Return the following character in the sentence without advancing `ip`."""
        assert self.ip < len(self.sentence)
        return self.sentence[self.ip]
