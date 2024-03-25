#Libraries
from fastapi import FastAPI
from routers.openAI import openAI_router

# Initialize FastAPI app
app = FastAPI()

# Additional endpoints can be added as needed
app.include_router(prefix="/openAI", router=openAI_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)

