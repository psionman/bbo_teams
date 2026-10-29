# forms/frm_main.py

"""AppFrame for BBO Team setup."""

import os
import tkinter as tk
from tkinter import filedialog, ttk

from psiutils.constants import PAD, FileTypes
from psiutils.utilities import restore_geometry, window_resize

from bbo_teams.buttons import ButtonFrame, IconButton
from bbo_teams.config import config
from bbo_teams.constants import APP_TITLE, DEFAULT_GEOMETRY
from bbo_teams.data_store import get_match_data
from bbo_teams.main_menu import MainMenu
from bbo_teams.models import OPPS_SEAT_PLANS, Team
from bbo_teams.seat_teams import BboSession
from bbo_teams.state import state
from bbo_teams.text import Text

txt = Text()
WORKBOOK_PATH = (
    "/home/jeff/Documents/Bridge/NBC/20261013/NBC_BR_Tigers_20261013.xlsx"
)

OUR_TEAM = 0
OPPONENTS_TEAM = 1


class AppFrame:
    """Create AppFrame for BBO Team setup application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.our_pairs = []
        self.opps_pairs = []
        self.match = None

        # tk variables
        self.workbook_path = tk.StringVar(value="")
        self.club_name = tk.StringVar(value="")
        self.opponents_club_name = tk.StringVar(value="")
        self.match_date = tk.StringVar(value="")
        self.boards_per_round = tk.StringVar(
            value=str(config.boards_per_round)
        )
        self.our_pairs_names = [tk.StringVar(value="") for _ in range(8)]
        self.our_pairs_usernames = [tk.StringVar(value="") for _ in range(8)]
        self.opps_pairs_names = [tk.StringVar(value="") for _ in range(8)]
        self.opps_pairs_usernames = [tk.StringVar(value="") for _ in range(8)]
        self.round_number = tk.IntVar()
        self.round_display = tk.IntVar()
        self.section_number = tk.IntVar()
        self.section_display = tk.IntVar()
        self.deal_file_display = tk.StringVar(value="")
        self.section_seats_N = [tk.StringVar(value="") for team in range(2)]
        self.section_seats_S = [tk.StringVar(value="") for team in range(2)]
        self.section_seats_E = [tk.StringVar(value="") for team in range(2)]
        self.section_seats_W = [tk.StringVar(value="") for team in range(2)]

        # Trace
        self.workbook_path.trace_add("write", self._value_changed)

        self._show()

        # TODO: Remove this in production
        self.workbook_path.set(WORKBOOK_PATH)
        self._open_workbook(WORKBOOK_PATH)
        # self.round_number.set(random.randint(0, 5))
        # self.section_number.set(random.randint(0, 1))
        # self._process()

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

    def _main_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
        frame.columnconfigure(0, weight=1)

        row = 0
        header_frame = self._header_frame(frame)
        header_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW)

        row += 1
        players_frame = self._player_frame(frame)
        players_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW)

        row += 1
        round_number_frame = self._round_number_frame(frame)
        round_number_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW)

        row += 1
        round_display_frame = self._round_display_frame(frame)
        round_display_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW)

        row += 1
        round_seats_frame = self._round_seats_holder(frame)
        round_seats_frame.grid(row=row, column=0, sticky=tk.EW)

        row += 1
        frame.rowconfigure(row, weight=1)

        return frame

    def _header_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
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
        label = ttk.Label(frame, text="Rounds per board")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Label(
            frame, textvariable=self.boards_per_round, relief=tk.SUNKEN
        )
        entry.grid(row=row, column=1, sticky=tk.EW)

        return frame

    def _player_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
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
        frame = tk.Frame(master, relief=tk.SUNKEN, borderwidth=2)

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

    def _round_number_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
        frame.columnconfigure(0, weight=1)

        row = 0
        column = 0
        label = ttk.Label(frame, text="Round number")
        label.grid(row=row, column=column, sticky=tk.E, padx=PAD, pady=PAD)
        column += 1
        for round in range(4):
            button = ttk.Radiobutton(
                frame,
                text=round + 1,
                variable=self.round_number,
                value=round,
                command=self._on_round_number_change,
            )
            button.grid(
                row=row, column=column, sticky=tk.W, padx=PAD, pady=PAD
            )
            column += 1

        column += 1
        label = ttk.Label(frame, text="Section number")
        label.grid(row=row, column=column, sticky=tk.E, padx=PAD, pady=PAD)
        column += 1
        for section in range(2):
            button = ttk.Radiobutton(
                frame,
                text=section + 1,
                variable=self.section_number,
                value=section,
                command=self._on_round_number_change,
            )
            button.grid(
                row=row, column=column, sticky=tk.W, padx=PAD, pady=PAD
            )
            column += 1

        row += 1
        column += 1
        frame.columnconfigure(column, weight=1)

        return frame

    def _round_display_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
        frame.columnconfigure(0, weight=1)

        row = 0
        column = 1
        label = ttk.Label(frame, text="Round", font=("Arial", 16))
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        label = ttk.Label(
            frame,
            textvariable=self.round_display,
            font=("Arial", 16),
            style="red-fg.TLabel",
        )
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        label = ttk.Label(frame, text="Section", font=("Arial", 16))
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        label = ttk.Label(
            frame,
            textvariable=self.section_display,
            font=("Arial", 16),
            style="red-fg.TLabel",
        )
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        label = ttk.Label(frame, text="Deal file", font=("Arial", 16))
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        label = ttk.Label(
            frame,
            textvariable=self.deal_file_display,
            font=("Arial", 16),
            style="red-fg.TLabel",
        )
        label.grid(row=row, column=column, padx=PAD, pady=PAD)

        column += 1
        frame.columnconfigure(column, weight=1)
        return frame

    def _round_seats_holder(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        row = 0
        column = 1
        round_seats_frame = self._round_seats_frame(frame, OUR_TEAM)
        round_seats_frame.grid(row=row, column=column, sticky=tk.EW)

        column += 1
        round_seats_frame = self._round_seats_frame(frame, OPPONENTS_TEAM)
        round_seats_frame.grid(row=row, column=column, sticky=tk.EW)

        column += 1
        frame.columnconfigure(column, weight=1)
        return frame

    def _round_seats_frame(self, master: tk.Frame, team: int) -> tk.Frame:
        frame = tk.Frame(master, relief=tk.SUNKEN, borderwidth=2)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, textvariable=self.section_seats_N[team])
        label.grid(row=row, column=0, columnspan=2, padx=PAD, pady=PAD)

        row += 1
        label = ttk.Label(frame, textvariable=self.section_seats_E[team])
        label.grid(row=row, column=0, padx=PAD, pady=PAD)

        label = ttk.Label(frame, textvariable=self.section_seats_W[team])
        label.grid(row=row, column=1, padx=PAD, pady=PAD)

        row += 1
        label = ttk.Label(frame, textvariable=self.section_seats_S[team])
        label.grid(row=row, column=0, columnspan=2, padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = self._frame_buttons(frame)
        frame.disable()
        return frame

    def _frame_buttons(self, frame: ButtonFrame) -> list[IconButton]:
        return [
            frame.icon_button("build", self._process, True),
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
        self.match = match
        self.club_name.set(match.club_name)
        self.opponents_club_name.set(match.opponents_club_name)
        self.match_date.set(match.match_date.strftime("%d %B %Y"))
        self.our_pairs = match.our_pairs
        self.opps_pairs = match.opps_pairs

        # Populate our pairs
        for i, pair in enumerate(match.our_pairs):
            self.our_pairs_names[i * 2].set(pair.player_a.name)
            self.our_pairs_names[i * 2 + 1].set(pair.player_b.name)
            self.our_pairs_usernames[i * 2].set(pair.player_a.username)
            self.our_pairs_usernames[i * 2 + 1].set(pair.player_b.username)

        # Populate opponent pairs
        for i, pair in enumerate(match.opps_pairs):
            self.opps_pairs_names[i * 2].set(pair.player_a.name)
            self.opps_pairs_names[i * 2 + 1].set(pair.player_b.name)
            self.opps_pairs_usernames[i * 2].set(pair.player_a.username)
            self.opps_pairs_usernames[i * 2 + 1].set(pair.player_b.username)

        self.deal_files = match.deal_files
        self.boards_per_round.set(match.boards_per_round)

        self._on_round_number_change()

    def _on_round_number_change(self) -> None:
        self.round_display.set(self.round_number.get() + 1)
        self.section_display.set(self.section_number.get() + 1)
        section = self.section_number.get()
        self.section_seats_N[OUR_TEAM].set(
            self.our_pairs[0 + section * 2].player_a.username
        )
        self.section_seats_S[OUR_TEAM].set(
            self.our_pairs[0 + section * 2].player_b.username
        )
        self.section_seats_E[OUR_TEAM].set(
            self.our_pairs[1 + section * 2].player_a.username
        )
        self.section_seats_W[OUR_TEAM].set(
            self.our_pairs[1 + section * 2].player_b.username
        )

        # Set opponent seats based on seat plan
        # The opps pair number comes fomr the seat plan
        round = self.round_number.get()
        seat_plan = OPPS_SEAT_PLANS[round][section]
        self.section_seats_N[OPPONENTS_TEAM].set(
            self.opps_pairs[seat_plan[0]].player_a.username
        )
        self.section_seats_S[OPPONENTS_TEAM].set(
            self.opps_pairs[seat_plan[0]].player_b.username
        )
        self.section_seats_E[OPPONENTS_TEAM].set(
            self.opps_pairs[seat_plan[1]].player_a.username
        )
        self.section_seats_W[OPPONENTS_TEAM].set(
            self.opps_pairs[seat_plan[1]].player_b.username
        )
        self.deal_file_display.set(self.deal_files[round])

    def _process(self, *args) -> None:
        match = self.match
        match.round = self.round_number.get() + 1
        match.section = self.section_number.get() + 1
        match.deal_file = self.deal_files[self.round_number.get()]
        match.description_text = config.description_text
        match.our_team = Team(
            north=self.section_seats_N[OUR_TEAM].get(),
            south=self.section_seats_S[OUR_TEAM].get(),
            east=self.section_seats_E[OUR_TEAM].get(),
            west=self.section_seats_W[OUR_TEAM].get(),
        )
        match.opps_team = Team(
            north=self.section_seats_N[OPPONENTS_TEAM].get(),
            south=self.section_seats_S[OPPONENTS_TEAM].get(),
            east=self.section_seats_E[OPPONENTS_TEAM].get(),
            west=self.section_seats_W[OPPONENTS_TEAM].get(),
        )

        if True:  # TODO remove for production
            session = BboSession()
            session.login(
                os.environ["BBO_USERNAME"], os.environ["BBO_PASSWORD"]
            )
            session.seat_teams(match)

    def _dismiss(self, *args) -> None:
        self.root.destroy()
