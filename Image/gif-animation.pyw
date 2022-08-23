from audioop import ratecv
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import PIL.Image
import PIL.ImageTk


# Defining of global variables...
_MODULE_DIR = Path(__file__).resolve().parent


class GifAnimationWin(tk.Tk):
    def __init__(
            self,
            res_dir: str | Path,
            screenName: str | None = None,
            baseName: str | None = None,
            className: str = 'Tk',
            useTk: bool = True,
            sync: bool = False,
            use: str | None = None
            ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.geometry('600x450+200+200')
        self.title('GIF animation')

        self._TIME_FRAME_RATE: int = 100
        """Specifies the frame rate of the GIF frames."""
        self._RES_DIR = res_dir
        self._frames: list[PIL.ImageTk.PhotoImage] = []

        # Resources...
        self._IMG_BROWSE: PIL.ImageTk.PhotoImage

        self._LoadRes()
        self._InitializeGui()
    
    def _LoadRes(self) -> None:
        # Loading images...
        # Loading 'browse.png'...
        self._IMG_BROWSE = self._RES_DIR / 'browse.png'
        self._IMG_BROWSE = PIL.Image.open(self._IMG_BROWSE)
        self._IMG_BROWSE = self._IMG_BROWSE.resize(size=(24, 24,))
        self._IMG_BROWSE = PIL.ImageTk.PhotoImage(image=self._IMG_BROWSE)
    
    def _InitializeGui(self) -> None:
        #
        self._frm_container = ttk.Frame(
            master=self)
        self._frm_container.columnconfigure(
            index=0,
            weight=1)
        self._frm_container.rowconfigure(
            index=1,
            weight=1)
        self._frm_container.pack(
            fill=tk.BOTH,
            expand=1)
        
        #
        self._frm_toolbar = ttk.Frame(
            master=self._frm_container)
        self._frm_toolbar.rowconfigure(
            index=0,
            weight=1)
        self._frm_toolbar.grid(
            column=0,
            row=0,
            sticky=tk.NW)
        
        #
        self._lbl_browse = ttk.Button(
            master=self._frm_toolbar,
            image=self._IMG_BROWSE,
            command=self._BrowseFiles)
        self._lbl_browse.grid(
            column=0,
            row=0,
            sticky=tk.W)
        
        #
        self._frm_gif = ttk.Frame(
            master=self._frm_container)
        self._frm_gif.columnconfigure(
            index=0,
            weight=1)
        self._frm_gif.rowconfigure(
            index=0,
            weight=1)
        self._frm_gif.grid(
            column=0,
            row=1,
            sticky=tk.NSEW)
        
        #
        self._lbl_gif = ttk.Label(
            master=self._frm_gif)
        self._lbl_gif.grid(
            column=0,
            row=0)
    
    def _BrowseFiles(self) -> None:
        gifFile = askopenfilename(
            title='Browse for GIF files',
            filetypes=[('GIF files', '*.gif')],
            initialdir=_MODULE_DIR)
        if gifFile:
            self._LoadGif(gifFile)
    
    def _LoadGif(self, gif_file: str) -> None:
        gifFile = PIL.Image.open(gif_file)
        self._frames.clear()
        frameRates: list[int] = []
        idx = 0
        while True:
            try:
                gifFile.seek(idx)
                self._frames.append(
                    PIL.ImageTk.PhotoImage(image=gifFile))
                frameRates.append(gifFile.info['duration'])
                idx += 1
            except KeyError:
                idx += 1
            except EOFError :
                break
        # Calculating the average frame rate...
        frameRates = [
            rate
            for rate in frameRates
            if rate]
        try:
            self._TIME_FRAME_RATE = round(sum(frameRates) / len(frameRates))
        except ZeroDivisionError:
            # Specifying the default frame rate...
            self._TIME_FRAME_RATE = 100
        # Animating the GIF...
        self.after(
            self._TIME_FRAME_RATE,
            self._AnimateGif,
            0)
    
    def _AnimateGif(self, frame_index: int) -> int:
        try:
            self._lbl_gif['image'] = self._frames[frame_index]
        except IndexError:
            frame_index = 0
            self._lbl_gif['image'] = self._frames[frame_index]
        self.after(
            self._TIME_FRAME_RATE,
            self._AnimateGif,
            frame_index + 1)

if __name__ == '__main__':
    gifAnimationWin = GifAnimationWin(
        res_dir=_MODULE_DIR / 'res')
    gifAnimationWin.mainloop()
