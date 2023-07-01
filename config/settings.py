
from pathlib import Path
from pydantic import BaseSettings

from yarl import URL

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):

    # test DB
    # test_postgres_host: str = "localhost"
    # test_postgres_port: int = 5432
    # test_postgres_user: str
    # test_postgres_password: str
    # test_postgres_db: str
    # test_postgres_echo: bool = False

    # postgres_db
    POSTGRES_PASS: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str
    POSTGRES_NAME: str

    # jwt settings
    JWT_SECRET_KEY: str
    jwt_algorithm: str = "HS256"
    jwt_expire: int = 30

    # infura ethereum node
    INFURA_API_URL: str
    INFURA_API_KEY: str

    # redis url
    REDIS_URL: str

    # etherscan
    ETHERSCAN_KEY: str

    # ASYNCAPI_DOCS_URL
    ASYNCAPI_DOCS_URL: str

    class Config:
        env_file = BASE_DIR / "local.env"

    @property
    def postgres_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.

        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASS,
            path=f"/{self.POSTGRES_NAME}",
        )


settings = Settings()
