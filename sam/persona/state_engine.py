"""
State Engine for managing affective states.

This module handles the dynamic management of mood, arousal, valence,
and other affective states with natural decay and event-based adjustments.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np

from .models import (
    AffectiveState,
    EventType,
    PersonalityConfig,
    StateUpdate,
)


logger = logging.getLogger(__name__)


class StateEngine:
    """
    Engine for managing affective states with decay and event-based updates.
    
    This class implements the state update algorithm:
    state = decay ⊙ state + Σ event_impacts
    """
    
    def __init__(self, config: PersonalityConfig):
        """
        Initialize the state engine.
        
        Args:
            config: Personality configuration
        """
        self.config = config
        
        # Event impact mappings
        self._event_impacts = self._initialize_event_impacts()
        
        # State transition rules
        self._transition_rules = self._initialize_transition_rules()
        
        logger.info("State Engine initialized")
    
    def _initialize_event_impacts(self) -> Dict[EventType, Dict[str, float]]:
        """Initialize the mapping of event types to their affective impacts."""
        return {
            EventType.POSITIVE_INTERACTION: {
                "valence": 0.3,
                "arousal": 0.2,
                "fatigue": -0.1,
            },
            EventType.NEGATIVE_INTERACTION: {
                "valence": -0.4,
                "arousal": 0.3,
                "fatigue": 0.1,
            },
            EventType.ACHIEVEMENT: {
                "valence": 0.5,
                "arousal": 0.4,
                "fatigue": -0.2,
            },
            EventType.FAILURE: {
                "valence": -0.6,
                "arousal": 0.2,
                "fatigue": 0.3,
            },
            EventType.SURPRISE: {
                "valence": 0.1,
                "arousal": 0.6,
                "fatigue": 0.0,
            },
            EventType.BOREDOM: {
                "valence": -0.2,
                "arousal": -0.3,
                "fatigue": 0.2,
            },
            EventType.STRESS: {
                "valence": -0.3,
                "arousal": 0.5,
                "fatigue": 0.4,
            },
            EventType.RELAXATION: {
                "valence": 0.2,
                "arousal": -0.4,
                "fatigue": -0.1,
            },
            EventType.CREATIVITY: {
                "valence": 0.4,
                "arousal": 0.3,
                "fatigue": 0.1,
            },
            EventType.LEARNING: {
                "valence": 0.3,
                "arousal": 0.2,
                "fatigue": 0.2,
            },
            EventType.SOCIAL: {
                "valence": 0.2,
                "arousal": 0.3,
                "fatigue": -0.1,
            },
            EventType.SOLITARY: {
                "valence": 0.1,
                "arousal": -0.2,
                "fatigue": 0.0,
            },
        }
    
    def _initialize_transition_rules(self) -> Dict[str, Dict[str, float]]:
        """Initialize rules for state transitions and interactions."""
        return {
            "valence_arousal": {
                "high_valence_high_arousal": 0.1,  # Excitement
                "low_valence_high_arousal": -0.1,  # Anxiety
                "high_valence_low_arousal": 0.05,  # Contentment
                "low_valence_low_arousal": -0.05,  # Sadness
            },
            "fatigue_impact": {
                "high_fatigue_valence": -0.2,  # Fatigue reduces positive mood
                "high_fatigue_arousal": -0.3,  # Fatigue reduces energy
            },
            "recovery_rules": {
                "valence_recovery_rate": 0.1,  # Natural recovery toward setpoint
                "arousal_recovery_rate": 0.15,  # Faster arousal recovery
                "fatigue_recovery_rate": 0.2,  # Fastest fatigue recovery
            },
        }
    
    def update_state(self, current_state: AffectiveState, update: StateUpdate) -> AffectiveState:
        """
        Update the affective state based on an event.
        
        Args:
            current_state: Current affective state
            update: State update containing event information
            
        Returns:
            Updated affective state
        """
        logger.debug("Updating state for event: %s (intensity: %.2f)", 
                    update.event_type, update.intensity)
        
        # Apply natural decay
        decayed_state = self._apply_decay(current_state)
        
        # Apply event impact
        event_impact = self._calculate_event_impact(update)
        
        # Apply state interactions
        interaction_impact = self._calculate_state_interactions(decayed_state)
        
        # Combine all impacts
        new_state = self._combine_impacts(decayed_state, event_impact, interaction_impact)
        
        # Apply recovery toward setpoints
        new_state = self._apply_recovery(new_state)
        
        # Clamp values to valid ranges
        new_state = self._clamp_state_values(new_state)
        
        # Update tags based on new state
        new_state.tags = self._update_state_tags(new_state)
        
        # Update timestamp
        new_state.ts = datetime.utcnow()
        
        logger.debug("State updated: valence=%.2f, arousal=%.2f, fatigue=%.2f",
                    new_state.valence, new_state.arousal, new_state.fatigue)
        
        return new_state
    
    def _apply_decay(self, state: AffectiveState) -> AffectiveState:
        """Apply natural decay to the current state."""
        decay_rate = state.decay
        
        # Apply decay to each component
        new_valence = state.valence * decay_rate
        new_arousal = state.arousal * decay_rate
        new_fatigue = state.fatigue * decay_rate
        
        return AffectiveState(
            valence=new_valence,
            arousal=new_arousal,
            fatigue=new_fatigue,
            tags=state.tags.copy(),
            decay=state.decay
        )
    
    def _calculate_event_impact(self, update: StateUpdate) -> Dict[str, float]:
        """Calculate the impact of an event on affective state."""
        event_type = update.event_type
        intensity = update.intensity
        
        # Get base impact for this event type
        base_impact = self._event_impacts.get(event_type, {})
        
        # Scale by intensity
        scaled_impact = {}
        for component, impact in base_impact.items():
            scaled_impact[component] = impact * intensity
        
        # Apply context modifiers
        context_modifiers = self._calculate_context_modifiers(update)
        for component, modifier in context_modifiers.items():
            if component in scaled_impact:
                scaled_impact[component] *= modifier
        
        return scaled_impact
    
    def _calculate_context_modifiers(self, update: StateUpdate) -> Dict[str, float]:
        """Calculate context-based modifiers for event impact."""
        modifiers = {"valence": 1.0, "arousal": 1.0, "fatigue": 1.0}
        
        # Audience modifiers
        if update.audience:
            if update.audience.type.value == "friend":
                modifiers["valence"] *= 1.2  # More positive with friends
            elif update.audience.type.value == "professional":
                modifiers["arousal"] *= 0.8  # More controlled in professional settings
            elif update.audience.type.value == "child":
                modifiers["valence"] *= 1.3  # More positive with children
                modifiers["arousal"] *= 1.1
        
        # Channel modifiers
        if update.channel:
            if update.channel.type.value == "voice":
                modifiers["arousal"] *= 1.1  # Voice is more engaging
            elif update.channel.type.value == "email":
                modifiers["arousal"] *= 0.9  # Email is less immediate
        
        # Time-based modifiers (if available)
        if update.timestamp:
            hour = update.timestamp.hour
            if 22 <= hour or hour <= 6:  # Late night
                modifiers["arousal"] *= 0.7
                modifiers["fatigue"] *= 1.2
        
        return modifiers
    
    def _calculate_state_interactions(self, state: AffectiveState) -> Dict[str, float]:
        """Calculate interactions between different state components."""
        interactions = {"valence": 0.0, "arousal": 0.0, "fatigue": 0.0}
        
        # Valence-Arousal interactions
        if state.valence > 0.5 and state.arousal > 0.5:
            interactions["valence"] += self._transition_rules["valence_arousal"]["high_valence_high_arousal"]
        elif state.valence < -0.5 and state.arousal > 0.5:
            interactions["valence"] += self._transition_rules["valence_arousal"]["low_valence_high_arousal"]
        elif state.valence > 0.5 and state.arousal < 0.3:
            interactions["valence"] += self._transition_rules["valence_arousal"]["high_valence_low_arousal"]
        elif state.valence < -0.5 and state.arousal < 0.3:
            interactions["valence"] += self._transition_rules["valence_arousal"]["low_valence_low_arousal"]
        
        # Fatigue interactions
        if state.fatigue > 0.7:
            interactions["valence"] += self._transition_rules["fatigue_impact"]["high_fatigue_valence"]
            interactions["arousal"] += self._transition_rules["fatigue_impact"]["high_fatigue_arousal"]
        
        return interactions
    
    def _combine_impacts(
        self,
        decayed_state: AffectiveState,
        event_impact: Dict[str, float],
        interaction_impact: Dict[str, float]
    ) -> AffectiveState:
        """Combine all impacts to create the new state."""
        # Start with decayed state
        new_valence = decayed_state.valence
        new_arousal = decayed_state.arousal
        new_fatigue = decayed_state.fatigue
        
        # Add event impacts
        new_valence += event_impact.get("valence", 0.0)
        new_arousal += event_impact.get("arousal", 0.0)
        new_fatigue += event_impact.get("fatigue", 0.0)
        
        # Add interaction impacts
        new_valence += interaction_impact.get("valence", 0.0)
        new_arousal += interaction_impact.get("arousal", 0.0)
        new_fatigue += interaction_impact.get("fatigue", 0.0)
        
        return AffectiveState(
            valence=new_valence,
            arousal=new_arousal,
            fatigue=new_fatigue,
            tags=decayed_state.tags.copy(),
            decay=decayed_state.decay
        )
    
    def _apply_recovery(self, state: AffectiveState) -> AffectiveState:
        """Apply recovery toward setpoints."""
        recovery_rules = self._transition_rules["recovery_rules"]
        
        # Calculate recovery toward setpoints
        valence_recovery = (self.config.valence_setpoint - state.valence) * recovery_rules["valence_recovery_rate"]
        arousal_recovery = (self.config.arousal_setpoint - state.arousal) * recovery_rules["arousal_recovery_rate"]
        fatigue_recovery = (0.0 - state.fatigue) * recovery_rules["fatigue_recovery_rate"]  # Recover toward 0
        
        return AffectiveState(
            valence=state.valence + valence_recovery,
            arousal=state.arousal + arousal_recovery,
            fatigue=state.fatigue + fatigue_recovery,
            tags=state.tags.copy(),
            decay=state.decay
        )
    
    def _clamp_state_values(self, state: AffectiveState) -> AffectiveState:
        """Clamp state values to valid ranges."""
        return AffectiveState(
            valence=np.clip(state.valence, -1.0, 1.0),
            arousal=np.clip(state.arousal, 0.0, 1.0),
            fatigue=np.clip(state.fatigue, 0.0, 1.0),
            tags=state.tags.copy(),
            decay=state.decay
        )
    
    def _update_state_tags(self, state: AffectiveState) -> List[str]:
        """Update state tags based on current values."""
        tags = []
        
        # Valence-based tags
        if state.valence > 0.5:
            tags.append("positive")
        elif state.valence < -0.5:
            tags.append("negative")
        else:
            tags.append("neutral")
        
        # Arousal-based tags
        if state.arousal > 0.7:
            tags.append("excited")
        elif state.arousal > 0.4:
            tags.append("engaged")
        elif state.arousal < 0.3:
            tags.append("calm")
        
        # Fatigue-based tags
        if state.fatigue > 0.7:
            tags.append("tired")
        elif state.fatigue > 0.4:
            tags.append("moderate_energy")
        else:
            tags.append("energetic")
        
        # Combined state tags
        if state.valence > 0.6 and state.arousal > 0.6:
            tags.append("enthusiastic")
        elif state.valence < -0.6 and state.arousal > 0.6:
            tags.append("anxious")
        elif state.valence > 0.6 and state.arousal < 0.3:
            tags.append("content")
        elif state.valence < -0.6 and state.arousal < 0.3:
            tags.append("sad")
        
        return tags
    
    def predict_state_evolution(
        self,
        current_state: AffectiveState,
        time_horizon: timedelta,
        expected_events: Optional[List[StateUpdate]] = None
    ) -> List[AffectiveState]:
        """
        Predict how the state will evolve over time.
        
        Args:
            current_state: Current affective state
            time_horizon: Time period to predict
            expected_events: List of expected events during the period
            
        Returns:
            List of predicted states over time
        """
        predictions = []
        current = current_state
        
        # Calculate number of time steps (assuming 1-minute intervals)
        total_minutes = int(time_horizon.total_seconds() / 60)
        step_minutes = max(1, total_minutes // 10)  # 10 prediction points
        
        for i in range(0, total_minutes, step_minutes):
            # Apply decay
            current = self._apply_decay(current)
            
            # Apply recovery
            current = self._apply_recovery(current)
            
            # Apply expected events if any
            if expected_events:
                for event in expected_events:
                    # Simple heuristic: apply events that might occur around this time
                    if i < 30:  # First 30 minutes
                        event_impact = self._calculate_event_impact(event)
                        current.valence += event_impact.get("valence", 0.0) * 0.1  # Reduced impact
                        current.arousal += event_impact.get("arousal", 0.0) * 0.1
                        current.fatigue += event_impact.get("fatigue", 0.0) * 0.1
            
            # Clamp values
            current = self._clamp_state_values(current)
            
            # Update timestamp
            current.ts = datetime.utcnow() + timedelta(minutes=i)
            
            predictions.append(current)
        
        return predictions
    
    def get_state_stability_score(self, state: AffectiveState) -> float:
        """
        Calculate a stability score for the current state.
        
        Args:
            state: Current affective state
            
        Returns:
            Stability score between 0 and 1 (higher = more stable)
        """
        # Calculate distance from setpoints
        valence_distance = abs(state.valence - self.config.valence_setpoint)
        arousal_distance = abs(state.arousal - self.config.arousal_setpoint)
        fatigue_distance = abs(state.fatigue - 0.0)  # Fatigue setpoint is 0
        
        # Average distance (lower = more stable)
        avg_distance = (valence_distance + arousal_distance + fatigue_distance) / 3.0
        
        # Convert to stability score (1 - distance)
        stability = max(0.0, 1.0 - avg_distance)
        
        return stability