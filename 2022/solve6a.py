#! /usr/bin/env python
import os
import re
from typing import Tuple


with open("input6.txt", "rt") as f:
    signal_lines = f.readlines()
    assert len(signal_lines) == 1
    
    msg_len = 14
    signal = signal_lines[0].strip()
    for i in range(msg_len, len(signal)):
        sub = signal[i - msg_len : i]
        if len(set(sub)) == msg_len:
            break

print(i)
