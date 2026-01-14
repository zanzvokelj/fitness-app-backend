from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, centers, class_types, sessions, bookings, admin
from app.db.database import engine
from app.db.base import Base
from app.models import User
from app.routers import tickets
from app.routers import ticket_plans
app = FastAPI(title="Group Fitness Booking API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(centers.router)
app.include_router(class_types.router)

app.include_router(sessions.router)

app.include_router(bookings.router)

app.include_router(tickets.router)

app.include_router(admin.router)

app.include_router(ticket_plans.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
"https://fitness-app-backend-c53u.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

