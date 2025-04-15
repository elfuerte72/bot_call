"""
Тест для проверки интеграции с OpenAI и работы RAG-системы
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в путь для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ai_service import AIService
from rag.engine import RAGEngine


async def test_rag_initialization():
    """Тестирование инициализации RAG-системы"""
    print("Тест 1: Инициализация RAG-системы")
    
    # Создаем RAG-движок
    rag_engine = RAGEngine()
    
    # Инициализируем с перезагрузкой документов
    await rag_engine.initialize(force_reload=True)
    
    print("RAG-система успешно инициализирована\n")


async def test_rag_search():
    """Тестирование поиска в RAG-системе"""
    print("Тест 2: Поиск в RAG-системе")
    
    # Создаем RAG-движок
    rag_engine = RAGEngine()
    
    # Инициализируем без перезагрузки документов
    await rag_engine.initialize(force_reload=False)
    
    # Выполняем тестовый поиск
    test_query = "Какие продукты богаты белком?"
    docs = await rag_engine.search(test_query, k=3)
    
    print(f"Найдено {len(docs)} релевантных документов для запроса '{test_query}'")
    for i, doc in enumerate(docs, 1):
        print(f"\nДокумент {i}:")
        print(f"Источник: {doc.metadata.get('source', 'Неизвестно')}")
        print(f"Содержание (первые 150 символов): {doc.page_content[:150]}...")
    
    print("\n")


async def test_ai_service():
    """Тестирование сервиса интеграции с OpenAI"""
    print("Тест 3: Работа сервиса интеграции с OpenAI")
    
    # Создаем AI-сервис
    ai_service = AIService()
    
    # Инициализируем RAG
    await ai_service.initialize_rag(force_reload=False)
    
    # Тестируем генерацию плана питания
    print("3.1. Генерация плана питания:")
    kbju = "Белки: 120г, Жиры: 60г, Углеводы: 200г, Калории: 1800 ккал"
    goal = "Похудение"
    restrictions = "Без молочных продуктов, аллергия на орехи"
    
    meal_plan = await ai_service.generate_meal_plan(kbju, goal, restrictions)
    print(f"План питания сгенерирован, длина текста: {len(meal_plan)} символов")
    print(f"Первые 200 символов плана:\n{meal_plan[:200]}...\n")
    
    # Тестируем ответы на вопросы с использованием RAG
    print("3.2. Ответы на вопросы с использованием RAG:")
    test_question = "Какое питание рекомендуется для набора мышечной массы?"
    
    answer_with_rag = await ai_service.answer_question(test_question, use_rag=True)
    print(f"Ответ с использованием RAG (первые 200 символов):\n{answer_with_rag[:200]}...\n")
    
    # Тестируем ответы на вопросы без использования RAG
    print("3.3. Ответы на вопросы без использования RAG:")
    
    answer_without_rag = await ai_service.answer_question(test_question, use_rag=False)
    print(f"Ответ без использования RAG (первые 200 символов):\n{answer_without_rag[:200]}...\n")


async def run_tests():
    """Запуск всех тестов"""
    print("Начало тестирования интеграции с OpenAI и RAG-системы\n")
    
    await test_rag_initialization()
    await test_rag_search()
    await test_ai_service()
    
    print("Все тесты успешно выполнены")


if __name__ == "__main__":
    # Загружаем переменные окружения
    load_dotenv()
    
    # Запускаем тесты
    asyncio.run(run_tests())
