import json
from typing import Dict, List, Any, Optional
from config.config import load_config
from rag.engine import RAGEngine


class MealPlanGenerator:
    """Класс для генерации планов питания с использованием OpenAI и RAG"""
    
    def __init__(self):
        """Инициализирует генератор планов питания"""
        self.config = load_config()
        self.rag_engine = RAGEngine()
    
    async def initialize(self):
        """Инициализирует RAG-систему"""
        await self.rag_engine.initialize()
    
    async def generate_meal_plan(
        self,
        calories: float,
        protein: float,
        fat: float, 
        carbs: float,
        restrictions: List[Dict[str, Any]] = None,
        preferences: Optional[str] = None
    ) -> str:
        """
        Генерирует план питания на день с учетом КБЖУ и ограничений
        
        Args:
            calories: Целевое количество калорий
            protein: Целевое количество белка в граммах
            fat: Целевое количество жира в граммах
            carbs: Целевое количество углеводов в граммах
            restrictions: Список ограничений (аллергии, религиозные ограничения и т.д.)
            preferences: Предпочтения по продуктам и блюдам
            
        Returns:
            План питания в текстовом формате
        """
        # Форматируем ограничения для запроса
        restrictions_text = ""
        if restrictions:
            for r in restrictions:
                restrictions_text += f"\n- {r['restriction_type']}: {r['description']}"
        
        preferences_text = f"\nПредпочтения: {preferences}" if preferences else ""
        
        # Составляем запрос для OpenAI
        prompt = f"""
        Создай план питания на один день с учетом следующих параметров:
        
        КБЖУ:
        - Калории: {calories} ккал
        - Белки: {protein} г
        - Жиры: {fat} г
        - Углеводы: {carbs} г
        
        Ограничения:{restrictions_text}{preferences_text}
        
        План должен включать завтрак, обед, ужин и 1-2 перекуса. Для каждого приема пищи укажи:
        1. Название блюда
        2. Примерный состав ингредиентов с указанием граммовки
        3. КБЖУ для каждого приема пищи
        
        Старайся использовать доступные продукты. Примерно распредели КБЖУ между приемами пищи.
        Дай практичный и реализуемый план питания, учитывая все ограничения.
        """
        
        # Используем RAG для генерации ответа
        response = await self.rag_engine.generate_answer(prompt)
        
        return response
    
    async def generate_example_meal(
        self,
        meal_type: str,
        calories: float,
        protein: float,
        fat: float,
        carbs: float,
        restrictions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Генерирует пример одного приема пищи (например, только завтрак)
        
        Args:
            meal_type: Тип приема пищи ('завтрак', 'обед', 'ужин', 'перекус')
            calories: Количество калорий для этого приема пищи
            protein: Количество белка в граммах
            fat: Количество жира в граммах
            carbs: Количество углеводов в граммах
            restrictions: Список ограничений
            
        Returns:
            Описание приема пищи
        """
        # Форматируем ограничения для запроса
        restrictions_text = ""
        if restrictions:
            for r in restrictions:
                restrictions_text += f"\n- {r['restriction_type']}: {r['description']}"
        
        # Составляем запрос для OpenAI
        prompt = f"""
        Создай пример {meal_type}а с учетом следующих параметров:
        
        КБЖУ для {meal_type}а:
        - Калории: {calories} ккал
        - Белки: {protein} г
        - Жиры: {fat} г
        - Углеводы: {carbs} г
        
        Ограничения:{restrictions_text}
        
        Укажи:
        1. Название блюда
        2. Примерный состав ингредиентов с указанием граммовки
        3. КБЖУ блюда
        
        Старайся использовать доступные продукты и давать практичные рецепты.
        """
        
        # Используем RAG для генерации ответа
        response = await self.rag_engine.generate_answer(prompt)
        
        return response
