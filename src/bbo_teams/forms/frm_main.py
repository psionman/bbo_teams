# forms/frm_main.py

"""AppFrame for BBO Team setup."""

import tkinter as tk
from tkinter import filedialog, ttk

from psiutils.constants import PAD, FileTypes
from psiutils.utilities import restore_geometry, window_resize

from bbo_teams.buttons import ButtonFrame, IconButton
from bbo_teams.config import config
from bbo_teams.constants import APP_TITLE, DEFAULT_GEOMETRY
from bbo_teams.data_store import get_match_data
from bbo_teams.main_menu import MainMenu
from bbo_teams.state import state
from bbo_teams.text import Text

txt = Text()
worksheet_path = (
    "/home/jeff/Documents/Bridge/NBC/20261013/NBC_BR_Tigers_20261013.xlsx"
)


class AppFrame:
    """Create AppFrame for BBO Team setup application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        # tk variables
        self.workbook_path = tk.StringVar(value="")
        self.club_name = tk.StringVar(value="")
        self.opponents_club_name = tk.StringVar(value="")
        self.match_date = tk.StringVar(value="")
        self.our_pairs_names = [tk.StringVar(value="") for _ in range(8)]
        self.our_pairs_usernames = [tk.StringVar(value="") for _ in range(8)]
        self.opps_pairs_names = [tk.StringVar(value="") for _ in range(8)]
        self.opps_pairs_usernames = [tk.StringVar(value="") for _ in range(8)]

        # Trace
        self.workbook_path.trace_add("write", self._value_changed)

        self._show()

        self._open_workbook(worksheet_path)

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
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(column=0, sticky=tk.SE)

        root.update_idletasks()
        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-o>", self._process)
        root.bind(
            "<Configure>",
            lambda e: window_resize(root, __file__, state),
        )

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="Teams workook")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.workbook_path)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, "open-folder", self._get_workbook)
        button.grid(row=row, column=2, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Club name")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Label(frame, textvariable=self.club_name, relief=tk.SUNKEN)
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        label = ttk.Label(frame, text="Opponent club name")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Label(
            frame, textvariable=self.opponents_club_name, relief=tk.SUNKEN
        )
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        label = ttk.Label(frame, text="Match date")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Label(
            frame, textvariable=self.match_date, relief=tk.SUNKEN
        )
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        players_frame = self._player_frame(frame)
        players_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW)

        row += 1
        frame.rowconfigure(row, weight=1)

        return frame

    def _player_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        row = 0
        players_frame = self._player_list_frame(
            frame,
            "Our players",
            self.our_pairs_names,
            self.our_pairs_usernames,
        )
        players_frame.grid(row=row, column=0, sticky=tk.EW)

        players_frame = self._player_list_frame(
            frame,
            "Opponent's players",
            self.opps_pairs_names,
            self.opps_pairs_usernames,
        )
        players_frame.grid(row=row, column=1, sticky=tk.EW)
        return frame

    def _player_list_frame(
        self,
        master: tk.Frame,
        heading: str,
        names_var: list[tk.StringVar],
        usernames_var: list[tk.StringVar],
    ) -> tk.Frame:
        frame = ttk.Frame(master, relief=tk.SUNKEN, borderwidth=2)

        row = 0
        label = ttk.Label(frame, text=heading)
        label.grid(row=row, column=0, columnspan=2, padx=PAD, pady=PAD)

        row += 1
        for i in range(8):
            label = ttk.Label(frame, textvariable=names_var[i])
            label.grid(row=row + i, column=0, sticky=tk.EW, padx=PAD)
            label = ttk.Label(frame, textvariable=usernames_var[i])
            label.grid(row=row + i, column=1, sticky=tk.EW)

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
        enable = self.workbook_path.get() != ""
        self.button_frame.enable(enable)

    def _get_workbook(self) -> str:
        initialdir = config.teams_directory
        path = filedialog.askopenfilename(
            parent=self.root,
            initialdir=initialdir,
            title="Select workbook:",
            filetypes=FileTypes.XLS.value,
        )
        self.workbook_path.set(path)
        if path:
            self._open_workbook(path)

    def _open_workbook(self, path: str) -> None:
        match = get_match_data(path)
        self.club_name.set(match.club_name)
        self.opponents_club_name.set(match.opponents_club_name)
        self.match_date.set(match.match_date.strftime("%d %B %Y"))

        # Populate our pairs
        for i, pair in enumerate(match.our_players):
            self.our_pairs_names[i * 2].set(pair.north_south.name)
            self.our_pairs_names[i * 2 + 1].set(pair.east_west.name)
            self.our_pairs_usernames[i * 2].set(pair.north_south.username)
            self.our_pairs_usernames[i * 2 + 1].set(pair.east_west.username)

        # Populate opponent pairs
        for i, pair in enumerate(match.opps_players):
            self.opps_pairs_names[i * 2].set(pair.north_south.name)
            self.opps_pairs_names[i * 2 + 1].set(pair.east_west.name)
            self.opps_pairs_usernames[i * 2].set(pair.north_south.username)
            self.opps_pairs_usernames[i * 2 + 1].set(pair.east_west.username)

    def _process(self, *args) -> None:
        pass

    def _dismiss(self, *args) -> None:
        self.root.destroy()
