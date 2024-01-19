#! /usr/bin/env python
from collections import deque
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

from utils import iterinput, logger


N_PRESSES = 1000


class Pulse(IntEnum):
    NONE = 0
    LOW = 1
    HIGH = 2


@dataclass(kw_only=True)
class Module:
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

    def feed(self, _: Pulse, origin: str) -> Pulse:
        raise NotImplementedError("Should be implemented by descendants")

    def state_list(self) -> List[int]:
        return []


class Untyped(Module):
    def feed(self, pulse: Pulse, _: str) -> Pulse:
        return Pulse.NONE


@dataclass(kw_only=True)
class FlipFlop(Module):
    class State(IntEnum):
        OFF = 0
        ON = 1

    state: State = State.OFF

    def flip(self):
        self.state = self.State.OFF if self.state == self.State.ON else self.State.ON

    def feed(self, pulse: Pulse, _: str) -> Pulse:
        if pulse == Pulse.LOW:
            self.flip()
            return Pulse.HIGH if self.state == self.State.ON else Pulse.LOW
        else:
            return Pulse.NONE

    def state_list(self) -> List[int]:
        return [self.state]


@dataclass(kw_only=True)
class Conjunction(Module):
    last_inputs: Optional[Dict[str, Pulse]] = None

    def feed(self, pulse: Pulse, origin: str) -> Pulse:
        assert origin in self.inputs
        self._check_last_inputs()

        self.last_inputs[origin] = pulse
        return Pulse.LOW if self.all_high() else Pulse.HIGH

    def all_high(self) -> bool:
        return all(_ == Pulse.HIGH for _ in self.last_inputs.values())

    def state_list(self) -> List[int]:
        self._check_last_inputs()
        return list(self.last_inputs.values())

    def _check_last_inputs(self):
        if self.last_inputs is None:
            self.last_inputs = {}
            for name in self.inputs:
                self.last_inputs[name] = Pulse.LOW


@dataclass(kw_only=True)
class Broadcaster(Module):
    def feed(self, pulse: Pulse, _: str) -> Pulse:
        return pulse


PulseHistory = List[Tuple[str, Pulse, str]]


@dataclass
class Network:
    modules: Dict[str, Module] = field(default_factory=dict)

    def add_module(self, name: str, module: Module):
        assert name not in self.modules
        self.modules[name] = module

    def send_pulse(self, to: str, pulse: Pulse = Pulse.LOW) -> PulseHistory:
        assert pulse != Pulse.NONE

        q = deque([(to, pulse, "button")])
        history = []
        while q:
            name, p, origin = q.pop()
            history.append((name, p, origin))
            module = self.modules[name]
            response = module.feed(p, origin)
            if response != Pulse.NONE:
                for target in module.outputs:
                    q.appendleft((target, response, name))

        return history

    def __contains__(self, name: str) -> bool:
        return name in self.modules

    def state_list(self) -> List[int]:
        l = []
        for module in self.modules.values():
            l.extend(module.state_list())

        return l

    def state_hash(self) -> int:
        return hash(tuple(self.state_list()))


def show_history(history: PulseHistory) -> str:
    l = []
    for name, pulse, origin in history:
        pulse_str = {Pulse.NONE: "0", Pulse.LOW: "-", Pulse.HIGH: "+"}[pulse]
        l.append(f"{origin} {pulse_str} -> {name}")

    s = ", ".join(l)
    return s


if __name__ == "__main__":
    net = Network()

    other_modules = set()
    for line in iterinput():
        origin_qual, targets_str = [_.strip() for _ in line.split("->")]
        targets = [_.strip() for _ in targets_str.split(",")]

        other_modules.update(targets)

        if not origin_qual[0].isalpha():
            origin_type = origin_qual[0]
            origin = origin_qual[1:]

            if origin not in net:
                if origin_type == "%":
                    module = FlipFlop(outputs=targets)
                elif origin_type == "&":
                    module = Conjunction(outputs=targets)
                else:
                    raise ValueError(f"Unknown node type {origin_type}")
            else:
                raise ValueError(f"Duplicated node {origin}")
        else:
            origin = origin_qual
            assert origin == "broadcaster"

            module = Broadcaster(outputs=targets)

        logger.debug(f"Adding {module=} with targets {', '.join(targets)}")
        net.add_module(origin, module)

    for name in other_modules:
        if name not in net:
            logger.info(f"Untyped module {name}")
            net.add_module(name, Untyped())

    for name, module in net.modules.items():
        for target_name in module.outputs:
            target = net.modules[target_name]
            target.inputs.append(name)

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
