from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models import models, schemas
from app.models.database import get_db
from app.utils import auth
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/reservations", tags=["reservations"])
reservation_service = ReservationService()

@router.get("/", response_model=List[schemas.Reservation])
def get_reservations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.ReservationStatus] = None,
    pending_rejection: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Reservation)
    
    if current_user.role != models.UserRole.ADMIN:
        query = query.filter(models.Reservation.user_id == current_user.id)
    
    if status:
        query = query.filter(models.Reservation.status == status)
    
    if pending_rejection:
        query = query.filter(
            models.Reservation.status == models.ReservationStatus.PENDING_REJECTION
        )
    
    reservations = query.offset(skip).limit(limit).all()
    return reservations

@router.post("/", response_model=schemas.Reservation)
def create_reservation(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    try:
        new_reservation = reservation_service.create_reservation(
            db,
            current_user.id,
            reservation
        )
        return new_reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{reservation_id}", response_model=schemas.Reservation)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    if current_user.role != models.UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="アクセス権限がありません")
    
    return reservation

@router.put("/{reservation_id}", response_model=schemas.Reservation)
def update_reservation(
    reservation_id: int,
    reservation_update: schemas.ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    if current_user.role != models.UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="アクセス権限がありません")
    
    if reservation_update.status:
        reservation.status = reservation_update.status
    if reservation_update.rejection_reason:
        reservation.rejection_reason = reservation_update.rejection_reason
    
    db.commit()
    db.refresh(reservation)
    return reservation

@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    if current_user.role != models.UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="アクセス権限がありません")
    
    reservation.status = models.ReservationStatus.CANCELLED
    db.commit()
    
    return {"message": "予約をキャンセルしました"}

@router.post("/{reservation_id}/confirm-rejection", response_model=schemas.Reservation)
def confirm_rejection(
    reservation_id: int,
    confirmation: schemas.ReservationConfirmRejection,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    try:
        updated_reservation = reservation_service.confirm_rejection(
            db,
            reservation_id,
            current_user.id,
            confirmation.confirm,
            confirmation.reason
        )
        return updated_reservation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))