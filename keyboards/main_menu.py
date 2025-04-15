from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Создает главное меню бота с кнопками.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками главного меню
    """
    # Создаем кнопки
    add_client_btn = KeyboardButton(text="Добавить нового клиента")
    client_list_btn = KeyboardButton(text="Список клиентов")
    
    # Формируем клавиатуру из кнопок
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [add_client_btn],
            [client_list_btn],
        ],
        resize_keyboard=True,  # Уменьшаем размер кнопок до размера текста
        input_field_placeholder="Выберите действие"  # Подсказка в поле ввода
    )
    
    return keyboard
