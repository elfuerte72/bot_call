from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from models.states import ClientAddingStates
from keyboards.dialog_keyboards import (
    get_cancel_keyboard,
    get_gender_keyboard,
    get_activity_level_keyboard,
    get_goal_keyboard,
    get_confirm_keyboard
)
from keyboards.main_menu import get_main_menu
from database.db_handlers import add_client
from services.nutrition import calculate_macros


# Создаем роутер для обработки диалога добавления клиента
router = Router()




# Активность и их множители для расчета КБЖУ
ACTIVITY_FACTORS = {
    "Минимальная активность": 1.2,
    "Низкая активность": 1.375,
    "Средняя активность": 1.55,
    "Высокая активность": 1.725,
    "Очень высокая активность": 1.9
}


# Обработчик для нажатия на кнопку "Добавить нового клиента"


@router.message(F.text == "Добавить нового клиента")
async def cmd_add_client(message: Message, state: FSMContext):
    """
    Обработчик начала процесса добавления клиента.

    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Переходим в состояние ожидания имени
    await state.set_state(ClientAddingStates.waiting_for_name)
    await message.answer(
        "Введите имя клиента:",
        reply_markup=get_cancel_keyboard()
    )



# Обработчик ввода имени клиента
@router.message(ClientAddingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """
    Обработчик ввода имени клиента.

    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем имя в данных состояния
    await state.update_data(name=message.text)
    # Переходим к запросу возраста
    await state.set_state(ClientAddingStates.waiting_for_age)
    await message.answer(
        "Введите возраст клиента (полных лет):",
        reply_markup=get_cancel_keyboard()
    )


# Обработчик ввода возраста клиента
@router.message(ClientAddingStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """
    Обработчик ввода возраста клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Проверяем, что возраст - это число в допустимом диапазоне
    age = message.text
    if (not age.isdigit() or int(age) <= 0 or int(age) > 120):
        await message.answer(
            "Пожалуйста, введите корректный возраст (положительное число от 1 до 120)."
        )
        return
    
    age = int(message.text)
    # Сохраняем возраст в данных состояния
    await state.update_data(age=age)
    # Переходим к запросу пола
    await state.set_state(ClientAddingStates.waiting_for_gender)
    await message.answer(
        "Выберите пол клиента:", 
        reply_markup=get_gender_keyboard()
    )


# Обработчик выбора пола клиента
@router.message(ClientAddingStates.waiting_for_gender, F.text.in_(["Мужской", "Женский"]))
async def process_gender(message: Message, state: FSMContext):
    """
    Обработчик выбора пола клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем пол в данных состояния
    await state.update_data(gender=message.text)
    # Переходим к запросу роста
    await state.set_state(ClientAddingStates.waiting_for_height)
    await message.answer(
        "Введите рост клиента в сантиметрах (например, 175):", 
        reply_markup=get_cancel_keyboard()
    )


# Обработчик ввода роста клиента
@router.message(ClientAddingStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """
    Обработчик ввода роста клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Проверяем, что рост - это число
    if not message.text.isdigit() or int(message.text) <= 0 or int(message.text) > 250:
        await message.answer(
            "Пожалуйста, введите корректный рост в сантиметрах (положительное число от 1 до 250)."
        )
        return
    
    height = int(message.text)
    # Сохраняем рост в данных состояния
    await state.update_data(height=height)
    # Переходим к запросу веса
    await state.set_state(ClientAddingStates.waiting_for_weight)
    await message.answer(
        "Введите вес клиента в килограммах (например, 70.5):", 
        reply_markup=get_cancel_keyboard()
    )


# Обработчик ввода веса клиента
@router.message(ClientAddingStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """
    Обработчик ввода веса клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Проверяем, что вес - это число (может быть с плавающей точкой)
    try:
        weight = float(message.text.replace(',', '.'))
        if weight <= 0 or weight > 300:
            raise ValueError("Вес должен быть положительным числом от 1 до 300")
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректный вес в килограммах (например, 70.5 или 70,5)."
        )
        return
    
    # Сохраняем вес в данных состояния
    await state.update_data(weight=weight)
    # Переходим к запросу уровня активности
    await state.set_state(ClientAddingStates.waiting_for_activity)
    await message.answer(
        "Выберите уровень активности клиента:", 
        reply_markup=get_activity_level_keyboard()
    )


# Обработчик выбора уровня активности клиента
@router.message(ClientAddingStates.waiting_for_activity, F.text.in_(ACTIVITY_FACTORS.keys()))
async def process_activity(message: Message, state: FSMContext):
    """
    Обработчик выбора уровня активности клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем уровень активности в данных состояния
    activity = message.text
    activity_factor = ACTIVITY_FACTORS[activity]
    await state.update_data(activity=activity, activity_factor=activity_factor)
    
    # Переходим к запросу цели
    await state.set_state(ClientAddingStates.waiting_for_goal)
    await message.answer(
        "Выберите цель клиента:", 
        reply_markup=get_goal_keyboard()
    )


# Обработчик выбора цели клиента
@router.message(ClientAddingStates.waiting_for_goal, F.text.in_(["Похудение", "Набор массы", "Поддержание веса"]))
async def process_goal(message: Message, state: FSMContext):
    """
    Обработчик выбора цели клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем цель в данных состояния
    goal = message.text
    await state.update_data(goal=goal)
    
    # Получаем все данные из состояния
    data = await state.get_data()
    
    # Рассчитываем КБЖУ по формуле Бенедикта
    macros = calculate_macros(
        gender=data['gender'], age=data['age'],
        height=data['height'], weight=data['weight'],
        activity_factor=data['activity_factor'],
        goal=data['goal']
    )
    
    # Сохраняем КБЖУ в данных состояния
    await state.update_data(macros=macros)
    
    # Формируем сообщение с данными клиента
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
    message_text = client_info + macros_info + confirm_msg
    
    # Переходим к подтверждению добавления клиента
    await state.set_state(ClientAddingStates.waiting_for_confirmation)
    await message.answer(
        message_text,
        reply_markup=get_confirm_keyboard()
    )


# Обработчик подтверждения добавления клиента
@router.message(ClientAddingStates.waiting_for_confirmation, F.text.in_(["Да", "Нет"]))
async def process_confirmation(message: Message, state: FSMContext):
    """
    Обработчик подтверждения добавления клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    if message.text == "Да":
        # Получаем все данные клиента
        data = await state.get_data()
        
        # Добавляем клиента в базу данных
        try:
            client_id = await add_client(
                name=data['name'],
                age=data['age'],
                gender=data['gender'],
                height=data['height'],
                weight=data['weight'],
                activity=data['activity'],
                goal=data['goal'],
                calories=data['macros']['calories'],
                protein=data['macros']['protein'],
                fat=data['macros']['fat'],
                carbs=data['macros']['carbs']
            )
            success_msg = (
                f"✅ Клиент {data['name']} успешно "
                f"добавлен в базу данных!\n"
                f"ID клиента: {client_id}"
            )
            await message.answer(
                success_msg,
                reply_markup=get_main_menu()
            )
        except Exception as e:
            error_msg = (
                f"❌ Ошибка при добавлении клиента: {str(e)}\n"
                "Попробуйте снова."
            )
            await message.answer(
                error_msg,
                reply_markup=get_main_menu()
            )
    else:
        await message.answer(
            "Отменено. Клиент не был добавлен.",
            reply_markup=get_main_menu()
        )
    # Очищаем состояние
    await state.clear()
