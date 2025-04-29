from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    statements = relationship("Statement", back_populates="user")

class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    statement_period_start = Column(DateTime)
    statement_period_end = Column(DateTime)
    issued_date = Column(DateTime)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Ensure user_id exists
    transaction_date = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    merchant_name = Column(String)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # Credit/Debit
    balance_after_transaction = Column(Float)
    category = Column(String)  # AI-generated
    created_at = Column(DateTime, default=datetime.utcnow)

    statement = relationship("Statement", back_populates="transactions")
    user = relationship("User")  # Ensure relation with User

# ✅ Ensure Category is Defined BEFORE TransactionCategorization
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class TransactionCategorization(Base):
    __tablename__ = "transaction_categorization"

    transaction_id = Column(Integer, ForeignKey("transactions.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    confidence_score = Column(Float, nullable=False)

    transaction = relationship("Transaction")
    category = relationship("Category")
