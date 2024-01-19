import itertools
import time
from collections import defaultdict
from queue import PriorityQueue as PQ
from termcolor import colored
import numpy as np

np.set_printoptions(linewidth=120)


class Dot:
    def __init__(self, color: str, cord: tuple[int, int], dot: bool):
        self.color: str = color
        self.loc: tuple[int, int] = cord
        self.is_dot: bool = dot

    DOT = "\u25a0"
    LINE = "\u25AA"

    @property
    def icon(self) -> str:
        return self.DOT if self.is_dot else self.LINE

    def __sub__(self, other):  #! manhattan
        return sum(abs(z1 - z2) for z1, z2 in zip(self.loc, other.loc))

    def copy(self):
        return self.__class__(self.color, self.cord)

    def __repr__(self) -> str:
        return colored(self.icon, self.color)


class DotGraph:
    EMPTY = "white"

    def __init__(self, size: int, pairs: dict[str, list[tuple[int, int]]]):
        self.recents = defaultdict(int)
        self.size = size
        self.mat: np.ndarray = np.array(
            [
                Dot(self.EMPTY, cord, False)
                for cord in itertools.product(range(size), repeat=2)
            ],
            dtype=Dot,
        ).reshape((size, size))
        self.pairs: dict[str, list[Dot]] = defaultdict(tuple)
        for col, cords in pairs.items():
            for cord in cords:
                dot: Dot = self.mat[cord]
                dot.color, dot.is_dot = col, True
                self.pairs[col] += (dot,)

    def copy_pairs(self):
        new_pairs = {}
        for col, (d1, d2) in self.pairs.items():
            new_pairs[col] = (d1, d2)
        return new_pairs

    @property
    def solved(self):
        return all(x.color != self.EMPTY for x in self.mat.flat)

    def order_colors(self):
        return sorted(
            self.pairs.items(),
            key=lambda item: (self.recents[item[0]], Dot.__sub__(*item[1])),
        )

    def get_all_near_dots(self, dot: Dot) -> list[Dot]:
        nears = []
        r, c = dot.loc
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            rrcc = r + dr, c + dc
            if -1 in rrcc:
                continue
            try:
                next_dot: Dot = self.mat[rrcc]
            except IndexError:
                continue
            nears.append(next_dot)
        return nears

    def get_near_dots(self, orig: Dot, dest: Dot) -> list[Dot]:
        pq = PQ(4)
        for next_dot in self.get_all_near_dots(orig):
            if next_dot.color == self.EMPTY:
                pq.put((next_dot - dest, next_dot.loc, next_dot))
        return [x[-1] for x in pq.queue]

    def check_path(self, start: Dot, end: Dot, color: str):
        rows = cols = self.size
        stack = [start]
        visited = np.full((rows, cols), False, dtype=bool)
        while stack:
            dot = stack.pop()
            if dot == end:
                return True
            visited[dot.loc] = True
            for near_dot in self.get_all_near_dots(dot):
                if near_dot.color in {self.EMPTY, color} and not visited[near_dot.loc]:
                    stack.append(near_dot)
        return False

    @property
    def good(self):
        for color, (d1, d2) in self.pairs.items():
            if not self.check_path(d1, d2, color):
                return False
        for dot in self.mat.flat:
            dot: Dot
            color = dot.color
            nears = [x.color for x in self.get_all_near_dots(dot)]
            if dot.color == self.EMPTY:
                if self.EMPTY in nears:
                    continue
                if len(set(nears)) == 1:
                    if Dot.__sub__(*self.pairs[nears[0]]) == 1:
                        return False
            elif all(c != color for c in nears):
                if self.EMPTY not in nears:
                    return False
            elif nears.count(color) >= 3:
                return False
        return True

    def do_dots(self) -> tuple[bool, list[Dot]]:
        for color, dots in self.order_colors():
            if Dot.__sub__(*dots) <= 1:
                continue
            for i, dot in enumerate(dots):
                match len(nears := self.get_near_dots(dot, dot)):
                    case 0:
                        return False, []  #!bad
                    case 1:
                        near = nears[0]
                        self.pairs[color] = (near, dots[1 - i])[:: -2 * i + 1]
                        near.color = color
                        return True, nears
        return True, []

    def do_if_not_good(self, po, ch):
        self.pairs = po
        for cc in ch:
            cc.color = self.EMPTY

    def solver(self, first=True):
        while True:
            if not self.good:
                return
            if self.solved:
                return self
            if not first:
                break
            match self.do_dots():
                case (False, _):
                    return
                case (True, []):
                    break
        if first:  # show after doing dots
            print(self.mat)
        for color, (orig, dest) in self.order_colors():
            if (orig - dest) > 1:  # if not already connected
                for near_dot in self.get_near_dots(orig, dest):
                    # ************************************
                    near_dot.color = color
                    self.pairs[color] = (near_dot, dest)
                    self.recents[color] -= 1
                    # ************************************
                    if self.solver(False):
                        return self
                    # ?????????????????????????????????????
                    self.recents[color] += 1
                    self.pairs[color] = (orig, dest)
                    near_dot.color = self.EMPTY
                    # ?????????????????????????????????????

    def show_solve_show(self):
        print("{0}x{0},".format(self.size), len(self.pairs), "colors")
        print(self.mat)
        t = time.time()
        self.solver()
        print(time.time() - t)
        print(self.mat, "\n")


# good showing colors:
#   grey red green yellow blue magenta cyan light_red light_green light_yellow

DotGraph(
    6,
    {
        "green": [(0, 5), (4, 3)],
        "magenta": [(2, 1), (3, 5)],
        "red": [(4, 1), (3, 3)],
        "blue": [(5, 3), (4, 5)],
        "light_yellow": [(2, 2), (4, 4)],
    },
).show_solve_show()

DotGraph(
    5,
    {
        "green": [(0, 0), (2, 2)],
        "light_yellow": [(0, 1), (3, 3)],
        "magenta": [(2, 0), (4, 2)],
        "red": [(0, 4), (4, 3)],
        "blue": [(3, 0), (4, 1)],
    },
).show_solve_show()

DotGraph(
    5,
    {
        "magenta": [(0, 0), (4, 2)],
        "green": [(1, 0), (4, 0)],
        "red": [(1, 1), (4, 1)],
        "light_yellow": [(2, 2), (3, 3)],
        "blue": [(0, 3), (1, 4)],
    },
).show_solve_show()

DotGraph(
    7,
    {  #! 7x7, 7 colors
        "blue": [(1, 2), (4, 2)],
        "cyan": [(3, 5), (5, 5)],
        "light_yellow": [(1, 0), (1, 3)],
        "red": [(6, 3), (0, 6)],
        "magenta": [(0, 5), (2, 5)],
        "green": [(2, 0), (6, 2)],
        "grey": [(0, 0), (5, 4)],
    },
).show_solve_show()


DotGraph(
    8,
    {  #! 8x8, 8 colors
        "red": [(4, 5), (7, 5)],
        "light_yellow": [(6, 1), (4, 3)],
        "blue": [(7, 0), (7, 4)],
        "green": [(4, 4), (7, 7)],
        "cyan": [(5, 3), (6, 5)],
        "light_magenta": [(1, 2), (6, 4)],
        "grey": [(2, 2), (4, 2)],
        "magenta": [(1, 3), (1, 6)],
    },
).show_solve_show()

DotGraph(
    9,
    {  #! 9x9, 8 colors
        "light_yellow": [(2, 0), (7, 5)],
        "red": [(4, 5), (8, 5)],
        "green": [(0, 5), (5, 8)],
        "blue": [(0, 6), (2, 8)],
        "magenta": [(0, 1), (4, 7)],
        "cyan": [(0, 0), (3, 1)],
        "grey": [(2, 1), (6, 2)],
        "yellow": [(3, 5), (7, 7)],
    },
).show_solve_show()
