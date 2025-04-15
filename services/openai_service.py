"""
Сервис для работы с OpenAI API без использования LangChain
"""
import os
import logging
from typing import List
from dotenv import load_dotenv

from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenAIService:
    """Класс для работы с OpenAI GPT-4.1 nano"""

    def __init__(self):
        """Инициализация сервиса OpenAI"""
        # Получаем API ключ OpenAI из переменных окружения
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Не найден API ключ OpenAI в переменных окружения")

        # Инициализируем клиент OpenAI
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.openai.com/v1")

        # Устанавливаем стандартные промпты
        self.meal_plan_prompt = """
        Ты - опытный диетолог и фитнес-тренер, который составляет 
        индивидуальные планы питания.

        Составь план питания на 1 день для человека со следующими параметрами:
        - КБЖУ: {kbju}
        - Цель: {goal}
        - Ограничения: {restrictions}

        Твой ответ должен быть:
        1. Дружелюбным и мотивирующим
        2. Структурированным (завтрак, обед, перекус, ужин)
        3. С указанием примерных граммовок и КБЖУ для каждого приема пищи
        4. Без использования markdown разметки
        5. С использованием <b>, <i> и других HTML-тегов для ключевых моментов
        6. С разбивкой на абзацы для удобства чтения
        7. Без ссылок на внешние источники информации

        Добавь актуальный мем или шутку о правильном питании для мотивации.
        """
        
        self.general_prompt = """
        Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании,
        тренировках и здоровье. Отвечай на основе общих знаний по теме, 
        не выдумывая факты.

        Пиши в дружелюбном тоне, по-русски, можешь иногда использовать 
        актуальные мемы, чтобы сделать общение более интересным. 
        Используй HTML-теги для форматирования (<b>, <i>, <u>), 
        но не используй markdown и не включай в ответ ссылки на источники.

        Вопрос: {question}
        """
        
        # Проверяем наличие промптов в переменных окружения и загружаем их
        env_meal_plan_prompt = os.getenv("MEAL_PLAN_PROMPT")
        env_general_prompt = os.getenv("RAG_PROMPT")
        
        if env_meal_plan_prompt:
            self.meal_plan_prompt = env_meal_plan_prompt
            
        if env_general_prompt:
            self.general_prompt = env_general_prompt

    async def generate_meal_plan(self, kbju: str, goal: str, 
                                restrictions: str) -> str:
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

    async def answer_question(self, question: str) -> str:
        """
        Отвечает на вопрос пользователя

        Args:
            question: Вопрос пользователя

        Returns:
            Ответ на вопрос
        """
        try:
            # Форматируем промпт с вопросом
            formatted_prompt = self.general_prompt.format(question=question)
            
            # Запрос к API OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Используем GPT-4.1 nano
                messages=[
                    {"role": "system", "content": formatted_prompt},
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

    async def extract_ingredients_from_text(self, text: str) -> List[str]:
        """
        Извлекает ингредиенты из текста рецепта

        Args:
            text: Текст рецепта

        Returns:
            Список ингредиентов
        """
        try:
            prompt = (
                "Извлеки все ингредиенты из следующего рецепта и верни их в виде "
                "списка, каждый ингредиент с новой строки. Не добавляй никакой "
                "дополнительной информации. Рецепт: {text}"
            )
            
            formatted_prompt = prompt.format(text=text)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": formatted_prompt},
                ],
                temperature=0.0,  # Низкая температура для более детерминированного ответа
                max_tokens=500,
            )
            
            # Получаем текст ответа и разбиваем его на строки
            ingredients_text = response.choices[0].message.content
            ingredients = [
                line.strip() for line in ingredients_text.split('\n') 
                if line.strip()
            ]
            
            return ingredients
        
        except Exception as e:
            logger.error(f"Ошибка при извлечении ингредиентов: {e}")
            return []
