"""
Модуль для работы с клиентами. 
Содержит бизнес-логику обработки данных клиентов, обновления и проверки.
"""
from typing import Dict, Any, Tuple, Optional, List
from database.db_handlers import get_client_by_id, update_client_data, add_client, get_clients
from services.nutrition import calculate_macros
from utils.logger import log_client_action, log_error


async def update_client(client_id: int, client_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Обновляет данные клиента с пересчетом КБЖУ.
    
    Args:
        client_id: ID клиента
        client_data: Словарь с новыми данными клиента
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]], str]: (успех, данные о макросах, сообщение)
    """
    try:
        # Рассчитываем новые КБЖУ
        macros = calculate_macros(
            gender=client_data.get('gender'),
            age=client_data.get('age'),
            height=client_data.get('height'),
            weight=client_data.get('weight'),
            activity_factor=client_data.get('activity_factor'),
            goal=client_data.get('goal')
        )
        
        # Объединяем данные клиента и КБЖУ
        update_data = {
            **client_data,
            "calories": macros['calories'],
            "protein": macros['protein'],
            "fat": macros['fat'],
            "carbs": macros['carbs']
        }
        
        # Обновляем в БД
        updated_client = await update_client_data(client_id, update_data)
        if not updated_client:
            log_client_action(client_id, "ошибка обновления", "Клиент не найден в БД")
            return False, None, "Не удалось обновить данные клиента"
        
        log_client_action(client_id, "обновление", f"КБЖУ: {macros['calories']} ккал")
        return True, macros, "Данные клиента успешно обновлены"
    except Exception as e:
        log_error("client_service", "update_client", e)
        return False, None, f"Ошибка при обновлении клиента: {str(e)}"


async def add_new_client(client_data: Dict[str, Any]) -> Tuple[bool, Optional[int], str]:
    """
    Добавляет нового клиента в базу данных.
    
    Args:
        client_data: Данные нового клиента
        
    Returns:
        Tuple[bool, Optional[int], str]: (успех, ID нового клиента, сообщение)
    """
    try:
        # Добавляем клиента в базу данных
        client_id = await add_client(
            name=client_data['name'],
            age=client_data['age'],
            gender=client_data['gender'],
            height=client_data['height'],
            weight=client_data['weight'],
            activity=client_data['activity'],
            goal=client_data['goal'],
            calories=client_data['macros']['calories'],
            protein=client_data['macros']['protein'],
            fat=client_data['macros']['fat'],
            carbs=client_data['macros']['carbs']
        )
        
        log_client_action(client_id, "добавление", 
                          f"Имя: {client_data['name']}, Цель: {client_data['goal']}")
        
        return True, client_id, f"Клиент {client_data['name']} успешно добавлен в базу данных!"
    except Exception as e:
        log_error("client_service", "add_new_client", e)
        return False, None, f"Ошибка при добавлении клиента: {str(e)}"


async def delete_client_by_id(client_id: int) -> Tuple[bool, str]:
    """
    Удаляет клиента из базы данных.
    
    Args:
        client_id: ID клиента для удаления
        
    Returns:
        Tuple[bool, str]: (успех, сообщение)
    """
    try:
        from database.db_handlers import delete_client
        
        # Получаем данные клиента перед удалением для лога
        client = await get_client_by_id(client_id)
        if not client:
            return False, "Клиент не найден"
        
        # Удаляем клиента
        result = await delete_client(client_id)
        if result:
            log_client_action(client_id, "удаление", f"Имя: {client.name}")
            return True, "Клиент успешно удален"
        else:
            log_client_action(client_id, "ошибка удаления", "Не удалось удалить из БД")
            return False, "Не удалось удалить клиента"
    except Exception as e:
        log_error("client_service", "delete_client_by_id", e)
        return False, f"Ошибка при удалении клиента: {str(e)}"


async def get_client_details(client_id: int) -> Tuple[bool, Optional[Any], str]:
    """
    Получает подробную информацию о клиенте.
    
    Args:
        client_id: ID клиента
        
    Returns:
        Tuple[bool, Optional[Any], str]: (успех, данные клиента, сообщение)
    """
    try:
        client = await get_client_by_id(client_id)
        if not client:
            return False, None, "Клиент не найден"
        
        log_client_action(client_id, "просмотр", f"Имя: {client.name}")
        return True, client, "Данные клиента получены"
    except Exception as e:
        log_error("client_service", "get_client_details", e)
        return False, None, f"Ошибка при получении данных клиента: {str(e)}"


async def get_all_clients() -> Tuple[bool, Optional[List[Any]], str]:
    """
    Получает список всех клиентов.
    
    Returns:
        Tuple[bool, Optional[List[Any]], str]: (успех, список клиентов, сообщение)
    """
    try:
        clients = await get_clients()
        if not clients:
            return False, None, "Список клиентов пуст"
        
        return True, clients, f"Получено {len(clients)} клиентов"
    except Exception as e:
        log_error("client_service", "get_all_clients", e)
        return False, None, f"Ошибка при получении списка клиентов: {str(e)}"
