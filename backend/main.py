
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import json

from backend.database import (
    initialize_database,
    create_ticket,
    get_all_tickets,
    update_ticket
)

from backend.services.ai_service import (
    generate_response,
    classify_ticket
)

app = FastAPI(
    title="NEXUS AI",
    description="Generative AI Powered Unified Service Management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

class ChatRequest(BaseModel):
    message: str

class TicketRequest(BaseModel):
    employee_name: str
    title: str
    description: str

class TicketUpdate(BaseModel):
    status: str
    resolution: Optional[str] = None

@app.on_event("startup")
def startup():
    initialize_database()

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "application": "NEXUS AI"
    }

@app.post("/api/chat")
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    try:
        answer = generate_response(request.message)

        return {
            "success": True,
            "response": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(error)}"
        )

@app.post("/api/analyze")
def analyze(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(400, "Issue cannot be empty")

    try:
        result = classify_ticket(request.message)

        return {
            "success": True,
            "analysis": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"AI analysis failed: {str(error)}"
        )

@app.post("/api/tickets")
def submit_ticket(request: TicketRequest):

    if not request.employee_name.strip():
        raise HTTPException(400, "Employee name required")

    if not request.title.strip() or not request.description.strip():
        raise HTTPException(400, "Title and description required")

    try:
        analysis = classify_ticket(request.description)

        ai_analysis = json.dumps(analysis)

        ticket_id = create_ticket({
            "employee_name": request.employee_name,
            "title": request.title,
            "description": request.description,
            "category": analysis.get("category", "Other"),
            "priority": analysis.get("priority", "Medium"),
            "ai_analysis": ai_analysis
        })

        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": "Ticket created successfully",
            "analysis": analysis
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Ticket creation failed: {str(error)}"
        )

@app.get("/api/tickets")
def tickets():
    return get_all_tickets()

@app.patch("/api/tickets/{ticket_id}")
def change_ticket_status(
    ticket_id: int,
    request: TicketUpdate
):

    allowed_statuses = [
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    ]

    if request.status not in allowed_statuses:
        raise HTTPException(400, "Invalid ticket status")

    updated = update_ticket(
        ticket_id,
        request.status,
        request.resolution
    )

    if not updated:
        raise HTTPException(404, "Ticket not found")

    return {
        "success": True,
        "message": "Ticket updated successfully"
    }

@app.get("/api/stats")
def statistics():

    all_tickets = get_all_tickets()

    return {
        "total": len(all_tickets),
        "open": sum(
            t["status"] == "Open" for t in all_tickets
        ),
        "in_progress": sum(
            t["status"] == "In Progress" for t in all_tickets
        ),
        "resolved": sum(
            t["status"] == "Resolved" for t in all_tickets
        ),
        "critical": sum(
            t["priority"] == "Critical"
            for t in all_tickets
            if t["status"] not in ["Resolved", "Closed"]
        )
    }

app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend"
)