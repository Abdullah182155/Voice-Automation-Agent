from fastapi import FastAPI

app = FastAPI()

@app.get("/Welcome")
def welcome():
    return {"message": "Hello World!"}
