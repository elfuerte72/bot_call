import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Класс для загрузки документов различных форматов и разделения на чанки для RAG-системы"""

    def __init__(self, data_dir: str):
        """
        Инициализирует загрузчик документов

        Args:
            data_dir: Путь к директории с документами
        """
        self.data_dir = data_dir
        
        # Создаем оптимизированный разделитель текста для PDF-документов с фитнес-тематикой
        # Меньший размер чанка и большее перекрытие для лучшего поиска по небольшим фрагментам с плотной информацией
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Уменьшаем размер чанка для более точного поиска
            chunk_overlap=250,  # Увеличиваем перекрытие для сохранения контекста
            length_function=len,
            separators=[
                "\n\n",  # Сначала пытаемся разделить по двойным переносам строк (абзацы)
                "\n",    # Затем по одиночным переносам
                ". ",    # Затем по предложениям
                ", ",    # Затем по запятым
                " ",     # Затем по пробелам
                ""       # Наконец, если ничего не помогло, посимвольно
            ]
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Загружает PDF-файл и разбивает его на оптимальные чанки

        Args:
            file_path: Путь к PDF-файлу

        Returns:
            Список документов-чанков
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Добавляем метаданные - имя файла
            file_name = os.path.basename(file_path)
            for doc in documents:
                doc.metadata["source"] = file_name
                
            # Разбиваем на чанки с оптимальными настройками
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(
                f"Файл {file_name} успешно загружен и разбит на {len(chunks)} чанков"
            )
            return chunks
        except Exception as e:
            logger.error(f"Ошибка при загрузке PDF-файла {file_path}: {e}")
            return []

    def load_all_pdfs(self) -> List[Document]:
        """
        Загружает все PDF-файлы из директории с данными
        
        Returns:
            Список всех документов из PDF-файлов
        """
        all_docs = []
        pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"В директории {self.data_dir} не найдено PDF-файлов")
            return []
        
        for filename in pdf_files:
            file_path = os.path.join(self.data_dir, filename)
            try:
                pdf_docs = self.load_pdf(file_path)
                all_docs.extend(pdf_docs)
                logger.info(
                    f"Загружен документ {filename}, получено {len(pdf_docs)} чанков"
                )
            except Exception as e:
                logger.error(f"Ошибка при загрузке {filename}: {e}")

        logger.info(f"Всего загружено {len(all_docs)} чанков из {len(pdf_files)} PDF-файлов")
        return all_docs

    def process_documents(self) -> List[Document]:
        """
        Обрабатывает все документы в директории данных
        
        Returns:
            Список всех обработанных документов
        """
        logger.info(f"Начало обработки документов из директории {self.data_dir}")
        return self.load_all_pdfs()
