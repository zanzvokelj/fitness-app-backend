from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.main import limiter
from app.models.booking import Booking
from app.models.session import Session
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.booking import BookingOut
from app.core.dependencies import get_current_user, require_active_ticket_for_session

from app.core.email_resend import send_email
from app.core.email import render_template


router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["bookings"],
)


# -------------------------------------------------------------------
# CREATE BOOKING
# -------------------------------------------------------------------
@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_booking(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 🔒 Lock session
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.is_active.is_(True))
        .with_for_update()
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not available")

    # 🎟️ Validate ticket
    ticket = require_active_ticket_for_session(
        session=session,
        current_user=current_user,
        db=db,
    )

    # ⏳ WAITING LIST
    if session.booked_count >= session.capacity:
        booking = Booking(
            user_id=current_user.id,
            session_id=session_id,
            status="waiting",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    # ✅ ACTIVE BOOKING
    booking = Booking(
        user_id=current_user.id,
        session_id=session_id,
        status="active",
    )

    db.add(booking)
    session.booked_count += 1

    # 🎟️ Consume entry (only limited tickets)
    if ticket.remaining_entries is not None:
        ticket.remaining_entries -= 1
        if ticket.remaining_entries <= 0:
            ticket.is_active = False

    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already booked")

    db.commit()
    db.refresh(booking)

    # 📧 EMAIL — NEVER BREAK FLOW
    try:
        html = render_template(
            "booking_confirmation.html",
            email=current_user.email,
            class_name=session.class_type.name,
            date=session.start_time.strftime("%d.%m.%Y"),
            time=session.start_time.strftime("%H:%M"),
            center_name=session.class_type.center.name,
        )

        send_email(
            to_email=current_user.email,
            subject="Booking confirmed ✅",
            html_body=html,
        )
    except Exception as e:
        print("Booking email failed:", e)

    return booking


# -------------------------------------------------------------------
# CANCEL BOOKING
# -------------------------------------------------------------------
@router.delete("/{booking_id}", status_code=200)
@limiter.limit("10/minute")
def cancel_booking(
    booking_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.status.in_(["active", "waiting"]),
        )
        .with_for_update()
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    was_active = booking.status == "active"

    session = (
        db.query(Session)
        .filter(Session.id == booking.session_id)
        .with_for_update()
        .first()
    )

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.user_id == current_user.id,
            Ticket.center_id == session.center_id,
        )
        .order_by(Ticket.created_at.desc())
        .with_for_update()
        .first()
    )

    # ❌ Cancel booking
    booking.status = "cancelled"

    # ✅ Only if ACTIVE booking
    if was_active:
        session.booked_count -= 1

        if ticket and ticket.remaining_entries is not None:
            ticket.remaining_entries += 1
            ticket.is_active = True

        # ⏫ Promote next waiting user
        next_waiting = (
            db.query(Booking)
            .filter(
                Booking.session_id == session.id,
                Booking.status == "waiting",
            )
            .order_by(Booking.created_at)
            .with_for_update()
            .first()
        )

        if next_waiting:
            next_waiting.status = "active"
            session.booked_count += 1

    db.commit()

    # 📧 EMAIL (OPTIONAL)
    try:
        send_email(
            to_email=current_user.email,
            subject="Booking cancelled ❌",
            html_body="<p>Your booking was successfully cancelled.</p>",
        )
    except Exception as e:
        print("Cancel email failed:", e)

    return {"status": "cancelled"}


# -------------------------------------------------------------------
# MY BOOKINGS
# -------------------------------------------------------------------
@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Booking)
        .filter(
            Booking.user_id == current_user.id,
            Booking.status.in_(["active", "waiting"]),
        )
        .order_by(Booking.created_at.desc())
        .all()
    )