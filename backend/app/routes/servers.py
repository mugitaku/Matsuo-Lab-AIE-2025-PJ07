from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import models, schemas
from app.models.database import get_db
from app.utils import auth

router = APIRouter(prefix="/api/servers", tags=["servers"])

@router.get("/", response_model=List[schemas.GPUServer])
def get_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    servers = db.query(models.GPUServer).filter(
        models.GPUServer.is_active == True
    ).offset(skip).limit(limit).all()
    return servers

@router.post("/", response_model=schemas.GPUServer)
def create_server(
    server: schemas.GPUServerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_admin_user)
):
    db_server = db.query(models.GPUServer).filter(
        models.GPUServer.name == server.name
    ).first()
    
    if db_server:
        raise HTTPException(status_code=400, detail="サーバー名が既に存在します")
    
    new_server = models.GPUServer(**server.dict())
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return new_server

@router.get("/{server_id}", response_model=schemas.GPUServer)
def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    server = db.query(models.GPUServer).filter(
        models.GPUServer.id == server_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="サーバーが見つかりません")
    
    return server

@router.put("/{server_id}", response_model=schemas.GPUServer)
def update_server(
    server_id: int,
    server_update: schemas.GPUServerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_admin_user)
):
    server = db.query(models.GPUServer).filter(
        models.GPUServer.id == server_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="サーバーが見つかりません")
    
    for key, value in server_update.dict().items():
        setattr(server, key, value)
    
    db.commit()
    db.refresh(server)
    return server

@router.delete("/{server_id}")
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_admin_user)
):
    server = db.query(models.GPUServer).filter(
        models.GPUServer.id == server_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="サーバーが見つかりません")
    
    server.is_active = False
    db.commit()
    
    return {"message": "サーバーを無効化しました"}