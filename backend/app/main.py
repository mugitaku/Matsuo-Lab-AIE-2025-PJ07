from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import engine, Base
from app.routes import auth, reservations, servers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GPU Server Reservation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reservations.router)
app.include_router(servers.router)

@app.get("/")
def read_root():
    return {"message": "GPU Server Reservation System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)