import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import load_config
from database.base import init_db
from handlers import register_all_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Основная функция запуска бота
    """
    # Загрузка конфигурации
    config = load_config()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.bot.token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Инициализация базы данных
    await init_db()
    logger.info("База данных инициализирована")
    
    # Регистрация роутеров
    register_all_handlers(dp)
    logger.info("Обработчики зарегистрированы")
    
    # Пропуск накопившихся апдейтов
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        logger.info("Бот запущен")
        # Запуск поллинга
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Бот остановлен")
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Выход из бота")
