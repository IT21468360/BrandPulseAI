from fastapi import FastAPI

# Create a FastAPI app instance
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python backend!"}
