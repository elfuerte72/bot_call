from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional, Dict, Any

from database.models import Client, MealPlan, Restriction

# Операции с клиентами
async def create_client(
    session: AsyncSession,
    name: str,
    age: int,
    gender: str,
    height: float,
    weight: float,
    activity_level: str,
    goal: str,
    calories: float,
    protein: float,
    fat: float,
    carbs: float
) -> Client:
    """
    Создает нового клиента в базе данных
    
    Args:
        session: Сессия SQLAlchemy
        name: Имя клиента
        age: Возраст клиента
        gender: Пол клиента
        height: Рост клиента в см
        weight: Вес клиента в кг
        activity_level: Уровень активности
        goal: Цель (похудение/набор/поддержание)
        calories: Расчетное количество калорий
        protein: Расчетное количество белка в граммах
        fat: Расчетное количество жира в граммах
        carbs: Расчетное количество углеводов в граммах
    
    Returns:
        Созданный объект клиента
    """
    client = Client(
        name=name,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        activity_level=activity_level,
        goal=goal,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs
    )

    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def get_client(session: AsyncSession, client_id: int) -> Optional[Client]:
    """
    Получает клиента по ID
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
    
    Returns:
        Объект клиента или None, если клиент не найден
    """
    result = await session.execute(select(Client).where(Client.id == client_id))
    return result.scalars().first()


async def get_all_clients(session: AsyncSession) -> List[Client]:
    """
    Получает список всех клиентов
    
    Args:
        session: Сессия SQLAlchemy
    
    Returns:
        Список всех клиентов
    """
    result = await session.execute(select(Client))
    return result.scalars().all()


async def update_client(
    session: AsyncSession,
    client_id: int,
    data: Dict[str, Any]
) -> Optional[Client]:
    """
    Обновляет данные клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
        data: Словарь с обновляемыми полями и их значениями
    
    Returns:
        Обновленный объект клиента или None, если клиент не найден
    """
    await session.execute(
        update(Client)
        .where(Client.id == client_id)
        .values(**data)
    )
    await session.commit()
    return await get_client(session, client_id)


async def delete_client(session: AsyncSession, client_id: int) -> bool:
    """
    Удаляет клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
    
    Returns:
        True, если клиент был удален, иначе False
    """
    result = await session.execute(delete(Client).where(Client.id == client_id))
    await session.commit()
    return result.rowcount > 0


# Операции с планами питания
async def create_meal_plan(
    session: AsyncSession, client_id: int, content: str
) -> Optional[MealPlan]:
    """
    Создает новый план питания для клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
        content: Содержание плана питания (JSON-строка)
    
    Returns:
        Созданный объект плана питания или None, если клиент не найден
    """
    # Проверяем существование клиента
    client = await get_client(session, client_id)
    if not client:
        return None

    meal_plan = MealPlan(
        client_id=client_id,
        content=content
    )

    session.add(meal_plan)
    await session.commit()
    await session.refresh(meal_plan)
    return meal_plan


async def get_meal_plans_for_client(
    session: AsyncSession, client_id: int
) -> List[MealPlan]:
    """
    Получает все планы питания клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
    
    Returns:
        Список планов питания клиента
    """
    result = await session.execute(
        select(MealPlan).where(MealPlan.client_id == client_id)
    )
    return result.scalars().all()


async def delete_meal_plan(session: AsyncSession, meal_plan_id: int) -> bool:
    """
    Удаляет план питания
    
    Args:
        session: Сессия SQLAlchemy
        meal_plan_id: ID плана питания
    
    Returns:
        True, если план был удален, иначе False
    """
    result = await session.execute(
        delete(MealPlan).where(MealPlan.id == meal_plan_id)
    )
    await session.commit()
    return result.rowcount > 0


# Операции с ограничениями
async def add_restriction(
    session: AsyncSession, client_id: int,
    restriction_type: str, description: str
) -> Optional[Restriction]:
    """
    Добавляет ограничение для клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
        restriction_type: Тип ограничения ('аллергия', 'предпочтение', 'религиозное')
        description: Описание ограничения
    
    Returns:
        Созданный объект ограничения или None, если клиент не найден
    """
    # Проверяем существование клиента
    client = await get_client(session, client_id)
    if not client:
        return None

    restriction = Restriction(
        client_id=client_id,
        restriction_type=restriction_type,
        description=description
    )

    session.add(restriction)
    await session.commit()
    await session.refresh(restriction)
    return restriction


async def get_client_restrictions(
    session: AsyncSession, client_id: int
) -> List[Restriction]:
    """
    Получает все ограничения клиента
    
    Args:
        session: Сессия SQLAlchemy
        client_id: ID клиента
    
    Returns:
        Список ограничений клиента
    """
    result = await session.execute(
        select(Restriction).where(Restriction.client_id == client_id)
    )
    return result.scalars().all()


async def delete_restriction(session: AsyncSession, restriction_id: int) -> bool:
    """
    Удаляет ограничение
    
    Args:
        session: Сессия SQLAlchemy
        restriction_id: ID ограничения
    
    Returns:
        True, если ограничение было удалено, иначе False
    """
    result = await session.execute(
        delete(Restriction).where(Restriction.id == restriction_id)
    )
    await session.commit()
    return result.rowcount > 0
