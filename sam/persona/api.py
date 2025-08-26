"""
FastAPI router for Personality Matrix API endpoints.

This module provides the REST API endpoints for interacting with the
Personality Matrix system.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .core import PersonalityMatrix
from .models import (
    AudienceContext,
    ChannelContext,
    EventType,
    StateUpdate,
    StyleTrace,
)


logger = logging.getLogger(__name__)


class StyleResponse(BaseModel):
    """Response model for style profile."""
    style: Dict[str, Any]
    state: Dict[str, Any]
    boundaries: Dict[str, Any]
    decoding: Dict[str, Any]


class UpdateRequest(BaseModel):
    """Request model for state updates."""
    event_type: EventType
    intensity: float
    context: Optional[Dict[str, Any]] = None
    audience: Optional[AudienceContext] = None
    channel: Optional[ChannelContext] = None


class MemoryLensingRequest(BaseModel):
    """Request model for memory lensing."""
    content: str
    memory_type: str = "interaction"


class MemoryLensingResponse(BaseModel):
    """Response model for memory lensing."""
    lenses: Dict[str, float]
    memory_type: str


class TraceResponse(BaseModel):
    """Response model for style traces."""
    traces: List[Dict[str, Any]]
    total_count: int


class PersonalitySummaryResponse(BaseModel):
    """Response model for personality summary."""
    summary: Dict[str, Any]


class ObservabilitySummaryResponse(BaseModel):
    """Response model for observability summary."""
    summary: Dict[str, Any]


def create_api_router(pmx: PersonalityMatrix) -> APIRouter:
    """
    Create the FastAPI router for Personality Matrix endpoints.
    
    Args:
        pmx: Personality Matrix instance
        
    Returns:
        FastAPI router with all endpoints
    """
    router = APIRouter()
    
    @router.get("/style", response_model=StyleResponse)
    async def get_style_profile():
        """Get the current style profile."""
        try:
            style = pmx.get_style_profile()
            state = pmx.get_current_state()
            boundaries = pmx.get_boundary_caps()
            decoding = pmx.get_decoding_profile()
            
            return StyleResponse(
                style=style.dict(),
                state=state.dict(),
                boundaries=boundaries.dict(),
                decoding=decoding.dict(),
            )
        except Exception as e:
            logger.error("Failed to get style profile: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/state")
    async def get_current_state():
        """Get the current affective state."""
        try:
            state = pmx.get_current_state()
            return state.dict()
        except Exception as e:
            logger.error("Failed to get current state: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/update", response_model=StyleResponse)
    async def update_state(request: UpdateRequest):
        """Update the personality state based on an event."""
        try:
            # Create state update
            update = StateUpdate(
                event_type=request.event_type,
                intensity=request.intensity,
                context=request.context or {},
                audience=request.audience,
                channel=request.channel,
            )
            
            # Update state
            style = await pmx.update_state(update)
            state = pmx.get_current_state()
            boundaries = pmx.get_boundary_caps()
            decoding = pmx.get_decoding_profile()
            
            return StyleResponse(
                style=style.dict(),
                state=state.dict(),
                boundaries=boundaries.dict(),
                decoding=decoding.dict(),
            )
        except Exception as e:
            logger.error("Failed to update state: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/traces", response_model=TraceResponse)
    async def get_recent_traces(
        limit: int = Query(10, ge=1, le=100, description="Number of traces to return")
    ):
        """Get recent style traces."""
        try:
            traces = pmx.get_recent_traces(limit)
            return TraceResponse(
                traces=[trace.dict() for trace in traces],
                total_count=len(traces),
            )
        except Exception as e:
            logger.error("Failed to get recent traces: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/traces/{event_type}")
    async def get_traces_by_event_type(event_type: str):
        """Get traces for a specific event type."""
        try:
            traces = pmx.observability.get_traces_by_event_type(event_type)
            return {
                "traces": [trace.dict() for trace in traces],
                "event_type": event_type,
                "count": len(traces),
            }
        except Exception as e:
            logger.error("Failed to get traces by event type: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/memory/lensing", response_model=MemoryLensingResponse)
    async def apply_memory_lensing(request: MemoryLensingRequest):
        """Apply memory lensing to content."""
        try:
            lenses = await pmx.apply_memory_lensing(
                request.content,
                request.memory_type
            )
            
            return MemoryLensingResponse(
                lenses=lenses,
                memory_type=request.memory_type,
            )
        except Exception as e:
            logger.error("Failed to apply memory lensing: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/personality/summary", response_model=PersonalitySummaryResponse)
    async def get_personality_summary():
        """Get a summary of the current personality state."""
        try:
            summary = pmx.get_personality_summary()
            return PersonalitySummaryResponse(summary=summary)
        except Exception as e:
            logger.error("Failed to get personality summary: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/personality/traits")
    async def get_traits():
        """Get the current trait kernel."""
        try:
            traits = pmx.get_traits()
            return traits.dict()
        except Exception as e:
            logger.error("Failed to get traits: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/boundaries")
    async def get_boundaries():
        """Get the current boundary caps."""
        try:
            boundaries = pmx.get_boundary_caps()
            return boundaries.dict()
        except Exception as e:
            logger.error("Failed to get boundaries: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/decoding")
    async def get_decoding_profile():
        """Get the current decoding profile."""
        try:
            decoding = pmx.get_decoding_profile()
            return decoding.dict()
        except Exception as e:
            logger.error("Failed to get decoding profile: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/reset")
    async def reset_to_baseline():
        """Reset the personality matrix to baseline state."""
        try:
            style = await pmx.reset_to_baseline()
            return {
                "message": "Personality matrix reset to baseline",
                "style": style.dict(),
            }
        except Exception as e:
            logger.error("Failed to reset to baseline: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/export")
    async def export_personality():
        """Export the current personality state."""
        try:
            export_data = pmx.export_personality()
            return export_data
        except Exception as e:
            logger.error("Failed to export personality: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/import")
    async def import_personality(data: Dict[str, Any]):
        """Import personality state from exported data."""
        try:
            pmx.import_personality(data)
            return {"message": "Personality state imported successfully"}
        except Exception as e:
            logger.error("Failed to import personality: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/summary", response_model=ObservabilitySummaryResponse)
    async def get_observability_summary():
        """Get observability summary."""
        try:
            summary = pmx.observability.get_observability_summary()
            return ObservabilitySummaryResponse(summary=summary)
        except Exception as e:
            logger.error("Failed to get observability summary: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/performance")
    async def get_performance_summary():
        """Get performance summary."""
        try:
            summary = pmx.observability.get_performance_summary()
            return summary
        except Exception as e:
            logger.error("Failed to get performance summary: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/drift-alerts")
    async def get_drift_alerts(
        limit: int = Query(10, ge=1, le=100, description="Number of alerts to return")
    ):
        """Get recent drift alerts."""
        try:
            alerts = pmx.observability.get_drift_alerts(limit)
            return {
                "alerts": alerts,
                "count": len(alerts),
            }
        except Exception as e:
            logger.error("Failed to get drift alerts: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/style-evolution")
    async def get_style_evolution(
        hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
    ):
        """Get style evolution summary."""
        try:
            summary = pmx.observability.get_style_evolution_summary(hours)
            return summary
        except Exception as e:
            logger.error("Failed to get style evolution: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/health")
    async def get_health_status():
        """Get health status."""
        try:
            health = pmx.observability.get_health_status()
            return health
        except Exception as e:
            logger.error("Failed to get health status: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/observability/export-traces")
    async def export_traces(
        format: str = Query("json", regex="^(json|csv)$", description="Export format"),
        hours: Optional[int] = Query(None, ge=1, le=168, description="Hours to export")
    ):
        """Export traces in specified format."""
        try:
            time_range = None
            if hours:
                from datetime import datetime, timedelta
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=hours)
                time_range = (start_time, end_time)
            
            exported = pmx.observability.export_traces(format, time_range)
            
            return {
                "format": format,
                "data": exported,
                "time_range": time_range,
            }
        except Exception as e:
            logger.error("Failed to export traces: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/observability/clear")
    async def clear_observability_data():
        """Clear all observability data (for testing/debugging)."""
        try:
            pmx.observability.clear_all_data()
            return {"message": "All observability data cleared"}
        except Exception as e:
            logger.error("Failed to clear observability data: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/boundary/check-safety")
    async def check_content_safety(
        content: str = Query(..., description="Content to check"),
    ):
        """Check content for safety and appropriateness."""
        try:
            boundaries = pmx.get_boundary_caps()
            safety_result = pmx.boundary_manager.check_content_safety(content, boundaries)
            return safety_result
        except Exception as e:
            logger.error("Failed to check content safety: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/boundary/summary")
    async def get_boundary_summary():
        """Get boundary summary."""
        try:
            boundaries = pmx.get_boundary_caps()
            summary = pmx.boundary_manager.get_boundary_summary(boundaries)
            return summary
        except Exception as e:
            logger.error("Failed to get boundary summary: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/memory/retrieval-priority")
    async def get_memory_retrieval_priority(
        memory_lenses: str = Query(..., description="Memory lenses (JSON)"),
        query_lenses: str = Query(..., description="Query lenses (JSON)"),
    ):
        """Calculate memory retrieval priority."""
        try:
            import json
            memory_lenses_dict = json.loads(memory_lenses)
            query_lenses_dict = json.loads(query_lenses)
            
            priority = pmx.memory_lenser.get_memory_retrieval_priority(
                memory_lenses_dict, query_lenses_dict
            )
            
            return {
                "priority": priority,
                "memory_lenses": memory_lenses_dict,
                "query_lenses": query_lenses_dict,
            }
        except Exception as e:
            logger.error("Failed to calculate memory retrieval priority: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    return router