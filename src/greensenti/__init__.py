from pathlib import Path

from dotenv import load_dotenv

env_file = Path(".env")
if env_file.is_file():
    print(f"⚙️ Loading settings from dotenv @ {env_file.absolute()}")
    load_dotenv(".env")