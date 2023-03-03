from pathlib import Path

from dotenv import load_dotenv

__version__ = "0.7.0"

if (env_file := Path(".env")).is_file():
    print(f"Loading settings from file {env_file.absolute()}")
    load_dotenv(env_file)
