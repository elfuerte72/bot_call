from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models.states import ClientEditingStates, MealPlanStates
from keyboards.dialog_keyboards import get_client_actions_keyboard, get_confirm_keyboard, get_cancel_keyboard
from keyboards.main_menu import get_main_menu
from database.db_handlers import get_clients, get_client_by_id, delete_client

# Создаем роутер для обработки работы со списком клиентов
router = Router()

# Обработчик для нажатия на кнопку "Список клиентов"
@router.message(F.text == "Список клиентов")
async def cmd_client_list(message: Message):
    """
    Обработчик отображения списка клиентов.

    Args:
        message: Объект сообщения от пользователя
    """
    # Получаем список всех клиентов
    clients = await get_clients()

    if not clients:
        await message.answer(
            "У вас пока нет ни одного клиента. "
            "Вы можете добавить нового клиента с помощью соответствующей кнопки.",
            reply_markup=get_main_menu()
        )
        return

    # Формируем сообщение со списком клиентов
    message_text = "📋 Список клиентов:\n\n"

    for client in clients:
        message_text += (
            f"👤 {client.name} (ID: {client.id})\n"
            f"🔥 КБЖУ: {client.calories} ккал / "
            f"Б:{client.protein}г, Ж:{client.fat}г, У:{client.carbs}г\n"
            f"🎯 Цель: {client.goal}\n\n"
        )

    message_text += "Для просмотра детальной информации по клиенту, отправьте его ID (например, 1)."

    await message.answer(
        message_text,
        reply_markup=get_main_menu()
    )


# Обработчик для выбора клиента по ID
@router.message(lambda message: message.text.isdigit())
async def show_client_details(message: Message):
    """
    Обработчик отображения детальной информации по клиенту.

    Args:
        message: Объект сообщения от пользователя с ID клиента
    """
    client_id = int(message.text)
    client = await get_client_by_id(client_id)

    if not client:
        await message.answer(
            f"Клиент с ID {client_id} не найден.",
            reply_markup=get_main_menu()
        )
        return

    # Формируем сообщение с детальной информацией о клиенте
    message_text = (
        f"📋 Детальная информация по клиенту:\n\n"
        f"👤 Имя: {client.name}\n"
        f"🆔 ID: {client.id}\n"
        f"🎂 Возраст: {client.age} лет\n"
        f"⚧ Пол: {client.gender}\n"
        f"📏 Рост: {client.height} см\n"
        f"⚖ Вес: {client.weight} кг\n"
        f"🏃 Активность: {client.activity}\n"
        f"🎯 Цель: {client.goal}\n\n"
        f"🧮 КБЖУ:\n"
        f"🔥 Калории: {client.calories} ккал\n"
        f"🥩 Белки: {client.protein} г\n"
        f"🥑 Жиры: {client.fat} г\n"
        f"🍚 Углеводы: {client.carbs} г\n"
    )

    # Отправляем информацию и клавиатуру с кнопками действий
    await message.answer(
        message_text,
        reply_markup=get_client_actions_keyboard(client_id)
    )


# Обработчик для нажатия на кнопку "Редактировать"
@router.callback_query(F.data.startswith("edit_client:"))
async def edit_client(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик начала процесса редактирования клиента.

    Args:
        callback: Объект callback запроса
        state: Контекст FSM
    """
    # Извлекаем ID клиента из данных колбэка
    client_id = int(callback.data.split(":")[1])
    
    # Получаем информацию о клиенте
    client = await get_client_by_id(client_id)
    
    if not client:
        await callback.answer("Клиент не найден")
        await callback.message.edit_text(
            "Клиент не найден. Возможно, он был удален.",
            reply_markup=None
        )
        return

    # Сохраняем ID клиента в состоянии
    await state.update_data(client_id=client_id)
    
    # Отправляем сообщение с предложением выбрать поле для редактирования
    # (Можно добавить инлайн-клавиатуру с выбором полей)
    await callback.message.answer(
        f"Редактирование клиента: {client.name}\n\n"
        f"Пока эта функция находится в разработке. "
        f"Она будет доступна в следующих версиях."
    )
    
    # Отвечаем на колбэк, чтобы убрать загрузку на кнопке
    await callback.answer()


# Обработчик для нажатия на кнопку "Удалить"
@router.callback_query(F.data.startswith("delete_client:"))
async def delete_client_request(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик запроса на удаление клиента.

    Args:
        callback: Объект callback запроса
        state: Контекст FSM
    """
    # Извлекаем ID клиента из данных колбэка
    client_id = int(callback.data.split(":")[1])
    
    # Получаем информацию о клиенте
    client = await get_client_by_id(client_id)
    
    if not client:
        await callback.answer("Клиент не найден")
        await callback.message.edit_text(
            "Клиент не найден. Возможно, он был удален.",
            reply_markup=None
        )
        return
    
    # Сохраняем ID клиента в состоянии
    await state.update_data(client_id=client_id)
    
    # Запрашиваем подтверждение удаления
    await callback.message.answer(
        f"Вы уверены, что хотите удалить клиента '{client.name}'?\n"
        f"Это действие нельзя отменить.",
        reply_markup=get_confirm_keyboard()
    )
    
    # Отвечаем на колбэк, чтобы убрать загрузку на кнопке
    await callback.answer()


# Обработчик для подтверждения удаления клиента
@router.message(F.text.in_(["Да", "Нет"]))
async def confirm_delete_client(message: Message, state: FSMContext):
    """
    Обработчик подтверждения удаления клиента.

    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    # Получаем данные из состояния
    data = await state.get_data()
    client_id = data.get("client_id")
    
    # Если ID клиента не найден в состоянии, это не запрос на подтверждение удаления
    if not client_id:
        return
    
    if message.text == "Да":
        try:
            # Удаляем клиента из базы данных
            result = await delete_client(client_id)
            if result:
                await message.answer(
                    "✅ Клиент успешно удален.",
                    reply_markup=get_main_menu()
                )
            else:
                await message.answer(
                    "❌ Не удалось удалить клиента. Пожалуйста, попробуйте снова.",
                    reply_markup=get_main_menu()
                )
        except Exception as e:
            await message.answer(
                f"❌ Ошибка при удалении клиента: {str(e)}",
                reply_markup=get_main_menu()
            )
    else:
        await message.answer(
            "Отменено. Клиент не был удален.",
            reply_markup=get_main_menu()
        )
    
    # Очищаем состояние
    await state.clear()


# Обработчик для нажатия на кнопку "Расписать план питания"
@router.callback_query(F.data.startswith("meal_plan:"))
async def create_meal_plan(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик запроса на создание плана питания.

    Args:
        callback: Объект callback запроса
        state: Контекст FSM
    """
    # Извлекаем ID клиента из данных колбэка
    client_id = int(callback.data.split(":")[1])
    
    # Получаем информацию о клиенте
    client = await get_client_by_id(client_id)
    
    if not client:
        await callback.answer("Клиент не найден")
        await callback.message.edit_text(
            "Клиент не найден. Возможно, он был удален.",
            reply_markup=None
        )
        return
    
    # Сохраняем ID клиента и данные о КБЖУ в состоянии
    await state.update_data(
        client_id=client_id,
        client_name=client.name,
        calories=client.calories,
        protein=client.protein,
        fat=client.fat,
        carbs=client.carbs,
        goal=client.goal
    )
    
    # Устанавливаем начальное состояние для FSM создания плана питания
    await state.set_state(MealPlanStates.waiting_for_allergies)
    
    # Отправляем сообщение с предложением указать аллергии
    await callback.message.answer(
        f"Создание плана питания для клиента: {client.name}\n"
        f"КБЖУ: {client.calories} ккал / "
        f"Б:{client.protein}г, Ж:{client.fat}г, У:{client.carbs}г\n\n"
        f"Укажите аллергии клиента (на какие продукты).\n"
        f"Если аллергий нет, просто напишите 'Нет':",
        reply_markup=get_cancel_keyboard()
    )
    
    # Отвечаем на колбэк, чтобы убрать загрузку на кнопке
    await callback.answer()
