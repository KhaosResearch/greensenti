from pydantic import BaseSettings as PydanticBaseSettings

__all__ = ("BaseSettings",)


class BaseSettings(PydanticBaseSettings):

    dhus_host: str = "https://scihub.copernicus.eu/dhus"
    dhus_username: str = ""
    dhus_password: str = ""

    class Config:
        env_file = ".env"
        fields = {
            "dhus_host": {"env": "DHUS_HOST"},
            "dhus_username": {"env": "DHUS_USERNAME"},
            "dhus_password": {"env": "DHUS_PASSWORD"},
        }
