"""
Тестовый скрипт для проверки работы с OpenAI API
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в системный путь
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Загружаем переменные окружения
load_dotenv()

from services.openai_service import OpenAIService

async def test_openai_service():
    """Тестирование сервиса OpenAI"""
    print("Запуск тестирования OpenAI сервиса...")
    
    # Инициализируем сервис OpenAI
    openai_service = OpenAIService()
    
    # Тест генерации плана питания
    kbju = "2000 ккал, 150г белка, 50г жиров, 220г углеводов"
    goal = "набор мышечной массы"
    restrictions = "без лактозы, орехов и морепродуктов"
    
    print(f"\n1. Тест генерации плана питания")
    print(f"КБЖУ: {kbju}")
    print(f"Цель: {goal}")
    print(f"Ограничения: {restrictions}")
    
    meal_plan = await openai_service.generate_meal_plan(kbju, goal, restrictions)
    print("\nРезультат генерации плана питания:")
    print(meal_plan)
    
    # Тест ответа на вопрос
    question = "Какие продукты лучше употреблять после тренировки для восстановления мышц?"
    
    print(f"\n2. Тест ответа на вопрос")
    print(f"Вопрос: {question}")
    
    answer = await openai_service.answer_question(question)
    print("\nРезультат ответа на вопрос:")
    print(answer)
    
    print("\nТестирование OpenAI сервиса завершено успешно!")

if __name__ == "__main__":
    asyncio.run(test_openai_service())
