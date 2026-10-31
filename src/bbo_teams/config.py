# config.py

"""Config for BBO Team setup."""

from pathlib import Path

from psiconfig import ConfigField, TomlConfig

from bbo_teams.constants import CONFIG_PATH

# FIELDS for config, and to create tkinter variables in frm_config.py
# e.g. self.data_directory is a tk.StringVar
FIELDS = {
    "deal_directory": ConfigField(str, str(Path.home())),
    "teams_directory": ConfigField(str, str(Path.home())),
    "boards_per_round": ConfigField(int, 6),
    "description_text": ConfigField(str, "+private+ +slow+"),
}

DEFAULT_CONFIG = {}

for name, field in FIELDS.items():
    DEFAULT_CONFIG[name] = field.default_value


def read_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    return TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults,
    )


def save_config(updated_config: TomlConfig) -> TomlConfig | None:
    """Save the config file."""
    result = updated_config.save()
    if result != updated_config.STATUS_OK:
        return None
    return TomlConfig(CONFIG_PATH)


# Module-level singleton (TomlConfig) - this is the instance everyone imports.
config = read_config()
