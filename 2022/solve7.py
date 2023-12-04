#! /usr/bin/env python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Tree:
    parent: Optional["Tree"] = None
    children: dict[str, "Tree"] = field(default_factory=dict)
    size: Optional[int] = None
    is_dir: bool = True


with open("input7.txt", "rt") as f:
    tree = Tree()
    pwd = None
    state = "command"
    for i, line in enumerate(f):
        line = line.strip()

        if line.startswith("$ "):
            state = "command"
            line = line[2:].strip()
            if line.startswith("cd "):
                d = line[3:].strip()
                if d == "/":
                    pwd = tree
                elif d == "..":
                    assert pwd is not None, "first cd should be cd /"
                    pwd = pwd.parent
                    assert pwd is not None, "cd .. on root"
                else:
                    assert pwd is not None, "first cd should be cd /"
                    assert d in pwd.children, "unknown sub-directory"
                    pwd = pwd.children[d]
                    assert pwd.is_dir, "cd to non-dir"
            elif line == "ls":
                assert pwd is not None
                state = "listing"
            else:
                raise AssertionError(f"unknown command, {line}")
        else:
            assert state == "listing"
            size_str, name, *_ = line.split(" ")
            assert len(_) == 0, "invalid listing output"
            if size_str.strip() == "dir":
                if name not in pwd.children:
                    pwd.children[name] = Tree(parent=pwd)
                else:
                    assert pwd.children[name].is_dir
            else:
                size = int(size_str)
                if name not in pwd.children:
                    pwd.children[name] = Tree(parent=pwd, size=size, is_dir=False)
                else:
                    old_size = pwd.children[name].size
                    assert old_size == size, (
                        f"old size {old_size} different from new size {size}",
                    )


def get_tree_size_str(tree: Tree) -> str:
    if tree.size is None:
        return ""
    else:
        return f", size={tree.size}"


def dfs_print(tree: Tree, indent: int = 0):
    if tree.parent is None:
        print(indent * " " + f"/ (dir{get_tree_size_str(tree)})")

    for name, child in tree.children.items():
        size_str = get_tree_size_str(child)
        if child.is_dir:
            print(indent * " " + name + f" (dir{size_str})")
            dfs_print(child, indent + 2)
        else:
            print(indent * " " + f"{name} (file{size_str})")


def dfs_set_size(tree: Tree):
    assert tree.is_dir

    total = 0
    for child in tree.children.values():
        if child.size is None:
            dfs_set_size(child)
        total += child.size

    tree.size = total


def sum_upto_bound(tree: Tree, bound: int = 100_000) -> int:
    assert tree.size is not None

    total = tree.size if tree.size <= bound else 0
    for child in tree.children.values():
        if child.is_dir:
            total += sum_upto_bound(child)

    return total


dfs_set_size(tree)
# dfs_print(tree)
bound = 100_000
total = sum_upto_bound(tree, bound=bound)
print(f"sum of directory sizes that are <= {bound} is: {total}")
