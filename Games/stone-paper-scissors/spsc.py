#
# 
#

from __future__ import annotations
import enum
from typing import Any


class Spsc(enum.IntEnum):
    """This enumeration offers choices of Roch, Paper, Scissors game.
    This class implements hashable and rich comparisonprotocols.
    """
    STONE = 1
    PAPER = 2
    SCISSORS = 3

    @classmethod
    def getComparer(cls, a: Spsc, b: Spsc) -> int:
        """If the return is:
        * positive: `a > b`
        * 0: `a == b`
        * negative: `a < b`
        """
        dif = a.value - b.value
        return dif * ((-1) ** (abs(dif) - 1))

    def getDefier(self) -> Spsc:
        """Gets the enumerator that defies this one."""
        match self:
            case Spsc.STONE:
                return Spsc.PAPER
            case Spsc.PAPER:
                return Spsc.SCISSORS
            case Spsc.SCISSORS:
                return Spsc.STONE
    
    def getLoser(self) -> Spsc:
        """Gets the enumerator that loses this one."""
        match self:
            case Spsc.STONE:
                return Spsc.SCISSORS
            case Spsc.PAPER:
                return Spsc.STONE
            case Spsc.SCISSORS:
                return Spsc.PAPER

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.getDefier() == other
    
    def __le__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.getLoser() != other
    
    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.getLoser() == other
    
    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.getDefier() != other
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value
    
    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value != other.value
    
    def __hash__(self) -> int:
        return self.value
