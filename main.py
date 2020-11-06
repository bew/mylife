#!/usr/bin/env python3

import abc
import io
from dataclasses import dataclass
from typing import Callable, List, Optional


class OutOfBoundError(Exception):
    pass


class GridInterface(abc.ABC):
    pass


@dataclass
class GameRules:
    cell_surviving_neighbors: List[int]
    cell_birth_neighbors: List[int]


@dataclass
class Cell:
    alive: bool
    computed_neighbors: Optional[int] = None


class FlatGrid:
    def __init__(
        self,
        grid_id: int,
        width: int,
        height: int,
        default_cell: Callable[[], Cell],
    ):
        self.grid_id = grid_id
        self.width = width
        self.height = height
        self.cells: List[Cell] = [
            default_cell()
            for _ in range(width * height)
        ]

    def set_cell(self, pos_x: int, pos_y: int, cell: Cell):
        """Set cell at the given x/y position to `cell`"""
        cell_index = self._cell_index_from_pos(pos_x=pos_x, pos_y=pos_y)
        self.cells[cell_index] = cell

    def get_cell(self, pos_x: int, pos_y: int) -> Cell:
        """Get cell the given x/y position"""
        cell_index = self._cell_index_from_pos(pos_x=pos_x, pos_y=pos_y)
        return self.cells[cell_index]

    def _cell_index_from_pos(self, pos_x: int, pos_y: int) -> int:
        """Get the 1D position of a cell at the given 2D position (with bound check)"""
        if not (0 <= pos_x < self.width and 0 <= pos_y < self.height):
            raise OutOfBoundError(f"Cannot get or set cell x:{pos_x} y:{pos_y} for a grid "
                                  f"of size {self.width}x{self.height}")
        return (self.width * pos_y) + pos_x

    def __str__(self):
        # Prints the grid in the same format as the input:
        # +-----+
        # |cells|
        # +-----+
        io_str = io.StringIO()
        io_str.write(f"{self.grid_id}\n")
        io_str.write(f"+{'-' * self.width}+")  # frame start
        for pos_y in range(self.height):
            io_str.write("\n|")  # frame
            for pos_x in range(self.width):
                cell = self.get_cell(pos_x=pos_x, pos_y=pos_y)
                io_str.write("x" if cell.alive else " ")
            io_str.write("|")  # frame
        io_str.write(f"\n+{'-' * self.width}+")  # frame end
        return io_str.getvalue()


def parse_flat_grid(width, height):
    grid_id = int(input())
    parsed_grid = FlatGrid(
        grid_id=grid_id,
        width=width,
        height=height,
        default_cell=(lambda: Cell(alive=False))  # type: ignore
    )
    _ = input()  # skip the frame
    for pos_y in range(height):
        line = input()[1:-1]  # skip the frame before/after the grid line
        for pos_x in range(width):
            cell_char = line[pos_x]
            alive = (cell_char == "x")
            parsed_grid.set_cell(
                pos_x=pos_x,
                pos_y=pos_y,
                cell=Cell(alive=alive)
            )
    _ = input()  # skip the frame
    return parsed_grid


class LifeSimulator:
    def __init__(self, initial_grid: GridInterface):
        pass


def parse_input():
    board_width, board_height = [
        int(val)
        for val in input().split("x", maxsplit=1)
    ]
    grid_type = input()
    surviving_conditions = [int(val) for val in input().split(",")]
    birth_conditions = [int(val) for val in input().split(",")]
    game_rules = GameRules(
        cell_surviving_neighbors=surviving_conditions,
        cell_birth_neighbors=birth_conditions,
    )
    _ = input()

    if grid_type == "flat":
        grid = parse_flat_grid(width=board_width, height=board_height)
    else:
        raise Exception(f"Unsupported grid type '{grid_type}'")

    print(f"Width: {board_width} x Height: {board_height}")
    from pprint import pprint; pprint(game_rules)  # noqa: E702

    print("-- Grid --")
    print(grid)

    return grid, game_rules


def main():
    parse_input()


if __name__ == "__main__":
    main()
