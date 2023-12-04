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


def choose_dir_to_delete(
    tree: Tree, min_size: int, current_choice: Optional[Tree] = None
) -> Optional[Tree]:
    best_choice = current_choice
    if tree is None:
        return best_choice

    if tree.size >= min_size and (
        current_choice is None or current_choice.size > tree.size
    ):
        best_choice = tree

    for child in tree.children.values():
        if child.is_dir:
            best_choice = choose_dir_to_delete(
                child, min_size=min_size, current_choice=best_choice
            )

    return best_choice


dfs_set_size(tree)
dfs_print(tree)

total_space = 70_000_000
needed_space = 30_000_000

free_space = total_space - tree.size
to_delete = max(needed_space - free_space, 0)

print("Size of /: ", tree.size)
print("Space needed to delete:", to_delete)

if to_delete <= 0:
    print(f"We already have enough free space ({free_space}).")
else:
    chosen_dir = choose_dir_to_delete(tree, min_size=to_delete)
    print(f"Size of directory to delete: {chosen_dir.size}")
