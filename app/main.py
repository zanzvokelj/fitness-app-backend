from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

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
from app.core.config import settings

# -------------------------------------------------
# 🔒 RATE LIMITER (IP-based)
# -------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Group Fitness Booking API")

# attach limiter to app state
app.state.limiter = limiter

# slowapi middleware
app.add_middleware(SlowAPIMiddleware)

# rate limit error handler
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."},
    )

# -------------------------------------------------
# 🌍 CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# 🚦 ROUTERS
# -------------------------------------------------
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

# -------------------------------------------------
#  HEALTH CHECK
# -------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}