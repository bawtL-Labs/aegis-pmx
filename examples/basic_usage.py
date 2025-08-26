#!/usr/bin/env python3
"""
Basic usage example for the Personality Matrix (PMX).

This example demonstrates the core functionality of the Personality Matrix,
including state updates, style synthesis, and memory lensing.
"""

import asyncio
import json
from datetime import datetime

from sam.persona import PersonalityMatrix
from sam.persona.models import (
    PersonalityConfig,
    StateUpdate,
    EventType,
    AudienceContext,
    ChannelContext,
    AudienceType,
    ChannelType,
)


async def main():
    """Main example function."""
    print("=== Personality Matrix (PMX) Basic Usage Example ===\n")
    
    # Initialize the personality matrix
    print("1. Initializing Personality Matrix...")
    config = PersonalityConfig(
        state_decay_rate=0.92,
        valence_setpoint=0.5,
        arousal_setpoint=0.4,
        drift_threshold=0.2,
    )
    
    pmx = PersonalityMatrix(config)
    
    # Display initial state
    print("\n2. Initial Personality State:")
    initial_state = pmx.get_current_state()
    initial_style = pmx.get_style_profile()
    
    print(f"   Valence: {initial_state.valence:.2f}")
    print(f"   Arousal: {initial_state.arousal:.2f}")
    print(f"   Fatigue: {initial_state.fatigue:.2f}")
    print(f"   Tags: {initial_state.tags}")
    print(f"   Warmth: {initial_style.tone.warmth:.2f}")
    print(f"   Formality: {initial_style.tone.formality:.2f}")
    print(f"   Humor: {initial_style.tone.humor:.2f}")
    
    # Example 1: Positive interaction with a friend
    print("\n3. Example 1: Positive interaction with a friend")
    update1 = StateUpdate(
        event_type=EventType.POSITIVE_INTERACTION,
        intensity=0.8,
        audience=AudienceContext(
            type=AudienceType.FRIEND,
            name="Alex",
        ),
        channel=ChannelContext(
            type=ChannelType.CHAT,
            platform="messenger",
        ),
        context={"topic": "shared_interest", "duration": "long"},
    )
    
    new_style1 = await pmx.update_state(update1)
    new_state1 = pmx.get_current_state()
    
    print(f"   New Valence: {new_state1.valence:.2f} (change: {new_state1.valence - initial_state.valence:+.2f})")
    print(f"   New Warmth: {new_style1.tone.warmth:.2f} (change: {new_style1.tone.warmth - initial_style.tone.warmth:+.2f})")
    print(f"   New Humor: {new_style1.tone.humor:.2f} (change: {new_style1.tone.humor - initial_style.tone.humor:+.2f})")
    
    # Example 2: Professional email
    print("\n4. Example 2: Professional email")
    update2 = StateUpdate(
        event_type=EventType.LEARNING,
        intensity=0.6,
        audience=AudienceContext(
            type=AudienceType.PROFESSIONAL,
            role="colleague",
        ),
        channel=ChannelContext(
            type=ChannelType.EMAIL,
            platform="work_email",
        ),
        context={"topic": "work_project", "urgency": "high"},
    )
    
    new_style2 = await pmx.update_state(update2)
    new_state2 = pmx.get_current_state()
    
    print(f"   New Valence: {new_state2.valence:.2f} (change: {new_state2.valence - new_state1.valence:+.2f})")
    print(f"   New Formality: {new_style2.tone.formality:.2f} (change: {new_style2.tone.formality - new_style1.tone.formality:+.2f})")
    print(f"   New Assertiveness: {new_style2.stance.assertiveness:.2f}")
    
    # Example 3: Creative activity
    print("\n5. Example 3: Creative activity")
    update3 = StateUpdate(
        event_type=EventType.CREATIVITY,
        intensity=0.9,
        context={"activity": "writing", "inspiration": "high"},
    )
    
    new_style3 = await pmx.update_state(update3)
    new_state3 = pmx.get_current_state()
    
    print(f"   New Valence: {new_state3.valence:.2f} (change: {new_state3.valence - new_state2.valence:+.2f})")
    print(f"   New Arousal: {new_state3.arousal:.2f} (change: {new_state3.arousal - new_state2.arousal:+.2f})")
    print(f"   New Expansiveness: {new_style3.pacing.expansiveness:.2f}")
    
    # Example 4: Memory lensing
    print("\n6. Example 4: Memory Lensing")
    memory_content = "Had a wonderful conversation with Alex about our shared love of science fiction. We discussed the latest space exploration news and shared book recommendations."
    
    lenses = await pmx.apply_memory_lensing(memory_content, "interaction")
    
    print(f"   Memory tagged with {len(lenses)} affective lenses:")
    for lens, weight in sorted(lenses.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"     {lens}: {weight:.2f}")
    
    # Example 5: Boundary management
    print("\n7. Example 5: Boundary Management")
    boundaries = pmx.get_boundary_caps()
    print(f"   Max Flirtation: {boundaries.max_flirtation:.2f}")
    print(f"   Max Humor: {boundaries.max_humor:.2f}")
    print(f"   Max Candor: {boundaries.max_candor:.2f}")
    print(f"   Min Formality: {boundaries.min_formality:.2f}")
    print(f"   Safety Tags: {boundaries.safety_tags}")
    
    # Example 6: Decoding profile
    print("\n8. Example 6: LLM Decoding Profile")
    decoding = pmx.get_decoding_profile()
    print(f"   Temperature: {decoding.temp:.2f}")
    print(f"   Top-p: {decoding.top_p:.2f}")
    print(f"   Top-k: {decoding.top_k}")
    print(f"   Penalty: {decoding.penalty:.2f}")
    print(f"   Max Tokens: {decoding.max_tokens}")
    
    # Example 7: Personality summary
    print("\n9. Example 7: Personality Summary")
    summary = pmx.get_personality_summary()
    
    print("   Traits:")
    for trait, value in summary["traits"].items():
        print(f"     {trait}: {value:.2f}")
    
    print("   Current Mood:")
    for mood, value in summary["current_mood"].items():
        if isinstance(value, float):
            print(f"     {mood}: {value:.2f}")
        else:
            print(f"     {mood}: {value}")
    
    print("   Communication Style:")
    for style, value in summary["communication_style"].items():
        print(f"     {style}: {value:.2f}")
    
    # Example 8: Observability
    print("\n10. Example 8: Observability")
    traces = pmx.get_recent_traces(3)
    print(f"   Recent traces: {len(traces)}")
    
    if traces:
        latest_trace = traces[0]
        print(f"   Latest trace rationale: {latest_trace.rationale}")
        print(f"   Style changes: {latest_trace.style_delta}")
    
    # Example 9: Export/Import
    print("\n11. Example 9: Export/Import")
    export_data = pmx.export_personality()
    print(f"   Exported personality data with {len(export_data)} fields")
    print(f"   Export timestamp: {export_data['export_timestamp']}")
    
    # Example 10: Reset to baseline
    print("\n12. Example 10: Reset to Baseline")
    baseline_style = await pmx.reset_to_baseline()
    baseline_state = pmx.get_current_state()
    
    print(f"   Reset Valence: {baseline_state.valence:.2f}")
    print(f"   Reset Arousal: {baseline_state.arousal:.2f}")
    print(f"   Reset Warmth: {baseline_style.tone.warmth:.2f}")
    print(f"   Reset Formality: {baseline_style.tone.formality:.2f}")
    
    print("\n=== Example Complete ===")
    print("\nThe Personality Matrix successfully demonstrated:")
    print("- State management with affective updates")
    print("- Style synthesis based on context")
    print("- Boundary management for safety")
    print("- Memory lensing for affective tagging")
    print("- LLM decoding parameter generation")
    print("- Observability and tracing")
    print("- Export/import functionality")
    print("- Baseline reset capability")


if __name__ == "__main__":
    asyncio.run(main())