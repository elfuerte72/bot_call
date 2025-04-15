import sys
import os
import unittest

# Добавляем корневую директорию проекта в путь импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nutrition import NutritionCalculator


class TestNutritionCalculator(unittest.TestCase):
    """Тесты для проверки работы калькулятора питания"""
    
    def test_calculate_bmr_male(self):
        """Проверка расчета базового метаболизма для мужчин"""
        # Мужчина, 80 кг, 180 см, 30 лет
        bmr = NutritionCalculator.calculate_bmr("мужской", 80, 180, 30)
        # Ожидаемое значение: 66 + (13.7 * 80) + (5 * 180) - (6.8 * 30)
        expected = 66 + (13.7 * 80) + (5 * 180) - (6.8 * 30)
        self.assertAlmostEqual(bmr, expected, delta=1)
    
    def test_calculate_bmr_female(self):
        """Проверка расчета базового метаболизма для женщин"""
        # Женщина, 60 кг, 165 см, 25 лет
        bmr = NutritionCalculator.calculate_bmr("женский", 60, 165, 25)
        # Ожидаемое значение: 655 + (9.6 * 60) + (1.8 * 165) - (4.7 * 25)
        expected = 655 + (9.6 * 60) + (1.8 * 165) - (4.7 * 25)
        self.assertAlmostEqual(bmr, expected, delta=1)
    
    def test_calculate_tdee(self):
        """Проверка расчета полного потребления энергии в день (TDEE) и КБЖУ"""
        # Мужчина, 80 кг, 180 см, 30 лет, средняя активность, поддержание веса
        nutrition_data = NutritionCalculator.calculate_tdee(
            "мужской", 80, 180, 30, "medium", "maintenance"
        )
        
        # Проверяем, что результат содержит все ожидаемые ключи
        self.assertIn("calories", nutrition_data)
        self.assertIn("protein", nutrition_data)
        self.assertIn("fat", nutrition_data)
        self.assertIn("carbs", nutrition_data)
        
        # Проверяем, что значения имеют ожидаемый порядок величин
        # Для мужчины 80 кг ожидаем примерно 2500-3000 калорий для поддержания веса
        self.assertGreater(nutrition_data["calories"], 2000)
        self.assertLess(nutrition_data["calories"], 3500)
        
        # Проверяем, что макронутриенты рассчитаны правильно
        # Для цели "maintenance" соотношение должно быть 25/25/50
        protein_calories = nutrition_data["protein"] * 4
        fat_calories = nutrition_data["fat"] * 9
        carb_calories = nutrition_data["carbs"] * 4
        
        total_calories = protein_calories + fat_calories + carb_calories
        
        # Проверяем, что общая сумма калорий из макронутриентов близка к расчетной
        self.assertAlmostEqual(total_calories, nutrition_data["calories"], delta=50)
        
        # Проверяем процентное соотношение макронутриентов
        protein_percent = protein_calories / total_calories
        fat_percent = fat_calories / total_calories
        carb_percent = carb_calories / total_calories
        
        self.assertAlmostEqual(protein_percent, 0.25, delta=0.05)
        self.assertAlmostEqual(fat_percent, 0.25, delta=0.05)
        self.assertAlmostEqual(carb_percent, 0.5, delta=0.05)
    
    def test_format_nutrition_info(self):
        """Проверка форматирования информации о КБЖУ"""
        nutrition_data = {
            "calories": 2500,
            "protein": 150,
            "fat": 70,
            "carbs": 300
        }
        
        formatted = NutritionCalculator.format_nutrition_info(nutrition_data)
        
        # Проверяем, что результат содержит все ожидаемые значения
        self.assertIn("2500", formatted)
        self.assertIn("150", formatted)
        self.assertIn("70", formatted)
        self.assertIn("300", formatted)


if __name__ == "__main__":
    unittest.main()
