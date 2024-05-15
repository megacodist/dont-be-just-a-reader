#
# 
#

from abc import ABC, abstractmethod
from queue import Queue

from spsc import Spsc


class ISpscPlayer(ABC):
    name: str

    def __init__(
            self,
            choice: Queue[Spsc],
            rival_choice: Queue[Spsc],
            history: list[Spsc],
            rival_history: list[Spsc],
            ) -> None:
        self._choice = choice
        self._rivalChoice = rival_choice
        self._history = history
        self._rivalHistory = rival_history
    
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def finish(self) -> None:
        pass
