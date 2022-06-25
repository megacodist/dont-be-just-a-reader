# This program is a collaboration of Tkinter and Async I/O in Python.
# If you need to perform HTTP operations in a GUI application, one good
# method is to use both packages. Main thread must houses windowing 
# system and the second thread runs Async I/O. The interactions between the
# two is achieved through queue module.

import asyncio
from queue import Queue, Empty
import sys
from threading import Thread, Event
import tkinter as tk
from tkinter import ttk

from aiohttp import ClientSession
import attrs


# Defining of demanding types...
@attrs.define
class ReqInfo:
    id: int
    url: str


@attrs.define
class RespInfo:
    id: int
    url: str
    statusCode: int


# Defining of global variables...
reqQ: Queue[ReqInfo] = Queue()
statusCodeQ: Queue[RespInfo] = Queue()
asyncioFinished = Event()


class UrlStatusCodeThrd(Thread):
    def run(self) -> None:
        self.running = True

        # Changing default event loop from Proactor to Selector on Windows
        # OS and Python 3.8+...
        if sys.platform.startswith('win'):
            if sys.version_info[:2] >= (3, 8,):
                asyncio.set_event_loop_policy(
                    asyncio.WindowsSelectorEventLoopPolicy())

        # Running the application...
        self.loop = asyncio.new_event_loop()
        try:
            self.loop.run_until_complete(self._LookForUrls())
        finally:
            self.loop.close()
        
    def close(self) -> None:
        self.running = False

    async def _LookForUrls(self) -> None:
        global reqQ
        global asyncioFinished

        async with ClientSession() as self.session:
            # This Async I/O thread goes on until the request queue is empty
            # and there is a call to exit
            while (not reqQ.empty()) or self.running:
                try:
                    reqInfo = reqQ.get(block=True, timeout=0.1)
                except Empty:
                    await asyncio.sleep(0.1)
                    continue
                await asyncio.create_task(self._GetPostStatusCode(reqInfo))

            # On quiting the Async I/O thread, first we are going to wait
            # the ongoing tasks except for this coroutine
            pending = asyncio.all_tasks()
            while len(pending) > 1:
                _, pending = await asyncio.wait(
                    pending,
                    timeout=0.02)

        # Informing the Tkinter thread that Async I/O thread quitted
        asyncioFinished.set()
    
    async def _GetPostStatusCode(
            self,
            reqInfo: ReqInfo
            ) -> None:
        global statusCodeQ

        async with self.session.get(reqInfo.url) as resp:
            statusCodeQ.put(
                RespInfo(
                    reqInfo.id,
                    reqInfo.url,
                    resp.status),
                block=True)


class UrlStatusCodeWin(tk.Tk):
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
        self.title('URL & Status code')
        self.theme = ttk.Style()
        self.theme.theme_use('clam')
        self._InitializeGui()
        self._id = 0

        #
        self.protocol('WM_DELETE_WINDOW', self._OnClosing)
    
    def _InitializeGui(self) -> None:
        # 
        self.frm_container = tk.Frame(
            master=self)
        self.frm_container.columnconfigure(
            index=0,
            weight=1)
        self.frm_container.rowconfigure(
            index=1,
            weight=1)
        self.frm_container.pack(
            fill='both',
            expand=1,
            padx=4,
            pady=4)
        
        #
        self.lblfrm_request = tk.LabelFrame(
            master=self.frm_container,
            text='HTTP request')
        self.lblfrm_request.columnconfigure(
            index=1,
            weight=1)
        self.lblfrm_request.grid(
            column=0,
            row=0,
            sticky=tk.EW,
            ipadx=4,
            ipady=4)
        
        #
        self.lbl_url = ttk.Label(
            master=self.lblfrm_request,
            text='URL:')
        self.lbl_url.grid(
            column=0,
            row=0,
            sticky=tk.E)
        
        #
        self.entry_url = ttk.Entry(
            master=self.lblfrm_request)
        self.entry_url.grid(
            column=1,
            row=0,
            sticky=tk.EW)
        
        #
        self.lbl_number = ttk.Label(
            master=self.lblfrm_request,
            text='Number:')
        self.lbl_number.grid(
            column=0,
            row=1,
            sticky=tk.E)
        
        #
        self.spn_number = ttk.Spinbox(
            master=self.lblfrm_request,
            from_=0,
            increment=1)
        self.spn_number.grid(
            column=1,
            row=1,
            sticky=tk.W)
        
        #
        self.btn_url = ttk.Button(
            master=self.lblfrm_request,
            command=self._PostUrls,
            text='Go')
        self.btn_url.grid(
            column=1,
            row=2,
            sticky=tk.E)
        
        #
        self.lblfrm_response = tk.LabelFrame(
            master=self.frm_container,
            text='HTTP response')
        self.lblfrm_response.grid(
            column=0,
            row=1,
            sticky=tk.NSEW)
        
        #
        self.vscrlbr_response = ttk.Scrollbar(
            master=self.lblfrm_response,
            orient=tk.VERTICAL)
        self.hscrlbr_response = ttk.Scrollbar(
            master=self.lblfrm_response,
            orient=tk.HORIZONTAL)
        self.txt_response = tk.Text(
            master=self.lblfrm_response,
            wrap=None,
            state=tk.DISABLED,
            xscrollcommand=self.hscrlbr_response.set,
            yscrollcommand=self.vscrlbr_response.set)
        self.vscrlbr_response.config(
            command=self.txt_response.yview)
        self.hscrlbr_response.config(
            command=self.txt_response.xview)
        self.hscrlbr_response.pack(
            side=tk.BOTTOM,
            fill=tk.X)
        self.vscrlbr_response.pack(
            side=tk.RIGHT,
            fill=tk.Y)
        self.txt_response.pack(
            fill=tk.BOTH,
            expand=1,
            padx=3,
            pady=3)
    
    def _OnClosing(self) -> None:
        global asyncioThrd

        self.btn_url['state'] = tk.DISABLED
        self.txt_response['state'] = tk.NORMAL
        self.txt_response.insert(
            tk.END,
            'Closing the Async I/O event loop, please wait...\n')
        self.txt_response['state'] = tk.DISABLED
        asyncioThrd.close()
        self.after(
            80,
            self._CheckForExit)
    
    def _PostUrls(self) -> None:
        global reqQ

        nReqs = int(self.spn_number.get())
        for _ in range(nReqs):
            reqQ.put(
                ReqInfo(
                    self._id,
                    self.entry_url.get()))
        self.after(
            80,
            self._ShowStatusCode,
            self._id,
            nReqs)
    
    def _ShowStatusCode(self, id: int, n: int) -> None:
        global statusCodeQ

        self.txt_response['state'] = tk.NORMAL
        while n > 0:
            try:
                respInfo = statusCodeQ.get(block=True, timeout=0.05)
            except Empty:
                break
            if respInfo.id == id:
                self.txt_response.insert(
                    tk.END,
                    (
                        f'{respInfo.statusCode} was returned from'
                        + f' {respInfo.url}\n'
                    ))
                n -= 1
            else:
                statusCodeQ.put(respInfo)
        self.txt_response['state'] = tk.DISABLED
        if n > 0:
            self.after(
                80,
                self._ShowStatusCode,
                id,
                n)
    
    def _CheckForExit(self) -> None:
        global statusCodeQ
        global asyncioFinished

        if asyncioFinished.is_set() and statusCodeQ.empty():
            #showinfo()
            self.destroy()
        else:
            self.after(
                80,
                self._CheckForExit)


if __name__ == '__main__':
    # Creating the AsyncIO in a thread...
    asyncioThrd = UrlStatusCodeThrd(name='asyncioThrd')
    asyncioThrd.start()

    # Creating the GUI in the main thread...
    urlStatusCodeWin = UrlStatusCodeWin()
    urlStatusCodeWin.mainloop()
