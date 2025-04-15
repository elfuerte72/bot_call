import os
import logging
from dotenv import load_dotenv

from openai import OpenAI
from rag.engine import RAGEngine

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIService:
    """Класс для работы с OpenAI GPT-4.1 nano"""

    def __init__(self):
        """Инициализация сервиса AI"""
        # Получаем API ключ OpenAI из переменных окружения
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Не найден API ключ OpenAI в переменных окружения")

        # Инициализируем клиент OpenAI
        self.client = OpenAI(api_key=self.api_key)

        # Устанавливаем стандартные промпты
        self.meal_plan_prompt = """
        Ты - опытный диетолог и фитнес-тренер, который составляет индивидуальные планы питания.

        Составь план питания на 1 день для человека со следующими параметрами:
        - КБЖУ: {kbju}
        - Цель: {goal}
        - Ограничения: {restrictions}

        Твой ответ должен быть:
        1. Дружелюбным и мотивирующим
        2. Структурированным (завтрак, обед, перекус, ужин)
        3. С указанием примерных граммовок и КБЖУ для каждого приема пищи
        4. Без использования markdown разметки
        5. С использованием <b>, <i> и других HTML-тегов для выделения ключевых моментов
        6. С разбивкой на абзацы для удобства чтения
        7. Без ссылок на внешние источники информации

        Добавь актуальный мем или шутку о правильном питании для мотивации.
        """
        
        self.rag_prompt = """
        Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании, тренировках и здоровье. 
        Используй приведенную ниже информацию для ответа на вопрос пользователя. 
        Если информации недостаточно, отвечай на основе общих знаний по теме, не выдумывая факты.

        Пиши в дружелюбном тоне, по-русски, можешь иногда использовать актуальные мемы, 
        чтобы сделать общение более интересным. Используй HTML-теги для форматирования (<b>, <i>, <u>), 
        но не используй markdown и не включай в ответ ссылки на источники.

        Контекст: {context}

        Вопрос: {question}

        Ответ:
        """
        
        # Проверяем наличие промптов в переменных окружения и загружаем их, если они есть
        env_meal_plan_prompt = os.getenv("MEAL_PLAN_PROMPT")
        env_rag_prompt = os.getenv("RAG_PROMPT")
        
        if env_meal_plan_prompt:
            self.meal_plan_prompt = env_meal_plan_prompt
            
        if env_rag_prompt:
            self.rag_prompt = env_rag_prompt

        # Инициализируем RAG-систему
        self.rag_engine = RAGEngine()

    async def initialize_rag(self, force_reload: bool = False) -> None:
        """
        Инициализирует RAG-систему

        Args:
            force_reload: Принудительно перезагрузить документы
        """
        await self.rag_engine.initialize(force_reload=force_reload)
        logger.info("RAG-система инициализирована")

    async def generate_meal_plan(self, kbju: str, goal: str, restrictions: str) -> str:
        """
        Генерирует план питания на основе параметров

        Args:
            kbju: Строка с информацией о КБЖУ
            goal: Цель (похудение, набор массы, поддержание)
            restrictions: Ограничения и предпочтения в питании

        Returns:
            Сгенерированный план питания
        """
        try:
            # Форматируем промпт с параметрами
            formatted_prompt = self.meal_plan_prompt.format(
                kbju=kbju,
                goal=goal,
                restrictions=restrictions
            )

            # Запрос к API OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Используем GPT-4.1 nano
                messages=[
                    {"role": "system", "content": formatted_prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            # Возвращаем текст ответа
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка при генерации плана питания: {e}")
            return (
                "Произошла ошибка при генерации плана питания. "
                "Пожалуйста, попробуйте позже."
            )

    async def answer_question(self, question: str, use_rag: bool = True) -> str:
        """
        Отвечает на вопрос пользователя, используя RAG при необходимости

        Args:
            question: Вопрос пользователя
            use_rag: Использовать ли RAG-систему

        Returns:
            Ответ на вопрос
        """
        try:
            if use_rag:
                # Используем RAG-систему для поиска релевантного контекста
                context_docs = await self.rag_engine.search(question, k=3)

                # Если документы найдены, формируем контекст
                if context_docs:
                    context = "\n\n".join(
                        [doc.page_content for doc in context_docs]
                    )
                else:
                    context = "Релевантный контекст не найден."

                # Форматируем промпт с контекстом и вопросом
                formatted_prompt = self.rag_prompt.format(
                    context=context,
                    question=question
                )

                # Запрос к API OpenAI с контекстом из RAG
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Используем GPT-4.1 nano
                    messages=[
                        {"role": "system", "content": formatted_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )
            else:
                # Если RAG не используется, задаем базовый промпт
                system_prompt = """
                Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании, 
                тренировках и здоровье. Отвечай на основе общих знаний по теме.
                Пиши в дружелюбном тоне, по-русски, можешь иногда использовать 
                актуальные мемы. Используй HTML-теги для форматирования, но не 
                используй markdown. Не включай в ответ ссылки на источники.
                """

                # Запрос к API OpenAI без контекста
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Используем GPT-4.1 nano
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

            # Возвращаем текст ответа
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return (
                "Произошла ошибка при обработке вашего вопроса. "
                "Пожалуйста, попробуйте позже."
            )
