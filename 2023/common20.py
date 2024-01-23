import itertools
from collections import deque
from dataclasses import dataclass, field
from enum import IntEnum
from types import SimpleNamespace
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from utils import logger


try:
    import graphviz

    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False


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

    def reset(self):
        pass


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

    def reset(self):
        self.state = self.State.OFF


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
            self.reset()

    def reset(self):
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

    def __len__(self) -> int:
        return len(self.modules)

    def state_list(self) -> List[int]:
        l = []
        for module in self.modules.values():
            l.extend(module.state_list())

        return l

    def state_hash(self) -> int:
        return hash(tuple(self.state_list()))

    def split_from(self, origin: str, target: str) -> List["Network"]:
        l = []
        origin_module = self.modules[origin]
        for child in origin_module.outputs:
            subnet = self.get_subnet(child)
            if target in subnet.modules:
                l.append(subnet)
            else:
                logger.warning(
                    f"Component with {len(subnet)} nodes missing {target}; ignoring"
                )

            # ensure the networks have only a special kind of external inputs:
            # * input from origin to child
            # * input to node(s) only projecting to target
            for name, module in subnet.modules.items():
                for inp in module.inputs:
                    if inp not in subnet.modules:
                        is_input = name == child and inp == origin
                        is_output = module.outputs == [target]
                        if not is_input and not is_output:
                            raise ValueError(
                                f"Subnetwork {child} has external input {inp}->{name} "
                                f"that is neither an input from {origin=}, "
                                f"nor projecting uniquely to {target}"
                            )

        return l

    def get_subnet(self, origin: str) -> "Network":
        q = deque([origin])
        component = [origin]
        visited = set(component)
        while q:
            name = q.pop()
            module = self.modules[name]
            for other in module.outputs:
                if other not in visited:
                    visited.add(other)
                    component.append(other)
                    q.appendleft(other)

        subnet = Network()
        for name in component:
            module = self.modules[name]
            subnet.add_module(name, module)
            for child in module.outputs:
                assert child in visited

        return subnet

    def reset(self):
        for module in self.modules.values():
            module.reset()

    def to_graphviz(
        self, components: Optional[List["Network"]] = None
    ) -> "graphviz.Digraph":
        if not HAS_GRAPHVIZ:
            raise RuntimeError("Need graphviz package")

        g = graphviz.Graph("G")

        colors = {name: "black" for name in self.modules}
        if components is not None:
            color_cycle = ["red", "green", "blue", "magenta", "cyan", "yellow", "black"]
            for subnet, color in zip(components, itertools.cycle(color_cycle)):
                for name in subnet.modules:
                    colors[name] = color

        for name in self.modules:
            g.node(name, color=colors[name])

        for origin, module in self.modules.items():
            for target in module.outputs:
                g.edge(origin, target)

        return g


def show_history(history: PulseHistory) -> str:
    l = []
    for name, pulse, origin in history:
        pulse_str = {Pulse.NONE: "0", Pulse.LOW: "-", Pulse.HIGH: "+"}[pulse]
        l.append(f"{origin} {pulse_str} -> {name}")

    s = ", ".join(l)
    return s


def read_network(it: Iterator[str]):
    net = Network()

    other_modules = set()
    for line in it:
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

    return net


def find_cycle(
    net: Network,
    origin: str = "broadcaster",
    max_presses: int = 1_000_000_000,
    return_histories: bool = False,
) -> SimpleNamespace:
    hashes = {}
    low_pulse_counts = []
    high_pulse_counts = []

    period_start = None
    period = None

    histories = []

    net.reset()
    for i in range(max_presses):
        crt_hash = net.state_hash()
        if crt_hash in hashes:
            period_start = hashes[crt_hash]
            period = i - period_start
            break

        hashes[crt_hash] = i
        history = net.send_pulse(origin)
        logger.debug(f"Results from press {i}: {show_history(history)}")

        if return_histories:
            histories.append(history)

        just_pulses = [_[1] for _ in history]
        low_pulse_counts.append(just_pulses.count(Pulse.LOW))
        high_pulse_counts.append(just_pulses.count(Pulse.HIGH))

    if period_start is not None:
        logger.debug(
            f"Pulse at {origin}, period started at {period_start} presses, {period=}"
        )
    else:
        logger.debug(
            f"Pulse at {origin}, no period found for the first {max_presses} presses"
        )

    res = SimpleNamespace(
        period_start=period_start,
        period=period,
        low_pulse_counts=low_pulse_counts,
        high_pulse_counts=high_pulse_counts,
    )
    if return_histories:
        res.histories = histories
    return res
