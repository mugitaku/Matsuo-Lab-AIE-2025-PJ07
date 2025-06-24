from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    PENDING_REJECTION = "pending_rejection"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reservations = relationship("Reservation", back_populates="user")

class GPUServer(Base):
    __tablename__ = "gpu_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    gpu_type = Column(String)
    gpu_count = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reservations = relationship("Reservation", back_populates="server")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("gpu_servers.id"), nullable=False)
    natural_language_request = Column(Text, nullable=False)
    purpose = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    priority_score = Column(Integer, default=50)
    status = Column(SQLAEnum(ReservationStatus), default=ReservationStatus.PENDING)
    ai_judgment_reason = Column(Text)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reservations")
    server = relationship("GPUServer", back_populates="reservations")
    conflicts = relationship("ReservationConflict", foreign_keys="ReservationConflict.reservation_id", back_populates="reservation")
    conflicting_with = relationship("ReservationConflict", foreign_keys="ReservationConflict.conflicting_reservation_id", back_populates="conflicting_reservation")

class ReservationConflict(Base):
    __tablename__ = "reservation_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    conflicting_reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    resolved = Column(Boolean, default=False)
    resolution_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reservation = relationship("Reservation", foreign_keys=[reservation_id], back_populates="conflicts")
    conflicting_reservation = relationship("Reservation", foreign_keys=[conflicting_reservation_id], back_populates="conflicting_with")