from aiogram import Router, Dispatcher
from handlers.start import router as start_router
from handlers.cancel import router as cancel_router
from handlers.client_adding import router as client_adding_router
from handlers.client_list import router as client_list_router
from handlers.meal_plan import router as meal_plan_router


# Функция для регистрации всех обработчиков
def register_all_handlers(dp: Dispatcher):
    """
    Регистрирует все обработчики команд бота

    Args:
        dp: Объект диспетчера
    """
    # Создаем корневой роутер
    root_router = Router()

    # Подключаем все роутеры
    root_router.include_router(start_router)

    # Подключаем универсальный обработчик отмены (с высоким приоритетом)
    root_router.include_router(cancel_router)

    # Подключаем роутеры для работы с клиентами и планами питания
    root_router.include_router(client_adding_router)
    root_router.include_router(client_list_router)
    root_router.include_router(meal_plan_router)

    # Включаем корневой роутер в диспетчер
    dp.include_router(root_router)