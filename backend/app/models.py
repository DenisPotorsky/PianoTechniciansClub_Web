from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_subscribed = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    access_requests = relationship("AccessRequest", foreign_keys="AccessRequest.user_id", back_populates="user")
    calculations = relationship("Calculation", back_populates="user")


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String, default="pending")
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="access_requests")
    processed_by_user = relationship("User", foreign_keys=[processed_by])


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    country = Column(String, nullable=False)
    info = Column(Text, nullable=True)
    type = Column(String, default="foreign")

    serial_ranges = relationship("SerialRange", back_populates="brand", cascade="all, delete-orphan")


class SerialRange(Base):
    __tablename__ = "serial_ranges"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    serial_start = Column(Integer, nullable=False)
    serial_end = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    brand = relationship("Brand", back_populates="serial_ranges")


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    winding_type = Column(String, nullable=False)
    core_diameter = Column(Float, nullable=False)
    total_diameter = Column(Float, nullable=False)
    string_length = Column(Float, nullable=False)
    result_data = Column(Text, nullable=False)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calculations")


# ============ РЕГУЛИРОВОЧНЫЕ ПАРАМЕТРЫ ============
class RegulatingParam(Base):
    """Таблица с параметрами настройки роялей"""
    __tablename__ = "regulating_params"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    parameter = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)