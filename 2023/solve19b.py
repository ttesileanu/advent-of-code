#! /usr/bin/env python
import re
from typing import Dict, List, Tuple, Union

from utils import iterinput, logger

from common19 import BaseNode, EndNode, MoveNode, Parser, PartInterval


def process_interval(
    interval: PartInterval, workflows: Dict[str, BaseNode], start: str = "in"
) -> Union[BaseNode, List[Tuple[PartInterval, BaseNode]]]:
    workflow = workflows[start]

    intermediate = workflow.run(interval)

    results = []
    for sub_interval, outcome in intermediate:
        assert not sub_interval.empty()
        if isinstance(outcome, MoveNode):
            sub_results = process_interval(
                sub_interval, workflows, start=outcome.workflow
            )
            results.extend(sub_results)
        else:
            assert isinstance(outcome, EndNode)
            results.append((sub_interval, outcome))

    return results


def count_accept(workflows: Dict[str, BaseNode], start: str = "in") -> int:
    ALL = (1, 4001)
    full_interval = PartInterval(ALL, ALL, ALL, ALL)
    outcomes = process_interval(full_interval, workflows, start=start)

    logger.debug(f"{outcomes=}")

    n = 0
    for interval, outcome in outcomes:
        assert isinstance(outcome, EndNode)
        if outcome.kind == "A":
            n += interval.count()

    return n


if __name__ == "__main__":
    workflow_regex = re.compile(r"([a-zA-Z]+){(.*)}")
    parts_regex = re.compile(r"{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}")

    workflows_str = []

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

        # these can be ignored here

    # parse the workflows
    workflows = {}
    for w in workflows_str:
        name = w[0]

        parser = Parser(w[1])

        graph = parser.expr()
        logger.debug(f"workflow={graph}")
        workflows[name] = graph

    # run the workflows on each part
    n_accept = count_accept(workflows)

    print(f"The total number of ratings that will be accepted is {n_accept}")
