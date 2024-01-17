#! /usr/bin/env python
import re
from types import SimpleNamespace
from typing import Dict, Tuple

from utils import iterinput, logger

from common19 import BaseNode, EndNode, MoveNode, Parser, Part


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
