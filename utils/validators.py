"""
Модуль для валидации данных пользователя.
Содержит функции для проверки корректности ввода возраста, роста, веса и других параметров.
"""
from typing import Tuple, Union


def validate_age(age_str: str) -> Tuple[bool, int, str]:
    """
    Валидация возраста.
    
    Args:
        age_str: Строка с возрастом для проверки
        
    Returns:
        Tuple[bool, int, str]: Тройка (успех, значение, сообщение об ошибке)
    """
    if not age_str.isdigit() or int(age_str) <= 0 or int(age_str) > 120:
        return False, 0, "Пожалуйста, введите корректный возраст (число от 1 до 120)"
    return True, int(age_str), ""


def validate_height(height_str: str) -> Tuple[bool, float, str]:
    """
    Валидация роста.
    
    Args:
        height_str: Строка с ростом для проверки
        
    Returns:
        Tuple[bool, float, str]: Тройка (успех, значение, сообщение об ошибке)
    """
    try:
        height = float(height_str.replace(',', '.'))
        if height <= 0 or height > 250:
            return False, 0, "Пожалуйста, введите корректный рост (число от 1 до 250 см)"
        return True, height, ""
    except ValueError:
        return False, 0, "Пожалуйста, введите корректное число для роста"


def validate_weight(weight_str: str) -> Tuple[bool, float, str]:
    """
    Валидация веса.
    
    Args:
        weight_str: Строка с весом для проверки
        
    Returns:
        Tuple[bool, float, str]: Тройка (успех, значение, сообщение об ошибке)
    """
    try:
        weight = float(weight_str.replace(',', '.'))
        if weight <= 0 or weight > 300:
            return False, 0, "Пожалуйста, введите корректный вес (число от 1 до 300 кг)"
        return True, weight, ""
    except ValueError:
        return False, 0, "Пожалуйста, введите корректное число для веса"


def validate_input(value: str, validator_func) -> Tuple[bool, Union[int, float], str]:
    """
    Общая функция валидации различных типов ввода.
    
    Args:
        value: Значение для проверки
        validator_func: Функция-валидатор
        
    Returns:
        Tuple[bool, Union[int, float], str]: Тройка (успех, значение, сообщение об ошибке)
    """
    return validator_func(value)
