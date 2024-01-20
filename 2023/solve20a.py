#! /usr/bin/env python
from utils import iterinput, logger

from common20 import Pulse, read_network, show_history


N_PRESSES = 1000


if __name__ == "__main__":
    net = read_network(iterinput())
    logger.debug(f"{net=}")
    logger.debug(f"net state hash = {net.state_hash()}")

    hashes = {}
    low_pulse_counts = []
    high_pulse_counts = []

    period_start = None
    period = None

    for i in range(N_PRESSES):
        crt_hash = net.state_hash()
        if crt_hash in hashes:
            period_start = hashes[crt_hash]
            period = i - period_start
            break

        hashes[crt_hash] = i
        history = net.send_pulse("broadcaster")
        logger.debug(f"Results from press {i}: {show_history(history)}")

        just_pulses = [_[1] for _ in history]
        low_pulse_counts.append(just_pulses.count(Pulse.LOW))
        high_pulse_counts.append(just_pulses.count(Pulse.HIGH))

    total_low_count = 0
    total_high_count = 0
    if period_start is not None:
        logger.debug(f"Period started at {period_start} presses, {period=}")
        total_low_count += sum(low_pulse_counts[:period_start])
        total_high_count += sum(high_pulse_counts[:period_start])

        # counts at period_start + k * period + i  = counts at period_start + i
        # maximum k:
        #   period_start + k * period < N_PRESSES
        #   k * period < N_PRESSES - period_start
        #   k_max = floor((N_PRESSES - period_start) / period)

        n_periods = (N_PRESSES - period_start) // period
        period_low_count = sum(low_pulse_counts[period_start : period_start + period])
        period_high_count = sum(high_pulse_counts[period_start : period_start + period])

        total_low_count += period_low_count * n_periods
        total_high_count += period_high_count * n_periods

        n_left = (N_PRESSES - period_start) % period
        total_low_count += sum(low_pulse_counts[period_start : period_start + n_left])
        total_high_count += sum(high_pulse_counts[period_start : period_start + n_left])
    else:
        logger.debug(f"No period found for the first {N_PRESSES} presses")
        total_low_count = sum(low_pulse_counts)
        total_high_count = sum(high_pulse_counts)

    logger.debug(f"Total low counts: {total_low_count}")
    logger.debug(f"Total high counts: {total_high_count}")

    p = total_low_count * total_high_count
    print(f"Product of number of low and high pulses: {p}")
