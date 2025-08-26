# Personality Matrix (PMX) - Survivable Personality Layer

The Personality Matrix (PMX) is a survivable personality layer for autonomous AI systems that provides consistency across different LLMs. It implements the protocols from `aegis-core` and exposes traits/affect that meaningfully tilt utility, decoding, memory lensing, and policy.

## Overview

PMX provides a static, survivable personality that is not dependent on specific LLMs but ensures consistency across multiple AI backends. It manages:

- **Trait Kernel**: Immutable baseline traits (creative, analytical, empathic, curiosity, balance)
- **Affect Engine**: Dynamic arousal/valence/stress with decay and event-driven updates
- **Boundary Manager**: Policy decision hints with reasons and conditions
- **Style Synthesizer**: FLOW/DEEP/CRISIS mode selection and decoding hints

## Key Features

### Trait Kernel
- **Immutable baseline traits**: creative, analytical, empathic, curiosity, balance ∈ [0,1]
- **Context-aware weight resolution**: `resolve_weights(context) -> dict`
- **Trait-based adjustments**: Influences style synthesis and decision making

### Affect Engine
- **Three-dimensional affect**: arousal, valence, stress with natural decay
- **Event-driven updates**: Reacts to EventBus topics (plan:*, tool:*, success/failure)
- **Affect snapshots**: `get_affect_snapshot() -> dict`
- **State interactions**: Complex interactions between affect dimensions

### Boundary Manager
- **Policy decision hints**: Exposes reasons and conditions
- **Cooldown management**: "require summary first", "no external post for 10m"
- **Context-aware boundaries**: Adjusts based on audience, channel, urgency
- **Safety and appropriateness**: Dynamic boundary adjustment

### Style Synthesizer
- **Mode selection**: FLOW/DEEP/CRISIS based on context and affect
- **Decoding hints**: Temperature, top_p, max_tokens, repetition_penalty
- **Context adaptation**: Audience, channel, time pressure adjustments
- **Trait integration**: Personality traits influence style parameters

## Architecture

```
aegis-pmx/
├── pyproject.toml          # Package configuration
├── src/pmx/
│   ├── __init__.py         # Package exports
│   ├── models.py           # Data models (Traits, AffectSnapshot, Config)
│   ├── matrix.py           # Main PersonalityMatrix class
│   ├── affect.py           # AffectEngine with decay and events
│   ├── boundary.py         # BoundaryManager with policy hints
│   ├── style.py            # StyleSynthesizer for mode selection
│   └── adapters.py         # SDE and scaffolding integration
└── tests/
    ├── test_traits_weights.py
    ├── test_affect_decay_and_events.py
    ├── test_boundary_policy_hints.py
    └── test_style_mode_selection.py
```

## Installation

```bash
# Install from source
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

## Quick Start

```python
from pmx import PersonalityMatrix, PMXConfig

# Create configuration
config = PMXConfig(
    affect_decay_rate=0.95,
    arousal_setpoint=0.5,
    valence_setpoint=0.0,
    stress_setpoint=0.2,
)

# Initialize personality matrix
pmx = PersonalityMatrix(config)

# Resolve trait weights for context
context = {
    "task_type": "creative",
    "audience": "friend",
    "urgency": "low",
}
weights = pmx.resolve_weights(context)

# Get current affect snapshot
affect = pmx.get_affect_snapshot()

# Get style mode for context
style_mode = pmx.get_style_mode(context)

# Get policy hints
policy_hints = pmx.get_policy_hints(context)
```

## Core Components

### PersonalityMatrix

The main orchestrator class that manages all PMX functionality:

```python
class PersonalityMatrix:
    def resolve_weights(self, context: Dict[str, Any]) -> TraitWeights
    def get_affect_snapshot(self) -> AffectSnapshot
    def get_style_mode(self, context: Dict[str, Any]) -> StyleMode
    def get_boundary_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
    def get_policy_hints(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
```

### AffectEngine

Manages affective states with decay and event-driven updates:

```python
class AffectEngine:
    def apply_decay(self, affect: AffectSnapshot) -> AffectSnapshot
    def apply_event_impact(self, affect: AffectSnapshot, event_type: str, intensity: float) -> AffectSnapshot
    def get_affect_stability_score(self, affect: AffectSnapshot) -> float
```

### BoundaryManager

Provides policy decision hints and boundary conditions:

```python
class BoundaryManager:
    def get_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
    def get_policy_hints(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
    def set_cooldown(self, condition_id: str, context: Dict[str, Any], duration_seconds: float)
```

### StyleSynthesizer

Synthesizes style modes and decoding parameters:

```python
class StyleSynthesizer:
    def synthesize_mode(self, weights: TraitWeights, affect: AffectSnapshot, context: Dict[str, Any]) -> StyleMode
    def get_mode_recommendation(self, weights: TraitWeights, affect: AffectSnapshot, context: Dict[str, Any]) -> Dict[str, Any]
```

## Integration with aegis-core

PMX implements the protocols from `aegis-core`:

```python
from sam_core.contracts.pmx import PersonalityMatrix as CorePersonalityMatrix
from sam_core.event_bus import EventBus
from sam_core.state_store import StateStore

# Convert to core contract
core_pmx = pmx.to_core()

# Use with event bus
pmx = PersonalityMatrix(event_bus=event_bus)

# Use with state store
pmx = PersonalityMatrix(state_store=state_store)
```

## Event Bus Integration

PMX subscribes to EventBus topics and publishes updates:

```python
# Subscribes to:
# - plan:* (plan:start, plan:complete, plan:fail)
# - tool:* (tool:success, tool:fail)
# - success/failure events
# - learning:* (learning:start, learning:breakthrough, learning:frustration)
# - social:* (social:interaction, social:conflict)

# Publishes:
# - pmx:affect-update
# - pmx:style-update
```

## Style Modes

PMX provides three primary style modes:

### FLOW Mode
- **Use case**: Creative tasks, brainstorming, casual conversation
- **Parameters**: High temperature (0.8), high creativity boost, longer responses
- **Triggers**: Creative tasks, low urgency, positive affect

### DEEP Mode
- **Use case**: Analytical tasks, problem solving, detailed analysis
- **Parameters**: Medium temperature (0.4), high analytical boost, longer responses
- **Triggers**: Analytical tasks, professional audience, moderate urgency

### CRISIS Mode
- **Use case**: Urgent situations, high-stakes decisions, time pressure
- **Parameters**: Low temperature (0.2), high analytical boost, shorter responses
- **Triggers**: High urgency, high stress, critical decisions

## Boundary Conditions

PMX provides several built-in boundary conditions:

- **External Post Cooldown**: Prevents spam and maintains quality
- **Summary Requirement**: Ensures complex topics are summarized first
- **High Stress Protection**: Protects against poor decisions during stress
- **Creative Flow Protection**: Protects creative states from interruption
- **Learning Mode Protection**: Protects learning sessions
- **Social Interaction Limits**: Maintains appropriate interaction frequency

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_traits_weights.py
pytest tests/test_affect_decay_and_events.py
pytest tests/test_boundary_policy_hints.py
pytest tests/test_style_mode_selection.py

# Run with coverage
pytest --cov=pmx --cov-report=html
```

## Configuration

PMX can be configured through the `PMXConfig` class:

```python
config = PMXConfig(
    # Trait settings
    default_traits=TraitKernel(
        creative=0.7,
        analytical=0.8,
        empathic=0.8,
        curiosity=0.9,
        balance=0.7,
    ),
    
    # Affect settings
    affect_decay_rate=0.95,
    arousal_setpoint=0.5,
    valence_setpoint=0.0,
    stress_setpoint=0.2,
    
    # Style settings
    style_adaptation_rate=0.3,
    
    # Boundary settings
    boundary_check_interval=5.0,
    
    # Persistence settings
    snapshot_interval=30.0,
    trait_delta_threshold=0.1,
)
```

## Adapters

PMX provides adapters for integration with other components:

### SDEAdapter
Integrates with the Decision Engine to provide style information and policy hints.

### ScaffoldingAdapter
Integrates with the Neural Core (scaffolding) for state persistence and memory lensing.

### EventBusAdapter
Handles event bus subscriptions and publishing for PMX updates.

## Definition of Done

The PMX implementation is complete when:

1. **Trait weights tilt as expected**: Given synthetic events, traits tilt weights as expected
2. **Mode selection influenced by PMX**: Style mode selection is influenced by personality state
3. **Boundary conditions surface reasons**: Policy hints provide clear reasons and conditions
4. **Event-driven updates work**: Affect updates respond to EventBus events
5. **Integration with core works**: PMX implements all required core protocols
6. **Comprehensive test coverage**: All functionality is thoroughly tested

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.