# backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, Float, JSON, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy.sql import func

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ticker = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # analyst | ceo | group_admin
    group_name = Column(String, nullable=True)  # optional
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class UserCompany(Base):
    __tablename__ = "user_companies"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), primary_key=True)

class BalanceSheet(Base):
    __tablename__ = "balance_sheets"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    period_label = Column(String)  # e.g. FY2024 or 2024-03-31 (simple)
    raw_json = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    company = relationship("Company", backref="balance_sheets")

class FinancialLine(Base):
    __tablename__ = "financial_lines"
    id = Column(Integer, primary_key=True, index=True)
    balance_sheet_id = Column(Integer, ForeignKey("balance_sheets.id"))
    line_code = Column(String, index=True)
    line_label = Column(String)
    amount = Column(Float)
    currency = Column(String, default="INR")
