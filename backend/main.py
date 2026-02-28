from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import referrals, auth, hospitals, chat, network  # <--- IMPORT CHAT
from app.routers import referral


app = FastAPI(title="Hospital Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(referrals.router, prefix="/api/referrals", tags=["Referrals"])
app.include_router(hospitals.router, prefix="/api/hospital", tags=["Hospital Dashboard"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Manager"]) # <--- ADD ROUTER
app.include_router(referral.router, prefix="/api/referral", tags=["Ambulance Referral"])
app.include_router(network.router, prefix="/api/network", tags=["Global Network"])


@app.get("/")
def home():
    return {"message": "Hospital System API is Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)