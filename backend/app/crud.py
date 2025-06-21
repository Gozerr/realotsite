from passlib.context import CryptContext
from sqlalchemy.orm import Session
import shutil
import os
from sqlalchemy import func

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_agency_by_name(db: Session, name: str):
    return db.query(models.Agency).filter(models.Agency.name == name).first()


def create_agency(db: Session, agency: schemas.AgencyCreate):
    db_agency = models.Agency(name=agency.name)
    db.add(db_agency)
    db.commit()
    db.refresh(db_agency)
    return db_agency


def create_realtor(
    db: Session, realtor: schemas.RealtorCreate, agency_id: int
):
    hashed_password = pwd_context.hash(realtor.password)
    db_realtor = models.Realtor(
        email=realtor.email,
        full_name=realtor.full_name,
        hashed_password=hashed_password,
        agency_id=agency_id,
    )
    db.add(db_realtor)
    db.commit()
    db.refresh(db_realtor)
    return db_realtor


def get_realtor_by_email(db: Session, email: str):
    return db.query(models.Realtor).filter(models.Realtor.email == email).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_property(db: Session, property: schemas.PropertyCreate, agency_id: int, realtor_id: int):
    db_property = models.Property(
        title=property.title,
        description=property.description,
        price=property.price,
        address=property.address,
        status=property.status,
        agency_id=agency_id,
        realtor_id=realtor_id,
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    add_property_history(db, db_property.id, realtor_id, "create", None, str(property.dict()))
    return db_property


def get_property(db: Session, property_id: int):
    return db.query(models.Property).filter(models.Property.id == property_id).first()


def get_properties(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Property).offset(skip).limit(limit).all()


def create_notification(db: Session, realtor_id: int, message: str):
    notification = models.Notification(realtor_id=realtor_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(db: Session, realtor_id: int, unread_only: bool = False):
    query = db.query(models.Notification).filter(models.Notification.realtor_id == realtor_id)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    return query.order_by(models.Notification.created_at.desc()).all()


def mark_notification_read(db: Session, notification_id: int, realtor_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.realtor_id == realtor_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


def update_property(db: Session, property_id: int, property_update: schemas.PropertyUpdate, realtor_id: int):
    db_property = get_property(db, property_id)
    if not db_property:
        return None

    old_values = {field: getattr(db_property, field) for field in property_update.dict(exclude_unset=True).keys()}
    old_status = db_property.status

    # Обновляем поля
    for field, value in property_update.dict(exclude_unset=True).items():
        setattr(db_property, field, value)
    
    db.add(db_property)
    db.commit()
    db.refresh(db_property)

    # Логируем историю
    for field, old_value in old_values.items():
        new_value = getattr(db_property, field)
        if old_value != new_value:
            action = f"update_{field}"
            # Для enum нужно брать .value
            if isinstance(old_value, models.PropertyStatusEnum):
                old_value = old_value.value
            if isinstance(new_value, models.PropertyStatusEnum):
                new_value = new_value.value
            
            add_property_history(db, property_id, realtor_id, action, str(old_value), str(new_value))

    # Создаем уведомление, если статус изменился
    if db_property.status != old_status:
        agency_realtors = db.query(models.Realtor).filter(models.Realtor.agency_id == db_property.agency_id).all()
        for realtor in agency_realtors:
            create_notification(
                db,
                realtor_id=realtor.id,
                message=f"Статус объекта '{db_property.title}' изменен на {db_property.status.value}"
            )

    return db_property


def add_property_history(db: Session, property_id: int, realtor_id: int, action: str, old_value: str, new_value: str):
    history = models.PropertyHistory(
        property_id=property_id,
        realtor_id=realtor_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(history)
    db.commit()


def get_property_history(db: Session, property_id: int):
    return db.query(models.PropertyHistory).filter(models.PropertyHistory.property_id == property_id).all()


def create_calendar_event(db: Session, event: schemas.CalendarEventCreate, realtor_id: int):
    db_event = models.CalendarEvent(
        property_id=event.property_id,
        event_type=event.event_type,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        realtor_id=realtor_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_calendar_events(db: Session, realtor_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.CalendarEvent).filter(models.CalendarEvent.realtor_id == realtor_id).offset(skip).limit(limit).all()


def get_calendar_event(db: Session, event_id: int, realtor_id: int):
    return db.query(models.CalendarEvent).filter(models.CalendarEvent.id == event_id, models.CalendarEvent.realtor_id == realtor_id).first()


def update_calendar_event(db: Session, event_id: int, event_update: schemas.CalendarEventCreate, realtor_id: int):
    db_event = get_calendar_event(db, event_id, realtor_id)
    if not db_event:
        return None
    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, field, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_calendar_event(db: Session, event_id: int, realtor_id: int):
    db_event = get_calendar_event(db, event_id, realtor_id)
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True


def create_document(db: Session, doc: schemas.DocumentCreate, realtor_id: int):
    db_doc = models.Document(
        filename=doc.filename,
        filepath=doc.filepath,
        agency_id=doc.agency_id,
        realtor_id=realtor_id,
        property_id=doc.property_id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def get_document(db: Session, doc_id: int, agency_id: int):
    return db.query(models.Document).filter(
        models.Document.id == doc_id,
        models.Document.agency_id == agency_id
    ).first()


def get_documents_by_agency(db: Session, agency_id: int):
    return db.query(models.Document).filter(models.Document.agency_id == agency_id).all()


def delete_document(db: Session, doc_id: int, agency_id: int):
    doc = get_document(db, doc_id, agency_id)
    if not doc:
        return False
    try:
        # Удаляем физический файл
        shutil.rmtree(doc.filepath, ignore_errors=True) # Используем rmtree, чтобы удалить папку, если она пуста
        if os.path.exists(doc.filepath):
             os.remove(doc.filepath)
    except OSError as e:
        print(f"Error deleting file {doc.filepath}: {e}")

    db.delete(doc)
    db.commit()
    return True


def get_realtor_stats(db: Session, realtor_id: int):
    realtor = db.query(models.Realtor).filter(models.Realtor.id == realtor_id).first()
    if not realtor:
        return None

    properties_for_sale = db.query(models.Property).filter(
        models.Property.realtor_id == realtor_id,
        models.Property.status == 'for_sale'
    ).count()

    properties_sold = db.query(models.Property).filter(
        models.Property.realtor_id == realtor_id,
        models.Property.status == 'sold'
    ).count()

    total_sales_value = db.query(func.sum(models.Property.price)).filter(
        models.Property.realtor_id == realtor_id,
        models.Property.status == 'sold'
    ).scalar() or 0

    return schemas.RealtorStats(
        realtor_id=realtor_id,
        full_name=realtor.full_name,
        properties_for_sale=properties_for_sale,
        properties_sold=properties_sold,
        total_sales_value=total_sales_value
    )


def get_agency_stats(db: Session, agency_id: int):
    agency = db.query(models.Agency).filter(models.Agency.id == agency_id).first()
    if not agency:
        return None

    total_realtors = db.query(models.Realtor).filter(models.Realtor.agency_id == agency_id).count()

    properties_for_sale = db.query(models.Property).filter(
        models.Property.agency_id == agency_id,
        models.Property.status == 'for_sale'
    ).count()

    properties_sold = db.query(models.Property).filter(
        models.Property.agency_id == agency_id,
        models.Property.status == 'sold'
    ).count()

    total_sales_value = db.query(func.sum(models.Property.price)).filter(
        models.Property.agency_id == agency_id,
        models.Property.status == 'sold'
    ).scalar() or 0

    return schemas.AgencyStats(
        agency_id=agency_id,
        name=agency.name,
        total_realtors=total_realtors,
        properties_for_sale=properties_for_sale,
        properties_sold=properties_sold,
        total_sales_value=total_sales_value
    )


# CRUD for Training Events
def create_training_event(db: Session, event: schemas.TrainingEventCreate):
    db_event = models.TrainingEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_training_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TrainingEvent).order_by(models.TrainingEvent.start_time).offset(skip).limit(limit).all()

def get_training_event(db: Session, event_id: int):
    return db.query(models.TrainingEvent).filter(models.TrainingEvent.id == event_id).first()

def register_for_event(db: Session, event_id: int, realtor_id: int):
    # Проверяем, что риэлтор еще не зарегистрирован
    existing_registration = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id,
        models.EventRegistration.realtor_id == realtor_id
    ).first()
    if existing_registration:
        return None # Уже зарегистрирован

    db_registration = models.EventRegistration(event_id=event_id, realtor_id=realtor_id)
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration

def get_registrations_for_event(db: Session, event_id: int):
    return db.query(models.EventRegistration).filter(models.EventRegistration.event_id == event_id).all()

def authenticate_realtor(db: Session, email: str, password: str):
    realtor = get_realtor_by_email(db, email=email)
    if not realtor or not verify_password(password, realtor.hashed_password):
        return None
    return realtor