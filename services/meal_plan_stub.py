from typing import Dict, List, Any, Optional
import random

# Функция-заглушка для генерации планов питания
async def generate_meal_plan(
    client_id: int,
    calories: float,
    protein: float,
    fat: float,
    carbs: float,
    goal: str,
    allergies: str = '',
    preferences: str = '',
    limitations: str = ''
) -> str:
    """
    Заглушка для генерации плана питания на день с учетом КБЖУ и ограничений
    
    Args:
        client_id: ID клиента
        calories: Целевое количество калорий
        protein: Целевое количество белка в граммах
        fat: Целевое количество жира в граммах
        carbs: Целевое количество углеводов в граммах
        goal: Цель клиента
        allergies: Информация об аллергиях (опционально)
        preferences: Предпочтения в еде (опционально)
        limitations: Ограничения религиозные и др. (опционально)
        
    Returns:
        План питания в текстовом формате
    """
    # Информация об ограничениях
    restrictions_text = ""
    if allergies:
        restrictions_text += f"\n🚫 Аллергия: {allergies}"
    if preferences:
        restrictions_text += f"\n👍 Предпочтения: {preferences}"
    if limitations:
        restrictions_text += f"\n⚠️ Ограничения: {limitations}"
    
    # Распределение КБЖУ по приемам пищи
    breakfast_percent = random.uniform(0.25, 0.30)
    lunch_percent = random.uniform(0.35, 0.40)
    dinner_percent = random.uniform(0.25, 0.30)
    snack_percent = 1 - (breakfast_percent + lunch_percent + dinner_percent)
    
    breakfast_cals = round(calories * breakfast_percent)
    lunch_cals = round(calories * lunch_percent)
    dinner_cals = round(calories * dinner_percent)
    snack_cals = round(calories * snack_percent)
    
    # Примерный план питания
    sample_plan = f"""📋 План питания на день

📊 Общие КБЖУ на день:
🔥 Калории: {round(calories)} ккал
🥩 Белки: {round(protein)} г
🧈 Жиры: {round(fat)} г
🍚 Углеводы: {round(carbs)} г
{restrictions_text}

🍳 ЗАВТРАК (~{breakfast_cals} ккал)
- Омлет из 2 яиц с овощами
- Каша овсяная на молоке 1%
- Тост из цельнозернового хлеба
- Чай/кофе без сахара

🥗 ОБЕД (~{lunch_cals} ккал)
- Куриная грудка запеченная 150г
- Гречка отварная 100г
- Салат из свежих овощей с оливковым маслом
- Компот из сухофруктов без сахара

🥩 УЖИН (~{dinner_cals} ккал)
- Рыба запеченная 150г
- Овощи на пару 150г
- Рис бурый 70г
- Чай зеленый

🍎 ПЕРЕКУС (~{snack_cals} ккал)
- Яблоко
- Творог 5% 100г
- Орехи миндаль 15г

❗️ Примечание: Это примерный план питания для тестирования интерфейса бота.
В полной версии бота план будет составляться индивидуально с использованием GPT и RAG-системы.
"""
    return sample_plan
