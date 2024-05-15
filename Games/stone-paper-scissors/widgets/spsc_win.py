#
# 
#

from datetime import timedelta
import enum
import logging
from queue import Empty, Queue
from random import shuffle
from time import perf_counter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkMessageBox
from typing import Mapping, MutableSequence

from utils.keyboard import KeyCodes, Modifiers
from spsc import Spsc
from spsc_player import ISpscPlayer


class _PlayerSide(enum.IntEnum):
    LEFT = 0
    RIGHT = 1


class _SpscPlayerData:
    def __init__(
            self,
            obj: ISpscPlayer,
            history: list[Spsc],
            q_choice: Queue[Spsc],
            q_rival_chc: Queue[Spsc],
            score: int = 0,
            duration: float = 0.00,
            ) -> None:
        self.spscObj = obj
        self.score = score
        self.duration = duration
        self.history = history
        self.qChoice = q_choice
        """The queue for receiving the player choice."""
        self.qRivalChoice = q_rival_chc
        """The queue for sending to the player his/her rival choice."""
        self.choice: Spsc | None = None
        """The current choice of the player."""


class SpscWin(tk.Tk, ISpscPlayer):
    def __init__(
            self,
            spsc_types: list[type[ISpscPlayer]],
            screenName: str | None = None,
            baseName: str | None = None,
            className: str = 'Tk',
            useTk: bool = True,
            sync: bool = False,
            use: str | None = None,
            ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.title('Stone, Paper, Scissors')
        #
        self.name = 'User'
        """The name of the player this class offers."""
        self._types: list[type[ISpscPlayer]] = [self, *spsc_types] # type: ignore
        self._players: dict[_PlayerSide, _SpscPlayerData] = {}
        self._userInputs = Queue[KeyCodes]()
        """The queue containing user inputs for the game."""
        # Declaring after IDs...
        self._userAfterId: str | None = None
        """After ID which manages user interactions in the game."""
        self._playAfterId: str | None = None
        """After ID for running the game"""
        self._TIMINT_AFTER = 50
        """Time interval for after methods."""
        self._pendingPause: bool = False
        """Specifies whether the user wants to pause the game."""
        self._pausedSides: MutableSequence[_PlayerSide]
        """A list of players when pause is reuqested."""
        # Declaring attributes of the game...
        self._leftScore = tk.IntVar(self, 0)
        self._rightScore = tk.IntVar(self, 0)
        self._leftDur = tk.StringVar(self, '0.00')
        self._rightDur = tk.StringVar(self, '0.00')
        self._leftPlayer = tk.IntVar(self, value=0)
        self._rightPlayer = tk.IntVar(self, value=0)
        # 'User' player attributes...
        self._choice: Queue[Spsc]
        """The current choice of the User."""
        self._rivalChoice: Queue[Spsc]
        """The last choice of the rival of the User."""
        self._history: list[Spsc]
        """A list (histiry) of all choices of the User."""
        self._rivalHistory: list[Spsc]
        """A list (histiry) of all choices of the rival of the User."""
        # Initializing GUI...
        self._initGui()
        # Initializing players randomly...
        self._choosePlayersRandomly()
        # Bindings...
        self.bind(
            '<Key>',
            self._OnKeyPressed)
    
    def _initGui(self) -> None:
        #
        self._frm_container = ttk.Frame(master=self)
        self._frm_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=7,
            pady=7)
        self._frm_container.rowconfigure(3, weight=1)
        self._frm_container.columnconfigure(0, weight=1)
        self._frm_container.columnconfigure(1, weight=1)
        #
        self._lbl_leftName = ttk.Label(
            self._frm_container,
            text=self._types[0].name,
            justify=tk.LEFT)
        self._lbl_leftName.grid(
            column=0,
            row=0,
            ipadx=3,
            ipady=3,
            sticky=tk.NW)
        #
        self._lbl_rightName = ttk.Label(
            self._frm_container,
            text=self._types[0].name,
            justify=tk.RIGHT)
        self._lbl_rightName.grid(
            column=1,
            row=0,
            ipadx=3,
            ipady=3,
            sticky=tk.NE)
        #
        self._lbl_leftScore = ttk.Label(
            self._frm_container,
            textvariable=self._leftScore)
        self._lbl_leftScore.grid(
            column=0,
            row=1,
            ipadx=3,
            ipady=3,
            sticky=tk.NW)
        #
        self._lbl_rightScore = ttk.Label(
            self._frm_container,
            textvariable=self._rightScore)
        self._lbl_rightScore.grid(
            column=1,
            row=1,
            ipadx=3,
            ipady=3,
            sticky=tk.NE)
        #
        self._lbl_leftDur = ttk.Label(
            self._frm_container,
            textvariable=self._leftDur)
        self._lbl_leftDur.grid(
            column=0,
            row=2,
            ipadx=3,
            ipady=3,
            sticky=tk.NW)
        #
        self._lbl_rightDur = ttk.Label(
            self._frm_container,
            textvariable=self._rightDur)
        self._lbl_rightDur.grid(
            column=1,
            row=2,
            ipadx=3,
            ipady=3,
            sticky=tk.NE)
        # Creating menu bar...
        self._menubar = tk.Menu(
            master=self)
        self['menu'] = self._menubar
        # Creating 'App' menu...
        self._menu_app = tk.Menu(
            master=self._menubar,
            tearoff=0)
        self._menu_app.add_command(
            label='Start a new game',
            command=self._startGame)
        self._menu_app.add_command(
            label='Pause/resume',
            command=self._pauseResume)
        self._menu_app.add_command(
            label='End this game',
            command=self._endGame)
        self._menubar.add_cascade(
            label='App',
            menu=self._menu_app)
        # Ceating 'Left player' menu...
        self._menu_leftPlayer = tk.Menu(
            master=self._menubar,
            tearoff=0)
        for idx, typ in enumerate(self._types):
            self._menu_leftPlayer.add_radiobutton(
                label=typ.name,
                value=idx,
                variable=self._leftPlayer,
                command=self._setLeftPlayer)
        self._menubar.add_cascade(
            label='Left player',
            menu=self._menu_leftPlayer)
        # Ceating 'Right player' menu...
        self._menu_rightPlayer = tk.Menu(
            master=self._menubar,
            tearoff=0)
        for idx, typ in enumerate(self._types):
            self._menu_rightPlayer.add_radiobutton(
                label=typ.name,
                value=idx,
                variable=self._rightPlayer,
                command=self._setRightPlayer)
        self._menubar.add_cascade(
            label='Right player',
            menu=self._menu_rightPlayer)
    
    def _OnKeyPressed(self, event: tk.Event) -> None:
        altCtrlShift = (
            Modifiers.ALT
            | Modifiers.CONTROL
            | Modifiers.SHIFT)
        altCtrl = Modifiers.ALT | Modifiers.CONTROL
        altShift = Modifiers.ALT | Modifiers.SHIFT
        ctrlShift = Modifiers.CONTROL | Modifiers.SHIFT

        # Checking for keyboard modefiers...
        if isinstance(event.state, str):
            logging.error(f'Unexpected state of {event.state}')
            event.state = Modifiers.NONE
        match event.state & altCtrlShift:
            case Modifiers.CONTROL:
                match event.keycode:
                    case _:
                        pass
            case Modifiers.NONE:
                match event.keycode:
                    case _:
                        if self._leftPlayer.get() == 0 or \
                                self._rightPlayer.get() == 0:
                            self._userInputs.put(KeyCodes(event.keycode))
    
    def __call__(
            self,
            choice: Queue[Spsc],
            rival_choice: Queue[Spsc],
            history: list[Spsc],
            rival_history: list[Spsc],
            ) -> ISpscPlayer:
        self._choice = choice
        self._rivalChoice = rival_choice
        self._history = history
        self._rivalHistory = rival_history
        return self
    
    def _choosePlayersRandomly(self) -> None:
        indicies = list(range(len(self._types)))
        if len(indicies) <= 1:
            tkMessageBox.showerror(message='No algorithm was found.')
            return
        shuffle(indicies)
        self._players[_PlayerSide.LEFT] = _SpscPlayerData(
            self._types[indicies[0]](None, None, None, None), # type: ignore
            None,  # type: ignore
            None,  # type: ignore
            None,) # type: ignore
        self._players[_PlayerSide.RIGHT] = _SpscPlayerData(
            self._types[indicies[1]](None, None, None, None), # type: ignore
            None,  # type: ignore
            None,  # type: ignore
            None,) # type: ignore
        self._leftPlayer.set(indicies[0])
        self._setLeftPlayer()
        self._rightPlayer.set(indicies[1])
        self._setRightPlayer()
        self._initBothData()
    
    def _initBothData(self) -> None:
        """Initializes both sides data structure (no effect in the GUI)."""
        #
        qLeftChc = Queue[Spsc]()
        qLeftRivalChc = Queue[Spsc]()
        qRightChc = Queue[Spsc]()
        qRightRivalChc = Queue[Spsc]()
        leftHistory = list[Spsc]()
        rightHistory = list[Spsc]()
        #
        self._players[_PlayerSide.LEFT] = _SpscPlayerData(
            self._types[self._leftPlayer.get()](
                choice=qLeftChc,
                rival_choice=qLeftRivalChc,
                history=leftHistory,
                rival_history=rightHistory),
            history=leftHistory,
            q_choice=qLeftChc,
            q_rival_chc=qLeftRivalChc,)
        self._players[_PlayerSide.RIGHT] = _SpscPlayerData(
            self._types[self._rightPlayer.get()](
                choice=qRightChc,
                rival_choice=qRightRivalChc,
                history=rightHistory,
                rival_history=leftHistory),
            history=rightHistory,
            q_choice=qRightChc,
            q_rival_chc=qRightRivalChc,)

    def _resetBothScoreDur(self) -> None:
        """Resets both sides score and duration in the GUI and data to
        zero.
        """
        self._players[_PlayerSide.LEFT].score = 0
        self._players[_PlayerSide.LEFT].duration = 0.0
        self._leftScore.set(0)
        self._leftDur.set('0.00')
        self._players[_PlayerSide.RIGHT].score = 0
        self._players[_PlayerSide.RIGHT].duration = 0.0
        self._rightScore.set(0)
        self._rightDur.set('0.00')
    
    def _setLeftPlayer(self) -> None:
        if self._playAfterId is not None:
            tkMessageBox.showerror(
                'Impossible to select a player during a game.')
            return
        self._lbl_leftName.config(
            text=self._types[self._leftPlayer.get()].name)
        self._resetBothScoreDur()
    
    def _setRightPlayer(self) -> None:
        if self._playAfterId is not None:
            tkMessageBox.showerror(
                'Impossible to select a player during a game.')
            return
        self._lbl_rightName.config(
            text=self._types[self._rightPlayer.get()].name)
        self._resetBothScoreDur()
    
    def _setSideDur(self, side: _PlayerSide, duration: float) -> None:
        self._players[side].duration = duration
        dur = timedelta(seconds=duration)
        match side:
            case _PlayerSide.LEFT:
                self._leftDur.set(str(dur)[:-3])
            case _PlayerSide.RIGHT:
                self._rightDur.set(str(dur)[:-3])
    
    def _incrementSideScore(self, side: _PlayerSide) -> None:
        self._players[side].score += 1
        if side == _PlayerSide.LEFT:
            self._leftScore.set(self._players[side].score)
        else:
            self._rightScore.set(self._players[side].score)
    
    def _startGame(self) -> None:
        if self._playAfterId is not None:
            tkMessageBox.showerror(message='The game is already playing.')
            return
        if self._leftPlayer.get() == 0 and self._rightPlayer.get() == 0:
            tkMessageBox.showerror(message='This program does not support '
                'a game between two users.')
            return
        self._resetBothScoreDur()
        self._initBothData()
        for side in self._players:
            self._players[side].spscObj.start()
        sides = list(iter(_PlayerSide))
        self._runNewRound(sides)

    def _endGame(self) -> None:
        if self._playAfterId is None:
            return
        self.after_cancel(self._playAfterId)
        self._playAfterId = None
        for side in self._players:
            self._players[side].spscObj.finish()
    
    def _runNewRound(self, sides: MutableSequence[_PlayerSide]) -> None:
        if self._pendingPause:
            self._pausedSides = sides
            return
        shuffle(sides)
        orig_durs = {side:self._players[side].duration for side in sides}
        self._playAfterId = self.after(
            self._TIMINT_AFTER,
            self._getBothChoice,
            perf_counter(),
            sides,
            orig_durs,)

    def _getBothChoice(
            self,
            start_tm: float,
            sides: MutableSequence[_PlayerSide],
            orig_durs: Mapping[_PlayerSide, float],
            ) -> None:
        # Checking for pause...
        if self._pendingPause:
            self._pausedSides = sides
            return
        # Lokking for players' choices...
        undecided = list[_PlayerSide]()
        for side in sides:
            try:
                self._players[side].choice = self._players[
                    side].qChoice.get_nowait()
            except Empty:
                undecided.append(side)
            duration = orig_durs[side] + perf_counter() - start_tm
            self._setSideDur(side, duration)
        match len(undecided):
            case 1 | 2:
                shuffle(undecided)
                self._playAfterId = self.after(
                    self._TIMINT_AFTER,
                    self._getBothChoice,
                    start_tm,
                    undecided,
                    orig_durs)
            case 0:
                self._scoreWinner()
            case _:
                logging.error('E1-1')
    
    def _scoreWinner(self) -> None:
        if self._players[_PlayerSide.LEFT].choice > self._players[ # type:ignore
                _PlayerSide.RIGHT].choice:
            self._incrementSideScore(_PlayerSide.LEFT)
            self._showWinner(_PlayerSide.LEFT)
        elif self._players[_PlayerSide.LEFT].choice < self._players[ # type:ignore
                _PlayerSide.RIGHT].choice:
            self._incrementSideScore(_PlayerSide.RIGHT)
            self._showWinner(_PlayerSide.RIGHT)
        else:
            self._showWinner(None)
    
    def _showWinner(self, winner: _PlayerSide | None) -> None:
        self._showWinner_after()
    
    def _showWinner_after(self) -> None:
        self._players[_PlayerSide.LEFT].qRivalChoice.put(
            self._players[_PlayerSide.RIGHT].choice) # type: ignore
        self._players[_PlayerSide.RIGHT].qRivalChoice.put(
            self._players[_PlayerSide.LEFT].choice) # type: ignore
        self._players[_PlayerSide.LEFT].history.append(
            self._players[_PlayerSide.LEFT].choice) # type: ignore
        self._players[_PlayerSide.RIGHT].history.append(
            self._players[_PlayerSide.RIGHT].choice) # type: ignore
        self._players[_PlayerSide.LEFT].choice = None
        self._players[_PlayerSide.RIGHT].choice = None
        self._runNewRound(list(iter(_PlayerSide)))
    
    def _pauseResume(self) -> None:
        """Pauses/resumes the game."""
        match (self._playAfterId is None, self._pendingPause):
            case (False, True,):
                self._pendingPause = False
                self._runNewRound(self._pausedSides)
            case (False, False,):
                self._pendingPause = True
            case (True, True,):
                logging.error('E2-3')
            case (True, False,):
                tkMessageBox.showerror(
                    message='No game is in progress to pause.')
    
    def start(self) -> None:
        self._userAfterId = self.after(
            self._TIMINT_AFTER,
            self._lookForInput)

    def finish(self) -> None:
        if self._userAfterId is None:
            return
        self.after_cancel(self._userAfterId)
        self._userAfterId = None
        while not self._userInputs.empty():
            self._userInputs.get()

    def _lookForInput(self) -> None:
        """Looks for user input and validate it."""
        toLookForUser = False
        try:
            while True:
                input_ = self._userInputs.get_nowait()
                match input_:
                    case KeyCodes.KB_1 | KeyCodes.KP_1:
                        self._choice.put(Spsc.STONE)
                        toLookForUser = False
                    case KeyCodes.KB_2 | KeyCodes.KP_2:
                        self._choice.put(Spsc.PAPER)
                        toLookForUser = False
                    case KeyCodes.KB_3 | KeyCodes.KP_3:
                        self._choice.put(Spsc.SCISSORS)
                        toLookForUser = False
                    case _:
                        toLookForUser = True
        except Empty:
            toLookForUser = True
        if toLookForUser:
            self._userAfterId = self.after(
                self._TIMINT_AFTER,
                self._lookForInput)
        else:
            self._userAfterId = self.after(
                self._TIMINT_AFTER,
                self._lookForRival)
    
    def _lookForRival(self) -> None:
        try:
            self._rivalChoice.get_nowait()
            self._userAfterId = self.after(
                self._TIMINT_AFTER,
                self._lookForInput)
        except Empty:
            self._userAfterId = self.after(
                self._TIMINT_AFTER,
                self._lookForRival)
