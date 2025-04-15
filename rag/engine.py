import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from config.config import load_config
from rag.loaders import DocumentLoader


class RAGEngine:
    """Класс для работы с RAG-системой"""
    
    def __init__(self, data_dir: str = None):
        """
        Инициализирует RAG-систему
        
        Args:
            data_dir: Путь к директории с документами. Если None, будет использован 
                      путь из переменной окружения или значение по умолчанию.
        """
        self.config = load_config()
        self.openai_api_key = self.config.openai.api_key
        
        # Устанавливаем директорию с данными
        if data_dir is None:
            # По умолчанию используем директорию 'data' в корне проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, 'data')
        else:
            self.data_dir = data_dir
        
        # Инициализируем загрузчик документов
        self.loader = DocumentLoader(self.data_dir)
        
        # Инициализируем модель для эмбеддингов
        import openai
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-ada-002",
            openai_api_base="https://api.openai.com/v1"
        )
        
        # Векторное хранилище будет инициализировано при вызове метода initialize
        self.vectorstore = None
        
        # Путь для сохранения индекса FAISS
        self.index_path = os.path.join(self.data_dir, 'faiss_index')
    
    async def initialize(self, force_reload: bool = False) -> None:
        """
        Инициализирует RAG-систему, загружая документы и создавая индекс
        
        Args:
            force_reload: Если True, принудительно перезагрузит документы,
                          иначе попытается загрузить существующий индекс
        """
        # Проверяем наличие сохраненного индекса
        if os.path.exists(self.index_path) and not force_reload:
            try:
                # Загружаем существующий индекс
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings
                )
                print(f"Индекс успешно загружен из {self.index_path}")
                return
            except Exception as e:
                print(f"Не удалось загрузить индекс: {e}")
                # Если не удалось загрузить, создадим новый
        
        # Загружаем и обрабатываем документы
        documents = self.loader.process_documents()
        
        if not documents:
            raise ValueError("Не удалось загрузить документы для индексации")
        
        # Создаем векторное хранилище
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # Сохраняем индекс
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.vectorstore.save_local(self.index_path)
        print(f"Индекс успешно создан и сохранен в {self.index_path}")
    
    async def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Выполняет поиск релевантных документов по запросу
        
        Args:
            query: Текст запроса
            k: Количество документов для возврата
            
        Returns:
            Список релевантных документов
        """
        if self.vectorstore is None:
            await self.initialize()
        
        return self.vectorstore.similarity_search(query, k=k)
    
    async def generate_answer(self, query: str, use_retrieval: bool = True) -> str:
        """
        Генерирует ответ на основе запроса, используя RAG-систему
        
        Args:
            query: Текст запроса
            use_retrieval: Использовать ли поиск по документам
            
        Returns:
            Сгенерированный ответ
        """
        if self.vectorstore is None:
            await self.initialize()
        
        # Настраиваем языковую модель
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Используем GPT-4.1 nano (на момент написания кода соответствует gpt-4o-mini)
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        if use_retrieval:
            # Создаем шаблон промпта для RAG
            template = """
            Ты - ассистент фитнес-тренера, который отвечает на вопросы о питании, тренировках 
            и здоровье. Используй приведенную ниже информацию для ответа на вопрос пользователя. 
            Если информации недостаточно, отвечай на основе общих знаний по теме, не выдумывая факты.
            Пиши в дружелюбном тоне, по-русски, можешь иногда использовать актуальные мемы, 
            чтобы сделать общение более интересным. Не включай в ответ ссылки на источники.
            
            Контекст: {context}
            
            Вопрос: {question}
            
            Ответ:
            """
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            
            # Создаем цепочку для ответа на вопрос с использованием RAG
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=False
            )
            
            response = qa_chain({"query": query})
            return response["result"]
        else:
            # Генерация ответа только с использованием LLM без извлечения контекста
            response = llm.invoke(query)
            return response.content
