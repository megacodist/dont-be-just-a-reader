#
# 
#

from queue import Empty, Queue
from threading import Thread

from . import ISpscPlayer
from spsc import Spsc


class _QuitException(Exception):
    pass


class NaiveSpscPlayer(ISpscPlayer, Thread):
    name = 'Naive'

    def __init__(
            self,
            choice: Queue[Spsc],
            rival_choice: Queue[Spsc],
            history: list[Spsc],
            rival_history: list[Spsc],
            ) -> None:
        super().__init__(choice, rival_choice, history, rival_history)
        super(ISpscPlayer, self).__init__(
            None,
            None,
            'Naive Spsc player',
            tuple(),
            None,
            daemon=True)
        self._pendingFinish = False
    
    def run(self) -> None:
        from random import choice as RandomChoice
        spscLst = list(Spsc)
        self._choice.put(RandomChoice(spscLst))
        try:
            while True:
                # Reading rival choice, checking for quit...
                while True:
                    try:
                        _ = self._rivalChoice.get(True, 0.025)
                        break
                    except Empty:
                        if self._pendingFinish:
                            raise _QuitException()
                # Producing next naive choice...
                self._choice.put(RandomChoice(spscLst))
        except _QuitException:
            pass
    
    def start(self) -> None:
        super(ISpscPlayer, self).start()

    def finish(self) -> None:
        self._pendingFinish = True
