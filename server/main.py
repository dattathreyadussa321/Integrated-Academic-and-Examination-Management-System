from fastapi import FastAPI
from debug_routes import router as debug_router
from attendance_routes import router as attendance_router

app = FastAPI(title="Academic Management API")

app.include_router(debug_router)
app.include_router(attendance_router)

@app.get("/")
def root():
    return {"message": "API is running"}
