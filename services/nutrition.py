from typing import Dict, Literal

# Отображение текстовых значений уровней активности на ключи для расчета
ACTIVITY_MAPPING = {
    "Минимальная активность": "minimal",
    "Низкая активность": "low",
    "Средняя активность": "medium",
    "Высокая активность": "high",
    "Очень высокая активность": "very_high"
}

# Отображение текстовых значений целей на ключи для расчета
GOAL_MAPPING = {
    "Похудение": "loss",
    "Набор массы": "gain",
    "Поддержание веса": "maintenance"
}


class NutritionCalculator:
    """Класс для расчета КБЖУ и планов питания"""

    # Коэффициенты для разных уровней активности
    ACTIVITY_LEVELS = {
        "minimal": 1.2,  # Минимальная активность
        "low": 1.375,    # Низкая активность
        "medium": 1.55,  # Средняя активность
        "high": 1.725,   # Высокая активность
        "very_high": 1.9  # Очень высокая активность
    }

    # Коэффициенты для разных целей
    GOAL_MODIFIERS = {
        "loss": 0.85,     # Снижение веса
        "maintenance": 1.0,  # Поддержание веса
        "gain": 1.15       # Набор веса
    }

    # Соотношение БЖУ для разных целей
    MACRO_RATIOS = {
        "loss": {"protein": 0.3, "fat": 0.3, "carbs": 0.4},
        "maintenance": {"protein": 0.25, "fat": 0.25, "carbs": 0.5},
        "gain": {"protein": 0.2, "fat": 0.2, "carbs": 0.6}
    }
    
    @staticmethod
    def calculate_bmr(
        gender: Literal["мужской", "женский"],
        weight: float,
        height: float,
        age: int
    ) -> float:
        """
        Расчет базового метаболизма (BMR) по формуле Бенедикта

        Args:
            gender: Пол ('мужской' или 'женский')
            weight: Вес в кг
            height: Рост в см
            age: Возраст в годах

        Returns:
            Базовый метаболизм в калориях
        """
        if gender == "мужской":
            # Формула для мужчин: 66 + (13.7 × вес) + (5 × рост) - (6.8 × возраст)
            return 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
        else:
            # Формула для женщин: 655 + (9.6 × вес) + (1.8 × рост) - (4.7 × возраст)
            return 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)

    @classmethod
    def calculate_tdee(
        cls,
        gender: Literal["мужской", "женский"],
        weight: float,
        height: float,
        age: int,
        activity_level: str,
        goal: str
    ) -> Dict[str, float]:
        """
        Рассчитывает полное потребление энергии в день (TDEE) и КБЖУ

        Args:
            gender: Пол ('мужской' или 'женский')
            weight: Вес в кг
            height: Рост в см
            age: Возраст в годах
            activity_level: Уровень активности
            goal: Цель ('loss', 'maintenance', 'gain')

        Returns:
            Словарь с расчетными значениями КБЖУ:
            - calories: Калории
            - protein: Белки в граммах
            - fat: Жиры в граммах
            - carbs: Углеводы в граммах
        """
        # Проверяем валидность входных параметров
        if activity_level not in cls.ACTIVITY_LEVELS:
            raise ValueError(f"Неверный уровень активности: {activity_level}")

        if goal not in cls.GOAL_MODIFIERS:
            raise ValueError(f"Неверная цель: {goal}")

        # Рассчитываем базовый метаболизм
        bmr = cls.calculate_bmr(gender, weight, height, age)

        # Рассчитываем TDEE с учетом активности и цели
        activity_factor = cls.ACTIVITY_LEVELS[activity_level]
        goal_factor = cls.GOAL_MODIFIERS[goal]

        tdee = bmr * activity_factor * goal_factor

        # Рассчитываем количество макронутриентов
        macro_ratio = cls.MACRO_RATIOS[goal]

        # Белки: 4 калории на грамм
        protein_calories = tdee * macro_ratio["protein"]
        protein_grams = protein_calories / 4

        # Жиры: 9 калорий на грамм
        fat_calories = tdee * macro_ratio["fat"]
        fat_grams = fat_calories / 9

        # Углеводы: 4 калории на грамм
        carb_calories = tdee * macro_ratio["carbs"]
        carb_grams = carb_calories / 4

        # Округляем значения для удобства
        return {
            "calories": round(tdee),
            "protein": round(protein_grams),
            "fat": round(fat_grams),
            "carbs": round(carb_grams)
        }
    
    @staticmethod
    def format_nutrition_info(nutrition_data: Dict[str, float]) -> str:
        """
        Форматирует информацию о КБЖУ для отображения

        Args:
            nutrition_data: Словарь с данными КБЖУ

        Returns:
            Отформатированная строка с КБЖУ
        """
        return (
            f"📊 КБЖУ:\n"
            f"🔥 Калории: {nutrition_data['calories']} ккал\n"
            f"🥩 Белки: {nutrition_data['protein']} г\n"
            f"🧈 Жиры: {nutrition_data['fat']} г\n"
            f"🍚 Углеводы: {nutrition_data['carbs']} г"
        )


# Функция-обертка для удобства использования в обработчиках
def calculate_macros(
    gender: str,
    age: int,
    height: float,
    weight: float,
    activity_factor: float,
    goal: str
) -> Dict[str, float]:
    """
    Рассчитывает КБЖУ на основе данных клиента
    
    Args:
        gender: Пол клиента ("Мужской" или "Женский")
        age: Возраст клиента в годах
        height: Рост клиента в см
        weight: Вес клиента в кг
        activity_factor: Коэффициент активности (число от 1.2 до 1.9)
        goal: Цель ("Похудение", "Набор массы", "Поддержание веса")
    
    Returns:
        Словарь с расчетными значениями КБЖУ:
        - calories: Калории
        - protein: Белки в граммах
        - fat: Жиры в граммах
        - carbs: Углеводы в граммах
    """
    # Преобразуем текстовые значения пола и цели в формат для калькулятора
    gender_normalized = "мужской" if gender == "Мужской" else "женский"
    
    # Определяем ключ цели для расчета
    goal_key = GOAL_MAPPING.get(goal, "maintenance")
    
    # Ищем ближайший уровень активности по коэффициенту
    activity_key = "medium"  # Значение по умолчанию
    min_diff = float('inf')
    
    for level, factor in NutritionCalculator.ACTIVITY_LEVELS.items():
        diff = abs(factor - activity_factor)
        if diff < min_diff:
            min_diff = diff
            activity_key = level
    
    # Рассчитываем КБЖУ с помощью калькулятора питания
    return NutritionCalculator.calculate_tdee(
        gender=gender_normalized,
        weight=weight,
        height=height,
        age=age,
        activity_level=activity_key,
        goal=goal_key
    )
