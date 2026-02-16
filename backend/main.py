"""
Context Rot Monitor - FastAPI Server
Exposes drift detection and supervisor analysis via REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

from drift_engine import DriftEngine, DriftMetrics
from supervisor import LLMSupervisor, SupervisorAnalysis

app = FastAPI(title="Context Rot Monitor API", version="1.0.0")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use Redis or similar)
engine = DriftEngine(similarity_threshold=0.7, check_interval=3)
supervisor = LLMSupervisor()


# Request/Response Models
class InitializeRequest(BaseModel):
    north_star: str


class TurnRequest(BaseModel):
    user_message: str
    assistant_response: str


class DriftResponse(BaseModel):
    turn_number: int
    similarity_score: float
    is_drifting: bool
    last_good_turn: int
    supervisor_analysis: Optional[dict] = None
    intervention_prompt: Optional[str] = None


class ConversationState(BaseModel):
    total_turns: int
    north_star: str
    last_good_turn: int
    current_drift_status: bool
    drift_checks: int
    recent_turns: List[dict]


# Endpoints
@app.get("/")
async def root():
    return {
        "service": "Context Rot Monitor",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/initialize",
            "/add-turn",
            "/check-drift",
            "/get-state",
            "/reset"
        ]
    }


@app.post("/initialize")
async def initialize_conversation(request: InitializeRequest):
    """Set the North Star (original goal) for the conversation"""
    try:
        engine.set_north_star(request.north_star)
        return {
            "status": "success",
            "message": "North Star set successfully",
            "north_star": request.north_star
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-turn", response_model=Optional[DriftResponse])
async def add_conversation_turn(request: TurnRequest):
    """
    Add a conversation turn and automatically check for drift if needed
    
    Returns drift analysis if this turn triggers a check (every N turns)
    """
    try:
        drift_metrics = engine.add_turn(
            user_message=request.user_message,
            assistant_response=request.assistant_response
        )
        
        if not drift_metrics:
            return None
        
        # If drifting, run supervisor analysis
        supervisor_data = None
        intervention = None
        
        if drift_metrics.is_drifting:
            current_state = engine.generate_state_summary()
            analysis = supervisor.analyze_drift(
                north_star=engine.north_star,
                current_conversation=current_state,
                similarity_score=drift_metrics.similarity_score
            )
            
            supervisor_data = {
                "pursuing_goal": analysis.is_pursuing_goal,
                "distraction": analysis.distraction,
                "realignment": analysis.realignment_instruction,
                "confidence": analysis.confidence
            }
            
            intervention = supervisor.generate_intervention_prompt(
                engine.north_star,
                analysis
            )
        
        return DriftResponse(
            turn_number=drift_metrics.turn_number,
            similarity_score=drift_metrics.similarity_score,
            is_drifting=drift_metrics.is_drifting,
            last_good_turn=drift_metrics.last_good_turn,
            supervisor_analysis=supervisor_data,
            intervention_prompt=intervention
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check-drift", response_model=DriftResponse)
async def manual_drift_check():
    """Manually trigger a drift check"""
    try:
        drift_metrics = engine.check_drift()
        
        supervisor_data = None
        intervention = None
        
        if drift_metrics.is_drifting:
            current_state = engine.generate_state_summary()
            analysis = supervisor.analyze_drift(
                north_star=engine.north_star,
                current_conversation=current_state,
                similarity_score=drift_metrics.similarity_score
            )
            
            supervisor_data = {
                "pursuing_goal": analysis.is_pursuing_goal,
                "distraction": analysis.distraction,
                "realignment": analysis.realignment_instruction,
                "confidence": analysis.confidence
            }
            
            intervention = supervisor.generate_intervention_prompt(
                engine.north_star,
                analysis
            )
        
        return DriftResponse(
            turn_number=drift_metrics.turn_number,
            similarity_score=drift_metrics.similarity_score,
            is_drifting=drift_metrics.is_drifting,
            last_good_turn=drift_metrics.last_good_turn,
            supervisor_analysis=supervisor_data,
            intervention_prompt=intervention
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-state", response_model=ConversationState)
async def get_conversation_state():
    """Get current conversation state and drift history"""
    try:
        summary = engine.get_conversation_summary()
        
        # Get last 5 turns for display
        recent_turns = summary["conversation_history"][-5:] if summary["conversation_history"] else []
        
        return ConversationState(
            total_turns=summary["total_turns"],
            north_star=summary["north_star"],
            last_good_turn=summary["last_good_turn"],
            current_drift_status=summary["current_drift_status"],
            drift_checks=summary["drift_checks"],
            recent_turns=recent_turns
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_conversation():
    """Reset the conversation state"""
    global engine
    engine = DriftEngine(similarity_threshold=0.45, check_interval=3)
    return {"status": "success", "message": "Conversation reset"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "groq_api_configured": bool(os.getenv("GROQ_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Context Rot Monitor API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 Docs available at: http://localhost:8000/docs")
    
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  WARNING: GROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your-key-here'")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
