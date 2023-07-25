import uvicorn

def run_app():
    uvicorn.run("backend.app.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run_app()
    
