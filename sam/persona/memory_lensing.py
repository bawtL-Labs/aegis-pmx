"""
Memory Lensing for affective tagging of memories.

This module handles the application of affective lenses to memories,
influencing future retrieval and decision-making based on emotional context.
"""

import logging
from typing import Any, Dict, List, Optional

from .models import (
    AffectiveState,
    PersonalityConfig,
    StyleProfile,
)


logger = logging.getLogger(__name__)


class MemoryLenser:
    """
    Applies affective lenses to memories for enhanced retrieval and influence.
    
    This class implements memory lensing by tagging memories with affective
    characteristics that influence future retrieval and decision-making.
    """
    
    def __init__(self, config: PersonalityConfig):
        """
        Initialize the memory lenser.
        
        Args:
            config: Personality configuration
        """
        self.config = config
        
        # Affective lens mappings
        self._lens_mappings = self._initialize_lens_mappings()
        
        # Memory type patterns
        self._memory_patterns = self._initialize_memory_patterns()
        
        logger.info("Memory Lenser initialized")
    
    def _initialize_lens_mappings(self) -> Dict[str, Dict[str, float]]:
        """Initialize mappings from affective states to lens weights."""
        return {
            "valence_lenses": {
                "positive": 0.8,
                "negative": 0.6,
                "neutral": 0.4,
                "mixed": 0.5,
            },
            "arousal_lenses": {
                "excited": 0.9,
                "calm": 0.3,
                "anxious": 0.7,
                "relaxed": 0.2,
            },
            "fatigue_lenses": {
                "energetic": 0.8,
                "tired": 0.4,
                "focused": 0.9,
                "distracted": 0.3,
            },
            "style_lenses": {
                "warm": 0.7,
                "formal": 0.6,
                "humorous": 0.8,
                "serious": 0.5,
                "assertive": 0.7,
                "tentative": 0.4,
            },
        }
    
    def _initialize_memory_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for different memory types."""
        return {
            "interaction": {
                "valence_weight": 0.8,
                "arousal_weight": 0.6,
                "style_weight": 0.9,
                "lens_tags": ["social", "communication"],
            },
            "achievement": {
                "valence_weight": 0.9,
                "arousal_weight": 0.7,
                "style_weight": 0.5,
                "lens_tags": ["success", "accomplishment"],
            },
            "learning": {
                "valence_weight": 0.6,
                "arousal_weight": 0.5,
                "style_weight": 0.4,
                "lens_tags": ["education", "growth"],
            },
            "emotional": {
                "valence_weight": 1.0,
                "arousal_weight": 0.8,
                "style_weight": 0.3,
                "lens_tags": ["emotional", "feeling"],
            },
            "creative": {
                "valence_weight": 0.7,
                "arousal_weight": 0.6,
                "style_weight": 0.8,
                "lens_tags": ["creative", "artistic"],
            },
            "problem_solving": {
                "valence_weight": 0.5,
                "arousal_weight": 0.7,
                "style_weight": 0.6,
                "lens_tags": ["analytical", "logical"],
            },
        }
    
    async def apply_lensing(
        self,
        state: AffectiveState,
        style: StyleProfile,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Apply affective lensing to current context.
        
        Args:
            state: Current affective state
            style: Current style profile
            context: Context information
            
        Returns:
            Affective lens tags with weights
        """
        logger.debug("Applying memory lensing")
        
        # Generate base lenses from affective state
        valence_lenses = self._generate_valence_lenses(state)
        arousal_lenses = self._generate_arousal_lenses(state)
        fatigue_lenses = self._generate_fatigue_lenses(state)
        
        # Generate style-based lenses
        style_lenses = self._generate_style_lenses(style)
        
        # Combine all lenses
        combined_lenses = {}
        combined_lenses.update(valence_lenses)
        combined_lenses.update(arousal_lenses)
        combined_lenses.update(fatigue_lenses)
        combined_lenses.update(style_lenses)
        
        # Apply context-specific adjustments
        context_lenses = self._apply_context_lenses(combined_lenses, context)
        
        # Normalize lens weights
        normalized_lenses = self._normalize_lens_weights(context_lenses)
        
        logger.debug("Memory lensing applied: %s", list(normalized_lenses.keys())[:5])
        
        return normalized_lenses
    
    async def tag_memory(
        self,
        content: str,
        memory_type: str,
        current_state: AffectiveState,
        current_style: StyleProfile
    ) -> Dict[str, float]:
        """
        Tag a memory with affective lenses.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            current_state: Current affective state
            current_style: Current style profile
            
        Returns:
            Affective lens tags with weights
        """
        logger.debug("Tagging memory of type: %s", memory_type)
        
        # Get memory pattern
        pattern = self._memory_patterns.get(memory_type, self._memory_patterns["interaction"])
        
        # Generate base lenses
        base_lenses = await self.apply_lensing(current_state, current_style, {})
        
        # Apply memory type specific adjustments
        adjusted_lenses = self._apply_memory_type_adjustments(base_lenses, pattern)
        
        # Add memory type specific tags
        for tag in pattern["lens_tags"]:
            adjusted_lenses[tag] = 0.6
        
        # Apply content-based adjustments
        content_lenses = self._apply_content_lenses(adjusted_lenses, content)
        
        # Normalize final weights
        final_lenses = self._normalize_lens_weights(content_lenses)
        
        logger.debug("Memory tagged with %d lenses", len(final_lenses))
        
        return final_lenses
    
    def _generate_valence_lenses(self, state: AffectiveState) -> Dict[str, float]:
        """Generate valence-based affective lenses."""
        lenses = {}
        
        if state.valence > 0.5:
            lenses["positive"] = self._lens_mappings["valence_lenses"]["positive"]
            if state.valence > 0.8:
                lenses["joyful"] = 0.9
                lenses["optimistic"] = 0.8
        elif state.valence < -0.5:
            lenses["negative"] = self._lens_mappings["valence_lenses"]["negative"]
            if state.valence < -0.8:
                lenses["sad"] = 0.9
                lenses["pessimistic"] = 0.8
        else:
            lenses["neutral"] = self._lens_mappings["valence_lenses"]["neutral"]
            lenses["balanced"] = 0.5
        
        return lenses
    
    def _generate_arousal_lenses(self, state: AffectiveState) -> Dict[str, float]:
        """Generate arousal-based affective lenses."""
        lenses = {}
        
        if state.arousal > 0.7:
            lenses["excited"] = self._lens_mappings["arousal_lenses"]["excited"]
            lenses["energetic"] = 0.8
        elif state.arousal > 0.4:
            lenses["engaged"] = 0.6
            lenses["active"] = 0.5
        elif state.arousal < 0.3:
            lenses["calm"] = self._lens_mappings["arousal_lenses"]["calm"]
            lenses["peaceful"] = 0.4
        
        # Check for anxiety (high arousal + negative valence)
        if state.arousal > 0.6 and state.valence < -0.3:
            lenses["anxious"] = self._lens_mappings["arousal_lenses"]["anxious"]
            lenses["stressed"] = 0.7
        
        return lenses
    
    def _generate_fatigue_lenses(self, state: AffectiveState) -> Dict[str, float]:
        """Generate fatigue-based affective lenses."""
        lenses = {}
        
        if state.fatigue < 0.3:
            lenses["energetic"] = self._lens_mappings["fatigue_lenses"]["energetic"]
            lenses["focused"] = self._lens_mappings["fatigue_lenses"]["focused"]
        elif state.fatigue > 0.7:
            lenses["tired"] = self._lens_mappings["fatigue_lenses"]["tired"]
            lenses["distracted"] = self._lens_mappings["fatigue_lenses"]["distracted"]
        else:
            lenses["moderate_energy"] = 0.5
        
        return lenses
    
    def _generate_style_lenses(self, style: StyleProfile) -> Dict[str, float]:
        """Generate style-based affective lenses."""
        lenses = {}
        
        # Tone-based lenses
        if style.tone.warmth > 0.7:
            lenses["warm"] = self._lens_mappings["style_lenses"]["warm"]
            lenses["friendly"] = 0.8
        elif style.tone.warmth < 0.3:
            lenses["cool"] = 0.6
            lenses["distant"] = 0.5
        
        if style.tone.formality > 0.7:
            lenses["formal"] = self._lens_mappings["style_lenses"]["formal"]
            lenses["professional"] = 0.8
        elif style.tone.formality < 0.3:
            lenses["casual"] = 0.7
            lenses["relaxed"] = 0.6
        
        if style.tone.humor > 0.7:
            lenses["humorous"] = self._lens_mappings["style_lenses"]["humorous"]
            lenses["playful"] = 0.8
        elif style.tone.humor < 0.3:
            lenses["serious"] = self._lens_mappings["style_lenses"]["serious"]
            lenses["grave"] = 0.6
        
        # Stance-based lenses
        if style.stance.assertiveness > 0.7:
            lenses["assertive"] = self._lens_mappings["style_lenses"]["assertive"]
            lenses["confident"] = 0.8
        elif style.stance.assertiveness < 0.3:
            lenses["tentative"] = self._lens_mappings["style_lenses"]["tentative"]
            lenses["uncertain"] = 0.6
        
        return lenses
    
    def _apply_context_lenses(
        self,
        lenses: Dict[str, float],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Apply context-specific lens adjustments."""
        adjusted = lenses.copy()
        
        # Social context
        if context.get("social_context", False):
            adjusted["social"] = 0.8
            adjusted["interpersonal"] = 0.7
        
        # Work context
        if context.get("work_context", False):
            adjusted["professional"] = 0.8
            adjusted["productive"] = 0.7
        
        # Learning context
        if context.get("learning_context", False):
            adjusted["educational"] = 0.8
            adjusted["growth"] = 0.7
        
        # Creative context
        if context.get("creative_context", False):
            adjusted["creative"] = 0.8
            adjusted["artistic"] = 0.7
        
        # Emotional context
        emotional_state = context.get("emotional_state", "neutral")
        if emotional_state != "neutral":
            adjusted[emotional_state] = 0.8
            adjusted["emotional"] = 0.7
        
        return adjusted
    
    def _apply_memory_type_adjustments(
        self,
        lenses: Dict[str, float],
        pattern: Dict[str, Any]
    ) -> Dict[str, float]:
        """Apply memory type specific adjustments to lenses."""
        adjusted = lenses.copy()
        
        # Weight adjustments based on memory type
        valence_weight = pattern["valence_weight"]
        arousal_weight = pattern["arousal_weight"]
        style_weight = pattern["style_weight"]
        
        # Adjust valence-related lenses
        for lens in ["positive", "negative", "neutral", "joyful", "sad"]:
            if lens in adjusted:
                adjusted[lens] *= valence_weight
        
        # Adjust arousal-related lenses
        for lens in ["excited", "calm", "anxious", "engaged", "energetic"]:
            if lens in adjusted:
                adjusted[lens] *= arousal_weight
        
        # Adjust style-related lenses
        for lens in ["warm", "formal", "humorous", "serious", "assertive", "tentative"]:
            if lens in adjusted:
                adjusted[lens] *= style_weight
        
        return adjusted
    
    def _apply_content_lenses(
        self,
        lenses: Dict[str, float],
        content: str
    ) -> Dict[str, float]:
        """Apply content-based lens adjustments."""
        adjusted = lenses.copy()
        content_lower = content.lower()
        
        # Content-based lens detection
        if any(word in content_lower for word in ["love", "care", "kind", "gentle"]):
            adjusted["caring"] = 0.8
            adjusted["compassionate"] = 0.7
        
        if any(word in content_lower for word in ["think", "analyze", "logic", "reason"]):
            adjusted["analytical"] = 0.8
            adjusted["logical"] = 0.7
        
        if any(word in content_lower for word in ["create", "imagine", "art", "design"]):
            adjusted["creative"] = 0.8
            adjusted["imaginative"] = 0.7
        
        if any(word in content_lower for word in ["help", "support", "assist", "guide"]):
            adjusted["helpful"] = 0.8
            adjusted["supportive"] = 0.7
        
        if any(word in content_lower for word in ["learn", "study", "understand", "knowledge"]):
            adjusted["educational"] = 0.8
            adjusted["intellectual"] = 0.7
        
        return adjusted
    
    def _normalize_lens_weights(self, lenses: Dict[str, float]) -> Dict[str, float]:
        """Normalize lens weights to ensure they sum to a reasonable total."""
        if not lenses:
            return {}
        
        # Find the maximum weight
        max_weight = max(lenses.values())
        
        # Normalize to keep max weight at 0.9
        if max_weight > 0.9:
            normalization_factor = 0.9 / max_weight
            normalized = {
                lens: weight * normalization_factor
                for lens, weight in lenses.items()
            }
        else:
            normalized = lenses.copy()
        
        # Remove very low weights
        filtered = {
            lens: weight
            for lens, weight in normalized.items()
            if weight >= 0.1
        }
        
        return filtered
    
    def get_lens_influence_score(
        self,
        memory_lenses: Dict[str, float],
        current_state: AffectiveState
    ) -> float:
        """
        Calculate how much a memory's lenses should influence current state.
        
        Args:
            memory_lenses: Affective lenses of a memory
            current_state: Current affective state
            
        Returns:
            Influence score between 0 and 1
        """
        if not memory_lenses:
            return 0.0
        
        # Calculate compatibility between memory lenses and current state
        compatibility_scores = []
        
        # Valence compatibility
        if "positive" in memory_lenses and current_state.valence > 0:
            compatibility_scores.append(memory_lenses["positive"] * current_state.valence)
        elif "negative" in memory_lenses and current_state.valence < 0:
            compatibility_scores.append(memory_lenses["negative"] * abs(current_state.valence))
        
        # Arousal compatibility
        if "excited" in memory_lenses and current_state.arousal > 0.6:
            compatibility_scores.append(memory_lenses["excited"] * current_state.arousal)
        elif "calm" in memory_lenses and current_state.arousal < 0.4:
            compatibility_scores.append(memory_lenses["calm"] * (1.0 - current_state.arousal))
        
        # Fatigue compatibility
        if "energetic" in memory_lenses and current_state.fatigue < 0.3:
            compatibility_scores.append(memory_lenses["energetic"] * (1.0 - current_state.fatigue))
        elif "tired" in memory_lenses and current_state.fatigue > 0.7:
            compatibility_scores.append(memory_lenses["tired"] * current_state.fatigue)
        
        # Calculate average compatibility
        if compatibility_scores:
            avg_compatibility = sum(compatibility_scores) / len(compatibility_scores)
        else:
            avg_compatibility = 0.3  # Default moderate influence
        
        # Apply time decay (older memories have less influence)
        # This would typically use memory age, but we'll use a default
        time_decay = 0.8  # Assume memory is relatively recent
        
        influence_score = avg_compatibility * time_decay
        
        return min(1.0, max(0.0, influence_score))
    
    def get_memory_retrieval_priority(
        self,
        memory_lenses: Dict[str, float],
        query_lenses: Dict[str, float]
    ) -> float:
        """
        Calculate retrieval priority for a memory based on query lenses.
        
        Args:
            memory_lenses: Affective lenses of a memory
            query_lenses: Affective lenses of the current query/context
            
        Returns:
            Retrieval priority score between 0 and 1
        """
        if not memory_lenses or not query_lenses:
            return 0.0
        
        # Calculate overlap between memory and query lenses
        overlap_score = 0.0
        overlap_count = 0
        
        for query_lens, query_weight in query_lenses.items():
            if query_lens in memory_lenses:
                memory_weight = memory_lenses[query_lens]
                overlap_score += query_weight * memory_weight
                overlap_count += 1
        
        # Normalize by number of overlapping lenses
        if overlap_count > 0:
            overlap_score /= overlap_count
        
        # Boost score for memories with more lenses (richer context)
        richness_boost = min(0.2, len(memory_lenses) * 0.02)
        
        final_score = overlap_score + richness_boost
        
        return min(1.0, max(0.0, final_score))