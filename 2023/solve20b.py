#! /usr/bin/env python
import time
from utils import IntegerLattice, iterinput, logger

from common20 import Conjunction, find_cycle, Pulse, read_network, Untyped


PROGRESS_EVERY = 5


if __name__ == "__main__":
    # inspired by
    # https://www.reddit.com/r/adventofcode/comments/18ms8d1/2023_day_20_part_2_general_solution/?rdt=61166

    # Basically we need to rely on the network having a specific subnetwork structure.
    # We are assuming that broadcaster projects to a set of subnetworks that are
    # effectively disjoint, with the only exception that they all converge onto a single
    # "hub". The "hub" must be a conjunction module, and it must be the only node
    # projecting to the target module.

    # Here we recognize the target module by the fact that it's the only untyped one in
    # the network, though that's not a necessary constraint.

    net = read_network(iterinput())

    target = None
    for name, module in net.modules.items():
        if isinstance(module, Untyped):
            if target is not None:
                raise ValueError("Ambiguous target module: more than one untyped")
            target = name

    assert target is not None
    logger.info(f"Target module: {target}")

    subnets = net.split_from("broadcaster", target=target)

    # Check that the constraints are obeyed.
    # split_from() already checks that each of the sub-networks only receive external
    # inputs in the form of a) subnet input (i.e., from broadcaster); and b) subnet
    # output, i.e., a node that projects to the target and nowhere else.
    hub = None
    for subnet in subnets:
        child = next(iter(subnet.modules))
        for name, module in subnet.modules.items():
            for inp in module.inputs:
                if inp not in subnet.modules:
                    is_input = name == child and inp == "broadcaster"
                    is_output = module.outputs == [target]
                    if not is_input:
                        assert is_output
                        if hub is not None:
                            assert hub == name
                        else:
                            hub = name

    hub_module = net.modules[hub]
    assert isinstance(hub_module, Conjunction)
    logger.info(f"Hub module: {hub}")

    try:
        g = net.to_graphviz(subnets)
        g.view()
    except RuntimeError:
        pass

    subcycles = []
    for i, subnet in enumerate(subnets):
        subcount = len(subnet.modules)
        subname = next(iter(subnet.modules))

        subnet.reset()
        subcycle = find_cycle(subnet, subname, return_histories=True)
        logger.info(
            f"Component {i} / {subname} with {subcount} nodes has period "
            f"{subcycle.period} starting at {subcycle.period_start}"
        )

        hub_low_counts = []
        hub_high_counts = []
        target_pulse_histories = []
        for history in subcycle.histories:
            target_pulses = [pulse for name, pulse, _ in history if name == hub]
            target_pulse_histories.append(target_pulses)
            hub_low_counts.append(target_pulses.count(Pulse.LOW))
            hub_high_counts.append(target_pulses.count(Pulse.HIGH))

        # ensure that at most one member of the cycle has a high pulse to hub
        # if there is a coincidence of all the subnets sending a high pulse to hub at
        # the "same" time (i.e., without intervening low pulses), thus making the hub
        # emit a low pulse (which is what we're looking for), then it'll happen at this
        # point. XXX not exactly sure how to ensure that the timing matches, though
        assert sum(hub_high_counts) == max(hub_high_counts)
        idx = hub_high_counts.index(max(hub_high_counts))

        subcycle.target_idx = idx
        subcycles.append(subcycle)

    # the check above also ensures there are no coincidences during the warmup (before
    # the periods start)

    # each subcycle k reaches its target at
    # s[k] + i[k] + p[k] * m ,
    # where m is any non-negative integer, s[k] is period_start, i[k] = target_idx,
    # p[k] = period.

    # we want all of these to match --> IntegerLattice intersections, like in day 8
    lattice = IntegerLattice(0, 1)
    for subcycle in subcycles:
        other_lattice = IntegerLattice(subcycle.target_idx, subcycle.period)
        lattice = lattice & other_lattice
        assert not lattice.empty()

    logger.debug(f"Lattice of solutions: {lattice}")
    warmup = max(_.period_start for _ in subcycles)
    count = lattice.first_after(warmup)
    print(f"Found low pulse to {target} after {count + 1} button presses")
