from itertools import combinations
from pprint import pprint
from typing import Any, Hashable, Sequence


def AreMutuallyDisjoint(__sets: Sequence[set], /) -> bool:
    """Checks a sequence of sets are mutually disjoint or not. If the
    sequence contains one element or it is empty, the result is always
    True.
    """
    if len(__sets) < 1:
        return True
    for i, j in combinations(range(len(__sets)), 2):
        if __sets[i] & __sets[j]:
            return False
    return True


def GetAllIntersections(
        __sets: dict[Hashable, set[Any]],
        /
        ) -> dict[frozenset[Hashable], set[Any]]:
    """Gets all possible intersections of a collection of sets. The input
    consists of a mapping between sets' identity (Hashable objects) and their
    objects (set). The output is made of a mapping between frozenset
    objects of intersected sets and their intersections (set). For example

    allSets = {
        'A': {1, 2, 3},

        'B': {1, 2, 4},

        'C': {1, 4, 5},

        'D': {5}}
    
    produces:

    {frozenset({'B', 'A'}): {2},

    frozenset({'B', 'C'}): {4},

    frozenset({'C', 'D'}): {5},

    frozenset({'B', 'C', 'A'}): {1}}
    """
    # Declaring variables ---------------------------------
    i: int
    j: int
    intersectFound: bool
    lsTemp: list[frozenset]
    intersect: set[Any]
    sets: dict[frozenset[str], set[Any]]
    allIntersects: dict[frozenset[str], set[Any]]
    # Finding all intersections ---------------------------
    sets = {frozenset([key]): value for key, value in __sets.items()}
    allIntersects = {}
    lsTemp:tuple[frozenset[str]] = tuple(sets.keys())
    for i, j in combinations(range(len(lsTemp)), 2):
        intersect = sets[lsTemp[i]] & sets[lsTemp[j]]
        if intersect:
            allIntersects[lsTemp[i] | lsTemp[j]] = intersect
    while True:
        intersectFound = False
        lsTemp = tuple(allIntersects.keys())
        for i, j in combinations(range(len(lsTemp)), 2):
            intersect = allIntersects[lsTemp[i]] & allIntersects[lsTemp[j]]
            if intersect:
                intersectFound = True
                allIntersects[lsTemp[i]] -= intersect
                allIntersects[lsTemp[j]] -= intersect
                allIntersects[lsTemp[i] | lsTemp[j]] = intersect
        if intersectFound:
            allIntersects = {
                key:value
                for key, value in allIntersects.items()
                if value}
        else:
            break
    return allIntersects
