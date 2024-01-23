#! /usr/bin/env python
from utils import iterinput, logger

from common20 import find_cycle, Pulse, read_network, show_history


N_PRESSES = 1000


if __name__ == "__main__":
    net = read_network(iterinput())
    logger.debug(f"{net=}")
    logger.debug(f"net state hash = {net.state_hash()}")

    cycle = find_cycle(net, max_presses=N_PRESSES)

    total_low_count = 0
    total_high_count = 0
    if cycle.period_start is not None:
        logger.debug(f"Period started at {cycle.period_start} presses, {cycle.period=}")
        total_low_count += sum(cycle.low_pulse_counts[: cycle.period_start])
        total_high_count += sum(cycle.high_pulse_counts[: cycle.period_start])

        # counts at period_start + k * period + i  = counts at period_start + i
        # maximum k:
        #   period_start + k * period < N_PRESSES
        #   k * period < N_PRESSES - period_start
        #   k_max = floor((N_PRESSES - period_start) / period)

        n_periods = (N_PRESSES - cycle.period_start) // cycle.period
        extents = slice(cycle.period_start, cycle.period_start + cycle.period)
        period_low_count = sum(cycle.low_pulse_counts[extents])
        period_high_count = sum(cycle.high_pulse_counts[extents])

        total_low_count += period_low_count * n_periods
        total_high_count += period_high_count * n_periods

        n_left = (N_PRESSES - cycle.period_start) % cycle.period
        extents = slice(cycle.period_start, cycle.period_start + n_left)
        total_low_count += sum(cycle.low_pulse_counts[extents])
        total_high_count += sum(cycle.high_pulse_counts[extents])
    else:
        logger.debug(f"No period found for the first {N_PRESSES} presses")
        total_low_count = sum(cycle.low_pulse_counts)
        total_high_count = sum(cycle.high_pulse_counts)

    logger.debug(f"Total low counts: {total_low_count}")
    logger.debug(f"Total high counts: {total_high_count}")

    p = total_low_count * total_high_count
    print(f"Product of number of low and high pulses: {p}")
