from fastapi import FastAPI
from .routers import openai_router, calendar_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='VGCC_backend',
    description='API service using FastAPI, with integrated OpenAI and Calendar functionalities',
    docs_url="/docs",
    redoc_url=None
)

# Configure CORS settings
origins = [
    "http://localhost",
    "http://localhost:4200",  # Angular frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"]
)

# Register routers
app.include_router(openai_router, prefix="/openAI", tags=["OpenAI"])
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
