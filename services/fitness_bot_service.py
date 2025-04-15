"""
Интегрированный сервис для фитнес-бота
"""
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from services.openai_simple import SimpleOpenAIService
from rag.simple_rag import SimpleRAG

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FitnessBotService:
    """Сервис для фитнес-бота, объединяющий RAG и OpenAI"""

    def __init__(self):
        """Инициализация сервиса фитнес-бота"""
        # Инициализируем сервис OpenAI
        self.openai_service = SimpleOpenAIService()
        
        # Инициализируем RAG-систему
        # Используем только файлы из папки data
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, 'data')
        self.rag = SimpleRAG(data_dir=self.data_dir)
        self.rag_initialized = False
        
        # Проверяем наличие папки для данных и файлов в ней
        if os.path.exists(self.data_dir):
            pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
            if pdf_files:
                logger.info(f"Найдено {len(pdf_files)} PDF-файлов в папке {self.data_dir}")
            else:
                logger.warning(f"В папке {self.data_dir} не найдено PDF-файлов")
        else:
            logger.error(f"Папка {self.data_dir} не существует")

    async def initialize_rag(self, force_reload: bool = False) -> None:
        """
        Инициализирует RAG-систему
        
        Args:
            force_reload: Если True, перезагрузит документы и создаст новые эмбеддинги
        """
        try:
            if not self.rag_initialized or force_reload:
                await self.rag.initialize(force_reload=force_reload)
                self.rag_initialized = True
                logger.info("RAG-система успешно инициализирована")
            else:
                logger.info("RAG-система уже инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации RAG-системы: {e}")
            raise

    async def generate_meal_plan(self, kbju: str, goal: str, restrictions: str) -> str:
        """
        Генерирует план питания с учетом КБЖУ, цели и ограничений
        
        Args:
            kbju: Строка с информацией о КБЖУ
            goal: Цель (похудение, набор массы, поддержание)
            restrictions: Ограничения и предпочтения в питании
            
        Returns:
            План питания
        """
        try:
            return await self.openai_service.generate_meal_plan(
                kbju=kbju,
                goal=goal,
                restrictions=restrictions
            )
        except Exception as e:
            logger.error(f"Ошибка при генерации плана питания: {e}")
            return "Произошла ошибка при генерации плана питания. Пожалуйста, попробуйте позже."

    async def answer_question(self, question: str) -> str:
        """
        Отвечает на вопрос, используя RAG-систему
        
        Args:
            question: Вопрос пользователя
            
        Returns:
            Ответ на вопрос
        """
        try:
            # Проверяем, инициализирована ли RAG-система
            if not self.rag_initialized:
                await self.initialize_rag()
            
            # Ищем ответ в RAG-системе
            answer = await self.rag.answer_question(question)
            return answer
        except Exception as e:
            logger.error(f"Ошибка при ответе на вопрос: {e}")
            try:
                # Если ошибка в RAG, пробуем использовать общий ответ через OpenAI
                return await self.openai_service.answer_question(question)
            except Exception as inner_e:
                logger.error(f"Ошибка при использовании резервного ответа: {inner_e}")
                return "Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже."

    async def calculate_kbju(self, gender: str, age: int, weight: float, 
                           height: float, activity_level: str, goal: str) -> Dict[str, Any]:
        """
        Рассчитывает КБЖУ по формуле Бенедикта
        
        Args:
            gender: Пол (мужской/женский)
            age: Возраст
            weight: Вес в кг
            height: Рост в см
            activity_level: Уровень активности
            goal: Цель (похудение/набор/поддержание)
            
        Returns:
            Словарь с рассчитанными значениями КБЖУ
        """
        try:
            # Коэффициенты активности
            activity_coefficients = {
                "минимальная": 1.2,  # Сидячий образ жизни, без физ. нагрузки
                "низкая": 1.375,     # Легкие тренировки 1-3 раза в неделю
                "средняя": 1.55,     # Умеренные тренировки 3-5 раз в неделю
                "высокая": 1.725,    # Интенсивные тренировки 6-7 раз в неделю
                "очень высокая": 1.9 # Тяжелая физическая работа, ежедневные тренировки
            }
            
            # Коэффициенты для цели
            goal_coefficients = {
                "похудение": 0.8,    # Дефицит калорий
                "поддержание": 1.0,  # Поддержание веса
                "набор": 1.2         # Профицит калорий
            }
            
            # Расчет базового метаболизма по формуле Бенедикта
            bmr = 0
            if gender.lower() == "мужской":
                bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
            else:  # женский
                bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
            
            # Учитываем уровень активности
            activity_coef = activity_coefficients.get(activity_level.lower(), 1.55)
            tdee = bmr * activity_coef
            
            # Учитываем цель
            goal_coef = goal_coefficients.get(goal.lower(), 1.0)
            total_calories = tdee * goal_coef
            
            # Рассчитываем БЖУ
            protein_percent = 0.3  # 30% от общей калорийности
            fat_percent = 0.3      # 30% от общей калорийности
            carbs_percent = 0.4    # 40% от общей калорийности
            
            # Калорийность 1 г: белок - 4 ккал, жиры - 9 ккал, углеводы - 4 ккал
            protein_calories = total_calories * protein_percent
            fat_calories = total_calories * fat_percent
            carbs_calories = total_calories * carbs_percent
            
            protein_grams = protein_calories / 4
            fat_grams = fat_calories / 9
            carbs_grams = carbs_calories / 4
            
            # Округляем значения
            total_calories = round(total_calories)
            protein_grams = round(protein_grams)
            fat_grams = round(fat_grams)
            carbs_grams = round(carbs_grams)
            
            # Результат
            result = {
                "calories": total_calories,
                "protein": protein_grams,
                "fat": fat_grams,
                "carbs": carbs_grams,
                "kbju_str": f"{total_calories} ккал, {protein_grams}г белка, {fat_grams}г жиров, {carbs_grams}г углеводов"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при расчете КБЖУ: {e}")
            raise
