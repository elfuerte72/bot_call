from aiogram.fsm.state import State, StatesGroup

class ClientAddingStates(StatesGroup):
    """
    Группа состояний для процесса добавления нового клиента.
    """
    waiting_for_name = State()         # Ожидание ввода имени
    waiting_for_age = State()          # Ожидание ввода возраста
    waiting_for_gender = State()       # Ожидание выбора пола
    waiting_for_height = State()       # Ожидание ввода роста
    waiting_for_weight = State()       # Ожидание ввода веса
    waiting_for_activity = State()     # Ожидание выбора уровня активности
    waiting_for_goal = State()         # Ожидание выбора цели
    waiting_for_confirmation = State() # Ожидание подтверждения добавления клиента


class ClientEditingStates(StatesGroup):
    """
    Группа состояний для процесса редактирования клиента.
    """
    waiting_for_field = State()        # Ожидание выбора поля для редактирования
    waiting_for_name = State()         # Ожидание ввода нового имени
    waiting_for_age = State()          # Ожидание ввода нового возраста
    waiting_for_gender = State()       # Ожидание выбора нового пола
    waiting_for_height = State()       # Ожидание ввода нового роста
    waiting_for_weight = State()       # Ожидание ввода нового веса
    waiting_for_activity = State()     # Ожидание выбора нового уровня активности
    waiting_for_goal = State()         # Ожидание выбора новой цели
    waiting_for_confirmation = State() # Ожидание подтверждения изменений


class MealPlanStates(StatesGroup):
    """
    Группа состояний для процесса создания плана питания.
    """
    waiting_for_allergies = State()    # Ожидание ввода аллергий
    waiting_for_preferences = State()  # Ожидание ввода предпочтений
    waiting_for_limitations = State()  # Ожидание ввода ограничений (религиозных и др.)
    waiting_for_confirmation = State() # Ожидание подтверждения генерации плана
    waiting_for_save = State()         # Ожидание подтверждения сохранения плана
