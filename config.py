"""Utilities for loading bot configuration from JSON files.

The configuration file is expected to provide the bot token, the guild to
monitor, and identifiers for the logging channel and double-booster role.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class BotConfig:
    """Strongly-typed representation of the bot configuration."""

    token: str
    guild_id: int
    log_channel_id: int
    double_role_id: int


class ConfigError(RuntimeError):
    """Raised when the configuration file is missing required fields."""


REQUIRED_FIELDS = {"token", "guild_id", "log_channel_id", "double_role_id"}


def _validate_raw_config(raw_config: Dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS.difference(raw_config)
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise ConfigError(
            f"Configuration file is missing required field(s): {missing_fields}."
        )


def load_config(path: str = "config.json") -> BotConfig:
    """Load the bot configuration from the provided ``path``.

    Parameters
    ----------
    path:
        Path to the JSON configuration file.

    Returns
    -------
    BotConfig
        Parsed configuration data.
    """

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"Configuration file '{config_path}' does not exist."
        )

    with config_path.open("r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)

    _validate_raw_config(raw_config)

    return BotConfig(
        token=str(raw_config["token"]),
        guild_id=int(raw_config["guild_id"]),
        log_channel_id=int(raw_config["log_channel_id"]),
        double_role_id=int(raw_config["double_role_id"]),
    )
