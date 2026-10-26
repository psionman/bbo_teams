# forms/frm_main.py

"""AppFrame for BBO Team setup."""
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.utilities import restore_geometry, window_resize

from bbo_teams.buttons import ButtonFrame, IconButton
from bbo_teams.config import config
from bbo_teams.constants import APP_TITLE, DEFAULT_GEOMETRY
from bbo_teams.main_menu import MainMenu
from bbo_teams.state import state
from bbo_teams.text import Text


txt = Text()


class AppFrame():
    """Create AppFrame for BBO Team setup application."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        # tk variables
        # self.xxx = tk.StringVar()

        # Trace
        # self.xxx.trace_add('write', self._value_changed)

        self._show()

    def _show(self):
        root = self.root
        restore_geometry(root, state, __file__, default=DEFAULT_GEOMETRY)
        root.title(APP_TITLE)

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(column=0, sticky=tk.SE)

        root.update_idletasks()
        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-o>', self._process)
        root.bind(
            "<Configure>",
            lambda e: window_resize(root, __file__, state),
        )

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = self._frame_buttons(frame)
        frame.disable()
        return frame

    def _frame_buttons(self, frame: ButtonFrame) -> list[IconButton]:
        return [
            frame.icon_button("build", self._process),
            frame.icon_button("cancel", self._dismiss),
        ]

    def _value_changed(self, *args) -> bool:
        """
        Determine whether any configuration value has changed.
        """
        enable = (
            self.xxx.get() != config.xxx
        )
        self.button_frame.enable(enable)

    def _process(self, *args) -> None:
        pass

    def _dismiss(self, *args) -> None:
        self.root.destroy()
