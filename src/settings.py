from pydantic import BaseSettings


class WebsocketsConfig(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 18000
