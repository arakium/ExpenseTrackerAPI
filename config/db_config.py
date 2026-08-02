"""Parses configuration files"""

from configparser import ConfigParser
from pathlib import Path


DB_CONFIG_FILE = Path(__file__).parent / "database.ini"
DB_CONFIG_SECTION='postgresql'

def database_config() -> dict[str, str]:
    """Parses config file for the database connection parameters"""
    parser = ConfigParser()
    if not parser.read(DB_CONFIG_FILE):
        raise FileNotFoundError(f"Configuration Error: Database configuration file not found: {DB_CONFIG_FILE}")
    if not parser.has_section(DB_CONFIG_SECTION):
        raise ValueError(f"Section '{DB_CONFIG_SECTION}' not found in {DB_CONFIG_FILE}")
    return dict(parser.items(DB_CONFIG_SECTION))