from enum import StrEnum

class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"

class EventCategory(StrEnum):
    CONFERENCE = "conference"
    MEETING = "meeting"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    WEBINAR = "webinar"
    OTHER = "other"
    

class UserRole(StrEnum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"

class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
