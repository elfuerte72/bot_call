from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Импортируем клавиатуру главного меню
from keyboards.main_menu import get_main_menu

# Создаем роутер для команды /start
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start

    Args:
        message: Объект сообщения от пользователя
    """
    user_full_name = message.from_user.full_name
    await message.answer(
        f"Привет, {user_full_name}! 👋\n\n"
        f"Я бот-помощник для фитнес-тренеров. Я помогу тебе вести базу "
        f"клиентов, рассчитывать КБЖУ и составлять планы питания.\n\n"
        f"Используйте кнопки ниже для работы с ботом:",
        reply_markup=get_main_menu()
    )



@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help

    Args:
        message: Объект сообщения от пользователя
    """
    await message.answer(
        "🤖 Бот для фитнес-тренеров\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "/about - Информация о боте"
    )

@router.message(Command("about"))
async def cmd_about(message: Message):
    """
    Обработчик команды /about

    Args:
        message: Объект сообщения от пользователя
    """
    await message.answer(
        "📋 О боте\n\n"
        "Этот бот помогает фитнес-тренерам вести клиентов, рассчитывать КБЖУ "
        "и составлять индивидуальные планы питания с использованием GPT.\n\n"
        "Бот использует формулу Бенедикта для расчета КБЖУ и современные "
        "технологии поиска информации для составления планов питания."
    )
