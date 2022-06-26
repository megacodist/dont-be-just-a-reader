import asyncio
import logging
import sys
from threading import Lock, Thread
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Iterable, Mapping

import aiohttp
import attrs


# Defining of demanding types...
@attrs.define
class ProgInfo:
    nFinished: int
    total: int


# Defining of required variables...
progInfo: ProgInfo
progInfoLock = Lock()


async def DoStressTest(url: str, n: int) -> None:
    global progInfo
    global progInfoLock

    with progInfoLock:
        progInfo = ProgInfo(0, n)
    async with aiohttp.ClientSession() as session:
        reqs =[
            session.get(url)
            for _ in range(n)]
        for future in asyncio.as_completed(reqs):
            try:
                await future
            except Exception:
                pass
            with progInfoLock:
                progInfo.nFinished += 1


class AsyncioThrd(Thread):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._running = True
        self._TIME_INTRVL = 0.1

    def run(self) -> None:
        # Changing default event loop from Proactor to Selector on Windows
        # OS and Python 3.8+...
        if sys.platform.startswith('win'):
            if sys.version_info[:2] >= (3, 8,):
                asyncio.set_event_loop_policy(
                    asyncio.WindowsSelectorEventLoopPolicy())

        try:
            # Running the application...
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._main())
        finally:
            self.loop.close()

    def close(self) -> None:
        self._running = False
    
    async def _main(self) -> None:
        while self._running:
            await asyncio.sleep(self._TIME_INTRVL)
        
        pending = asyncio.all_tasks()
        while len(pending) > 1:
            _, pending = asyncio.wait(
                pending,
                timeout=self._TIME_INTRVL)


class HttpStressTestWin(tk.Tk):
    def __init__(
            self,
            screenName: str | None = None,
            baseName: str | None = None,
            className: str = 'Tk',
            useTk: bool = True,
            sync: bool = False,
            use: str | None = None
            ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title('HTTP stress test')
        self.geometry('650x160+200+200')
        self.resizable(True, False)

        self._TIME_INTRVL = 40
        self._showProgID: int
        self._updateElapsedID: int

        self._InitializeGui()

        self.bind('<Return>', self._OnReturn)
    
    def _InitializeGui(self) -> None:
        #
        self.frm_container = tk.Frame(
            master=self)
        self.frm_container.columnconfigure(
            index=1,
            weight=1)
        self.frm_container.pack(
            fill=tk.BOTH,
            expand=1,
            padx=4,
            pady=4)
        
        #
        self.lbl_url = ttk.Label(
            master=self.frm_container,
            text='URL:')
        self.lbl_url.grid(
            column=0,
            row=0,
            sticky=tk.E,
            padx=2,
            pady=2)
        
        #
        self.entry_url = ttk.Entry(
            master=self.frm_container)
        self.entry_url.grid(
            column=1,
            row=0,
            sticky=tk.EW,
            padx=2,
            pady=2)
        
        #
        self.lbl_number = ttk.Label(
            master=self.frm_container,
            text='Number:')
        self.lbl_number.grid(
            column=0,
            row=1,
            sticky=tk.E,
            padx=2,
            pady=2)
        
        #
        self.spn_number = ttk.Spinbox(
            master=self.frm_container,
            values=(5, 10, 20, 50, 100, 200, 500, 1_000, 2_000),
            increment=1)
        self.spn_number.grid(
            column=1,
            row=1,
            sticky=tk.W,
            padx=2,
            pady=2)
        
        #
        self.btn_startStop = ttk.Button(
            master=self.frm_container,
            text='Start',
            command=self._StartStopTest)
        self.btn_startStop.grid(
            column=1,
            row=2,
            sticky=tk.E,
            padx=2,
            pady=2)
        
        #
        self.lblfrm_status = tk.LabelFrame(
            master=self.frm_container,
            text='Status')
        self.lblfrm_status.columnconfigure(
            index=0,
            weight=1)
        self.lblfrm_status.grid(
            column=0,
            columnspan=2,
            row=3,
            sticky=tk.NSEW,
            padx=2,
            pady=2)
        
        #
        self.lbl_status = ttk.Label(
            master=self.lblfrm_status,
            text='Ready')
        self.lbl_status.grid(
            column=0,
            row=0,
            sticky=tk.EW,
            padx=2,
            pady=2)
        
        #
        self.prgrs_status = ttk.Progressbar(
            master=self.lblfrm_status,
            orient=tk.HORIZONTAL,
            mode='determinate')
        self.prgrs_status.grid(
            column=0,
            row=1,
            sticky=tk.EW,
            padx=2,
            pady=2)
    
    def _OnReturn(self, event: tk.Event) -> None:
        self._StartStopTest()
    
    def _StartStopTest(self) -> None:
        global asyncioThrd
        global progInfo

        if self.btn_startStop['text'] == 'Start':
            nReqs = int(self.spn_number.get())
            self.prgrs_status.config(maximum=nReqs)
            self.btn_startStop.config(text='Stop')
            self.lbl_status.config(text='Starting test...')
            self._testTask = asyncio.run_coroutine_threadsafe(
                DoStressTest(
                    self.entry_url.get(),
                    nReqs),
                asyncioThrd.loop)
            self._showProgID = self.after(
                self._TIME_INTRVL,
                self._ShowProg)
            self._updateElapsedID = self.after(
                1000,
                self._UpdateElapsed,
                1)
        elif self.btn_startStop['text'] == 'Stop':
            self._testTask.cancel()
            if self._showProgID:
                self.after_cancel(self._showProgID)
            if self._updateElapsedID:
                self.after_cancel(self._updateElapsedID)
            if self._testTask.cancelled():
                self._ResetStatus()
            else:
                self.after(
                    self._TIME_INTRVL,
                    self._CheckCanceling)
        else:
            logging.warning('Button text is incorrect')
    
    def _ShowProg(self) -> None:
        global progInfo
        global progInfoLock

        with progInfoLock:
            currProg = progInfo
        if currProg.nFinished < currProg.total:
            self.prgrs_status['value'] = currProg.nFinished
            self._showProgID = self.after(
                self._TIME_INTRVL,
                self._ShowProg)
        else:
            self._ResetStatus()
            # Canceling all 'after' callbacks...
            self.after_cancel(self._updateElapsedID)
    
    def _ResetStatus(self) -> None:
        self.btn_startStop.config(text='Start')
        self.lbl_status.config(text='Ready')
        self.prgrs_status.config(value=0)
    
    def _CheckCanceling(self) -> None:
        if self._testTask.cancelled():
            self._ResetStatus()
        else:
            self.after(
                self._TIME_INTRVL,
                self._CheckCanceling)
    
    def _UpdateElapsed(self, elapsed: int) -> None:
        self.lbl_status['text'] = f'Elapsed {elapsed} seconds'
        self._updateElapsedID = self.after(
                1000,
                self._UpdateElapsed,
                elapsed + 1)


if __name__ == '__main__':
    # Creating the AsyncIO in a thread...
    asyncioThrd = AsyncioThrd(name='asyncioThrd')
    asyncioThrd.start()

    # Creating the GUI in the main thread..
    httpStressTestWin = HttpStressTestWin()
    httpStressTestWin.mainloop()

    asyncioThrd.close()
    m = 2
