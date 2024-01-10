from collections import defaultdict
import itertools
import numpy as np


class Dot:
    def __init__(self, color: str, cord: tuple[int, int], dot: bool):
        self.color: str = color
        self.loc: tuple[int, int] = cord
        self.is_dot: bool = dot

    def copy(self):
        return self.__class__(self.color, self.cord)

    def __repr__(self) -> str:
        return "." + str((self.color, self.is_dot))


class DotGraph:
    def __init__(self, size: int, pairs: dict[str, list[tuple[int, int]]]):
        self.pairs: dict[str, list[tuple[int, int]]] = pairs
        self.size = size
        self.mat = np.array(
            [Dot(" ", cord, False) for cord in itertools.product(range(9), repeat=2)],
            dtype=Dot,
        ).reshape((size, size))
        for col, cords in pairs.items():
            for cord in cords:
                dot: Dot = self.mat[cord]
                dot.color, dot.is_dot = col, True


size = 9
pairs = {
    "yellow": [(0, 1), (3, 6)],
    "green": [(5, 2), (7, 5)],
    "pink": [(3, 5), (5, 7)],
    "orange": [(1, 8), (8, 2)],
    "blue": [(4, 1), (7, 0)],
}
dg = DotGraph(size, pairs)
print(dg.mat)
