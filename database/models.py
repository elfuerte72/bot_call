from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from database.base import Base
from datetime import date

class Client(Base):
    """Модель для хранения данных о клиентах"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # 'мужской' или 'женский'
    height = Column(Float, nullable=False)  # рост в см
    weight = Column(Float, nullable=False)  # вес в кг
    activity_level = Column(String(50), nullable=False)  # уровень активности
    goal = Column(String(50), nullable=False)  # цель (похудение/набор/поддержание)

    # Рассчитанные значения КБЖУ
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)

    # Отношения
    meal_plans = relationship(
        "MealPlan", back_populates="client", cascade="all, delete-orphan"
    )
    restrictions = relationship(
        "Restriction", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', goal='{self.goal}')>"


class MealPlan(Base):
    """Модель для хранения планов питания"""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    date_created = Column(Date, nullable=False, default=date.today)
    content = Column(Text, nullable=False)  # JSON-строка плана питания

    # Отношения
    client = relationship("Client", back_populates="meal_plans")

    def __repr__(self):
        return (f"<MealPlan(id={self.id}, client_id={self.client_id}, "
                f"date_created='{self.date_created}')>")


class Restriction(Base):
    """Модель для хранения ограничений/аллергий клиентов"""
    __tablename__ = "restrictions"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    restriction_type = Column(String(50), nullable=False)  # тип ограничения
    description = Column(Text, nullable=False)

    # Отношения
    client = relationship("Client", back_populates="restrictions")

    def __repr__(self):
        return f"<Restriction(id={self.id}, client_id={self.client_id}, type='{self.restriction_type}')>"
