from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой отмены.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопкой отмены
    """
    cancel_btn = KeyboardButton(text="Отмена")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[cancel_btn]],
        resize_keyboard=True
    )
    return keyboard


def get_gender_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для выбора пола.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками выбора пола
    """
    male_btn = KeyboardButton(text="Мужской")
    female_btn = KeyboardButton(text="Женский")
    cancel_btn = KeyboardButton(text="Отмена")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [male_btn, female_btn],
            [cancel_btn]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_activity_level_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для выбора уровня активности.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками выбора уровня активности
    """
    minimal_btn = KeyboardButton(text="Минимальная активность")
    low_btn = KeyboardButton(text="Низкая активность")
    medium_btn = KeyboardButton(text="Средняя активность")
    high_btn = KeyboardButton(text="Высокая активность")
    very_high_btn = KeyboardButton(text="Очень высокая активность")
    cancel_btn = KeyboardButton(text="Отмена")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [minimal_btn],
            [low_btn],
            [medium_btn],
            [high_btn],
            [very_high_btn],
            [cancel_btn]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_goal_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для выбора цели.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками выбора цели
    """
    weight_loss_btn = KeyboardButton(text="Похудение")
    weight_gain_btn = KeyboardButton(text="Набор массы")
    weight_maintain_btn = KeyboardButton(text="Поддержание веса")
    cancel_btn = KeyboardButton(text="Отмена")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [weight_loss_btn],
            [weight_gain_btn],
            [weight_maintain_btn],
            [cancel_btn]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_client_actions_keyboard(client_id: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с действиями для клиента.

    Args:
        client_id: ID клиента

    Returns:
        InlineKeyboardMarkup: Объект инлайн-клавиатуры с кнопками действий
    """
    edit_btn = InlineKeyboardButton(text="Редактировать", callback_data=f"edit_client:{client_id}")
    delete_btn = InlineKeyboardButton(text="Удалить", callback_data=f"delete_client:{client_id}")
    meal_plan_btn = InlineKeyboardButton(text="Расписать план питания", callback_data=f"meal_plan:{client_id}")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [edit_btn],
            [delete_btn],
            [meal_plan_btn]
        ]
    )
    return keyboard


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения действия.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками подтверждения
    """
    yes_btn = KeyboardButton(text="Да")
    no_btn = KeyboardButton(text="Нет")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[yes_btn, no_btn]],
        resize_keyboard=True
    )
    return keyboard
