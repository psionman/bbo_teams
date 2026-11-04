# main.py

"""
A tkinter application for BBO Team setup.
"""

import os
import sys
import tkinter as tk

from dotenv import load_dotenv
from psiutils.widgets import get_styles

from bbo_teams import __app_name__, __version__
from bbo_teams.constants import APP_TITLE, ICON_ICO, ICON_PNG
from bbo_teams.forms.frm_main import AppFrame
from bbo_teams.module_caller import ModuleCaller

load_dotenv()
if sys.platform == "linux":
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

PARSER_ARGS = (
    ("module", "Module to load"),
    ("project", "Project name"),
    ("secondary", "Secondary argument"),
)


def main() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)
    if sys.platform == "win32":
        root.iconbitmap(default=str(ICON_ICO))
    else:
        root.iconphoto(True, tk.PhotoImage(file=str(ICON_PNG)))

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


if __name__ == "__main__":
    if "--version" in sys.argv:
        print(f"{__app_name__}. Version: {__version__}")
        sys.exit(0)
    main()
