from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Enum as SqlEnum, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    realtors = relationship("Realtor", back_populates="agency")


class RealtorRoleEnum(enum.Enum):
    realtor = "realtor"
    manager = "manager"  # Руководитель агентства
    admin = "admin"      # Администратор платформы


class Realtor(Base):
    __tablename__ = "realtors"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SqlEnum(RealtorRoleEnum), default=RealtorRoleEnum.realtor, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    agency_id = Column(Integer, ForeignKey("agencies.id"))

    agency = relationship("Agency", back_populates="realtors")


class PropertyStatusEnum(enum.Enum):
    for_sale = "for_sale"
    reserved = "reserved"
    sold = "sold"
    archived = "archived"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)
    address = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(SqlEnum(PropertyStatusEnum), default=PropertyStatusEnum.for_sale)
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agency = relationship("Agency")
    realtor = relationship("Realtor")
    history = relationship("PropertyHistory", back_populates="property")


class PropertyHistory(Base):
    __tablename__ = "property_history"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    action = Column(String)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="history")
    realtor = relationship("Realtor")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    realtor = relationship("Realtor")


class CalendarEventType(enum.Enum):
    viewing = "viewing"
    deal = "deal"
    other = "other"


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    event_type = Column(SqlEnum(CalendarEventType), default=CalendarEventType.viewing)
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property")
    realtor = relationship("Realtor")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String, unique=True)
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    realtor = relationship("Realtor")
    agency = relationship("Agency")
    property = relationship("Property")


class TrainingEvent(Base):
    __tablename__ = "training_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    speaker = Column(String) # Имя спикера или организатора
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    is_online = Column(Boolean, default=False)
    link = Column(String, nullable=True) # Ссылка на вебинар/трансляцию
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    registrations = relationship("EventRegistration", back_populates="event")


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("training_events.id"))
    realtor_id = Column(Integer, ForeignKey("realtors.id"))
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship("TrainingEvent", back_populates="registrations")
    realtor = relationship("Realtor") 