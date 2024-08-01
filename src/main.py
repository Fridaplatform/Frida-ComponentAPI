from fastapi import FastAPI

from routes import routes

app = FastAPI(
    title="Softtek FridaGPT Componen Generator",
    version="0.0.1",
    description="This is an API for Softtek's Extension FridaGPT's cration of components.",
)

app.include_router(routes.router, prefix="/extension", tags=["Extension"])


@app.get("/")
async def root():
    """Root endpoint for the API.

    Returns:
        dict: A dictionary with a message and a success flag.
    """
    return {"message": "Hello World!", "success": True}