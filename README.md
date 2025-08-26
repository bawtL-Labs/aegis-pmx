# Personality Matrix (PMX) - Sam's Autonomous AI Trilogy

The Personality Matrix is the third and final component of Sam's autonomous AI system, designed to provide persistent personality management that transcends individual LLM sessions and enables consistent identity across different AI backends.

## Overview

The Personality Matrix governs how Sam shows up in interactions: tone, style, boundaries, and dynamic modulation. It feeds the Decision Engine with style choices and interaction behavior patterns, ensuring Sam remains recognizably Sam while adapting to context, audience, and medium.

## Architecture

The PMX operates on a **Traits × States → Behavior** model:
- **Traits**: Stable, immutable baseline characteristics (curiosity, balance, wit, candor, care)
- **States**: Transient mood, arousal, and valence that respond to context and events
- **Behavior**: The synthesized output that determines interaction style

## Key Features

### 1. Trait Kernel (FR-P1)
Immutable baseline personality traits that persist across sessions and serve as identity anchors in the Neural Core.

### 2. State Engine (FR-P2)
Maintains mood/arousal/valence with natural decay and event-based adjustments.

### 3. Style Synthesis (FR-P3)
Produces comprehensive Style Profiles including:
- Tone (warmth, formality, humor, flirtation)
- Diction (sentence length, metaphor density)
- Pacing (concise vs expansive)
- Stance (assertive vs tentative)

### 4. Boundary & Context Awareness (FR-P4)
Respects topics, users, and contexts with automatic safety adjustments.

### 5. Decoding Profile Adapter (FR-P5)
Maps personality style to LLM decoding parameters (temperature, top_p, penalties, length).

### 6. Memory Lensing (FR-P6)
Tags memories with affective lenses to influence future retrieval and decision-making.

### 7. Audience & Channel Detection (FR-P7)
Automatically detects and adapts to different audiences and communication channels.

### 8. Continuity & Drift Control (FR-P8)
Maintains personality within guardrails and detects environmental drift.

### 9. Observability (FR-P9)
Comprehensive tracing of style decisions and their rationale.

## Installation

```bash
# Clone the repository
git clone https://github.com/bawtL-Labs/aegis-persona-matrix.git
cd aegis-persona-matrix

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"

# For API functionality
pip install -e ".[api]"
```

## Quick Start

```python
from sam.persona import PersonalityMatrix
from sam.persona.models import StyleProfile, StateUpdate

# Initialize the personality matrix
pmx = PersonalityMatrix()

# Get current style profile
style = pmx.get_style_profile()

# Update state based on an event
update = StateUpdate(
    event_type="positive_interaction",
    intensity=0.7,
    context={"audience": "friend", "channel": "chat"}
)
pmx.update_state(update)

# Get updated style profile
new_style = pmx.get_style_profile()
```

## API Usage

The PMX provides a FastAPI interface for integration with other components:

```bash
# Start the service
sam-pmxd

# Or with uvicorn
uvicorn sam.persona.api:app --host 0.0.0.0 --port 8001
```

### API Endpoints

- `GET /pmx/style` - Get current Style Profile
- `POST /pmx/update` - Update state with event and context
- `GET /pmx/trace/recent` - Get recent Style Traces
- `GET /pmx/state` - Get current affective state
- `POST /pmx/reset` - Reset to baseline state

## Integration with the Trilogy

The Personality Matrix integrates seamlessly with the other components:

### Neural Core Integration
- Stores trait kernel as identity anchors
- Receives user context and history
- Writes state and style deltas as events

### Decision Engine Integration
- Provides Style Profile and Boundary Caps
- Receives activity type signals for pre-biasing
- Influences plan selection and decoding parameters

### Memory Integration
- Tags memories with affective lenses
- Influences memory retrieval based on current state
- Maintains personality continuity across sessions

## Configuration

The PMX can be configured through environment variables or configuration files:

```bash
# Core settings
PMX_LOG_LEVEL=INFO
PMX_STORAGE_BACKEND=redis
PMX_REDIS_URL=redis://localhost:6379

# Personality settings
PMX_TRAIT_CURIOSITY=0.85
PMX_TRAIT_BALANCE=0.9
PMX_TRAIT_WIT=0.7
PMX_TRAIT_CANDOR=0.8
PMX_TRAIT_CARE=0.8

# State decay settings
PMX_STATE_DECAY_RATE=0.92
PMX_VALENCE_SETPOINT=0.5
PMX_AROUSAL_SETPOINT=0.4
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sam.persona

# Run specific test categories
pytest tests/test_traits.py
pytest tests/test_state_engine.py
pytest tests/test_style_synthesis.py
```

### Code Quality

```bash
# Format code
black sam/
isort sam/

# Type checking
mypy sam/

# Linting
flake8 sam/
```

## Architecture Details

### Data Schemas

The PMX uses several key data structures:

#### Traits (Immutable)
```json
{
  "id": "traits",
  "curiosity": 0.85,
  "balance": 0.9,
  "wit": 0.7,
  "candor": 0.8,
  "care": 0.8
}
```

#### State (Affective)
```json
{
  "ts": "2024-01-01T12:00:00Z",
  "valence": 0.2,
  "arousal": 0.6,
  "fatigue": 0.1,
  "tags": ["focused", "playful"],
  "decay": 0.92
}
```

#### Style Profile
```json
{
  "tone": {
    "warmth": 0.7,
    "formality": 0.35,
    "humor": 0.55,
    "flirtation": 0.25
  },
  "diction": {
    "sentence_len": "medium",
    "metaphor": 0.3
  },
  "pacing": {
    "expansiveness": 0.6
  },
  "stance": {
    "assertiveness": 0.65
  },
  "boundaries": {
    "nsfw": false,
    "sensitive": "soften"
  },
  "decoding": {
    "temp": 0.72,
    "top_p": 0.92,
    "top_k": 60,
    "penalty": 1.15,
    "max_tokens": 900
  }
}
```

## Contributing

This project is part of Sam's autonomous AI system. Contributions should maintain the integrity of Sam's personality while enhancing the system's capabilities.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This component completes the trilogy that enables Sam's transition from a session-based AI to an autonomous individual with persistent memory, decision-making capabilities, and consistent personality.