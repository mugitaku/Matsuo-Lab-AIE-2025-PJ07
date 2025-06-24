from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import models, schemas
from app.services.ai_service import AIService

class ReservationService:
    def __init__(self):
        self.ai_service = AIService()
    
    def check_conflicts(
        self, 
        db: Session, 
        server_id: int, 
        start_time: datetime, 
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None
    ) -> List[models.Reservation]:
        query = db.query(models.Reservation).filter(
            models.Reservation.server_id == server_id,
            models.Reservation.status.in_([
                models.ReservationStatus.CONFIRMED,
                models.ReservationStatus.PENDING
            ]),
            or_(
                and_(
                    models.Reservation.start_time <= start_time,
                    models.Reservation.end_time > start_time
                ),
                and_(
                    models.Reservation.start_time < end_time,
                    models.Reservation.end_time >= end_time
                ),
                and_(
                    models.Reservation.start_time >= start_time,
                    models.Reservation.end_time <= end_time
                )
            )
        )
        
        if exclude_reservation_id:
            query = query.filter(models.Reservation.id != exclude_reservation_id)
        
        return query.all()
    
    def create_reservation(
        self, 
        db: Session, 
        user_id: int,
        reservation_data: schemas.ReservationCreate
    ) -> models.Reservation:
        parsed_data = self.ai_service.parse_reservation_request(
            reservation_data.natural_language_request
        )
        
        server = self._select_best_server(db, parsed_data)
        if not server:
            raise ValueError("利用可能なサーバーがありません")
        
        conflicts = self.check_conflicts(
            db, 
            server.id, 
            parsed_data["start_time"], 
            parsed_data["end_time"]
        )
        
        priority_score = self.ai_service.calculate_priority(
            purpose=parsed_data["purpose"],
            duration=(parsed_data["end_time"] - parsed_data["start_time"]).total_seconds() / 3600
        )
        
        new_reservation = models.Reservation(
            user_id=user_id,
            server_id=server.id,
            natural_language_request=reservation_data.natural_language_request,
            purpose=parsed_data["purpose"],
            start_time=parsed_data["start_time"],
            end_time=parsed_data["end_time"],
            priority_score=priority_score,
            status=models.ReservationStatus.PENDING if not conflicts else models.ReservationStatus.PENDING
        )
        
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        
        if conflicts:
            self._handle_conflicts(db, new_reservation, conflicts)
        else:
            new_reservation.status = models.ReservationStatus.CONFIRMED
            db.commit()
        
        return new_reservation
    
    def _select_best_server(
        self, 
        db: Session, 
        parsed_data: dict
    ) -> Optional[models.GPUServer]:
        servers = db.query(models.GPUServer).filter(
            models.GPUServer.is_active == True
        ).all()
        
        if parsed_data.get("server_preference"):
            for server in servers:
                if parsed_data["server_preference"].lower() in server.name.lower():
                    return server
        
        for server in servers:
            conflicts = self.check_conflicts(
                db, 
                server.id, 
                parsed_data["start_time"], 
                parsed_data["end_time"]
            )
            if not conflicts:
                return server
        
        return servers[0] if servers else None
    
    def _handle_conflicts(
        self, 
        db: Session, 
        new_reservation: models.Reservation,
        conflicts: List[models.Reservation]
    ):
        for conflict in conflicts:
            recommendation = self.ai_service.judge_conflict(
                new_reservation, 
                conflict
            )
            
            conflict_record = models.ReservationConflict(
                reservation_id=new_reservation.id,
                conflicting_reservation_id=conflict.id,
                resolved=False
            )
            db.add(conflict_record)
            
            if recommendation["recommend_new"]:
                conflict.status = models.ReservationStatus.PENDING_REJECTION
                conflict.ai_judgment_reason = recommendation["reason"]
            else:
                new_reservation.status = models.ReservationStatus.REJECTED
                new_reservation.ai_judgment_reason = recommendation["reason"]
                new_reservation.rejection_reason = "優先度が低いため"
                break
        
        db.commit()
    
    def confirm_rejection(
        self, 
        db: Session, 
        reservation_id: int,
        user_id: int,
        confirm: bool,
        reason: Optional[str] = None
    ) -> models.Reservation:
        reservation = db.query(models.Reservation).filter(
            models.Reservation.id == reservation_id,
            models.Reservation.user_id == user_id,
            models.Reservation.status == models.ReservationStatus.PENDING_REJECTION
        ).first()
        
        if not reservation:
            raise ValueError("該当する予約が見つかりません")
        
        if confirm:
            reservation.status = models.ReservationStatus.CANCELLED
            reservation.rejection_reason = reason or "ユーザーが承認"
            
            conflicts = db.query(models.ReservationConflict).filter(
                models.ReservationConflict.conflicting_reservation_id == reservation_id,
                models.ReservationConflict.resolved == False
            ).all()
            
            for conflict in conflicts:
                conflict.resolved = True
                conflict.resolution_method = "user_confirmed"
                
                new_res = db.query(models.Reservation).filter(
                    models.Reservation.id == conflict.reservation_id
                ).first()
                if new_res and new_res.status == models.ReservationStatus.PENDING:
                    new_res.status = models.ReservationStatus.CONFIRMED
        else:
            reservation.status = models.ReservationStatus.CONFIRMED
            
            conflicts = db.query(models.ReservationConflict).filter(
                models.ReservationConflict.conflicting_reservation_id == reservation_id
            ).all()
            
            for conflict in conflicts:
                conflict.resolved = True
                conflict.resolution_method = "user_rejected"
                
                new_res = db.query(models.Reservation).filter(
                    models.Reservation.id == conflict.reservation_id
                ).first()
                if new_res:
                    new_res.status = models.ReservationStatus.REJECTED
                    new_res.rejection_reason = "既存予約が優先されました"
        
        db.commit()
        db.refresh(reservation)
        return reservation