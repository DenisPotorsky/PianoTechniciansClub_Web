from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)

    # === НОВЫЕ ПОЛЯ ===
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
    # ==================

    hashed_password = Column(String, nullable=True)
    is_subscribed = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    access_requests = relationship("AccessRequest", foreign_keys="AccessRequest.user_id", back_populates="user")
    calculations = relationship("Calculation", back_populates="user", cascade="all, delete-orphan")


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


class RegulatingParam(Base):
    __tablename__ = "regulating_params"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    parameter = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Scale(Base):
    __tablename__ = "scales"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    chor_nummer = Column(Integer, nullable=False)
    saiten_im_chor = Column(Integer, nullable=True)
    laenge_mm = Column(Float, nullable=True)
    kern_mm = Column(Float, nullable=False)
    erste_wicklung_mm = Column(Float, nullable=True)
    zweite_wicklung_mm = Column(Float, nullable=True)
    typ = Column(String(50), nullable=True)
    year = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    user = relationship("User", foreign_keys=[user_id])