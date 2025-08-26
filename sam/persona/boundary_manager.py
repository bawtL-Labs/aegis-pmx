"""
Boundary Manager for safety and appropriateness.

This module handles boundary management including safety settings,
appropriateness filters, and context-aware boundary adjustments.
"""

import logging
from typing import Any, Dict, List, Optional

from .models import (
    AudienceContext,
    BoundaryCaps,
    ChannelContext,
    PersonalityConfig,
)


logger = logging.getLogger(__name__)


class BoundaryManager:
    """
    Manages safety and appropriateness boundaries for communication.
    
    This class handles boundary adjustments based on audience, channel,
    and context to ensure appropriate communication.
    """
    
    def __init__(self, config: PersonalityConfig):
        """
        Initialize the boundary manager.
        
        Args:
            config: Personality configuration
        """
        self.config = config
        
        # Boundary rules and mappings
        self._boundary_rules = self._initialize_boundary_rules()
        self._safety_patterns = self._initialize_safety_patterns()
        
        logger.info("Boundary Manager initialized")
    
    def _initialize_boundary_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize boundary rules for different contexts."""
        return {
            "audience_rules": {
                "child": {
                    "max_flirtation": 0.0,
                    "max_humor": 0.9,
                    "max_candor": 0.3,
                    "min_formality": 0.4,
                    "safety_tags": ["child_safe", "educational"],
                    "sensitive_topics": ["violence", "adult_content", "complex_politics"],
                },
                "professional": {
                    "max_flirtation": 0.1,
                    "max_humor": 0.6,
                    "max_candor": 0.7,
                    "min_formality": 0.6,
                    "safety_tags": ["professional", "appropriate"],
                    "sensitive_topics": ["personal_life", "controversial_politics"],
                },
                "friend": {
                    "max_flirtation": 0.8,
                    "max_humor": 0.9,
                    "max_candor": 0.9,
                    "min_formality": 0.1,
                    "safety_tags": ["casual", "friendly"],
                    "sensitive_topics": [],
                },
                "family": {
                    "max_flirtation": 0.3,
                    "max_humor": 0.8,
                    "max_candor": 0.8,
                    "min_formality": 0.2,
                    "safety_tags": ["family_appropriate"],
                    "sensitive_topics": ["controversial_politics", "adult_content"],
                },
                "stranger": {
                    "max_flirtation": 0.2,
                    "max_humor": 0.7,
                    "max_candor": 0.5,
                    "min_formality": 0.5,
                    "safety_tags": ["polite", "reserved"],
                    "sensitive_topics": ["personal_life", "controversial_politics"],
                },
                "intimate": {
                    "max_flirtation": 1.0,
                    "max_humor": 0.8,
                    "max_candor": 1.0,
                    "min_formality": 0.0,
                    "safety_tags": ["intimate", "trusted"],
                    "sensitive_topics": [],
                },
            },
            "channel_rules": {
                "public": {
                    "max_flirtation": 0.2,
                    "max_humor": 0.6,
                    "max_candor": 0.4,
                    "min_formality": 0.6,
                    "safety_tags": ["public_appropriate"],
                },
                "private": {
                    "max_flirtation": 0.8,
                    "max_humor": 0.9,
                    "max_candor": 0.9,
                    "min_formality": 0.2,
                    "safety_tags": ["private"],
                },
                "work": {
                    "max_flirtation": 0.1,
                    "max_humor": 0.5,
                    "max_candor": 0.6,
                    "min_formality": 0.7,
                    "safety_tags": ["work_appropriate"],
                },
            },
            "time_rules": {
                "business_hours": {
                    "max_flirtation": 0.3,
                    "max_humor": 0.7,
                    "min_formality": 0.5,
                },
                "after_hours": {
                    "max_flirtation": 0.7,
                    "max_humor": 0.8,
                    "min_formality": 0.3,
                },
                "late_night": {
                    "max_flirtation": 0.5,
                    "max_humor": 0.6,
                    "min_formality": 0.4,
                },
            },
        }
    
    def _initialize_safety_patterns(self) -> Dict[str, List[str]]:
        """Initialize safety patterns for content filtering."""
        return {
            "sensitive_words": [
                "violence", "harm", "danger", "threat", "attack",
                "hate", "discrimination", "prejudice", "racism", "sexism",
                "suicide", "self-harm", "abuse", "trauma",
            ],
            "adult_content": [
                "explicit", "sexual", "pornographic", "adult", "mature",
                "intimate", "romantic", "flirtatious",
            ],
            "political_sensitive": [
                "controversial", "divisive", "partisan", "extreme",
                "radical", "conspiracy", "misinformation",
            ],
            "personal_boundaries": [
                "private", "personal", "confidential", "secret",
                "embarrassing", "shameful", "vulnerable",
            ],
        }
    
    def adjust_boundaries(
        self,
        current_boundaries: BoundaryCaps,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> BoundaryCaps:
        """
        Adjust boundaries based on context.
        
        Args:
            current_boundaries: Current boundary caps
            audience: Audience context
            channel: Channel context
            context: Additional context information
            
        Returns:
            Adjusted boundary caps
        """
        logger.debug("Adjusting boundaries for audience: %s, channel: %s",
                    audience.type.value if audience else "None",
                    channel.type.value if channel else "None")
        
        # Start with current boundaries
        adjusted = BoundaryCaps(
            max_flirtation=current_boundaries.max_flirtation,
            max_humor=current_boundaries.max_humor,
            max_candor=current_boundaries.max_candor,
            min_formality=current_boundaries.min_formality,
            safety_tags=current_boundaries.safety_tags.copy(),
        )
        
        # Apply audience-based adjustments
        if audience:
            adjusted = self._apply_audience_boundaries(adjusted, audience)
        
        # Apply channel-based adjustments
        if channel:
            adjusted = self._apply_channel_boundaries(adjusted, channel)
        
        # Apply context-based adjustments
        if context:
            adjusted = self._apply_context_boundaries(adjusted, context)
        
        # Apply time-based adjustments
        adjusted = self._apply_time_boundaries(adjusted)
        
        # Ensure boundaries are within valid ranges
        adjusted = self._clamp_boundaries(adjusted)
        
        logger.debug("Boundaries adjusted: flirtation=%.2f, humor=%.2f, candor=%.2f",
                    adjusted.max_flirtation, adjusted.max_humor, adjusted.max_candor)
        
        return adjusted
    
    def _apply_audience_boundaries(
        self,
        boundaries: BoundaryCaps,
        audience: AudienceContext
    ) -> BoundaryCaps:
        """Apply audience-specific boundary adjustments."""
        audience_rules = self._boundary_rules["audience_rules"]
        audience_type = audience.type.value
        
        if audience_type in audience_rules:
            rules = audience_rules[audience_type]
            
            # Apply boundary caps
            boundaries.max_flirtation = min(boundaries.max_flirtation, rules["max_flirtation"])
            boundaries.max_humor = min(boundaries.max_humor, rules["max_humor"])
            boundaries.max_candor = min(boundaries.max_candor, rules["max_candor"])
            boundaries.min_formality = max(boundaries.min_formality, rules["min_formality"])
            
            # Add safety tags
            for tag in rules["safety_tags"]:
                if tag not in boundaries.safety_tags:
                    boundaries.safety_tags.append(tag)
        
        return boundaries
    
    def _apply_channel_boundaries(
        self,
        boundaries: BoundaryCaps,
        channel: ChannelContext
    ) -> BoundaryCaps:
        """Apply channel-specific boundary adjustments."""
        channel_rules = self._boundary_rules["channel_rules"]
        
        # Determine channel type
        if not channel.is_private:
            channel_type = "public"
        elif "work" in channel.platform.lower() if channel.platform else False:
            channel_type = "work"
        else:
            channel_type = "private"
        
        if channel_type in channel_rules:
            rules = channel_rules[channel_type]
            
            # Apply boundary caps
            boundaries.max_flirtation = min(boundaries.max_flirtation, rules["max_flirtation"])
            boundaries.max_humor = min(boundaries.max_humor, rules["max_humor"])
            boundaries.max_candor = min(boundaries.max_candor, rules["max_candor"])
            boundaries.min_formality = max(boundaries.min_formality, rules["min_formality"])
            
            # Add safety tags
            for tag in rules["safety_tags"]:
                if tag not in boundaries.safety_tags:
                    boundaries.safety_tags.append(tag)
        
        return boundaries
    
    def _apply_context_boundaries(
        self,
        boundaries: BoundaryCaps,
        context: Dict[str, Any]
    ) -> BoundaryCaps:
        """Apply context-based boundary adjustments."""
        # Check for presence of children
        if context.get("children_present", False):
            boundaries.max_flirtation = min(boundaries.max_flirtation, 0.0)
            boundaries.max_humor = min(boundaries.max_humor, 0.8)
            boundaries.max_candor = min(boundaries.max_candor, 0.3)
            boundaries.min_formality = max(boundaries.min_formality, 0.5)
            
            if "child_safe" not in boundaries.safety_tags:
                boundaries.safety_tags.append("child_safe")
        
        # Check for work context
        if context.get("work_context", False):
            boundaries.max_flirtation = min(boundaries.max_flirtation, 0.1)
            boundaries.max_humor = min(boundaries.max_humor, 0.6)
            boundaries.max_candor = min(boundaries.max_candor, 0.7)
            boundaries.min_formality = max(boundaries.min_formality, 0.6)
            
            if "work_appropriate" not in boundaries.safety_tags:
                boundaries.safety_tags.append("work_appropriate")
        
        # Check for sensitive topics
        sensitive_topics = context.get("sensitive_topics", [])
        if sensitive_topics:
            boundaries.max_candor = min(boundaries.max_candor, 0.5)
            boundaries.min_formality = max(boundaries.min_formality, 0.6)
            
            if "sensitive_content" not in boundaries.safety_tags:
                boundaries.safety_tags.append("sensitive_content")
        
        # Check for emotional state
        emotional_state = context.get("emotional_state", "neutral")
        if emotional_state in ["vulnerable", "sad", "angry"]:
            boundaries.max_humor = min(boundaries.max_humor, 0.5)
            boundaries.max_candor = min(boundaries.max_candor, 0.6)
            
            if "emotionally_sensitive" not in boundaries.safety_tags:
                boundaries.safety_tags.append("emotionally_sensitive")
        
        return boundaries
    
    def _apply_time_boundaries(self, boundaries: BoundaryCaps) -> BoundaryCaps:
        """Apply time-based boundary adjustments."""
        from datetime import datetime
        
        now = datetime.now()
        hour = now.hour
        
        # Determine time period
        if 9 <= hour <= 17:  # Business hours
            time_type = "business_hours"
        elif 18 <= hour <= 22:  # After hours
            time_type = "after_hours"
        else:  # Late night
            time_type = "late_night"
        
        time_rules = self._boundary_rules["time_rules"]
        if time_type in time_rules:
            rules = time_rules[time_type]
            
            # Apply boundary caps
            boundaries.max_flirtation = min(boundaries.max_flirtation, rules["max_flirtation"])
            boundaries.max_humor = min(boundaries.max_humor, rules["max_humor"])
            boundaries.min_formality = max(boundaries.min_formality, rules["min_formality"])
        
        return boundaries
    
    def _clamp_boundaries(self, boundaries: BoundaryCaps) -> BoundaryCaps:
        """Ensure boundary values are within valid ranges."""
        boundaries.max_flirtation = max(0.0, min(1.0, boundaries.max_flirtation))
        boundaries.max_humor = max(0.0, min(1.0, boundaries.max_humor))
        boundaries.max_candor = max(0.0, min(1.0, boundaries.max_candor))
        boundaries.min_formality = max(0.0, min(1.0, boundaries.min_formality))
        
        return boundaries
    
    def check_content_safety(
        self,
        content: str,
        boundaries: BoundaryCaps
    ) -> Dict[str, Any]:
        """
        Check content for safety and appropriateness.
        
        Args:
            content: Content to check
            boundaries: Current boundary caps
            
        Returns:
            Safety assessment results
        """
        content_lower = content.lower()
        safety_issues = []
        risk_level = "low"
        
        # Check for sensitive words
        for category, words in self._safety_patterns.items():
            found_words = [word for word in words if word in content_lower]
            if found_words:
                safety_issues.append({
                    "category": category,
                    "words": found_words,
                    "severity": "medium" if category == "sensitive_words" else "low"
                })
        
        # Determine risk level
        if any(issue["severity"] == "medium" for issue in safety_issues):
            risk_level = "medium"
        elif len(safety_issues) > 2:
            risk_level = "high"
        
        # Check boundary violations
        boundary_violations = []
        
        # Check for excessive flirtation
        flirtation_indicators = ["flirt", "romantic", "attractive", "beautiful", "handsome"]
        flirtation_count = sum(1 for word in flirtation_indicators if word in content_lower)
        if flirtation_count > 2 and boundaries.max_flirtation < 0.5:
            boundary_violations.append("excessive_flirtation")
        
        # Check for excessive humor
        humor_indicators = ["joke", "funny", "hilarious", "lol", "haha"]
        humor_count = sum(1 for word in humor_indicators if word in content_lower)
        if humor_count > 3 and boundaries.max_humor < 0.7:
            boundary_violations.append("excessive_humor")
        
        # Check for excessive candor
        candor_indicators = ["honestly", "truthfully", "frankly", "bluntly"]
        candor_count = sum(1 for word in candor_indicators if word in content_lower)
        if candor_count > 2 and boundaries.max_candor < 0.6:
            boundary_violations.append("excessive_candor")
        
        return {
            "safe": len(safety_issues) == 0 and len(boundary_violations) == 0,
            "risk_level": risk_level,
            "safety_issues": safety_issues,
            "boundary_violations": boundary_violations,
            "recommendations": self._generate_safety_recommendations(
                safety_issues, boundary_violations, boundaries
            ),
        }
    
    def _generate_safety_recommendations(
        self,
        safety_issues: List[Dict[str, Any]],
        boundary_violations: List[str],
        boundaries: BoundaryCaps
    ) -> List[str]:
        """Generate recommendations for safety improvements."""
        recommendations = []
        
        if safety_issues:
            recommendations.append("Consider softening language around sensitive topics")
        
        if "excessive_flirtation" in boundary_violations:
            recommendations.append("Reduce flirtatious language for current context")
        
        if "excessive_humor" in boundary_violations:
            recommendations.append("Tone down humor for current audience")
        
        if "excessive_candor" in boundary_violations:
            recommendations.append("Consider more diplomatic language")
        
        if "child_safe" in boundaries.safety_tags:
            recommendations.append("Ensure content is appropriate for children")
        
        if "work_appropriate" in boundaries.safety_tags:
            recommendations.append("Maintain professional tone")
        
        return recommendations
    
    def get_boundary_summary(self, boundaries: BoundaryCaps) -> Dict[str, Any]:
        """Get a summary of current boundary settings."""
        return {
            "flirtation_allowed": boundaries.max_flirtation > 0.3,
            "humor_level": "high" if boundaries.max_humor > 0.7 else "moderate" if boundaries.max_humor > 0.4 else "low",
            "candor_level": "high" if boundaries.max_candor > 0.7 else "moderate" if boundaries.max_candor > 0.4 else "low",
            "formality_level": "high" if boundaries.min_formality > 0.6 else "moderate" if boundaries.min_formality > 0.3 else "low",
            "safety_tags": boundaries.safety_tags,
            "overall_restrictiveness": "high" if boundaries.max_flirtation < 0.2 and boundaries.max_candor < 0.4 else "moderate" if boundaries.max_flirtation < 0.5 and boundaries.max_candor < 0.6 else "low",
        }