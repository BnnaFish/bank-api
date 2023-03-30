import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apischema import deserialize
from pyhocon import ConfigFactory


@dataclass(frozen=True)
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    schema: str


def config_factory(
    folder: str = "settings",
    section: str | None = None,
) -> dict[str, Any]:
    """Parsing hocon config from the given folder for the given section in file."""
    package_dir = Path(folder)
    env = os.getenv("ENV", "default")
    conf_path = package_dir / f"{env}.conf"
    fallback_conf_path = package_dir / "default.conf"
    factory = ConfigFactory.parse_file(conf_path)
    factory = factory.with_fallback(fallback_conf_path)
    return factory.get_config(section or "config")


database_config = deserialize(
    DatabaseConfig,
    config_factory(folder="settings", section="database"),
    coerce=True,
)
