from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from enum import Enum
from pydantic import field_validator
import re


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./events.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_tables():
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EventStatus(str, Enum):
    open = "Open"
    closed = "Closed"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class EventBase(SQLModel):
    title: str = Field(min_length=1, description="Name of the event")
    venue: str = Field(description="Location where the event is held")
    capacity: int = Field(gt=0, description="Maximum number of participants")
    organizer: str = Field(description="Name of the organizer or department")
    status: EventStatus = Field(default=EventStatus.open, description="Open or Closed")


class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EventCreate(EventBase):
    pass


class EventUpdate(SQLModel):
    title: Optional[str] = None
    venue: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    organizer: Optional[str] = None
    status: Optional[EventStatus] = None


class ReservationBase(SQLModel):
    student_name: str = Field(min_length=1, description="Full name of the student")
    roll_number: str = Field(min_length=1, description="Student roll number")
    email: str = Field(description="Student email address")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(pattern, value):
            raise ValueError("Please provide a valid email address")
        return value


class Reservation(ReservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")


class ReservationCreate(ReservationBase):
    """What the client sends when booking a seat — event_id comes from the URL."""
    pass


class AvailabilityResponse(SQLModel):
    capacity: int
    booked: int
    remaining: int


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Campus Event Reservation API",
    description="Manage campus events and student seat reservations",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_tables()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_event_or_404(session: Session, event_id: int) -> Event:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    return event


# ---------------------------------------------------------------------------
# Event Routes
# ---------------------------------------------------------------------------

@app.post("/events", response_model=Event, status_code=201, tags=["Events"])
def create_event(event: EventCreate):
    """Create a new campus event."""
    with Session(engine) as session:
        db_event = Event(**event.model_dump())
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


@app.get("/events", response_model=list[Event], tags=["Events"])
def get_all_events():
    """Return all events."""
    with Session(engine) as session:
        return session.exec(select(Event)).all()


@app.get("/events/{event_id}", response_model=Event, tags=["Events"])
def get_event(event_id: int):
    """Return a single event by ID."""
    with Session(engine) as session:
        return get_event_or_404(session, event_id)


@app.put("/events/{event_id}", response_model=Event, tags=["Events"])
def update_event(event_id: int, event_data: EventUpdate):
    """Update event details."""
    with Session(engine) as session:
        event = get_event_or_404(session, event_id)
        updates = event_data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(event, field, value)
        session.add(event)
        session.commit()
        session.refresh(event)
        return event


@app.delete("/events/{event_id}", status_code=204, tags=["Events"])
def delete_event(event_id: int):
    """Delete an event (also removes its reservations)."""
    with Session(engine) as session:
        event = get_event_or_404(session, event_id)
        # Remove linked reservations first to keep DB clean
        reservations = session.exec(
            select(Reservation).where(Reservation.event_id == event_id)
        ).all()
        for r in reservations:
            session.delete(r)
        session.delete(event)
        session.commit()


# ---------------------------------------------------------------------------
# Reservation Routes
# ---------------------------------------------------------------------------

@app.post("/events/{event_id}/reserve", response_model=Reservation, status_code=201, tags=["Reservations"])
def reserve_seat(event_id: int, reservation: ReservationCreate):
    """
    Book a seat for an event.
    Checks: event exists → event is Open → seats are still available.
    """
    with Session(engine) as session:
        event = get_event_or_404(session, event_id)

        if event.status != EventStatus.open:
            raise HTTPException(
                status_code=400,
                detail="Reservations are closed for this event"
            )

        current_bookings = session.exec(
            select(Reservation).where(Reservation.event_id == event_id)
        ).all()

        if len(current_bookings) >= event.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"Sorry, this event is full. Capacity is {event.capacity} seats."
            )

        db_reservation = Reservation(**reservation.model_dump(), event_id=event_id)
        session.add(db_reservation)
        session.commit()
        session.refresh(db_reservation)
        return db_reservation


@app.get("/events/{event_id}/reservations", response_model=list[Reservation], tags=["Reservations"])
def get_event_reservations(event_id: int):
    """Return all reservations for a given event."""
    with Session(engine) as session:
        get_event_or_404(session, event_id)  # Confirm event exists
        reservations = session.exec(
            select(Reservation).where(Reservation.event_id == event_id)
        ).all()
        return reservations


@app.delete("/reservations/{reservation_id}", status_code=204, tags=["Reservations"])
def cancel_reservation(reservation_id: int):
    """Cancel (delete) a reservation by its ID."""
    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=404,
                detail=f"Reservation with id {reservation_id} not found"
            )
        session.delete(reservation)
        session.commit()


@app.get("/events/{event_id}/availability", response_model=AvailabilityResponse, tags=["Reservations"])
def check_availability(event_id: int):
    """Return total seats, booked seats, and remaining seats for an event."""
    with Session(engine) as session:
        event = get_event_or_404(session, event_id)
        booked = len(
            session.exec(
                select(Reservation).where(Reservation.event_id == event_id)
            ).all()
        )
        return AvailabilityResponse(
            capacity=event.capacity,
            booked=booked,
            remaining=event.capacity - booked
        )
