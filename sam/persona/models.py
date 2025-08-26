"""
Data models for the Personality Matrix (PMX).

This module defines all the core data structures used by the PMX system,
including traits, states, style profiles, and traces.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class SentenceLength(str, Enum):
    """Enumeration for sentence length preferences."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class SensitivityLevel(str, Enum):
    """Enumeration for sensitivity handling levels."""
    NORMAL = "normal"
    SOFTEN = "soften"
    HIDE = "hide"


class ChannelType(str, Enum):
    """Enumeration for communication channels."""
    CHAT = "chat"
    EMAIL = "email"
    VOICE = "voice"
    VIDEO = "video"
    TEXT = "text"


class AudienceType(str, Enum):
    """Enumeration for audience types."""
    FRIEND = "friend"
    FAMILY = "family"
    COLLEAGUE = "colleague"
    STRANGER = "stranger"
    CHILD = "child"
    PROFESSIONAL = "professional"
    INTIMATE = "intimate"


class EventType(str, Enum):
    """Enumeration for event types that affect personality state."""
    POSITIVE_INTERACTION = "positive_interaction"
    NEGATIVE_INTERACTION = "negative_interaction"
    ACHIEVEMENT = "achievement"
    FAILURE = "failure"
    SURPRISE = "surprise"
    BOREDOM = "boredom"
    STRESS = "stress"
    RELAXATION = "relaxation"
    CREATIVITY = "creativity"
    LEARNING = "learning"
    SOCIAL = "social"
    SOLITARY = "solitary"


class TraitKernel(BaseModel):
    """Immutable baseline personality traits."""
    
    id: str = Field(default="traits", description="Trait kernel identifier")
    curiosity: float = Field(ge=0.0, le=1.0, description="Curiosity level")
    balance: float = Field(ge=0.0, le=1.0, description="Emotional balance")
    wit: float = Field(ge=0.0, le=1.0, description="Wit and humor")
    candor: float = Field(ge=0.0, le=1.0, description="Honesty and directness")
    care: float = Field(ge=0.0, le=1.0, description="Empathy and caring")
    
    class Config:
        frozen = True  # Make traits immutable


class AffectiveState(BaseModel):
    """Current affective state including mood, arousal, and valence."""
    
    ts: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    valence: float = Field(ge=-1.0, le=1.0, description="Positive/negative mood")
    arousal: float = Field(ge=0.0, le=1.0, description="Energy/activation level")
    fatigue: float = Field(ge=0.0, le=1.0, description="Tiredness level")
    tags: List[str] = Field(default_factory=list, description="State tags")
    decay: float = Field(ge=0.0, le=1.0, description="Decay rate for this state")
    
    @validator('valence', 'arousal', 'fatigue')
    def validate_affective_values(cls, v):
        """Ensure affective values are within valid ranges."""
        if not isinstance(v, (int, float)):
            raise ValueError("Affective values must be numeric")
        return float(v)


class ToneProfile(BaseModel):
    """Tone characteristics for communication."""
    
    warmth: float = Field(ge=0.0, le=1.0, description="Warmth and friendliness")
    formality: float = Field(ge=0.0, le=1.0, description="Formal vs casual")
    humor: float = Field(ge=0.0, le=1.0, description="Humor and playfulness")
    flirtation: float = Field(ge=0.0, le=1.0, description="Flirtatiousness")


class DictionProfile(BaseModel):
    """Diction and language style preferences."""
    
    sentence_len: SentenceLength = Field(default=SentenceLength.MEDIUM)
    metaphor: float = Field(ge=0.0, le=1.0, description="Metaphor density")


class PacingProfile(BaseModel):
    """Communication pacing preferences."""
    
    expansiveness: float = Field(ge=0.0, le=1.0, description="Detailed vs concise")


class StanceProfile(BaseModel):
    """Communication stance and assertiveness."""
    
    assertiveness: float = Field(ge=0.0, le=1.0, description="Confident vs tentative")


class BoundaryProfile(BaseModel):
    """Boundary and safety settings."""
    
    nsfw: bool = Field(default=False, description="Allow NSFW content")
    sensitive: SensitivityLevel = Field(default=SensitivityLevel.NORMAL)


class DecodingProfile(BaseModel):
    """LLM decoding parameters derived from personality."""
    
    temp: float = Field(ge=0.0, le=2.0, description="Temperature")
    top_p: float = Field(ge=0.0, le=1.0, description="Top-p sampling")
    top_k: int = Field(ge=1, le=100, description="Top-k sampling")
    penalty: float = Field(ge=0.0, le=2.0, description="Repetition penalty")
    max_tokens: int = Field(ge=1, le=4000, description="Maximum tokens")


class StyleProfile(BaseModel):
    """Complete style profile for communication."""
    
    tone: ToneProfile = Field(default_factory=ToneProfile)
    diction: DictionProfile = Field(default_factory=DictionProfile)
    pacing: PacingProfile = Field(default_factory=PacingProfile)
    stance: StanceProfile = Field(default_factory=StanceProfile)
    boundaries: BoundaryProfile = Field(default_factory=BoundaryProfile)
    decoding: DecodingProfile = Field(default_factory=DecodingProfile)


class AudienceContext(BaseModel):
    """Context information about the audience."""
    
    name: Optional[str] = Field(default=None, description="Audience name")
    type: AudienceType = Field(default=AudienceType.STRANGER)
    role: Optional[str] = Field(default=None, description="Professional role")
    locale: Optional[str] = Field(default=None, description="Geographic locale")
    relationship: Optional[str] = Field(default=None, description="Relationship type")
    age_group: Optional[str] = Field(default=None, description="Age group")
    expertise_level: Optional[str] = Field(default=None, description="Expertise level")


class ChannelContext(BaseModel):
    """Context information about the communication channel."""
    
    type: ChannelType = Field(default=ChannelType.CHAT)
    platform: Optional[str] = Field(default=None, description="Platform name")
    is_private: bool = Field(default=True, description="Private vs public")
    has_audience: bool = Field(default=False, description="Multiple recipients")
    is_synchronous: bool = Field(default=True, description="Real-time vs async")


class StateUpdate(BaseModel):
    """Update to the affective state."""
    
    event_type: EventType = Field(description="Type of event")
    intensity: float = Field(ge=0.0, le=1.0, description="Event intensity")
    context: Dict[str, Any] = Field(default_factory=dict, description="Event context")
    audience: Optional[AudienceContext] = Field(default=None)
    channel: Optional[ChannelContext] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StyleTrace(BaseModel):
    """Trace of style changes for observability."""
    
    id: UUID = Field(default_factory=uuid4, description="Trace identifier")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    inputs: Dict[str, Any] = Field(description="Input context")
    state: AffectiveState = Field(description="Current state")
    style_delta: Dict[str, str] = Field(description="Style changes")
    boundaries: Dict[str, Any] = Field(description="Boundary adjustments")
    decoding_delta: Dict[str, str] = Field(description="Decoding changes")
    rationale: Optional[str] = Field(default=None, description="Change rationale")


class BoundaryCaps(BaseModel):
    """Boundary caps for safety and appropriateness."""
    
    max_flirtation: float = Field(ge=0.0, le=1.0, description="Maximum flirtation")
    max_humor: float = Field(ge=0.0, le=1.0, description="Maximum humor")
    max_candor: float = Field(ge=0.0, le=1.0, description="Maximum candor")
    min_formality: float = Field(ge=0.0, le=1.0, description="Minimum formality")
    safety_tags: List[str] = Field(default_factory=list, description="Safety tags")


class PersonalityConfig(BaseModel):
    """Configuration for the personality matrix."""
    
    # Trait settings
    default_traits: TraitKernel = Field(default_factory=lambda: TraitKernel())
    
    # State settings
    state_decay_rate: float = Field(default=0.92, ge=0.0, le=1.0)
    valence_setpoint: float = Field(default=0.5, ge=-1.0, le=1.0)
    arousal_setpoint: float = Field(default=0.4, ge=0.0, le=1.0)
    
    # Style settings
    style_adaptation_rate: float = Field(default=0.3, ge=0.0, le=1.0)
    drift_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # Decoding settings
    decoding_ranges: Dict[str, Dict[str, Union[float, int]]] = Field(
        default_factory=lambda: {
            "flow": {"temp": (0.6, 0.9), "max_tokens": (500, 1500)},
            "deep": {"temp": (0.3, 0.6), "max_tokens": (800, 2000)},
            "crisis": {"temp": (0.1, 0.3), "max_tokens": (200, 800)},
        }
    )
    
    # Boundary settings
    default_boundaries: BoundaryCaps = Field(default_factory=BoundaryCaps)
    
    # Observability settings
    trace_retention_days: int = Field(default=30, ge=1)
    enable_drift_alerts: bool = Field(default=True)