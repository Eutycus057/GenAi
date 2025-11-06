from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend API is running successfully"}

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    repo_path = data.get("path", ".")
    try:
        result = subprocess.run(
            ["jac", "run", "main.jac"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

