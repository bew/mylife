#!/usr/bin/env python3

import io
import os
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TypeVar, Union
from pprint import pprint

_T = TypeVar("_T")  # generic type declaration

DEBUG = os.environ.get("DEBUG", default=False)
DEBUG_PREFIX = "DEBUG: "


def debug(*args, use_pprint=False, add_prefix=True, **kwargs):
    if DEBUG:
        if add_prefix:
            print(DEBUG_PREFIX, end="")
        print_fn = pprint if use_pprint else print
        print_fn(*args, **kwargs)  # type: ignore


def debug_multiline(text: str):
    if DEBUG:
        for line in text.split("\n"):
            print(DEBUG_PREFIX, end="")
            print(line)


@dataclass
class GameRules:
    cell_surviving_neighbors: List[int]
    cell_birth_neighbors: List[int]


@dataclass
class Cell:
    alive: bool
    computed_neighbor_count: Optional[int] = None


@dataclass(eq=True, frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: Union[int, "Point"]) -> "Point":
        if isinstance(other, Point):
            return Point(
                x=self.x + other.x,
                y=self.y + other.y,
            )
        elif isinstance(other, int):
            return Point(
                x=self.x + other,
                y=self.y + other,
            )


@dataclass
class Rectangle:
    top_left: Point
    width: int
    height: int

    @classmethod
    def from_2_points(cls, point1: Point, point2: Point) -> "Rectangle":
        min_x, max_x = min(point1.x, point2.x), max(point1.x, point2.x)
        min_y, max_y = min(point1.y, point2.y), max(point1.y, point2.y)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        return cls(
            top_left=Point(x=min_x, y=min_y),
            width=width,
            height=height
        )


@dataclass
class WantedResult:
    generation: int
    output_rect: Rectangle


class InfiniteGrid:
    def __init__(self):
        self.alive_cells: Dict[Point, Cell] = {}

    def set_cell(self, point: Point, cell: Cell):
        """Set cell at the given `point` to `cell`"""
        self.alive_cells[point] = cell

    def get_cell(self, point: Point) -> Cell:
        """Get cell at the given `point`, defaults to a dead cell"""
        return self.alive_cells.get(point, Cell(alive=False))

    def to_str_between(self, point1: Point, point2: Point):
        rect = Rectangle.from_2_points(point1, point2)
        return self.to_str_at(rect)

    def to_str_at(self, rect: Rectangle):
        # Prints the grid between at given rectangle in the same format
        # as the input:
        # +-----+
        # |cells|
        # +-----+

        debug("Grid to str at: ", end="")
        debug(rect, use_pprint=True, add_prefix=False)

        io_str = io.StringIO()
        io_str.write(f"+{'-' * rect.width}+")  # top frame
        for relative_y in range(rect.height):
            io_str.write("\n|")  # left frame
            for relative_x in range(rect.width):
                real_x = rect.top_left.x + relative_x
                real_y = rect.top_left.y + relative_y
                cell = self.get_cell(Point(x=real_x, y=real_y))
                # debug(f"Read cell REAL[{real_x:>2},{real_y:>2}] "
                #       f"REL:[{relative_x:>2},{relative_y:>2}]: "
                #       f"{'alive' if cell.alive else 'dead'}")
                io_str.write("x" if cell.alive else " ")
            # debug()
            io_str.write("|")  # right frame
        io_str.write(f"\n+{'-' * rect.width}+")  # bottom frame
        return io_str.getvalue()


def _input_parse_grid(starting_point: Point, width: int, height: int):
    grid = InfiniteGrid()
    _ = input()  # skip the top frame
    for relative_y in range(height):
        line = input()[1:-1]  # skip the left/right frame around the grid line
        for relative_x in range(width):
            cell_char = line[relative_x]
            alive = (cell_char == "x")
            grid.set_cell(
                starting_point + Point(x=relative_x, y=relative_y),
                cell=Cell(alive=alive)
            )
    _ = input()  # skip the bottom frame
    return grid


# class LifeSimulator:
#     def __init__(self, initial_grid: InfiniteGrid, rules: GameRules):
#         self.initial_grid = initial_grid
#         self.current_grid = initial_grid
#         self.rules = rules


def _input_split(sep: str, fn: Callable[[str], _T], maxsplit=-1) -> List[_T]:
    """
    Read input and split it up to `maxsplit` times, and pass each elements to `fn`.
    """
    return [fn(elem) for elem in input().split(sep, maxsplit=maxsplit)]


def _input_parse_point():
    x, y = _input_split(",", int, maxsplit=1)
    return Point(x=x, y=y)


def parse_challenge_input():
    surviving_conditions = _input_split(",", int)
    birth_conditions = _input_split(",", int)
    game_rules = GameRules(
        cell_surviving_neighbors=surviving_conditions,
        cell_birth_neighbors=birth_conditions,
    )

    starting_point = _input_parse_point()
    given_width, given_height = _input_split("x", int, maxsplit=1)

    grid = _input_parse_grid(
        starting_point=starting_point,
        width=given_width,
        height=given_height
    )

    wanted_generation = int(input())
    wanted_view_point1 = _input_parse_point()
    wanted_view_point2 = _input_parse_point()
    wanted_result = WantedResult(
        generation=wanted_generation,
        output_rect=Rectangle.from_2_points(wanted_view_point1, wanted_view_point2),
    )

    debug("--- GIVEN INPUT ---")
    debug("Initial given grid:")
    debug(f"  Starting point: {starting_point}")
    debug(f"  Width: {given_width}")
    debug(f"  Height: {given_height}")
    debug_multiline(grid.to_str_at(Rectangle(
        top_left=starting_point,
        width=given_width,
        height=given_height,
    )))

    debug(game_rules, use_pprint=True)
    debug(wanted_result, use_pprint=True)
    debug()

    return grid, game_rules, wanted_result


def main():
    grid, rules, wanted_result = parse_challenge_input()

    debug("--- OUPUT ---")
    print(grid.to_str_at(wanted_result.output_rect))


if __name__ == "__main__":
    main()
