#! /usr/bin/env python
import sys
import re
import math
import time
from itertools import product
from tqdm import tqdm
from typing import List


def get_upper_bound(blueprint: dict, robots: List, resources: List, t: int) -> int:
    addtl_robots = [0, 0, 0, 0]
    crt_resources = list(resources)
    for _ in range(t):
        # update resources
        for i in range(4):
            crt_resources[i] += robots[i] + addtl_robots[i]

        # update robots without worrying about overlapping resource use
        for i, robot_type in enumerate(["ore", "clay", "obsidian", "geode"]):
            crt_needed = blueprint[robot_type + "_robot"]
            if all(
                __ >= _ * (addtl_robots[i] + 1)
                for _, __ in zip(crt_needed, crt_resources)
            ):
                addtl_robots[i] += 1

    return crt_resources[-1]


def optimize(blueprint: dict, n_minutes: int) -> int:
    mt0 = time.time()

    # we start with just 1 ore robot, no resources, but plenty of time
    stack = [[1, 0, 0, 0, 0, 0, 0, 0, n_minutes]]

    # keep track of best found number of geodes
    best = -1
    best_node = None

    # you never need more robots than the maximum number of corresponding resources
    # needed to build a robot -- they would never get used
    max_needed = [0, 0, 0]
    for i in range(3):
        for crt_needed in blueprint.values():
            max_needed[i] = max(max_needed[i], crt_needed[i])

    parents = {tuple(stack[0]): None}

    n_visited = 0
    while stack:
        mt = time.time()
        if mt - mt0 >= 1.0:
            print(f"nodes visited: {n_visited}; stack size: {len(stack)}")
            mt0 = mt

        node = stack.pop()
        robots = node[:4]
        resources = node[4:8]
        t = node[-1]

        # upper bound on final number of geodes from this branch of the tree
        upper_bound = get_upper_bound(blueprint, robots, resources, t)
        if upper_bound <= best:
            # even the best possible estimate isn't good enough -- no point continuing
            continue

        final_geodes = resources[-1] + robots[-1] * t
        if final_geodes > best:
            best = final_geodes
            best_node = node

        for i, robot_type in enumerate(["ore", "clay", "obsidian", "geode"]):
            if i < 3 and robots[i] >= max_needed[i]:
                # definitely don't need to build more of these
                continue

            needed = blueprint[robot_type + "_robot"]
            delta = 0
            for crt_needed, crt_robots, crt_had in zip(needed, robots, resources):
                if crt_had >= crt_needed:
                    delta = max(delta, 1)
                elif crt_robots > 0:
                    delta = max(
                        delta, 1 + (crt_needed + crt_robots - crt_had - 1) // crt_robots
                    )
                else:
                    delta = math.inf
                    break

            if delta < t:
                new_robots = list(robots)
                new_robots[i] += 1

                new_resources = [
                    old + nr * delta - used
                    for old, nr, used in zip(resources, robots, needed + (0,))
                ]
                new_t = t - delta

                new_node = [*new_robots, *new_resources, new_t]
                parents[tuple(new_node)] = tuple(node)
                stack.append(new_node)

        n_visited += 1

    trajectory = []
    node = tuple(best_node)
    while node is not None:
        trajectory.append(node)
        node = parents[node]

    trajectory = trajectory[::-1]
    for node in trajectory:
        print(
            f"after {n_minutes - node[-1]} minutes, robots: {node[:4]}, resources: {node[4:8]}"
        )

    return best


fname = "input19" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    pattern = re.compile(
        r"Blueprint (\d+): "
        r"Each ore robot costs (\d+) ore. "
        r"Each clay robot costs (\d+) ore. "
        r"Each obsidian robot costs (\d+) ore and (\d+) clay. "
        r"Each geode robot costs (\d+) ore and (\d+) obsidian."
    )
    i = 0

    blueprints = []
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        i += 1

        parse = pattern.fullmatch(line)
        assert parse is not None, f"cannot parse blueprint: {line}"

        groups = parse.groups()
        blueprint_id = int(groups[0])
        assert blueprint_id == i

        # costs: (ore, clay, obsidian)
        blueprint = {}
        blueprint["ore_robot"] = (int(groups[1]), 0, 0)
        blueprint["clay_robot"] = (int(groups[2]), 0, 0)
        blueprint["obsidian_robot"] = (int(groups[3]), int(groups[4]), 0)
        blueprint["geode_robot"] = (int(groups[5]), 0, int(groups[6]))

        blueprints.append(blueprint)

max_blueprints = 3

n_minutes = 32
product_max_geodes = 1
for i, blueprint in enumerate(blueprints[:max_blueprints]):
    print(
        f"B{i + 1}: ore robot: {blueprint['ore_robot']}; "
        f"clay robot: {blueprint['clay_robot']}; "
        f"obsidian robot: {blueprint['obsidian_robot']}; "
        f"geode robot: {blueprint['geode_robot']}"
    )
    max_geodes = optimize(blueprint, n_minutes)
    product_max_geodes *= max_geodes
    print(f"blueprint {i + 1} can open a maximum of {max_geodes} geodes")

print(f"product of maximum geodes over all blueprints: {product_max_geodes}")

# for i, blueprint in enumerate(blueprints):
#     print(
#         f"B{i + 1}: ore robot: {blueprint['ore_robot']}; "
#         f"clay robot: {blueprint['clay_robot']}; "
#         f"obsidian robot: {blueprint['obsidian_robot']}; "
#         f"geode robot: {blueprint['geode_robot']}"
#     )
