from fastapi import Depends, FastAPI, HTTPException, status, Query, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
import uuid

from . import crud, models, schemas
from .database import SessionLocal, engine

# --- Constants and Setup ---
SECRET_KEY = "your_secret_key_here" # В реальном проекте это нужно вынести в переменные окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
UPLOADS_DIR = "uploads"

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="RealtyPro API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_realtor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    realtor = crud.get_realtor_by_email(db, email=token_data.email)
    if realtor is None:
        raise credentials_exception
    return realtor

# --- Role-based Dependencies ---
def get_current_active_realtor(current_user: models.Realtor = Depends(get_current_realtor)) -> models.Realtor:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_manager(current_user: models.Realtor = Depends(get_current_active_realtor)) -> models.Realtor:
    if current_user.role not in [models.RealtorRoleEnum.manager, models.RealtorRoleEnum.admin]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires manager or admin role")
    return current_user

def get_current_active_admin(current_user: models.Realtor = Depends(get_current_active_realtor)) -> models.Realtor:
    if current_user.role != models.RealtorRoleEnum.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin role")
    return current_user

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to RealtyPro API"}

# Auth
@app.post("/token", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    realtor = crud.authenticate_realtor(db, form_data.username, form_data.password)
    if not realtor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": realtor.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Users & Agencies
@app.post("/agencies/", response_model=schemas.Agency, tags=["Users & Agencies"])
def create_agency(agency: schemas.AgencyCreate, db: Session = Depends(get_db)):
    db_agency = crud.get_agency_by_name(db, name=agency.name)
    if db_agency:
        raise HTTPException(status_code=400, detail="Agency with this name already registered")
    return crud.create_agency(db=db, agency=agency)

@app.post("/realtors/", response_model=schemas.Realtor, tags=["Users & Agencies"])
def create_realtor(realtor: schemas.RealtorCreate, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_manager)):
    if crud.get_realtor_by_email(db, email=realtor.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_realtor(db=db, realtor=realtor, agency_id=current_user.agency_id)

@app.get("/users/me", response_model=schemas.Realtor, tags=["Users & Agencies"])
def read_users_me(current_user: models.Realtor = Depends(get_current_active_realtor)):
    return current_user

# Properties
@app.post("/properties/", response_model=schemas.Property, tags=["Properties"])
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.create_property(db=db, property=property, agency_id=current_user.agency_id, realtor_id=current_user.id)

@app.get("/properties/", response_model=List[schemas.Property], tags=["Properties"])
def read_properties(skip: int = 0, limit: int = Query(100, le=100), db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    properties = crud.get_properties(db, skip=skip, limit=limit)
    return properties

@app.get("/properties/{property_id}", response_model=schemas.Property, tags=["Properties"])
def read_property(property_id: int, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    db_property = crud.get_property(db, property_id)
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property

@app.patch("/properties/{property_id}", response_model=schemas.Property, tags=["Properties"])
def update_property_endpoint(property_id: int, property_update: schemas.PropertyUpdate, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    db_property = crud.update_property(db, property_id, property_update, current_user.id)
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property

@app.get("/properties/{property_id}/history", response_model=List[schemas.PropertyHistory], tags=["Properties"])
def property_history(property_id: int, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.get_property_history(db, property_id)

# Notifications
@app.get("/notifications/", response_model=List[schemas.Notification], tags=["Notifications"])
def get_my_notifications(unread_only: bool = False, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.get_notifications(db, realtor_id=current_user.id, unread_only=unread_only)

@app.post("/notifications/{notification_id}/read", response_model=schemas.Notification, tags=["Notifications"])
def mark_my_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    notification = crud.mark_notification_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# Calendar
@app.post("/calendar/", response_model=schemas.CalendarEvent, tags=["Calendar"])
def create_calendar_event_endpoint(event: schemas.CalendarEventCreate, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.create_calendar_event(db, event, current_user.id)

@app.get("/calendar/", response_model=List[schemas.CalendarEvent], tags=["Calendar"])
def read_calendar_events_endpoint(skip: int = 0, limit: int = Query(100, le=100), db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.get_calendar_events(db, current_user.id, skip=skip, limit=limit)

# Documents
@app.post("/documents/upload", response_model=schemas.Document, tags=["Documents"])
def upload_document_endpoint(property_id: int = None, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOADS_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    doc_create = schemas.DocumentCreate(filename=file.filename, filepath=file_path, agency_id=current_user.agency_id, property_id=property_id)
    return crud.create_document(db, doc_create, current_user.id)

# Stats
@app.get("/stats/me", response_model=schemas.RealtorStats, tags=["Stats"])
def get_my_stats_endpoint(db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_realtor)):
    return crud.get_realtor_stats(db, realtor_id=current_user.id)

# Events
@app.post("/events/", response_model=schemas.TrainingEvent, status_code=status.HTTP_201_CREATED, tags=["Events"])
def create_training_event_endpoint(event: schemas.TrainingEventCreate, db: Session = Depends(get_db), current_user: models.Realtor = Depends(get_current_active_admin)):
    return crud.create_training_event(db=db, event=event)

@app.get("/events/", response_model=List[schemas.TrainingEvent], tags=["Events"])
def read_training_events_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_training_events(db, skip=skip, limit=limit)