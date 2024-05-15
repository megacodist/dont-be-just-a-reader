#
# 
#

from collections import defaultdict
from queue import Empty, Queue
from threading import Thread

from . import ISpscPlayer
from spsc import Spsc


class _QuitException(Exception):
    pass


class Spsc10Player(ISpscPlayer, Thread):
    name = 'SPSC 10'

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
            'Spsc 10 player',
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
                self._choice.put(self._getSpsc())
        except _QuitException:
            pass
    
    def _getSpsc(self) -> Spsc:
        # Declaring of variables --------------------------
        import random
        # Functioning -------------------------------------
        predicts: dict[Spsc, int] = defaultdict(lambda: 0)
        if len(self._rivalHistory) >= 5:
            map_ = self._listToDict(self._rivalHistory[-5:])
            res = self._decide(map_, 5)
            if isinstance(res, Spsc):
                return res.getDefier()
            elif isinstance(res, tuple):
                for spsc in res:
                    predicts[spsc] += 1
        if len(self._rivalHistory) >= 10:
            map_ = self._listToDict(self._rivalHistory[-10:-5], map_) # type: ignore
            res = self._decide(map_, 10)
            if isinstance(res, Spsc):
                return res.getDefier()
            elif isinstance(res, tuple):
                for spsc in predicts:
                    predicts[spsc] += 1
                for spsc in res:
                    predicts[spsc] += 1
        if len(self._rivalHistory) >= 20:
            for n in range(20, len(self._rivalHistory), 10):
                map_ = self._listToDict(self._rivalHistory[-n:(10-n)], map_) # type: ignore
                res = self._decide(map_, 10)
                if isinstance(res, Spsc):
                    for spsc in predicts:
                        predicts[spsc] += 1
                    predicts[res] += 1
                elif isinstance(res, tuple):
                    for spsc in predicts:
                        predicts[spsc] += 1
                    for spsc in res:
                        predicts[spsc] += 1
        for spsc in Spsc:
            predicts[spsc] += 1
        weights = [predicts[spsc] for spsc in Spsc]
        guess = random.choices(list(Spsc), weights, k=1)[0]
        return guess.getDefier()
    
    def _listToDict(
            self,
            sub_history: list[Spsc],
            map_: dict[Spsc, int] | None = None,
            ) -> dict[Spsc, int]:
        """Converts queue of user choices into a mapping of
        `Spsc -> number of choices`. if `map_` is provided, it will be
        updated with the new slice of the queue. Otherwise `map_` will
        be created, intialized and returned.
        """
        if map_ is None:
            map_ = defaultdict(lambda: 0)
        for elem in sub_history:
            map_[elem] += 1
        return map_
    
    def _decide(
            self,
            map_: dict[Spsc, int],
            sum_: int,
            ) -> None | Spsc | tuple[Spsc] | tuple[Spsc, Spsc]:
        highFreq: list[Spsc] = []
        for elem in map_:
            freq = map_[elem] / sum_
            if freq >= 0.65:
                return elem
            elif freq >= 0.4:
                highFreq.append(elem)
        if len(highFreq) > 0:
            return tuple(highFreq) # type: ignore
    
    def start(self) -> None:
        super(ISpscPlayer, self).start()

    def finish(self) -> None:
        self._pendingFinish = True
