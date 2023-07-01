
from pathlib import Path
from pydantic import BaseSettings

from yarl import URL

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):

    # test DB
    test_postgres_host: str = "localhost"
    test_postgres_port: int = 5432
    test_postgres_user: str
    test_postgres_password: str
    test_postgres_db: str
    test_postgres_echo: bool = False

    # postgres_db
    postgres_pass: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_user: str
    postgres_name: str

    # jwt settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire: int = 30

    @property
    def postgres_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.

        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.postgres_host,
            port=self.postgres_port,
            user=self.postgres_user,
            password=self.postgres_pass,
            path=f"/{self.postgres_name}",
        )


settings = Settings()
