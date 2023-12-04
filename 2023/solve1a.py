#! /usr/bin/env python

with open("input1.txt", "rt") as f:
    calibrations = []
    for line in f:
        numbers = [ch for ch in line if "0" <= ch <= "9"]
        calibration = int(numbers[0] + numbers[-1])
        calibrations.append(calibration)

print(f"The sum of all calibration values is {sum(calibrations)}.")
