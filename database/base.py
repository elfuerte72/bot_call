from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import load_config

# Создаем базовый класс для моделей
Base = declarative_base()

# Загружаем конфигурацию
config = load_config()

# Создаем асинхронный движок SQLAlchemy
# Замечание: для SQLite необходимо изменить URL для асинхронной работы
db_url = config.db.url
if db_url.startswith('sqlite:'):
    db_url = db_url.replace('sqlite:', 'sqlite+aiosqlite:')

engine = create_async_engine(db_url, echo=False)

# Создаем фабрику сессий
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_db():
    """
    Инициализирует базу данных, создавая все таблицы, если они не существуют
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



class AsyncSessionContextManager:
    """
    Класс контекстного менеджера для асинхронной сессии базы данных
    """

    def __init__(self):
        self.session = None

    async def __aenter__(self) -> AsyncSession:
        self.session = async_session()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()


def get_session():
    """
    Создает и возвращает контекстный менеджер для сессии базы данных

    Returns:
        AsyncSessionContextManager: контекстный менеджер для сессии
    """
    return AsyncSessionContextManager()
