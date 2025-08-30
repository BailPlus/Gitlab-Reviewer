import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="::", port=8000, reload=False)
