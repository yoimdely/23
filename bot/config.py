from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    bot_token: str = Field(
        default="8558081257:AAGMBIh2JcT93Ffczt5H82jxA5KX-2NdfLI",
        description="Telegram bot token",
    )
    admin_ids: List[int] = Field(default_factory=lambda: [298753135])
    documents_per_day_free: int = 1
    documents_per_day_pro: int = 50
    pro_price_rub: int = 499
    enable_logging: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_settings() -> Settings:
    return Settings()
