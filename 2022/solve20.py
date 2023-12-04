#! /usr/bin/env python
import sys
from dataclasses import dataclass
from typing import List, Optional
from tqdm import tqdm


@dataclass
class Node:
    """Node in a circular list."""

    value: int
    left: Optional["Node"]
    right: Optional["Node"]

    def __init__(
        self,
        value: int = 0,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
    ):
        self.value = value

        if left is None and right is None:
            left = right = self
        else:
            assert left is not None and right is not None
            left.right = self
            right.left = self

        self.left = left
        self.right = right


def bump(node: Node, shift: int):
    if shift == 0:
        return

    # find the target
    target = node
    if shift >= 0:
        for i in range(shift):
            target = target.right
    else:
        for i in range(-shift + 1):
            target = target.left

    original_left = node.left
    original_right = node.right

    # let our original neighbors know that we're not there anymore
    original_left.right = original_right
    original_right.left = original_left

    # let target's right neighbor know that we are now there
    target.right.left = node
    
    # update our neighbors
    node.left = target
    node.right = target.right

    # let target know that we're now their neighbor
    target.right = node


def to_list(start: Node) -> List[int]:
    res = []
    node = start
    while True:
        res.append(node.value)
        node = node.right

        if id(node) == id(start):
            break

    return res


def mix(signal: List[int]) -> List[int]:
    n = len(signal)

    # turn the signal into a circular list
    start = Node(signal[0])

    # keep track of the elements in order
    order = [start]
    node = start
    for value in signal[1:]:
        node = Node(value, left=node, right=start)
        order.append(node)
        
    # in order, move each element to its new place
    for node in tqdm(order):
        shift = node.value
        shift = shift % (n - 1)
        if shift == 0:
            continue

        if shift > n // 2:
            shift = shift - n + 1

        bump(node, shift)

    # turn this back into a list
    mixed = to_list(start)

    return mixed


fname = "input20" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    signal = []
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        signal.append(int(line))

mixed = mix(signal)
print(mixed)

shifts = [1000, 2000, 3000]
idx0 = mixed.index(0)
idxs = [(idx0 + _) % len(mixed) for _ in shifts]

coordinates = [mixed[_] for _ in idxs]
print(f"grove coordinates: {coordinates}; sum: {sum(coordinates)}")
