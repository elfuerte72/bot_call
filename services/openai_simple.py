"""
Упрощенный сервис для работы с OpenAI API
"""
import os
import logging
from typing import List
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleOpenAIService:
    """Упрощенный класс для работы с OpenAI GPT-4.1 nano"""

    def __init__(self):
        """Инициализация сервиса OpenAI"""
        # Получаем API ключ OpenAI из переменных окружения
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Не найден API ключ OpenAI в переменных окружения")

        # Устанавливаем стандартные промпты
        self.meal_plan_prompt = (
            "Ты - опытный диетолог и фитнес-тренер, который составляет "
            "индивидуальные планы питания. "
            "Составь план питания на 1 день для человека со следующими параметрами: "
            "- КБЖУ: {kbju} "
            "- Цель: {goal} "
            "- Ограничения: {restrictions} "
            "Твой ответ должен быть: "
            "1. Дружелюбным и мотивирующим "
            "2. Структурированным (завтрак, обед, перекус, ужин) "
            "3. С указанием примерных граммовок и КБЖУ для каждого приема пищи "
            "4. Без использования markdown разметки "
            "5. С использованием <b>, <i> и других HTML-тегов для ключевых моментов "
            "6. С разбивкой на абзацы для удобства чтения "
            "7. Без ссылок на внешние источники информации "
            "Добавь актуальный мем или шутку о правильном питании для мотивации."
        )
        
        self.general_prompt = (
            "Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании, "
            "тренировках и здоровье. Отвечай на основе общих знаний по теме, "
            "не выдумывая факты. "
            "Пиши в дружелюбном тоне, по-русски, можешь иногда использовать "
            "актуальные мемы, чтобы сделать общение более интересным. "
            "Используй HTML-теги для форматирования (<b>, <i>, <u>), "
            "но не используй markdown и не включай в ответ ссылки на источники. "
            "Вопрос: {question}"
        )
        
        # Проверяем наличие промптов в переменных окружения и загружаем их
        env_meal_plan_prompt = os.getenv("MEAL_PLAN_PROMPT")
        env_general_prompt = os.getenv("RAG_PROMPT")
        
        if env_meal_plan_prompt:
            self.meal_plan_prompt = env_meal_plan_prompt
            
        if env_general_prompt:
            self.general_prompt = env_general_prompt

    async def _make_openai_request(self, prompt, system=True, temperature=0.7, max_tokens=1500):
        """
        Отправляет запрос к API OpenAI через requests для максимальной совместимости
        
        Args:
            prompt: Текст промпта
            system: Если True, то промпт отправляется как system message, иначе как user
            temperature: Температура генерации (0.0 - 1.0)
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Текст ответа от OpenAI
        """
        import requests
        import json
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                logger.error(f"Неожиданный формат ответа от OpenAI: {response_data}")
                return "Произошла ошибка при обработке ответа от OpenAI."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к OpenAI API: {e}")
            return "Произошла ошибка при обращении к API OpenAI. Пожалуйста, попробуйте позже."
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            return "Произошла ошибка при обработке ответа от OpenAI."
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            return "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."

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
            
            # Отправляем запрос к API
            return await self._make_openai_request(formatted_prompt)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации плана питания: {e}")
            return (
                "Произошла ошибка при генерации плана питания. "
                "Пожалуйста, попробуйте позже."
            )

    async def answer_question(self, question: str, context: str = "") -> str:
        """
        Отвечает на вопрос пользователя

        Args:
            question: Вопрос пользователя
            context: Контекст для ответа (из RAG системы), по умолчанию пустой

        Returns:
            Ответ на вопрос
        """
        try:
            # Форматируем промпт с вопросом и контекстом
            formatted_prompt = self.general_prompt.format(
                question=question,
                context=context if context else "Специфического контекста нет, используй общие знания."
            )
            
            # Отправляем запрос к API
            return await self._make_openai_request(formatted_prompt)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return (
                "Произошла ошибка при обработке вашего вопроса. "
                "Пожалуйста, попробуйте позже."
            )
