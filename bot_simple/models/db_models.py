from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)

    is_approved = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    calculations = relationship("Calculation", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    winding_type = Column(String, nullable=False)
    core_diameter = Column(Float, nullable=False)
    total_diameter = Column(Float, nullable=False)
    string_length = Column(Float, nullable=False)
    result_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calculations")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="subscription")