# main_menu.py

"""Main menu for BBO Team setup."""

import tkinter as tk
import webbrowser
from tkinter import messagebox

from psiutils.menus import Menu, MenuItem

from bbo_teams import (
    __app_name__,
    __author__,
    __summary__,
    __version__,
)
from bbo_teams.config import config
from bbo_teams.constants import HELP_URI
from bbo_teams.forms.frm_config import ConfigFrame
from bbo_teams.text import Text

txt = Text()

SPACES = 30
SEPARATOR = "-" * 50


class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root

    def create(self):
        menubar = tk.Menu()
        self.root["menu"] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label="File")

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label="Help")

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.CONFIG}{txt.ELLIPSIS}", self._show_config_frame),
            MenuItem(txt.CLOSE, self._dismiss),
        ]

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.ONLINE_HELP}{txt.ELLIPSIS}", self._show_help),
            MenuItem(
                f"{txt.DATA_DIRECTORY} location{txt.ELLIPSIS}",
                self._show_data_directory,
            ),
            MenuItem(f"{txt.ABOUT}{txt.ELLIPSIS}", self._show_about),
        ]

    def _show_help(self):
        """Open online help in default browser."""
        try:
            webbrowser.open(HELP_URI)
        except Exception as e:
            messagebox.showwarning(
                "Help Error", f"Could not open help page:\n{e}"
            )

    def _show_data_directory(self):
        dir = f"{txt.DATA_DIRECTORY}: {str(config.data_directory):<{SPACES}}"
        messagebox.showinfo(title=txt.DATA_DIRECTORY, message=dir)

    def _show_about(self):
        about = (
            f"{__summary__}\n"
            f"{SEPARATOR}\n"
            f"{txt.VERSION}: {__version__}\n"
            f"{SEPARATOR}\n"
            f"{txt.AUTHOR}: {__author__:<{SPACES}}"
        )
        messagebox.showinfo(title=f"{txt.ABOUT} {__app_name__}", message=about)

    def _dismiss(self, *args):
        self.root.destroy()
