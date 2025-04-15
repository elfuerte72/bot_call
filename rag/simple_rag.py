"""
Упрощенная RAG-система для работы с PDF-файлами
"""
import os
import logging
import json
import requests
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

from rag.loaders import DocumentLoader

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleRAG:
    """Упрощенная реализация RAG-системы без использования LangChain"""

    def __init__(self, data_dir: str = None):
        """
        Инициализирует RAG-систему

        Args:
            data_dir: Путь к директории с документами. Если None, будет использован 
                      путь из переменной окружения или значение по умолчанию.
        """
        # Получаем API ключ OpenAI из переменных окружения
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("Не найден API ключ OpenAI в переменных окружения")
        
        # Устанавливаем директорию с данными
        if data_dir is None:
            # По умолчанию используем директорию 'data' в корне проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, 'data')
        else:
            self.data_dir = data_dir
        
        # Инициализируем загрузчик документов
        self.loader = DocumentLoader(self.data_dir)
        
        # Путь для сохранения индекса
        self.index_path = os.path.join(self.data_dir, 'simple_rag_index.pkl')
        
        # Данные и эмбеддинги будут инициализированы при вызове метода initialize
        self.documents = []
        self.embeddings = []
        self.is_initialized = False

    async def initialize(self, force_reload: bool = False) -> None:
        """
        Инициализирует RAG-систему, загружая документы и создавая эмбеддинги
        
        Args:
            force_reload: Если True, принудительно перезагрузит документы и пересоздаст эмбеддинги
        """
        # Проверяем наличие сохраненного индекса
        if os.path.exists(self.index_path) and not force_reload:
            try:
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.embeddings = data['embeddings']
                    self.is_initialized = True
                    
                logger.info(f"Индекс успешно загружен из {self.index_path}")
                logger.info(f"Загружено {len(self.documents)} документов и эмбеддингов")
                return
            except Exception as e:
                logger.error(f"Не удалось загрузить индекс: {e}")
        
        # Загружаем и обрабатываем документы
        logger.info("Начало загрузки и индексации документов...")
        self.documents = self.loader.process_documents()
        
        if not self.documents:
            raise ValueError("Не удалось загрузить документы для индексации")
        
        logger.info(f"Загружено {len(self.documents)} документов, создание эмбеддингов...")
        
        # Создаем эмбеддинги для каждого документа
        self.embeddings = []
        
        # Обрабатываем документы порциями по 20, чтобы не перегружать API
        batch_size = 20
        for i in range(0, len(self.documents), batch_size):
            batch_docs = self.documents[i:i+batch_size]
            batch_texts = [doc.page_content for doc in batch_docs]
            batch_embeddings = await self._get_embeddings(batch_texts)
            self.embeddings.extend(batch_embeddings)
            logger.info(f"Обработано {min(i+batch_size, len(self.documents))} документов из {len(self.documents)}")
        
        # Сохраняем индекс
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'embeddings': self.embeddings
            }, f)
        
        self.is_initialized = True
        logger.info(f"Индекс успешно создан и сохранен в {self.index_path}")

    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Получает эмбеддинги для списка текстов с помощью OpenAI API
        
        Args:
            texts: Список текстов для создания эмбеддингов
            
        Returns:
            Список эмбеддингов (векторов)
        """
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "input": texts,
                "model": "text-embedding-ada-002"
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return [item["embedding"] for item in result["data"]]
            
        except Exception as e:
            logger.error(f"Ошибка при получении эмбеддингов: {e}")
            raise

    async def _get_query_embedding(self, query: str) -> List[float]:
        """
        Получает эмбеддинг для запроса
        
        Args:
            query: Текст запроса
            
        Returns:
            Эмбеддинг (вектор) запроса
        """
        embeddings = await self._get_embeddings([query])
        return embeddings[0]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Вычисляет косинусное сходство между двумя векторами
        
        Args:
            a: Первый вектор
            b: Второй вектор
            
        Returns:
            Значение косинусного сходства
        """
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Выполняет поиск релевантных документов по запросу
        
        Args:
            query: Текст запроса
            k: Количество документов для возврата
            
        Returns:
            Список релевантных документов
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Получаем эмбеддинг запроса
        query_embedding = await self._get_query_embedding(query)
        
        # Вычисляем сходство запроса с каждым документом
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Сортируем по убыванию сходства и берем top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k_indices = [idx for idx, _ in similarities[:k]]
        
        # Возвращаем соответствующие документы
        results = []
        for idx in top_k_indices:
            doc = self.documents[idx]
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity": similarities[top_k_indices.index(idx)][1]
            })
        
        return results

    async def answer_question(self, question: str) -> str:
        """
        Генерирует ответ на вопрос, используя найденные документы в качестве контекста
        
        Args:
            question: Вопрос пользователя
            
        Returns:
            Ответ на вопрос
        """
        # Находим релевантные документы
        relevant_docs = await self.search(question, k=3)
        
        # Формируем контекст из найденных документов
        context = ""
        for doc in relevant_docs:
            source = doc["metadata"].get("source", "Неизвестный источник")
            context += f"Источник: {source}\n{doc['content']}\n\n"
        
        # Отправляем запрос к OpenAI API для получения ответа
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            prompt = f"""
            Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании, 
            тренировках и здоровье. Используй приведенную ниже информацию для ответа 
            на вопрос пользователя. Если информации недостаточно, отвечай на основе 
            общих знаний по теме, не выдумывая факты.

            Пиши в дружелюбном тоне, по-русски, можешь иногда использовать актуальные 
            мемы, чтобы сделать общение более интересным. Используй HTML-теги для 
            форматирования (<b>, <i>, <u>), но не используй markdown и не включай 
            в ответ ссылки на источники.

            Контекст:
            {context}

            Вопрос: {question}

            Ответ:
            """
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return f"Произошла ошибка при обработке вашего вопроса: {str(e)}"
