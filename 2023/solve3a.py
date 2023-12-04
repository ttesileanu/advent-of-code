#! /usr/bin/env python
from utils import loadmatrix, logger, Matrix


EMPTY = "."


def has_part_neighbor(matrix: Matrix[str], i: int, j: int) -> bool:
    for value in matrix.iterneighborvalues(i, j):
        if value != EMPTY and not value.isdigit():
            return True

    return False


if __name__ == "__main__":
    matrix = loadmatrix()
    logger.debug(str(matrix))

    sum_part_numbers = 0

    for i in range(matrix.nrows):
        number_list = []
        number_start = None
        is_part = False
        for j in range(matrix.ncols):
            value = matrix[i, j]
            if value.isdigit():
                number_list += value
                is_part = is_part or has_part_neighbor(matrix, i, j)

                if number_start is None:
                    number_start = (i, j)
            elif len(number_list) > 0:
                number_str = "".join(number_list)
                number = int(number_str)
                if is_part:
                    sum_part_numbers += number
                    logger.debug(f"Part number {number} at {number_start}.")
                else:
                    logger.debug(
                        f"Number {number} at {number_start} is not a part number."
                    )

                number_list = []
                number_start = None
                is_part = False

        if len(number_list) > 0:
            number_str = "".join(number_list)
            number = int(number_str)
            if is_part:
                sum_part_numbers += number
                logger.debug(f"Part number {number} at {number_start}.")
            else:
                logger.debug(f"Number {number} at {number_start} is not a part number.")

    print(f"Sum of part numbers: {sum_part_numbers}")
