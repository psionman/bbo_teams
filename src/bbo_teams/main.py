# main.py

"""
 A tkinter application for BBO Team setup.
"""
import os
import sys
import argparse
import tkinter as tk
import clipboard
from dotenv import load_dotenv

from psiutils.widgets import get_styles
from psiutils.utilities import display_icon

from bbo_teams import __version__, logger, __app_name__
from bbo_teams.constants import ICON_FILE, APP_TITLE
from bbo_teams.module_caller import ModuleCaller

from forms.frm_main import AppFrame

from bbo_teams import logger

load_dotenv()
uv_python = os.getenv('UV_PYTHON')
if not uv_python:
    print(f"Have you run export UV_PYTHON=/usr/bin/python3?"
           f" - copied to clipboard")
    clipboard.copy('export UV_PYTHON=/usr/bin/python3')


PARSER_ARGS = (
    ("module", "Module to load"),
    ("project", "Project name"),
    ("secondary", "Secondary argument"),
)

def main() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)
    display_icon(root, ICON_FILE, ignore_error=True)

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    get_styles()

    if PARSER_ARGS:
        args = ModuleCaller.create_parser(PARSER_ARGS)
        if args.module:
            try:
                ModuleCaller(root, args)
            except Exception:
                root.destroy()
        else:
            AppFrame(root)

    root.mainloop()


if __name__ == '__main__':
    if "--version" in sys.argv:
        print(f"{__app_name__}. Version: {__version__}")
        sys.exit(0)
    main()
