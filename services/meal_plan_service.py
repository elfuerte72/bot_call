"""
Модуль с сервисами для генерации плана питания.
Содержит абстрактный класс и реализации для разных способов генерации.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.logger import log_meal_plan, log_error


class MealPlanGenerator(ABC):
    """Абстрактный класс для генераторов плана питания."""
    
    @abstractmethod
    async def generate_plan(self, client_data: Dict[str, Any]) -> str:
        """
        Генерирует план питания на основе данных клиента.
        
        Args:
            client_data: Данные клиента и параметры для генерации
            
        Returns:
            str: Текст плана питания
        """
        pass


class StubMealPlanGenerator(MealPlanGenerator):
    """Заглушка генератора плана питания для тестирования."""
    
    async def generate_plan(self, client_data: Dict[str, Any]) -> str:
        """
        Генерирует тестовый план питания.
        
        Args:
            client_data: Данные клиента и параметры для генерации
            
        Returns:
            str: Текст плана питания (заглушка)
        """
        log_meal_plan(
            client_data['client_id'], 
            client_data['client_name'], 
            "генерация (заглушка)", 
            f"КБЖУ: {client_data['calories']} ккал"
        )
        
        return (
            f"🍽 ПЛАН ПИТАНИЯ НА ДЕНЬ (ТЕСТОВЫЙ РЕЖИМ) 🍽\n\n"
            f"🧮 КБЖУ: {client_data['calories']} ккал / "
            f"Б:{client_data['protein']}г, Ж:{client_data['fat']}г, У:{client_data['carbs']}г\n\n"
            f"🥞 ЗАВТРАК (около 25% дневных калорий):\n"
            f"- Овсянка на воде/молоке - 200г\n"
            f"- Яйца - 2шт\n"
            f"- Фрукты - 100г\n\n"
            f"🍎 ПЕРЕКУС:\n"
            f"- Творог 5% - 150г\n"
            f"- Орехи - 20г\n\n"
            f"🍲 ОБЕД (около 35% дневных калорий):\n"
            f"- Куриная грудка - 150г\n"
            f"- Бурый рис - 100г\n"
            f"- Овощной салат - 150г\n\n"
            f"🍌 ПЕРЕКУС:\n"
            f"- Протеиновый коктейль - 1 порция\n"
            f"- Банан - 1шт\n\n"
            f"🍗 УЖИН (около 25% дневных калорий):\n"
            f"- Рыба запеченная - 150г\n"
            f"- Овощи на пару - 200г\n"
            f"- Сложные углеводы - 50г\n\n"
            f"🍵 ПОЗДНИЙ ПЕРЕКУС (при необходимости):\n"
            f"- Кефир 1% - 200мл\n"
            f"- Белковый продукт - на выбор\n\n"
            f"💧 Не забывайте пить воду - не менее 30мл на 1кг веса тела.\n\n"
            f"⚠️ Это тестовый план питания. В реальной версии будет "
            f"индивидуальная подборка продуктов с учетом предпочтений и ограничений."
        )


class GPTMealPlanGenerator(MealPlanGenerator):
    """Генератор плана питания на основе OpenAI GPT."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация генератора.
        
        Args:
            api_key: API ключ для OpenAI
        """
        self.api_key = api_key
    
    async def generate_plan(self, client_data: Dict[str, Any]) -> str:
        """
        Генерирует план питания с использованием OpenAI GPT.
        
        Args:
            client_data: Данные клиента и параметры для генерации
            
        Returns:
            str: Текст плана питания
        """
        try:
            log_meal_plan(
                client_data['client_id'], 
                client_data['client_name'], 
                "запрос к GPT", 
                f"КБЖУ: {client_data['calories']} ккал"
            )
            
            # В реальной реализации здесь будет запрос к OpenAI API
            # Пока используем заглушку
            return await StubMealPlanGenerator().generate_plan(client_data)
        except Exception as e:
            log_error("meal_plan_service", "GPTMealPlanGenerator.generate_plan", e)
            raise ValueError(f"Ошибка при генерации плана питания: {str(e)}")


class RAGMealPlanGenerator(MealPlanGenerator):
    """Генератор плана питания на основе RAG (Retrieval Augmented Generation)."""
    
    def __init__(self, api_key: Optional[str] = None, data_path: str = "data/nutrition"):
        """
        Инициализация генератора.
        
        Args:
            api_key: API ключ для OpenAI
            data_path: Путь к данным для RAG-системы
        """
        self.api_key = api_key
        self.data_path = data_path
    
    async def generate_plan(self, client_data: Dict[str, Any]) -> str:
        """
        Генерирует план питания с использованием RAG-системы.
        
        Args:
            client_data: Данные клиента и параметры для генерации
            
        Returns:
            str: Текст плана питания
        """
        try:
            log_meal_plan(
                client_data['client_id'], 
                client_data['client_name'], 
                "запрос к RAG", 
                f"КБЖУ: {client_data['calories']} ккал"
            )
            
            # В реальной реализации здесь будет использование RAG-системы
            # Пока используем заглушку
            return await StubMealPlanGenerator().generate_plan(client_data)
        except Exception as e:
            log_error("meal_plan_service", "RAGMealPlanGenerator.generate_plan", e)
            raise ValueError(f"Ошибка при генерации плана питания: {str(e)}")


async def generate_meal_plan(
        client_id: int,
        client_name: str,
        calories: int,
        protein: int,
        fat: int,
        carbs: int,
        goal: str,
        allergies: str = "",
        preferences: str = "",
        limitations: str = "",
        use_gpt: bool = False,
        use_rag: bool = False
    ) -> str:
    """
    Фасад для генерации плана питания с выбором подходящего генератора.
    
    Args:
        client_id: ID клиента
        client_name: Имя клиента
        calories: Калории
        protein: Белки
        fat: Жиры
        carbs: Углеводы
        goal: Цель
        allergies: Аллергии
        preferences: Предпочтения
        limitations: Ограничения
        use_gpt: Использовать GPT
        use_rag: Использовать RAG
        
    Returns:
        str: Текст плана питания
    """
    client_data = {
        'client_id': client_id,
        'client_name': client_name,
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs,
        'goal': goal,
        'allergies': allergies,
        'preferences': preferences,
        'limitations': limitations
    }
    
    try:
        # Выбираем генератор в зависимости от параметров
        if use_rag:
            generator = RAGMealPlanGenerator()
        elif use_gpt:
            generator = GPTMealPlanGenerator()
        else:
            generator = StubMealPlanGenerator()
        
        # Генерируем план
        plan = await generator.generate_plan(client_data)
        
        # Логируем успешную генерацию
        log_meal_plan(
            client_id, 
            client_name, 
            "успешная генерация", 
            f"Размер плана: {len(plan)} символов"
        )
        
        return plan
    except Exception as e:
        log_error("meal_plan_service", "generate_meal_plan", e)
        raise ValueError(f"Ошибка при генерации плана питания: {str(e)}")
