#! /usr/bin/env python
import sys
from typing import Optional, List, Dict
from dataclasses import dataclass, field

@dataclass
class Node:
    value: Optional[int] = None
    operator: str = "literal"
    operands: List[str] = field(default_factory=list)


def dfs(name: str, node_map: Dict[str, Node]):
    stack = [(name, "traverse")]

    while stack:
        name, state = stack.pop()
        node = node_map[name]

        assert state in ["traverse", "evaluate"], f"invalid state: {state}"

        if state == "traverse" and node.value is None:
            # need to process the operands, then come back here
            stack.append((name, "evaluate"))
            for child_name in node.operands:
                child = node_map[child_name]
                if child.value is None:
                    stack.append((child_name, "traverse"))
        elif node.value is None:
            assert node.operator != "literal"
            a_name, b_name = node.operands
            a = node_map[a_name].value
            b = node_map[b_name].value
            
            assert a is not None
            assert b is not None

            if node.operator == "+":
                node.value = a + b
            elif node.operator == "-":
                node.value = a -b
            elif node.operator == "*":
                node.value = a * b
            elif node.operator == "/":
                node.value = a // b
            else:
                raise ValueError(f"unknown operator: {node.operator}")


fname = "input21" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    node_map = {}
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        
        name, operation = [_.strip() for _ in line.split(":")]
        
        try:
            value = int(operation)
        except ValueError:
            value = None

        if value is not None:
            node = Node(value)
        else:
            if "+" in operation:
                operator = "+"
            elif "-" in operation:
                operator = "-"
            elif "*" in operation:
                operator = "*"
            elif "/" in operation:
                operator = "/"
            else:
                raise ValueError(f"unrecognized operation: {operation}")

            a, b = [_.strip() for _ in operation.split(operator)]
            node = Node(None, operator, [a, b])

        node_map[name] = node

dfs("root", node_map)

root = node_map["root"]
print(f"root yells {root.value}")
