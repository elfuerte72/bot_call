import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Класс с настройками бота"""
    token: str
    admin_id: int


@dataclass
class OpenAIConfig:
    """Класс с настройками OpenAI"""
    api_key: str


@dataclass
class DbConfig:
    """Класс с настройками базы данных"""
    url: str


@dataclass
class Config:
    """Общий класс конфигурации"""
    bot: BotConfig
    openai: OpenAIConfig
    db: DbConfig
    environment: str


def load_config() -> Config:
    """
    Загружает конфигурацию из переменных окружения
    
    Returns:
        Config: объект с настройками
    """
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    return Config(
        bot=BotConfig(
            token=os.getenv("BOT_TOKEN"),
            admin_id=int(os.getenv("ADMIN_USER_ID", 0))
        ),
        openai=OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        db=DbConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///database/fitness_bot.db")
        ),
        environment=os.getenv("ENVIRONMENT", "dev")
    )
