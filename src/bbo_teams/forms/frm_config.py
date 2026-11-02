# forms/frm_config.py
"""ConfigFrame for BBO Team setup.."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from psiutils.constants import PAD
from psiutils.utilities import restore_geometry, window_resize
from psiutils.widgets import clickable_widget

from bbo_teams import logger
from bbo_teams.buttons import ButtonFrame, IconButton
from bbo_teams.config import FIELDS, config, save_config
from bbo_teams.constants import APP_TITLE, DEFAULT_GEOMETRY
from bbo_teams.state import state
from bbo_teams.text import Text

txt = Text()


class ConfigFrame:
    """
    A configuration dialog for editing application settings.
    """

    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.dialog_opened = False
        self.save_button = None

        # Assign tk variables and check for changes
        config.assign_tk_variables(self, FIELDS, self._check_value_changed)

        self._show()

    def _show(self) -> None:
        """
        Initialize and display the configuration form GUI.
        """
        root = self.root
        restore_geometry(root, state, __file__, default=DEFAULT_GEOMETRY)
        root.transient(self.parent.root)
        root.title(f"{APP_TITLE} - {txt.CONFIG}")

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-s>", self._save_config)
        root.bind(
            "<Configure>",
            lambda e: window_resize(root, __file__, state),
        )

        # root.bind("<FocusIn>", self._set_config)

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        """
        Create and return the main frame containing form input widgets.
        """
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="BBO login url")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.login_url)
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        label = ttk.Label(frame, text="Teams directory")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.teams_directory)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(
            frame, txt.OPEN, "open-folder", self._get_teams_directory
        )
        button.grid(row=row, column=2, padx=PAD, pady=PAD)

        row += 1

        label = ttk.Label(frame, text="Deal directory")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.deal_directory)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(
            frame, txt.OPEN, "open-folder", self._get_data_directory
        )
        button.grid(row=row, column=2, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Boards per round")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        spinbox = ttk.Spinbox(
            frame,
            from_=1,
            to=28,
            increment=1,
            textvariable=self.boards_per_round,
        )
        spinbox.grid(row=row, column=1, sticky=tk.W, padx=PAD)
        clickable_widget(spinbox)

        row += 1
        label = ttk.Label(frame, text="Description text")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.description_text)
        entry.grid(row=row, column=1, sticky=tk.EW)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = self._frame_buttons(frame)
        self.save_button = frame.get_button("save")
        frame.disable()
        return frame

    def _frame_buttons(self, frame: ButtonFrame) -> list[IconButton]:
        return [
            frame.icon_button("save", self._save_config, True, tag="save"),
            frame.icon_button("exit", self._dismiss),
        ]

    def _check_value_changed(self, *args) -> bool:
        """
        Enable or disable form buttons based on changes in configuration.
        """
        enable = bool(self._config_changes())
        self.button_frame.enable(enable)

    def _get_data_directory(self, *args) -> None:
        directory = self._get_directory(self.deal_directory.get())
        if directory:
            self.deal_directory.set(directory)

    def _get_teams_directory(self, *args) -> None:
        directory = self._get_directory(self.teams_directory.get())
        if directory:
            self.teams_directory.set(directory)

    def _get_directory(self, default: str) -> str:
        """
        Prompt the user to select a new data directory and update the value.
        """
        self.dialog_opened = True
        return filedialog.askdirectory(
            initialdir=Path(default),
            parent=self.root,
        )

    def _save_config(self):
        changes = {
            field: f"(old value={change[0]}, new_value={change[1]})"
            for field, change in self._config_changes().items()
        }

        for field in FIELDS:
            config.update(field, getattr(self, field).get())

        save_config(config)
        logger.info("Config saved", changes=changes)
        self.save_button.disable()
        self._dismiss()

    def _config_changes(self) -> dict:
        stored = config.config
        return {
            field: (stored[field], getattr(self, field).get())
            for field in FIELDS
            if stored[field] != getattr(self, field).get()
        }

    def _set_config(self, *args) -> None:
        if self.dialog_opened:
            self.dialog_opened = False
            return
        for field in FIELDS:
            getattr(self, field).set(config.config[field])

    def _dismiss(self, *args) -> None:
        """
        Close the configuration window and terminate the application.
        """
        self.root.grab_release()
        self.root.destroy()
