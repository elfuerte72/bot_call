"""
Тестовый скрипт для проверки интегрированного сервиса фитнес-бота
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

from services.fitness_bot_service import FitnessBotService


async def test_fitness_bot_service():
    """Тестирование интегрированного сервиса фитнес-бота"""
    print("Запуск тестирования интегрированного сервиса фитнес-бота...")
    
    # Инициализируем сервис
    service = FitnessBotService()
    
    # Инициализируем RAG-систему
    print("\nИнициализация RAG-системы...")
    await service.initialize_rag()
    
    # Тестируем расчет КБЖУ
    print("\nТестирование расчета КБЖУ:")
    
    test_profiles = [
        {
            "name": "Мужчина, 30 лет, набор массы",
            "gender": "мужской",
            "age": 30,
            "weight": 75.0,
            "height": 180.0,
            "activity_level": "средняя",
            "goal": "набор"
        },
        {
            "name": "Женщина, 25 лет, похудение",
            "gender": "женский",
            "age": 25,
            "weight": 65.0,
            "height": 165.0,
            "activity_level": "низкая",
            "goal": "похудение"
        }
    ]
    
    for profile in test_profiles:
        print(f"\nРасчет КБЖУ для профиля: {profile['name']}")
        kbju = await service.calculate_kbju(
            gender=profile["gender"],
            age=profile["age"],
            weight=profile["weight"],
            height=profile["height"],
            activity_level=profile["activity_level"],
            goal=profile["goal"]
        )
        print(f"Результат расчета КБЖУ: {kbju['kbju_str']}")
    
    # Тестируем генерацию плана питания
    print("\nТестирование генерации плана питания:")
    kbju_str = "2500 ккал, 150г белка, 80г жиров, 250г углеводов"
    goal = "набор мышечной массы"
    restrictions = "без лактозы, орехов и морепродуктов"
    
    print(f"КБЖУ: {kbju_str}")
    print(f"Цель: {goal}")
    print(f"Ограничения: {restrictions}")
    
    meal_plan = await service.generate_meal_plan(kbju_str, goal, restrictions)
    print("\nСгенерированный план питания:")
    
    # Ограничим вывод первыми 300 символами для краткости
    print(f"{meal_plan[:300]}...")
    
    # Тестируем ответы на вопросы через RAG-систему
    print("\nТестирование ответов на вопросы через RAG-систему:")
    
    test_questions = [
        "Какие продукты содержат много белка?",
        "Какова калорийность фруктов?",
        "Как рассчитать дневную норму калорий?"
    ]
    
    for question in test_questions:
        print(f"\nВопрос: {question}")
        answer = await service.answer_question(question)
        # Ограничим вывод первыми 200 символами для краткости
        print(f"Ответ: {answer[:200]}...")
    
    print("\nТестирование интегрированного сервиса фитнес-бота завершено успешно!")


if __name__ == "__main__":
    asyncio.run(test_fitness_bot_service())
