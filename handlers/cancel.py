from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import get_main_menu

# Создаем роутер для обработки кнопки отмены
router = Router()


# Универсальный обработчик кнопки "Отмена"
@router.message(F.text == "Отмена")
async def universal_cancel_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик отмены любого процесса и возврата в главное меню.
    Работает со всеми FSM процессами: добавление клиента,
    редактирование, создание плана питания.

    Args:
        message: Объект сообщения от пользователя
        state: Контекст FSM
    """
    current_state = await state.get_state()
    if current_state is not None:
        # Сбрасываем состояние и данные
        await state.clear()
        await message.answer(
            "Действие отменено. Возвращаемся в главное меню.",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "Нечего отменять. Вы в главном меню.",
            reply_markup=get_main_menu()
        )
