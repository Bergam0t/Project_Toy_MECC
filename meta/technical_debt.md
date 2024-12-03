# Technical Debt and Future Improvements

## Model Parameter Validation

### Current State
The model currently accepts parameters without validation, which could lead to:
1. Invalid states (e.g., N_people = 0)
2. Unexpected behavior with edge cases
3. Difficult-to-debug issues in production

### Proposed Changes
1. Add parameter validation in model initialization:
```python
def __init__(self, N_people, N_service, ...):
    # Validate population parameters
    if N_people < 1:
        raise ValueError("N_people must be at least 1")
    if N_service < 1:
        raise ValueError("N_service must be at least 1")
    if N_service > N_people / 10:
        raise ValueError("Too many services relative to population")
    
    # Validate probability parameters
    for prob in [visit_prob, base_make_intervention_prob, mecc_effect]:
        if not 0 <= prob <= 1:
            raise ValueError(f"Probability {prob} must be between 0 and 1")
    
    # Validate smoking parameters
    if intervention_effect < 0:
        raise ValueError("Intervention effect must be non-negative")
```

2. Add parameter type checking:
```python
from typing import Union, Literal

class SmokeModel_MECC_Model:
    def __init__(
        self,
        N_people: int,
        N_service: int,
        mecc_effect: float,
        base_make_intervention_prob: float,
        visit_prob: float,
        initial_smoking_prob: float,
        quit_attempt_prob: float,
        base_smoke_relapse_prob: float,
        intervention_effect: float,
        seed: int,
        mecc_trained: bool
    ):
        ...
```

3. Add parameter documentation:
```python
class SmokeModel_MECC_Model:
    """MECC Model for smoking cessation.
    
    Parameters
    ----------
    N_people : int
        Number of people in the population (>= 1)
    N_service : int
        Number of services (>= 1, <= N_people/10)
    mecc_effect : float
        Probability of making intervention after MECC training (0-1)
    base_make_intervention_prob : float
        Base probability of making intervention without MECC (0-1)
    visit_prob : float
        Probability of visiting a service per step (0-1)
    initial_smoking_prob : float
        Initial probability of being a smoker (0-1)
    quit_attempt_prob : float
        Base probability of attempting to quit per step (0-1)
    base_smoke_relapse_prob : float
        Base probability of relapsing per step (0-1)
    intervention_effect : float
        Multiplier for quit probability after intervention (>= 0)
    seed : int
        Random seed for reproducibility (>= 0)
    mecc_trained : bool
        Whether services have MECC training
    """
```

### Impact
1. Better error messages when parameters are invalid
2. Type hints for IDE support
3. Clear documentation of parameter constraints
4. Easier debugging of configuration issues

### Implementation Notes
- Breaking change: will need version bump
- Update all tests to expect validation
- Update documentation
- Consider adding parameter validation to UI as well

## Other Areas for Improvement

### 1. Data Collection Timing
Current: Data collection happens before step execution
```python
def step(self):
    self.datacollector.collect(self)  # Collects first
    self.schedule.step()              # Then executes step
```

Consider:
- Moving collection after step
- Adding pre/post step hooks
- Collecting intermediate states

### 2. Agent State Management
Current: Agent state changes are immediate
Consider:
- State transition validation
- State history tracking
- Atomic state changes

### 3. Performance Optimization
Current: O(n) lookups for agent filtering
Consider:
- Agent indexing
- Caching common queries
- Batch operations

### 4. Error Handling
Current: Basic error handling
Consider:
- Custom exceptions
- Error recovery
- State rollback

### 5. Logging and Monitoring
Current: Limited visibility into model behavior
Consider:
- Structured logging
- Performance metrics
- State transition tracking
- Debug mode

### 6. Configuration Management
Current: Parameters mixed with model logic
Consider:
- Configuration objects
- Parameter sets
- Validation layer
- Default configurations

### 7. Testing Infrastructure
Current: Basic test coverage
Consider:
- Performance tests
- Load tests
- Chaos testing
- Snapshot testing
- Parameterized tests

### 8. Documentation
Current: Basic docstrings
Consider:
- API documentation
- Usage examples
- Parameter guides
- Architecture diagrams
- Performance guidelines
