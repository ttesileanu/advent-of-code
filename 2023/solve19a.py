#! /usr/bin/env python
import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict, Literal, Tuple, Union

from utils import iterinput, logger


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int


@dataclass
class BaseNode:
    kind: Literal["<", ">", "M", "A", "R"]  # M = move to different workflow

    def run(self, part: Part) -> "BaseNode":
        raise NotImplementedError("This should only be called on descendants.")


@dataclass
class IfNode(BaseNode):
    var: str
    threshold: int
    left: BaseNode  # this is the "then" branch
    right: BaseNode  # this is the "else" branch

    def __post_init__(self):
        assert self.kind in "<>"

    def run(self, part: Part) -> BaseNode:
        value = getattr(part, self.var)
        flag = value < self.threshold if self.kind == "<" else value > self.threshold
        return [self.right, self.left][flag].run(part)


@dataclass
class MoveNode(BaseNode):
    kind: str = "M"
    workflow: str = ""

    def __post_init__(self):
        assert self.kind == "M"
        assert len(self.workflow) > 0

    def run(self, _: Part) -> "MoveNode":
        return self


@dataclass
class EndNode(BaseNode):
    def __post_init__(self):
        assert self.kind in "AR"

    def run(self, _: Part) -> "EndNode":
        return self


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

        return MoveNode(workflow=s)

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


def process(
    part: Part, workflows: Dict[str, BaseNode], start: str = "in"
) -> Tuple[bool, SimpleNamespace]:
    workflow_chain = [start]
    workflow = workflows[start]
    while True:
        result = workflow.run(part)
        if isinstance(result, MoveNode):
            workflow = workflows[result.workflow]
            workflow_chain.append(result.workflow)
        elif isinstance(result, EndNode):
            workflow_chain.append(result.kind)
            return result.kind == "A", workflow_chain


if __name__ == "__main__":
    workflow_regex = re.compile(r"([a-zA-Z]+){(.*)}")
    parts_regex = re.compile(r"{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}")

    workflows_str = []
    parts = []

    it = iterinput()
    for line in it:
        if not line:
            # workflows are over
            break

        workflow_match = workflow_regex.fullmatch(line)
        assert workflow_match is not None

        workflows_str.append(workflow_match.groups())

    logger.debug(f"{workflows_str=}")

    for line in it:
        parts_match = parts_regex.fullmatch(line)
        assert parts_match is not None

        x, m, a, s = [int(_) for _ in parts_match.groups()]
        parts.append(Part(x, m, a, s))

    logger.debug(f"{parts=}")

    # parse the workflows
    workflows = {}
    for w in workflows_str:
        name = w[0]

        parser = Parser(w[1])

        graph = parser.expr()
        logger.debug(f"workflow={graph}")
        workflows[name] = graph

    # run the workflows on each part
    s = 0
    for part in parts:
        accept, chain = process(part, workflows)
        logger.debug(f"{part}: {' -> '.join(chain)}")

        if accept:
            s += part.x + part.m + part.a + part.s

    print(f"The sum of all rating numbers of all accepted parts is {s}")
