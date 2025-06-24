from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models.models import UserRole, ReservationStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class GPUServerBase(BaseModel):
    name: str
    description: Optional[str] = None
    gpu_type: Optional[str] = None
    gpu_count: int = 1

class GPUServerCreate(GPUServerBase):
    pass

class GPUServer(GPUServerBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    natural_language_request: str
    server_id: Optional[int] = None

class ReservationCreate(BaseModel):
    natural_language_request: str

class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    rejection_reason: Optional[str] = None

class Reservation(BaseModel):
    id: int
    user_id: int
    server_id: int
    natural_language_request: str
    purpose: Optional[str] = None
    start_time: datetime
    end_time: datetime
    priority_score: int
    status: ReservationStatus
    ai_judgment_reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: User
    server: GPUServer
    
    class Config:
        from_attributes = True

class ReservationConfirmRejection(BaseModel):
    confirm: bool
    reason: Optional[str] = None

class ConflictingReservation(BaseModel):
    reservation: Reservation
    conflicting_reservation: Reservation
    ai_recommendation: str