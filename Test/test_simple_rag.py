"""
Тестовый скрипт для проверки работы упрощенной RAG-системы
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

from rag.simple_rag import SimpleRAG


async def test_simple_rag():
    """Тестирование упрощенной RAG-системы"""
    print("Запуск тестирования упрощенной RAG-системы...")
    
    # Путь к директории с данными
    data_dir = os.path.join(root_dir, 'data')
    print(f"Директория с данными: {data_dir}")
    
    # Проверяем наличие PDF-файлов
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    print(f"Найдено PDF-файлов: {len(pdf_files)}")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    # Инициализируем RAG-систему
    print("\nИнициализация RAG-системы...")
    rag = SimpleRAG(data_dir=data_dir)
    
    # Инициализируем систему (загружаем документы и создаем эмбеддинги)
    print("\nЗагрузка документов и создание эмбеддингов...")
    await rag.initialize()
    
    # Тестируем поиск
    test_queries = [
        "Какова калорийность яблока?",
        "Какие продукты богаты белком?",
        "Как рассчитать КБЖУ?"
    ]
    
    print("\nТестирование поиска:")
    for query in test_queries:
        print(f"\nПоиск по запросу: '{query}'")
        results = await rag.search(query, k=2)
        print(f"Найдено результатов: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"Результат {i+1}:")
            print(f"  Источник: {result['metadata'].get('source', 'Неизвестно')}")
            print(f"  Релевантность: {result['similarity']:.4f}")
            print(f"  Релевантный текст: {result['content'][:150]}...")
    
    # Тестируем генерацию ответов
    print("\nТестирование генерации ответов:")
    for query in test_queries:
        print(f"\nГенерация ответа на вопрос: '{query}'")
        answer = await rag.answer_question(query)
        print(f"Ответ: {answer}")
    
    print("\nТестирование упрощенной RAG-системы завершено успешно!")


if __name__ == "__main__":
    asyncio.run(test_simple_rag())
