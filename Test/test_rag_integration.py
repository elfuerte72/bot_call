"""
Тестовый скрипт для проверки работы RAG-системы
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

from rag.engine import RAGEngine
from rag.loaders import DocumentLoader


async def test_rag_system():
    """Тестирование загрузки документов и создания эмбеддингов в RAG-системе"""
    print("Запуск тестирования RAG-системы...")
    
    # Путь к директории с данными
    data_dir = os.path.join(root_dir, 'data')
    print(f"Директория с данными: {data_dir}")
    
    # Проверяем наличие PDF-файлов
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    print(f"Найдено PDF-файлов: {len(pdf_files)}")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    # Инициализируем загрузчик документов
    print("\nИнициализация загрузчика документов...")
    loader = DocumentLoader(data_dir)
    
    # Загружаем документы
    print("\nЗагрузка документов...")
    documents = loader.process_documents()
    print(f"Загружено документов: {len(documents)}")
    
    # Выводим примеры чанков
    if documents:
        print("\nПримеры чанков:")
        for i, doc in enumerate(documents[:3]):  # Первые 3 чанка
            print(f"Чанк {i+1}:")
            print(f"  Источник: {doc.metadata.get('source', 'Неизвестно')}")
            print(f"  Содержимое: {doc.page_content[:150]}...")  # Первые 150 символов
            print()
    
    # Инициализируем RAG-движок
    print("\nИнициализация RAG-движка...")
    rag_engine = RAGEngine(data_dir=data_dir)
    
    # Инициализируем векторное хранилище (создаем эмбеддинги)
    print("\nСоздание эмбеддингов и индексация документов...")
    await rag_engine.initialize(force_reload=True)
    
    # Тестируем поиск
    test_queries = [
        "Какие упражнения лучше для мышц ног?",
        "Как правильно питаться для набора массы?",
        "Что делать при болях в спине после тренировки?"
    ]
    
    print("\nТестирование поиска:")
    for query in test_queries:
        print(f"\nПоиск по запросу: '{query}'")
        results = await rag_engine.search(query, k=2)
        print(f"Найдено результатов: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"Результат {i+1}:")
            print(f"  Источник: {result.metadata.get('source', 'Неизвестно')}")
            print(f"  Релевантный текст: {result.page_content[:150]}...")
    
    # Тестируем генерацию ответов
    print("\nТестирование генерации ответов:")
    for query in test_queries:
        print(f"\nГенерация ответа на вопрос: '{query}'")
        answer = await rag_engine.generate_answer(query, use_retrieval=True)
        print(f"Ответ: {answer[:200]}...")  # Первые 200 символов ответа
    
    print("\nТестирование RAG-системы завершено успешно!")


if __name__ == "__main__":
    asyncio.run(test_rag_system())
