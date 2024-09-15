from fastapi import FastAPI
from api.routes import auth, calendar, chatbot
from core.exceptions import setup_exception_handlers
from db.couchbase_client import init_couchbase
from db.redis_client import init_redis

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_couchbase()
    await init_redis()

setup_exception_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)