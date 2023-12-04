#! /usr/bin/env python
import sys
import re
from tqdm import tqdm

from collections import defaultdict
from typing import Tuple, Dict


fname = "input16" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    pattern = re.compile(
        r"Valve ([A-Z]+) has flow rate=(\d+); tunnels? leads? to valves? ([A-Z,\s]+)"
    )
    graph = defaultdict(list)
    flows = {}
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        parse = pattern.fullmatch(line)
        assert parse is not None, f"cannot parse entry: {line}"

        valve, rate_str, targets_str = parse.groups()
        rate = int(rate_str)

        targets = [_.strip() for _ in targets_str.split(",")]

        graph[valve].extend(targets)

        assert valve not in flows
        if rate > 0:
            flows[valve] = rate

# keep track of the highest pressure released after k steps
# start in state where all valves are closed and we are at AA
start = "AA"
assert start in graph

n_steps = 26
idx_map = {valve: i for i, valve in enumerate(flows)}
best = {(tuple(False for valve in flows), start, start): 0}

trace = []

for k in tqdm(range(n_steps)):
    trace.append(best)
    new_best = {}
    for (valve_state, node_me, node_ele), released in best.items():
        further_release = sum(
            flow for i, flow in enumerate(flows.values()) if valve_state[i]
        )
        value = released + further_release

        # can stay here and do nothing for a minute...
        # ...or could go through a tunnel...
        actions_me = [node_me] + graph[node_me]
        actions_ele = [node_ele] + graph[node_ele]

        # ...or could maybe open a valve
        if node_me in flows:
            actions_me.append(f"*o:{node_me}")
        if node_ele in flows and node_ele != node_me:
            # (but make sure we don't both open the same valve)
            actions_ele.append(f"*o:{node_ele}")

        for action_me in actions_me:
            for action_ele in actions_ele:
                if action_me[0] != "*" and action_ele[0] != "*":
                    # valves stay the same
                    key = (valve_state, action_me, action_ele)
                    new_best[key] = max(new_best.get(key, 0), value)
                else:
                    valve_idxs = set()
                    for action in [action_me, action_ele]:
                        if action[0] == "*":
                            assert action.startswith("*o:")
                            node = action[3:]
                            i = idx_map[node]
                            if not valve_state[i]:
                                valve_idxs.add(i)

                    new_valve_state = tuple(
                        True if j in valve_idxs else state
                        for j, state in enumerate(valve_state)
                    )
                    new_node_me = node_me if action_me[0] == "*" else action_me
                    new_node_ele = node_ele if action_ele[0] == "*" else action_ele

                    key = (new_valve_state, new_node_me, new_node_ele)
                    new_best[key] = max(new_best.get(key, 0), value)

        # go on to the next step
        best = new_best

max_released = -1
max_key = None
for key, value in best.items():
    if value > max_released:
        max_released = value
        max_key = key

actions = []
for i in range(len(trace) - 1, -1, -1):
    pass

print(f"maximum pressure that can be released: {max_released}")


def summarize_key(key: Tuple[Tuple[bool], str]) -> str:
    valves_open = [valve for i, valve in enumerate(flows) if key[0][i]]
    valves_open_str = f"valves open: {valves_open}"

    node = key[1]

    return f"at node {node}, {valves_open_str}"


def summarize_dict(d: Dict[Tuple[Tuple[bool], str], int]) -> str:
    s = []
    for key, value in d.items():
        key_str = summarize_key(key)
        s.append(f"{key_str}, total: {value}")

    return "; ".join(s)


# for i, crt in enumerate(trace):
# print("step", i)
# print(summarize_dict(trace[i]))
