from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from models.states import MealPlanStates
from keyboards.dialog_keyboards import get_cancel_keyboard, get_confirm_keyboard
from keyboards.main_menu import get_main_menu
from database.db_handlers import get_client_by_id, save_meal_plan
# Используем заглушку для тестирования
from services.meal_plan_stub import generate_meal_plan

# Создаем роутер для обработки создания плана питания
router = Router()

# Используется в handlers/client_list.py в функции create_meal_plan
# Мы переходим сюда после выбора клиента и нажатия на кнопку "Расписать план питания"

# Обработчик для запроса аллергий
@router.message(MealPlanStates.waiting_for_allergies)
async def process_allergies(message: Message, state: FSMContext):
    """
    Обработчик ввода аллергий клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем аллергии в данных состояния
    allergies = message.text if message.text != "Нет" else ""
    await state.update_data(allergies=allergies)
    
    # Переходим к запросу предпочтений
    await state.set_state(MealPlanStates.waiting_for_preferences)
    await message.answer(
        "Укажите предпочтения клиента в еде (например, любимые продукты или блюда).\n"
        "Если нет особых предпочтений, просто напишите 'Нет':",
        reply_markup=get_cancel_keyboard()
    )


# Обработчик для запроса предпочтений
@router.message(MealPlanStates.waiting_for_preferences)
async def process_preferences(message: Message, state: FSMContext):
    """
    Обработчик ввода предпочтений клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем предпочтения в данных состояния
    preferences = message.text if message.text != "Нет" else ""
    await state.update_data(preferences=preferences)
    
    # Переходим к запросу ограничений
    await state.set_state(MealPlanStates.waiting_for_limitations)
    await message.answer(
        "Укажите ограничения клиента (религиозные, диетические и т.д.).\n"
        "Если нет ограничений, просто напишите 'Нет':",
        reply_markup=get_cancel_keyboard()
    )


# Обработчик для запроса ограничений
@router.message(MealPlanStates.waiting_for_limitations)
async def process_limitations(message: Message, state: FSMContext):
    """
    Обработчик ввода ограничений клиента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Сохраняем ограничения в данных состояния
    limitations = message.text if message.text != "Нет" else ""
    await state.update_data(limitations=limitations)
    
    # Получаем все данные из состояния
    data = await state.get_data()
    
    # Формируем сообщение с параметрами для генерации плана питания
    message_text = (
        f"📋 Параметры для генерации плана питания:\n\n"
        f"👤 Клиент: {data['client_name']}\n"
        f"🧮 КБЖУ: {data['calories']} ккал / "
        f"Б:{data['protein']}г, Ж:{data['fat']}г, У:{data['carbs']}г\n"
        f"🎯 Цель: {data['goal']}\n\n"
    )
    
    if data.get('allergies'):
        message_text += f"⚠️ Аллергии: {data['allergies']}\n"
    else:
        message_text += "⚠️ Аллергии: нет\n"
    
    if data.get('preferences'):
        message_text += f"👍 Предпочтения: {data['preferences']}\n"
    else:
        message_text += "👍 Предпочтения: нет\n"
    
    if data.get('limitations'):
        message_text += f"🚫 Ограничения: {data['limitations']}\n\n"
    else:
        message_text += "🚫 Ограничения: нет\n\n"
    
    message_text += "Всё верно? Генерировать план питания?"
    
    # Переходим к подтверждению генерации плана
    await state.set_state(MealPlanStates.waiting_for_confirmation)
    await message.answer(
        message_text,
        reply_markup=get_confirm_keyboard()
    )


# Обработчик для подтверждения генерации плана питания
@router.message(MealPlanStates.waiting_for_confirmation, F.text.in_(["Да", "Нет"]))
async def process_confirmation(message: Message, state: FSMContext):
    """
    Обработчик подтверждения генерации плана питания.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    if message.text == "Да":
        # Получаем все данные из состояния
        data = await state.get_data()
        
        # Отправляем сообщение о начале генерации
        await message.answer(
            "⏳ Генерирую план питания, это может занять некоторое время...",
            reply_markup=None
        )
        
        try:
            # Генерируем план питания
            meal_plan = await generate_meal_plan(
                client_id=data['client_id'],
                calories=data['calories'],
                protein=data['protein'],
                fat=data['fat'],
                carbs=data['carbs'],
                goal=data['goal'],
                allergies=data.get('allergies', ''),
                preferences=data.get('preferences', ''),
                limitations=data.get('limitations', '')
            )
            
            # Отправляем сгенерированный план питания
            await message.answer(
                f"✅ План питания для клиента {data['client_name']} сгенерирован:\n\n{meal_plan}",
                reply_markup=get_main_menu()
            )
            
            # Спрашиваем, хочет ли пользователь сохранить план питания
            await state.set_state(MealPlanStates.waiting_for_save)
            await state.update_data(meal_plan=meal_plan)
            await message.answer(
                "Хотите сохранить этот план питания в базе данных?",
                reply_markup=get_confirm_keyboard()
            )
        except Exception as e:
            await message.answer(
                f"❌ Ошибка при генерации плана питания: {str(e)}\n"
                f"Попробуйте снова.",
                reply_markup=get_main_menu()
            )
            await state.clear()
    else:
        await message.answer(
            "Отменено. План питания не был сгенерирован.",
            reply_markup=get_main_menu()
        )
        await state.clear()


# Обработчик для подтверждения сохранения плана питания
@router.message(MealPlanStates.waiting_for_save, F.text.in_(["Да", "Нет"]))
async def process_save_confirmation(message: Message, state: FSMContext):
    """
    Обработчик подтверждения сохранения плана питания.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    if message.text == "Да":
        # Получаем все данные из состояния
        data = await state.get_data()
        
        try:
            # Сохраняем план питания в базе данных
            plan_id = await save_meal_plan(
                client_id=data['client_id'],
                content=data['meal_plan']
            )
            await message.answer(
                f"✅ План питания успешно сохранен в базе данных.\n"
                f"ID плана питания: {plan_id}",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            await message.answer(
                f"❌ Ошибка при сохранении плана питания: {str(e)}\n"
                f"Попробуйте снова.",
                reply_markup=get_main_menu()
            )
    else:
        await message.answer(
            "План питания не был сохранен в базе данных.",
            reply_markup=get_main_menu()
        )
    
    # Очищаем состояние
    await state.clear()
