#! /usr/bin/env python
import os
import re
from typing import Tuple


with open("input6.txt", "rt") as f:
    signal_lines = f.readlines()
    assert len(signal_lines) == 1
    
    signal = signal_lines[0].strip()
    for i in range(4, len(signal)):
        sub = signal[i - 4 : i]
        if len(set(sub)) == 4:
            break

print(i)
