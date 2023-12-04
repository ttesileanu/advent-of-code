#! /usr/bin/env python
import inspect
import math
from typing import TextIO, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Monkey:
    items: List[int] = field(default_factory=list)
    operation: Optional[Callable] = None
    test: Optional[Callable] = None
    targets: List[int] = field(default_factory=list)


def read_line(f: TextIO) -> str:
    line = ""
    while len(line) == 0:
        line = next(f).strip()

    return line


def parse_monkey_idx(f: TextIO, idx_hint: int) -> int:
    line = read_line(f)
    assert line.startswith("Monkey ")
    assert line.endswith(":")

    idx = int(line[7:-1])
    assert idx == idx_hint

    return idx


def parse_items(f: TextIO) -> List[int]:
    line = read_line(f)
    prefix, items_str, *_ = line.split(":")
    assert len(_) == 0
    assert "items" in prefix

    items = [int(_) for _ in items_str.split(",")]
    return items


def parse_operation(f: TextIO) -> Callable:
    line = read_line(f)
    assert line.startswith("Operation:")

    op_str = line[10:].strip()
    lhs, rhs, *_ = op_str.split("=")
    assert len(_) == 0

    lhs = lhs.strip()
    rhs = rhs.strip()

    assert lhs == "new"
    if "*" in rhs:
        operator = "*"
        op1, op2, *_ = rhs.split("*")
    elif "+" in rhs:
        operator = "+"
        op1, op2, *_ = rhs.split("+")
    else:
        raise ValueError(f"unknown operation, {op_str}")

    assert len(_) == 0

    op1 = op1.strip()
    op2 = op2.strip()

    if op1 == "old" and op2 == "old":
        if operator == "*":
            return lambda old: old * old
        elif operator == "+":
            return lambda old: 2 * old
    else:
        if op2 == "old":
            op1, op2 = op2, op1

        op2 = int(op2)
        if op1 != "old":
            op1 = int(op1)
            if operator == "*":
                return lambda old, op1=op1, op2=op2: op1 * op2
            elif operator == "+":
                return lambda old, op1=op1, op2=op2: op1 + op2
        else:
            if operator == "*":
                return lambda old, op2=op2: old * op2
            elif operator == "+":
                return lambda old, op2=op2: old + op2


def parse_test(f: TextIO) -> Callable:
    line = read_line(f)
    assert line.startswith("Test:")

    condition = line[5:].strip()
    assert condition.startswith("divisible by")

    modulo = int(condition[12:])
    return lambda count, modulo=modulo: (count % modulo) == 0


def parse_if(f: TextIO, value: str) -> int:
    line = read_line(f)
    prefix = f"If {value}: throw to monkey "
    assert line.startswith(prefix)

    monkey_idx = int(line[len(prefix) :])
    return monkey_idx


def parse_monkey(f: TextIO, idx_hint: int) -> Monkey:
    idx = parse_monkey_idx(f, idx_hint)
    items = parse_items(f)
    operation = parse_operation(f)
    test = parse_test(f)
    target_true = parse_if(f, "true")
    target_false = parse_if(f, "false")

    return Monkey(items, operation, test, [target_true, target_false])


def print_monkey(monkey: Monkey, idx: int):
    print(f"Monkey {idx}:")
    print(f"  Items: {monkey.items}")
    s = inspect.getsource(monkey.operation).strip()
    print(f"  Operation: {s}")
    s = inspect.getsource(monkey.test).strip()
    print(f"  Test: {s}")
    print(f"    If true: throw to monkey {monkey.targets[0]}")
    print(f"    If false: throw to monkey {monkey.targets[1]}")


def run_round(monkeys: List[Monkey], inspections: List[int]):
    for k, monkey in enumerate(monkeys):
        for item in monkey.items:
            worry = monkey.operation(item) // 3
            target = monkey.targets[0 if monkey.test(worry) else 1]

            assert target != k
            monkeys[target].items.append(worry)

            inspections[k] += 1

        monkey.items.clear()


with open("input11.txt", "rt") as f:
    monkeys = []
    while True:
        try:
            monkeys.append(parse_monkey(f, len(monkeys)))
        except StopIteration:
            break


n_rounds = 20
inspections = len(monkeys) * [0]
for i in range(n_rounds):
    run_round(monkeys, inspections)


for i, monkey in enumerate(monkeys):
    print_monkey(monkey, i)
    print()

for i, count in enumerate(inspections):
    print(f"Monkey {i} inspected items {count} times.")

n_highest = 2
sorted_inspections = sorted(inspections)

monkey_business = math.prod(sorted_inspections[-n_highest:])
print(f"level of monkey business after {n_rounds} rounds: {monkey_business}")
