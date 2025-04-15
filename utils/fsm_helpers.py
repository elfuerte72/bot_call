"""
Модуль с вспомогательными функциями для работы с FSM (конечными автоматами).
Содержит общие обработчики для диалогов с пользователем.
"""
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.validators import validate_age, validate_height, validate_weight
from typing import Any, Callable, Optional


async def process_age_input(
        message: Message, 
        state: FSMContext, 
        next_state: Any, 
        current_field: str = "age", 
        keyboard_getter: Optional[Callable] = None
    ) -> bool:
    """
    Универсальный обработчик ввода возраста.
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
        next_state: Следующее состояние FSM
        current_field: Поле для хранения значения
        keyboard_getter: Функция для получения клавиатуры для следующего сообщения
        
    Returns:
        bool: True если валидация прошла успешно, иначе False
    """
    is_valid, age_value, error_msg = validate_age(message.text)
    if not is_valid:
        await message.answer(error_msg)
        return False
        
    await state.update_data({current_field: age_value})
    await state.set_state(next_state)
    
    # Если передана функция для получения клавиатуры, используем её
    if keyboard_getter:
        keyboard = keyboard_getter()
        await message.answer(
            "Выберите пол клиента:", 
            reply_markup=keyboard
        )
    return True


async def process_height_input(
        message: Message, 
        state: FSMContext, 
        next_state: Any, 
        current_field: str = "height", 
        keyboard_getter: Optional[Callable] = None,
        next_message: str = "Введите вес клиента (кг):"
    ) -> bool:
    """
    Универсальный обработчик ввода роста.
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
        next_state: Следующее состояние FSM
        current_field: Поле для хранения значения
        keyboard_getter: Функция для получения клавиатуры для следующего сообщения
        next_message: Текст следующего сообщения
        
    Returns:
        bool: True если валидация прошла успешно, иначе False
    """
    is_valid, height_value, error_msg = validate_height(message.text)
    if not is_valid:
        await message.answer(error_msg)
        return False
        
    await state.update_data({current_field: height_value})
    await state.set_state(next_state)
    
    # Если передана функция для получения клавиатуры, используем её
    if keyboard_getter:
        keyboard = keyboard_getter()
        await message.answer(next_message, reply_markup=keyboard)
    else:
        await message.answer(next_message)
    return True


async def process_weight_input(
        message: Message, 
        state: FSMContext, 
        next_state: Any, 
        current_field: str = "weight", 
        keyboard_getter: Optional[Callable] = None,
        next_message: str = "Выберите уровень активности клиента:"
    ) -> bool:
    """
    Универсальный обработчик ввода веса.
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
        next_state: Следующее состояние FSM
        current_field: Поле для хранения значения
        keyboard_getter: Функция для получения клавиатуры для следующего сообщения
        next_message: Текст следующего сообщения
        
    Returns:
        bool: True если валидация прошла успешно, иначе False
    """
    is_valid, weight_value, error_msg = validate_weight(message.text)
    if not is_valid:
        await message.answer(error_msg)
        return False
        
    await state.update_data({current_field: weight_value})
    await state.set_state(next_state)
    
    # Если передана функция для получения клавиатуры, используем её
    if keyboard_getter:
        keyboard = keyboard_getter()
        await message.answer(next_message, reply_markup=keyboard)
    else:
        await message.answer(next_message)
    return True


async def format_client_summary(data: dict, macros: dict) -> str:
    """
    Форматирует сводку данных клиента и КБЖУ.
    
    Args:
        data: Данные клиента
        macros: Рассчитанные макронутриенты
        
    Returns:
        str: Отформатированная строка с данными клиента
    """
    client_info = (
        f"📋 Данные клиента:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🎂 Возраст: {data['age']} лет\n"
        f"⚧ Пол: {data['gender']}\n"
        f"📏 Рост: {data['height']} см\n"
        f"⚖ Вес: {data['weight']} кг\n"
        f"🏃 Активность: {data['activity']}\n"
        f"🎯 Цель: {data['goal']}\n\n"
    )
    
    # Формируем сообщение с КБЖУ
    macros_info = (
        f"🧮 Рассчитанные КБЖУ:\n"
        f"🔥 Калории: {macros['calories']} ккал\n"
        f"🥩 Белки: {macros['protein']} г\n"
        f"🥑 Жиры: {macros['fat']} г\n"
        f"🍚 Углеводы: {macros['carbs']} г\n\n"
    )
    
    confirm_msg = "Всё верно? Добавить клиента в базу данных?"
    return client_info + macros_info + confirm_msg
