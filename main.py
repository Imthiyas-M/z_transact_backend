from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.exception import setup_exception_handlers
from db.database import Base, engine
from routers.email_router import router as email_router
from routers import auth, oauth
from core.config import settings  # Assuming Settings now includes SESSION_SECRET

# Create database tables on startup (development only)
import logging



Base.metadata.create_all(bind=engine)

# logging.basicConfig(
#     filename='logs/server.log',
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# Initialize FastAPI app
app = FastAPI()

setup_exception_handlers(app)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="iiy90UMOx_bbhhhCj5s7M3cAPBIShUAEXME5fXaoMks",
    session_cookie="session"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080","https://6cea-106-51-51-220.ngrok-free.app"],  # Update as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router,  tags=["Auth"])
app.include_router(oauth.router,  tags=["OAuth"])
app.include_router(email_router, tags=["Email Conf"])


# Start app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")




