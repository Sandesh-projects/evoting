from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.vote import router as vote_router
from routes.admin import router as admin_router

app = FastAPI(title="E-Voting API", description="Secure Blockchain Voting System")

# 🔒 Security Enhancement: Add CORS Middleware
# Allows a frontend (like React or Vanilla JS) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, change "*" to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Include Routers
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(vote_router, prefix="/election", tags=["Voting"])

@app.get("/", tags=["Health"])
def home():
    return {
        "status": "Online", 
        "message": "E-Voting Backend is Running Securely"
    }