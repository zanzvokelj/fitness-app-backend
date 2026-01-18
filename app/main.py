from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.exceptions import register_exception_handlers

from slowapi.middleware import SlowAPIMiddleware

from app.core.limiter import limiter
from app.core.config import settings
from app.routers import (
    auth,
    users,
    centers,
    class_types,
    sessions,
    bookings,
    admin,
    orders,
    tickets,
    ticket_plans,
    webhooks,
    debug,
)

app = FastAPI(title="Group Fitness Booking API")

register_exception_handlers(app)

# attach limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(centers.router)
app.include_router(class_types.router)
app.include_router(sessions.router)
app.include_router(bookings.router)
app.include_router(tickets.router)
app.include_router(admin.router)
app.include_router(ticket_plans.router)
app.include_router(webhooks.router)
app.include_router(orders.router)
app.include_router(debug.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}