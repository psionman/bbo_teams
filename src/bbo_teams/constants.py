# constants.py

"""Constants for BBO Team setup."""

from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_state_dir
from psiutils.known_paths import resolve_path

from bbo_teams import __app_name__, __author__

# General
HTML_DIR = resolve_path("html", __file__)
HELP_URI = ""

# Paths
CONFIG_PATH = Path(user_config_dir(__app_name__, __author__), "config.toml")
USER_DATA_DIR = Path(user_data_dir(__app_name__, __author__))
USER_DATA_DIR.mkdir(exist_ok=True)
USER_DATA_FILE = Path(USER_DATA_DIR, "data.json")
STATE_DIR = user_state_dir(__app_name__, __author__)
HOME = str(Path.home())
ICON_DIR = f"{Path(__file__).parent}/assets/icons/"
ICON_PNG = Path(ICON_DIR, "games-config-board.png")
ICON_ICO = Path(ICON_DIR, "games-config-board.ico")

# Buttons and text
PSIUTILS_DIR = user_data_dir("psiutils", __author__)
BUTTONS_DIR = Path(PSIUTILS_DIR, "buttons")
BUTTON_ICON_PATH = str(Path(BUTTONS_DIR, "icons"))
BUTTON_CONFIG_PATH = str(Path(BUTTONS_DIR, "buttons.json"))
TEXT_FILE = Path(PSIUTILS_DIR, "text", "text.json")

# GUI
APP_TITLE = "BBO Team setup"
DEFAULT_GEOMETRY = "300x250"
