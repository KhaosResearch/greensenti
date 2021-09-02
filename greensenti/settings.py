from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for greensenti.
    """

    DHUS_HOST: str = "https://scihub.copernicus.eu/dhus"
    DHUS_USERNAME: str = ""
    DHUS_PASSWORD: str = ""

    MINIO_HOST: str = ""
    MINIO_PORT: int = 8090
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "minio"

    class Config:
        env_file = ".env"


settings = Settings()
