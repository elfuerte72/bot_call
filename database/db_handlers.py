from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_session
from database.models import Client, MealPlan, Restriction
from database.db_operations import (
    create_client, get_client, get_all_clients, 
    update_client, delete_client as delete_client_op,
    create_meal_plan, get_meal_plans_for_client,
    delete_meal_plan, add_restriction, 
    get_client_restrictions, delete_restriction
)


# Функции-обертки для работы с клиентами
async def add_client(
    name: str,
    age: int,
    gender: str,
    height: float,
    weight: float,
    activity: str,
    goal: str,
    calories: float,
    protein: float,
    fat: float,
    carbs: float
) -> int:
    """
    Добавляет нового клиента в базу данных
    
    Args:
        name: Имя клиента
        age: Возраст клиента
        gender: Пол клиента
        height: Рост клиента в см
        weight: Вес клиента в кг
        activity: Уровень активности
        goal: Цель (похудение/набор/поддержание)
        calories: Расчетное количество калорий
        protein: Расчетное количество белка в граммах
        fat: Расчетное количество жира в граммах
        carbs: Расчетное количество углеводов в граммах
    
    Returns:
        ID созданного клиента
    """
    async with get_session() as session:
        client = await create_client(
            session=session,
            name=name,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            activity_level=activity,
            goal=goal,
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs
        )
        return client.id


async def get_client_by_id(client_id: int) -> Optional[Client]:
    """
    Получает клиента по ID
    
    Args:
        client_id: ID клиента
    
    Returns:
        Объект клиента или None, если клиент не найден
    """
    async with get_session() as session:
        return await get_client(session, client_id)


async def get_clients() -> List[Client]:
    """
    Получает список всех клиентов
    
    Returns:
        Список всех клиентов
    """
    async with get_session() as session:
        return await get_all_clients(session)


async def update_client_data(client_id: int, data: Dict[str, Any]) -> Optional[Client]:
    """
    Обновляет данные клиента
    
    Args:
        client_id: ID клиента
        data: Словарь с обновляемыми полями и их значениями
    
    Returns:
        Обновленный объект клиента или None, если клиент не найден
    """
    async with get_session() as session:
        return await update_client(session, client_id, data)


async def delete_client(client_id: int) -> bool:
    """
    Удаляет клиента
    
    Args:
        client_id: ID клиента
    
    Returns:
        True, если клиент был удален, иначе False
    """
    async with get_session() as session:
        return await delete_client_op(session, client_id)


# Функции-обертки для работы с планами питания
async def save_meal_plan(client_id: int, content: str) -> int:
    """
    Создает новый план питания для клиента
    
    Args:
        client_id: ID клиента
        content: Содержание плана питания
    
    Returns:
        ID созданного плана питания или None, если клиент не найден
    """
    async with get_session() as session:
        meal_plan = await create_meal_plan(session, client_id, content)
        if meal_plan:
            return meal_plan.id
        return None


async def get_meal_plans(client_id: int) -> List[MealPlan]:
    """
    Получает все планы питания клиента
    
    Args:
        client_id: ID клиента
    
    Returns:
        Список планов питания клиента
    """
    async with get_session() as session:
        return await get_meal_plans_for_client(session, client_id)


async def remove_meal_plan(meal_plan_id: int) -> bool:
    """
    Удаляет план питания
    
    Args:
        meal_plan_id: ID плана питания
    
    Returns:
        True, если план был удален, иначе False
    """
    async with get_session() as session:
        return await delete_meal_plan(session, meal_plan_id)


# Функции-обертки для работы с ограничениями
async def add_client_restriction(
    client_id: int,
    restriction_type: str,
    description: str
) -> int:
    """
    Добавляет ограничение для клиента
    
    Args:
        client_id: ID клиента
        restriction_type: Тип ограничения ('аллергия', 'предпочтение', 'религиозное')
        description: Описание ограничения
    
    Returns:
        ID созданного ограничения или None, если клиент не найден
    """
    async with get_session() as session:
        restriction = await add_restriction(
            session, client_id, restriction_type, description
        )
        if restriction:
            return restriction.id
        return None


async def get_restrictions(client_id: int) -> List[Restriction]:
    """
    Получает все ограничения клиента
    
    Args:
        client_id: ID клиента
    
    Returns:
        Список ограничений клиента
    """
    async with get_session() as session:
        return await get_client_restrictions(session, client_id)


async def remove_restriction(restriction_id: int) -> bool:
    """
    Удаляет ограничение
    
    Args:
        restriction_id: ID ограничения
    
    Returns:
        True, если ограничение было удалено, иначе False
    """
    async with get_session() as session:
        return await delete_restriction(session, restriction_id)
