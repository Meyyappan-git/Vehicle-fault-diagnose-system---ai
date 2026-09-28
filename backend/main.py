"""FastAPI entry point for the Vehicle Fault Diagnosis Assistant."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.diagnosis import load_knowledge_base, run_diagnosis
from backend.qa import answer_question

app = FastAPI(title="Vehicle Fault Diagnosis Assistant", version="1.0.0", description="Educational FOPL, Bayesian-network, and decision-network vehicle triage.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VehicleDetails(BaseModel):
    make: str = ""
    model: str = ""
    year: int | None = None
    mileage: int | None = None
    fuel_type: str = ""


class DiagnosisRequest(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    absent_symptoms: list[str] = Field(default_factory=list)
    free_text: str = ""
    vehicle: VehicleDetails = Field(default_factory=VehicleDetails)
    vehicle_id: str = "vehicle"
    sensor_values: dict[str, float] = Field(default_factory=dict)


class QuestionRequest(BaseModel):
    question: str
    payload: DiagnosisRequest
    diagnosis: dict[str, Any] | None = None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vehicle-fault-diagnosis"}


@app.get("/api/meta")
def metadata() -> dict[str, Any]:
    kb = load_knowledge_base()
    return {"symptoms": kb["facts"]["symptoms"], "faults": kb["facts"]["faults"], "systems": list(dict.fromkeys(item["system"] for item in kb["facts"]["symptoms"]))}


@app.post("/api/diagnose")
def diagnose(request: DiagnosisRequest) -> dict[str, Any]:
    try:
        return run_diagnosis(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/qa")
def question_answer(request: QuestionRequest) -> dict[str, Any]:
    try:
        return answer_question(request.question, request.payload.model_dump(), request.diagnosis)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
