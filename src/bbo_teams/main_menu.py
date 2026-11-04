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
from bbo_teams.bbo_session import get_session
from bbo_teams.constants import HELP_URI
from bbo_teams.data_store import get_match_data
from bbo_teams.forms.frm_config import ConfigFrame
from bbo_teams.state import state
from bbo_teams.text import Text

txt = Text()

SPACES = 30
SEPARATOR = "-" * 50


class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self.session = parent.session

    def create(self):
        menubar = tk.Menu()
        self.root["menu"] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label="File")

        # Data menu
        data_menu = Menu(menubar, self._data_menu_items())
        menubar.add_cascade(menu=data_menu, label="Data")

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label="Help")

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.CONFIG}{txt.ELLIPSIS}", self._show_config_frame),
            MenuItem(txt.CLOSE, self._dismiss),
        ]

    def _data_menu_items(self) -> list:
        return [
            MenuItem(f"Remove people{txt.ELLIPSIS}", self._remove_players),
            MenuItem(
                f"Remove deal files{txt.ELLIPSIS}", self._remove_deal_files
            ),
        ]

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)

    def _remove_players(self):
        """Remove people from the database."""
        result = messagebox.askyesno(
            "Remove Players",
            "Are you sure you want to remove the usernames from BBO?",
        )
        if result:
            match, errors = get_match_data(state.workbook)
            if errors:
                messagebox.showerror("Error", "\n".join(errors))
                return
            usernames = []
            for section in range(2):
                username = match.bbo_usernames[section]
                match.username = username
                match.password = match.bbo_passwords[section]
                if username not in usernames:
                    session = get_session(self.session)
                    session.remove_players(match)
                    session.close()
                    usernames.append(username)
            messagebox.showinfo(
                "Remove players",
                f"Players removed successfully for {', '.join(usernames)}",
            )

    def _remove_deal_files(self):
        """Remove deal files from the database."""
        result = messagebox.askyesno(
            "Remove Deal Files",
            "Are you sure you want to remove the deal files from BBO?",
        )
        if result:
            match, errors = get_match_data(state.workbook)
            if errors:
                messagebox.showerror("Error", "\n".join(errors))
                return
            usernames = []
            for section in range(2):
                username = match.bbo_usernames[section]
                match.username = username
                match.password = match.bbo_passwords[section]
                if username not in usernames:
                    session = get_session(self.session)
                    session.remove_deal_files(match)
                    session.close()
                    usernames.append(username)
            messagebox.showinfo(
                "Upload Deal Files",
                f"Deal files removed successfully for {', '.join(usernames)}",
            )

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.ONLINE_HELP}{txt.ELLIPSIS}", self._show_help),
            MenuItem(f"{txt.ABOUT}{txt.ELLIPSIS}", self._show_about),
        ]

    def _show_help(self):
        """Open online help in default browser."""
        if not HELP_URI:
            messagebox.showwarning("Help Error", "No online help available")
            return
        try:
            webbrowser.open(HELP_URI)
        except Exception as e:
            messagebox.showwarning(
                "Help Error", f"Could not open help page:\n{e}"
            )

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
