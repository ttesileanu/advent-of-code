#! /usr/bin/env python
from typing import List, Optional

from utils import loadmatrix, logger, Matrix


EMPTY = "."
GEARLIKE = "*"


def check_number(matrix: Matrix[str], i: int, j: int) -> Optional[int]:
    if i < 0 or i >= matrix.nrows or j < 0 or j >= matrix.ncols:
        return None
    if not matrix[i, j].isdigit():
        return None

    # find where the digits start
    while j >= 0 and matrix[i, j].isdigit():
        j -= 1

    # read out the number
    j += 1
    l = []
    while j < matrix.ncols and matrix[i, j].isdigit():
        l.append(matrix[i, j])
        j += 1

    return int("".join(l))


def find_neighbor_numbers(matrix: Matrix[str], i: int, j: int) -> List[int]:
    numbers = []
    for row in range(i - 1, i + 2):
        if row >= 0 and row < matrix.nrows:
            center_number = check_number(matrix, row, j)
            if center_number is not None:
                numbers.append(center_number)
            else:
                for k in [j - 1, j + 1]:
                    number = check_number(matrix, row, k)
                    if number is not None:
                        numbers.append(number)

    return numbers


if __name__ == "__main__":
    matrix = loadmatrix()
    logger.debug(str(matrix))

    sum_gear_ratio = 0

    for i in range(matrix.nrows):
        for j in range(matrix.ncols):
            if matrix[i, j] == GEARLIKE:
                logger.debug(f"Found gear-like symbol at ({i}, {j}).")
                numbers = find_neighbor_numbers(matrix, i, j)
                if len(numbers) == 2:
                    gear_ratio = numbers[0] * numbers[1]
                    sum_gear_ratio += gear_ratio

                    logger.debug(f"Gear at ({i}, {j}), {numbers=}, {gear_ratio=}.")
                else:
                    logger.debug(
                        f"Gear-like at ({i}, {j}), but {len(numbers)} numbers, "
                        f"{numbers}."
                    )

    print(f"Sum of gear ratios: {sum_gear_ratio}")
