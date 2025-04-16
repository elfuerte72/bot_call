"""
Модуль настройки логирования для проекта.
Создает логгеры для различных компонентов системы.
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Настройка логгера с ротацией файлов.
    
    Args:
        name: Имя логгера
        log_file: Имя файла для записи логов
        level: Уровень логирования
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создаем директорию для логов, если её нет
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Создаем обработчик с ротацией файлов (10MB на файл, до 5 файлов)    
    handler = RotatingFileHandler(
        os.path.join(log_dir, log_file), 
        maxBytes=10485760,  # 10MB 
        backupCount=5
    )
    handler.setFormatter(formatter)
    
    # Настраиваем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Проверяем, не добавлен ли уже обработчик с таким же именем файла
    handler_exists = False
    for h in logger.handlers:
        if isinstance(h, RotatingFileHandler) and h.baseFilename == handler.baseFilename:
            handler_exists = True
            break
    
    if not handler_exists:
        logger.addHandler(handler)
    
    return logger


# Создаем основные логгеры приложения
client_logger = setup_logger('client', 'client.log')
meal_plan_logger = setup_logger('meal_plan', 'meal_plan.log')
error_logger = setup_logger('error', 'error.log', level=logging.ERROR)
db_logger = setup_logger('database', 'database.log')
rag_logger = setup_logger('rag', 'rag.log')
openai_logger = setup_logger('openai', 'openai.log')


def log_client_action(client_id: Optional[int], action: str, details: str = "") -> None:
    """
    Логирование действий с клиентами.
    
    Args:
        client_id: ID клиента или None, если неприменимо
        action: Тип действия (добавление, редактирование, удаление и т.д.)
        details: Дополнительные детали действия
    """
    client_id_str = str(client_id) if client_id is not None else "Н/Д"
    client_logger.info(f"Клиент ID {client_id_str}: {action} | {details}")


def log_error(module: str, func: str, error: Exception) -> None:
    """
    Логирование ошибок.
    
    Args:
        module: Имя модуля, где произошла ошибка
        func: Имя функции, где произошла ошибка
        error: Объект исключения
    """
    error_logger.error(f"Ошибка в {module}.{func}: {str(error)}", exc_info=True)


def log_meal_plan(client_id: int, client_name: str, action: str, details: str = "") -> None:
    """
    Логирование действий с планами питания.
    
    Args:
        client_id: ID клиента
        client_name: Имя клиента
        action: Тип действия (генерация, сохранение и т.д.)
        details: Дополнительные детали действия
    """
    meal_plan_logger.info(f"Клиент ID {client_id} ({client_name}): {action} | {details}")
