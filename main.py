#!/usr/bin/env python3

import io
import os
import time
import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, TypeVar, Union, Set
from pprint import pprint

_T = TypeVar("_T")  # generic type declaration

DEBUG = os.environ.get("DEBUG", default=False)
DEBUG_PREFIX = "DEBUG: "


def debug(*args, use_pprint=False, add_prefix=True, **kwargs):
    if DEBUG:
        if add_prefix:
            print(DEBUG_PREFIX, end="", file=sys.stderr)
        if use_pprint:
            pprint(*args, stream=sys.stderr, **kwargs)  # type: ignore
        else:
            print(*args, file=sys.stderr, **kwargs)


def debug_multiline(text: str):
    if DEBUG:
        for line in text.split("\n"):
            print(DEBUG_PREFIX, end="", file=sys.stderr)
            print(line, file=sys.stderr)


@dataclass
class GameRules:
    cell_birth_neighbors: List[int]
    cell_surviving_neighbors: List[int]


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
        self._alive_cell_points: Set[Point] = set()

    def set_state(self, point: Point, alive: bool):
        """Set alive state of cell at the given `point`"""
        if alive:
            # NOTE: does not raise if present
            self._alive_cell_points.add(point)
        else:
            # NOTE: does not raise if not present
            self._alive_cell_points.discard(point)

    def is_alive(self, point: Point) -> bool:
        return point in self._alive_cell_points

    def all_alive_cell_points(self) -> Set[Point]:
        return self._alive_cell_points.copy()

    def to_str_between(self, point1: Point, point2: Point):
        rect = Rectangle.from_2_points(point1, point2)
        return self.to_str_at(rect)

    def to_str_at(self, rect: Rectangle):
        # Prints the grid between at given rectangle in the same format
        # as the input:
        # +-----+
        # |cells|
        # +-----+

        # debug("Grid to str at: ", end="")
        # debug(rect, use_pprint=True, add_prefix=False)

        alive_cell_char = "█" if DEBUG else "x"

        io_str = io.StringIO()
        io_str.write(f"+{'-' * rect.width}+")  # top frame
        for relative_y in range(rect.height):
            io_str.write("\n|")  # left frame
            for relative_x in range(rect.width):
                real_x = rect.top_left.x + relative_x
                real_y = rect.top_left.y + relative_y
                is_alive = self.is_alive(Point(x=real_x, y=real_y))
                # debug(f"Read cell REAL[{real_x:>2},{real_y:>2}] "
                #       f"REL:[{relative_x:>2},{relative_y:>2}]: "
                #       f"{'alive' if is_alive else 'dead'}")
                io_str.write(alive_cell_char if is_alive else " ")
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
            grid.set_state(
                starting_point + Point(x=relative_x, y=relative_y),
                alive=alive
            )
    _ = input()  # skip the bottom frame
    return grid


class GodPower:
    # HE, who decides who lives / dies / is born for the next generation

    def __init__(self, rules: GameRules):
        self.rules = rules

    def apply_rules(self, grid: InfiniteGrid) -> InfiniteGrid:
        # Holds the potential new/surviving cells for next generation
        # and their current neighbors count
        potential_new_cells: Dict[Point, int] = {}
        potential_surviving_cells: Dict[Point, int] = {}

        for alive_cell in grid.all_alive_cell_points():
            # An alive cell is a candidate for next gen
            potential_surviving_cells[alive_cell] = self._count_neighbors(grid, alive_cell)
            # All its neighbors are candidates for next gen
            for neighbor_cell in self._neighbor_cells(alive_cell):
                potential_new_cells[neighbor_cell] = self._count_neighbors(grid, neighbor_cell)

        new_grid = InfiniteGrid()
        # use god power to decide who lives / dies / is born, based on the world rules
        for cell, neighbors_count in potential_new_cells.items():
            if neighbors_count in self.rules.cell_birth_neighbors:
                new_grid.set_state(cell, alive=True)
        for cell, neighbors_count in potential_surviving_cells.items():
            if neighbors_count in self.rules.cell_surviving_neighbors:
                new_grid.set_state(cell, alive=True)

        # return a new grid with the next generation of cells
        return new_grid

    def _count_neighbors(self, grid: InfiniteGrid, cell_point: Point) -> int:
        neighbors_count = 0
        for neighbor_point in self._neighbor_cells(cell_point):
            if grid.is_alive(neighbor_point):
                neighbors_count += 1
        return neighbors_count

    def _neighbor_cells(self, cell_point: Point) -> List[Point]:
        # ABC
        # D E (the center is the cell being checked)
        # FGH
        return [
            cell_point + Point(x=-1, y=-1),  # A
            cell_point + Point(x=0, y=-1),  # B
            cell_point + Point(x=1, y=-1),  # C
            cell_point + Point(x=-1, y=0),  # D
            # skipping the checked cell
            cell_point + Point(x=1, y=0),  # E
            cell_point + Point(x=-1, y=1),  # F
            cell_point + Point(x=0, y=1),  # G
            cell_point + Point(x=1, y=1),  # H
        ]


def _input_split(sep: str, fn: Callable[[str], _T], maxsplit=-1) -> List[_T]:
    """
    Read input and split it up to `maxsplit` times, and pass each elements to `fn`.
    """
    return [fn(elem) for elem in input().split(sep, maxsplit=maxsplit)]


def _input_parse_point():
    x, y = _input_split(",", int, maxsplit=1)
    return Point(x=x, y=y)


def parse_challenge_input():
    birth_conditions = _input_split(",", int)
    surviving_conditions = _input_split(",", int)
    game_rules = GameRules(
        cell_birth_neighbors=birth_conditions,
        cell_surviving_neighbors=surviving_conditions,
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

    god = GodPower(rules)
    for generation in range(0, wanted_result.generation + 1):  # range condition is `idx < stop`
        if generation != 0:  # We already have the grid of generation 0
            grid = god.apply_rules(grid)
        debug(f"--- GENERATION {generation}")
        debug()
        debug_multiline(grid.to_str_at(wanted_result.output_rect))
        debug()
        if DEBUG:
            time.sleep(0.1)

    debug("--- OUPUT ---")
    print(grid.to_str_at(wanted_result.output_rect))


if __name__ == "__main__":
    main()
