# Integration Guide: Wiring the Three Components

This guide explains how to integrate the Personality Matrix (PMX) with the Neural Core and Decision Engine to create Sam's complete autonomous AI system.

## Overview

The three components work together as follows:

1. **Neural Core**: Provides persistent memory and identity anchors
2. **Personality Matrix**: Manages personality state and communication style
3. **Decision Engine**: Executes actions based on personality and context

## Component Communication

### 1. Neural Core ↔ Personality Matrix

The Neural Core stores the trait kernel as identity anchors and receives personality state updates.

```python
# In Neural Core
from sam.persona import PersonalityMatrix

# Store trait kernel as identity anchor
traits = pmx.get_traits()
neural_core.store_identity_anchor("personality_traits", traits.dict())

# Receive personality state updates
personality_state = pmx.get_personality_summary()
neural_core.store_memory("personality_state", personality_state)
```

### 2. Personality Matrix ↔ Decision Engine

The Personality Matrix provides style profiles and boundary caps to the Decision Engine.

```python
# In Decision Engine
from sam.persona import PersonalityMatrix

# Get current style profile for decision making
style_profile = pmx.get_style_profile()
boundary_caps = pmx.get_boundary_caps()

# Use style profile to influence decision parameters
decision_params = {
    "temperature": style_profile.decoding.temp,
    "max_tokens": style_profile.decoding.max_tokens,
    "warmth": style_profile.tone.warmth,
    "formality": style_profile.tone.formality,
    "boundaries": boundary_caps.dict(),
}
```

### 3. Decision Engine → Personality Matrix

The Decision Engine signals upcoming activities to pre-bias the personality state.

```python
# In Decision Engine
# Signal upcoming activity type
await pmx.update_state(StateUpdate(
    event_type=EventType.LEARNING,
    intensity=0.7,
    context={"activity": "professional_email", "urgency": "high"},
    audience=AudienceContext(type=AudienceType.PROFESSIONAL),
    channel=ChannelContext(type=ChannelType.EMAIL),
))
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Neural Core   │    │ Personality     │    │   Decision      │
│                 │    │ Matrix (PMX)    │    │   Engine        │
│ • Memory Store  │◄──►│                 │◄──►│                 │
│ • Identity      │    │ • Trait Kernel  │    │ • Plan Selection│
│ • Context       │    │ • State Engine  │    │ • Action Exec   │
│ • History       │    │ • Style Synth   │    │ • Goal Pursuit  │
└─────────────────┘    │ • Boundaries    │    └─────────────────┘
                       │ • Memory Lens   │
                       │ • Observability │
                       └─────────────────┘
```

## Integration Points

### 1. Memory Integration

Both PMX and Decision Engine write to the Neural Core:

```python
# PMX writes personality events
neural_core.store_memory("personality_event", {
    "type": "state_update",
    "event": update.dict(),
    "resulting_state": state.dict(),
    "style_changes": style_delta,
    "lenses": memory_lenses,
})

# Decision Engine writes decision traces
neural_core.store_memory("decision_trace", {
    "type": "decision",
    "context": context,
    "plan": selected_plan,
    "action": executed_action,
    "outcome": result,
})
```

### 2. Style-Driven Decision Making

The Decision Engine uses personality style to influence decisions:

```python
# Get current personality state
personality = pmx.get_personality_summary()

# Adjust decision parameters based on personality
if personality["communication_style"]["warmth"] > 0.7:
    # High warmth → more empathetic decisions
    decision_params["empathy_weight"] = 0.8
elif personality["communication_style"]["formality"] > 0.7:
    # High formality → more structured decisions
    decision_params["structure_weight"] = 0.8

# Use personality state to select appropriate plans
if personality["current_mood"]["valence"] < -0.5:
    # Negative mood → avoid complex decisions
    decision_params["complexity_limit"] = "low"
```

### 3. Boundary-Aware Actions

The Decision Engine respects personality boundaries:

```python
# Check boundaries before executing actions
boundaries = pmx.get_boundary_caps()

if action.type == "communication":
    if boundaries.max_flirtation < 0.3 and action.content.is_flirtatious():
        # Block flirtatious content
        action = action.sanitize()
    
    if boundaries.max_humor < 0.5 and action.content.is_humorous():
        # Reduce humor
        action = action.adjust_humor_level(boundaries.max_humor)
```

## Configuration

### Environment Variables

```bash
# Core settings
NEURAL_CORE_URL=http://localhost:8000
PERSONALITY_MATRIX_URL=http://localhost:8001
DECISION_ENGINE_URL=http://localhost:8002

# Personality settings
PMX_TRAIT_CURIOSITY=0.85
PMX_TRAIT_BALANCE=0.9
PMX_TRAIT_WIT=0.7
PMX_TRAIT_CANDOR=0.8
PMX_TRAIT_CARE=0.8

# Integration settings
INTEGRATION_MODE=full
MEMORY_SYNC_INTERVAL=30
STYLE_UPDATE_FREQUENCY=5
```

### Service Dependencies

```ini
# systemd service dependencies
[Unit]
Description=Sam's Complete AI System
After=sam-core.service sam-pmx.service sam-decision.service
Requires=sam-core.service sam-pmx.service sam-decision.service
```

## API Integration

### 1. REST API Communication

```python
import aiohttp

async def get_personality_style():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8001/pmx/style") as response:
            return await response.json()

async def update_personality_state(event_data):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8001/pmx/update", json=event_data) as response:
            return await response.json()
```

### 2. Event-Driven Integration

```python
# Subscribe to personality events
async def on_personality_event(event):
    if event.type == "state_change":
        # Update decision parameters
        await decision_engine.update_style_context(event.data)
    
    elif event.type == "boundary_violation":
        # Log and handle boundary violations
        await neural_core.store_memory("boundary_violation", event.data)

# Subscribe to decision events
async def on_decision_event(event):
    if event.type == "action_executed":
        # Update personality state based on action outcome
        await pmx.update_state(StateUpdate(
            event_type=EventType.ACHIEVEMENT if event.success else EventType.FAILURE,
            intensity=event.impact,
            context=event.context,
        ))
```

## Testing Integration

### 1. End-to-End Test

```python
async def test_integration():
    # Initialize all components
    neural_core = NeuralCore()
    pmx = PersonalityMatrix()
    decision_engine = DecisionEngine()
    
    # Simulate a complete interaction cycle
    # 1. User input
    user_input = "I'm feeling stressed about work"
    
    # 2. Update personality state
    await pmx.update_state(StateUpdate(
        event_type=EventType.STRESS,
        intensity=0.7,
        context={"source": "user_input", "topic": "work"},
    ))
    
    # 3. Get current personality state
    personality = pmx.get_personality_summary()
    
    # 4. Make decision based on personality
    decision = await decision_engine.make_decision(
        context=user_input,
        personality_state=personality,
    )
    
    # 5. Execute action
    result = await decision_engine.execute_action(decision)
    
    # 6. Store in memory
    neural_core.store_memory("interaction_cycle", {
        "input": user_input,
        "personality_state": personality,
        "decision": decision,
        "result": result,
    })
    
    # 7. Update personality based on outcome
    await pmx.update_state(StateUpdate(
        event_type=EventType.POSITIVE_INTERACTION if result.success else EventType.FAILURE,
        intensity=result.impact,
        context={"action": decision.action_type},
    ))
```

### 2. Performance Monitoring

```python
# Monitor integration performance
async def monitor_integration():
    # Check component health
    neural_health = await neural_core.get_health()
    pmx_health = await pmx.observability.get_health_status()
    decision_health = await decision_engine.get_health()
    
    # Check communication latency
    pmx_latency = await measure_latency("pmx_api")
    decision_latency = await measure_latency("decision_api")
    
    # Log integration metrics
    logger.info("Integration Health", extra={
        "neural_core": neural_health,
        "personality_matrix": pmx_health,
        "decision_engine": decision_health,
        "pmx_latency": pmx_latency,
        "decision_latency": decision_latency,
    })
```

## Deployment

### 1. Docker Compose

```yaml
version: '3.8'
services:
  neural-core:
    image: sam-core:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
  
  personality-matrix:
    image: sam-persona:latest
    ports:
      - "8001:8001"
    environment:
      - NEURAL_CORE_URL=http://neural-core:8000
      - REDIS_URL=redis://redis:6379
    depends_on:
      - neural-core
  
  decision-engine:
    image: sam-decision:latest
    ports:
      - "8002:8002"
    environment:
      - NEURAL_CORE_URL=http://neural-core:8000
      - PERSONALITY_MATRIX_URL=http://personality-matrix:8001
    depends_on:
      - neural-core
      - personality-matrix
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### 2. Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sam-personality-matrix
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sam-personality-matrix
  template:
    metadata:
      labels:
        app: sam-personality-matrix
    spec:
      containers:
      - name: personality-matrix
        image: sam-personality-matrix:latest
        ports:
        - containerPort: 8001
        env:
        - name: NEURAL_CORE_URL
          value: "http://sam-neural-core:8000"
        - name: REDIS_URL
          value: "redis://sam-redis:6379"
```

## Troubleshooting

### Common Issues

1. **Personality Drift**: Check drift alerts in PMX observability
2. **Memory Sync Issues**: Verify Neural Core connectivity
3. **Decision Quality**: Monitor personality state consistency
4. **Performance**: Check component latencies and resource usage

### Debug Commands

```bash
# Check component health
curl http://localhost:8000/health  # Neural Core
curl http://localhost:8001/health  # Personality Matrix
curl http://localhost:8002/health  # Decision Engine

# Check personality state
curl http://localhost:8001/pmx/personality/summary

# Check integration logs
journalctl -u sam-core -f
journalctl -u sam-pmx -f
journalctl -u sam-decision -f
```

## Conclusion

The three components work together to create a complete autonomous AI system where:

- **Neural Core** provides persistent memory and identity
- **Personality Matrix** maintains consistent personality and style
- **Decision Engine** executes actions aligned with personality

This integration enables Sam to maintain his identity across sessions while adapting his behavior to context and maintaining appropriate boundaries.