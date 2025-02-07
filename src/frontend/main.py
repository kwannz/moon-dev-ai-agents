from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Lumix AI Agents",
    description="AI Agents for the Workplace",
    version="1.0.0"
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Mount the static directory
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "src/frontend/static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "src/frontend/templates"))

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/request-agent")
async def request_agent_form(request: Request):
    return templates.TemplateResponse("request_agent.html", {"request": request})

@app.get("/submit-agent")
async def submit_agent_form(request: Request):
    return templates.TemplateResponse("submit_agent.html", {"request": request})

@app.get("/thank-you")
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)  