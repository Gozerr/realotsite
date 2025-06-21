from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel
from .models import RealtorRoleEnum


# Realtor Schemas
class RealtorBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class RealtorCreate(RealtorBase):
    password: str
    role: RealtorRoleEnum = RealtorRoleEnum.realtor


class Realtor(RealtorBase):
    id: int
    is_active: bool
    role: RealtorRoleEnum
    agency_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Agency Schemas
class AgencyBase(BaseModel):
    name: str


class AgencyCreate(AgencyBase):
    pass


class Agency(AgencyBase):
    id: int
    created_at: datetime
    realtors: List[Realtor] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class PropertyStatusEnum(str, Enum):
    for_sale = "for_sale"
    reserved = "reserved"
    sold = "sold"
    archived = "archived"


class PropertyBase(BaseModel):
    title: str
    description: str | None = None
    price: int
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: PropertyStatusEnum = PropertyStatusEnum.for_sale


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    address: str | None = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: PropertyStatusEnum | None = None


class Property(PropertyBase):
    id: int
    agency_id: int
    realtor_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PropertyHistory(BaseModel):
    id: int
    property_id: int
    realtor_id: int
    action: str
    old_value: str | None = None
    new_value: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    message: str


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    realtor_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarEventType(str, Enum):
    viewing = "viewing"
    deal = "deal"
    other = "other"


class CalendarEventBase(BaseModel):
    property_id: int
    event_type: CalendarEventType = CalendarEventType.viewing
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEvent(CalendarEventBase):
    id: int
    realtor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    filepath: str
    agency_id: int
    property_id: int | None = None


class Document(DocumentBase):
    id: int
    realtor_id: int
    agency_id: int
    property_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas for Stats & KPI
class RealtorStats(BaseModel):
    realtor_id: int
    full_name: str
    properties_for_sale: int
    properties_sold: int
    total_sales_value: int


class AgencyStats(BaseModel):
    agency_id: int
    name: str
    total_realtors: int
    properties_for_sale: int
    properties_sold: int
    total_sales_value: int


# Schemas for Training Events
class TrainingEventBase(BaseModel):
    title: str
    description: str | None = None
    speaker: str
    start_time: datetime
    end_time: datetime
    is_online: bool = False
    link: str | None = None


class TrainingEventCreate(TrainingEventBase):
    pass


class TrainingEvent(TrainingEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventRegistration(BaseModel):
    id: int
    event_id: int
    realtor_id: int
    registered_at: datetime

    class Config:
        from_attributes = True 