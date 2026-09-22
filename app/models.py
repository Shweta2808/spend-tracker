from sqlalchemy import Column, Integer, String, Float, Date, Index

from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    note = Column(String, nullable=True)
    date = Column(Date, nullable=False)

    __table_args__ = (
        Index("ix_expenses_category", "category"),
        Index("ix_expenses_date", "date"),
    )
