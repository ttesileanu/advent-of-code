#! /usr/bin/env python
import sys
from typing import Optional, List, Dict
from dataclasses import dataclass, field

@dataclass
class Node:
    value: Optional[int] = None
    operator: str = "literal"
    operands: List[str] = field(default_factory=list)


def dfs(name: str, node_map: Dict[str, Node], parent_map: Dict[str, str]):
    stack = [(name, "traverse")]

    visited = set()
    while stack:
        name, state = stack.pop()
        node = node_map[name]
        
        visited.add(name)

        assert state in ["traverse", "evaluate"], f"invalid state: {state}"

        if state == "traverse" and node.value is None:
            # need to ..., ..., then come back here
            stack.append((name, "evaluate"))

            # need to ..., process the operands, ...
            for child_name in node.operands:
                child = node_map[child_name]
                if child.value is None and child_name not in visited:
                    stack.append((child_name, "traverse"))

            # need to process the parent, ..., ...
            if name in parent_map:
                parent_name = parent_map[name]
                parent = node_map[parent_name]
                if parent.value is None and parent_name not in visited:
                    stack.append((parent_name, "traverse"))
        elif node.value is None:
            if name != "humn":
                assert node.operator != "literal"
                a_name, b_name = node.operands
                a = node_map[a_name].value
                b = node_map[b_name].value
            else:
                a = b = None

            if a is not None and b is not None:
                # straightforward evaluation
                if node.operator == "+":
                    node.value = a + b
                elif node.operator == "-":
                    node.value = a -b
                elif node.operator == "*":
                    node.value = a * b
                elif node.operator == "/":
                    node.value = a // b
                elif node.operator == "=":
                    assert a == b
                else:
                    raise ValueError(f"unknown operator: {node.operator}")
            elif node.operator == "=":
                known = a if a is not None else b
                assert known is not None

                node.value = known
            else:
                # try to infer from parent
                parent_name = parent_map[name]
                parent = node_map[parent_name]

                assert parent.value is not None
                
                assert len(parent.operands) == 2
                other_names = [_ for _ in parent.operands if _ != name]
                assert len(other_names) == 1
                
                other = node_map[other_names[0]].value
                assert other is not None

                if parent.operator == "=":
                    node.value = other
                elif parent.operator == "+":
                    node.value = parent.value - other
                elif parent.operator == "*":
                    assert (parent.value % other) == 0
                    node.value = parent.value // other
                elif parent.operator == "-":
                    sign = 1 if parent.operands[0] == name else -1
                    node.value = sign * parent.value + other
                elif parent.operator == "/":
                    if parent.operands[0] == name:
                        node.value = parent.value * other
                    else:
                        node.value = other / parent.value
                else:
                    raise ValueError(f"unknown operator: {node.operator}")


fname = "input21" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    node_map = {}
    parent_map = {}
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
            # fix human value
            if name == "humn":
                value = None

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
            
            # fix root operator
            if name == "root":
                operator = "="
            
            assert a not in parent_map
            assert b not in parent_map
            
            parent_map[a] = name
            parent_map[b] = name
            node = Node(None, operator, [a, b])

        node_map[name] = node

# print(node_map)

dfs("humn", node_map, parent_map)

humn = node_map["humn"]
print(f"human yells {humn.value}")
