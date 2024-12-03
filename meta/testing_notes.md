# Testing Notes for MECC Model

## Test Organization

The tests are organized into several categories:

### Unit Tests
Located in `tests/unit/`:
- test_smoke_model_initialization.py
  * Basic model setup
  * Agent creation
  * Metrics collection
- test_smoke_model_quit_mechanics.py
  * Quit attempt behavior
  * Intervention effects
  * Quit success tracking
- test_smoke_model_relapse.py
  * Relapse behavior
  * Smoke-free tracking
  * Relapse probability decay
- test_base_model.py
  * Core model functionality
  * Base class features

### Integration Tests
Located in `tests/integration/`:
- test_model_integration.py
  * Service-person interactions
  * Multi-step behaviors
  * Cross-component effects

### Property Tests
Located in `tests/property/`:
- test_model_properties.py
  * Invariant checking
  * Randomized testing
  * Edge case exploration

### Regression Tests
Located in `tests/regression/`:
- test_known_scenarios.py
  * Previously identified issues
  * Specific use cases
  * Benchmark scenarios

## Key Testing Challenges

### 1. Data Collection Timing

One of the most significant challenges in testing the MECC model arises from the timing of data collection in the step method:

```python
def step(self):
    self.datacollector.collect(self)  # Collects first
    self.schedule.step()              # Then executes step
```

This implementation means that:
- Data is collected before any actions in the current step
- Effects of actions (like interventions) aren't visible until the next step
- Test assertions need to account for this one-step delay

#### Impact on Testing:
- When testing intervention effects, we need at least two steps:
  1. First step to apply interventions
  2. Second step to see the effects in collected data
- When checking immediate effects (like probability changes), we should:
  1. Check agent states directly after the first step
  2. Check collected data after the second step

#### Solution Patterns:
1. Direct Agent State Inspection:
```python
# Run step to apply interventions
model.step()
# Check agent states directly
person_agents = [a for a in model.schedule.agents if isinstance(a, PersonAgent)]
current_state = [a.some_property for a in person_agents]
```

2. Two-Step Verification:
```python
# First step: apply interventions
model.step()
# Check immediate effects on agents
intermediate_state = check_agents(model)
# Second step: see effects in collected data
model.step()
final_data = model.datacollector.get_model_vars_dataframe()
```

### 2. Testing Relapse Behavior

Testing relapse mechanics presents unique challenges due to:
1. Concurrent quit attempts and relapses
2. Time-dependent probability decay
3. Population-level effects

#### Challenges:
1. Population Changes:
   - Changes in smoker population can be positive (relapses) or negative (quits)
   - Need to track both types of changes separately
   - Changes can happen simultaneously

2. Probability Decay:
   ```python
   # From model code
   recidivism_prob = base_smoke_relapse_prob * (0.95 ** months_smoke_free)
   ```
   - Relapse probability decreases over time
   - Each ex-smoker has different smoke-free duration
   - Need to account for decay in expected values

3. Never-Smoked Status:
   ```python
   if not self.smoker and not self.never_smoked:  # Only ex-smokers can relapse
   ```
   - Only ex-smokers can relapse
   - Need to distinguish between never-smokers and ex-smokers
   - Initial conditions affect relapse pool

#### Solution Patterns:

1. Testing Population Changes:
```python
# Calculate separate bounds for quits and relapses
max_relapse_change = non_smokers * base_relapse_prob
max_quit_change = smokers * quit_attempt_prob

# Check changes against appropriate bounds
for change in population_changes:
    if change > 0:  # Relapse
        assert change <= max_relapse_change
    else:  # Quit
        assert abs(change) <= max_quit_change
```

2. Testing Decay Effects:
```python
# Track relapses over time
relapses_by_step = []
for step in range(steps):
    model.step()
    current_relapses = calculate_relapses(model)
    relapses_by_step.append(current_relapses)

# Verify decay
assert all(a > b for a, b in zip(relapses_by_step[:-1], relapses_by_step[1:]))
```

3. Setting Up Initial Conditions:
```python
# Ensure population starts as smokers
params = {
    'initial_smoking_prob': 1.0,  # All start as smokers
    'quit_attempt_prob': 1.0,     # Everyone tries to quit
}

# First step: everyone starts as smoker
model.step()
# Second step: everyone tries to quit
model.step()
# Now we have a population of ex-smokers for testing relapses
```

### 3. Randomness and Probability Testing

Testing probabilistic behaviors requires careful consideration:

1. Seed Management:
   - Always set a seed for reproducibility
   - But be aware that identical seeds might still produce different results due to different execution paths

2. Statistical Testing:
   - Single-run assertions might fail due to randomness
   - Better to run multiple times and check aggregate behavior
   - Use appropriate margins of error

#### Example Pattern:
```python
def test_probabilistic_behavior():
    results = []
    for _ in range(5):  # Multiple runs
        model = Model(seed=42)
        model.step()
        results.append(get_result(model))
    
    # Assert on aggregate behavior
    assert average(results) > expected_minimum
```

### 4. Calculating Expected Values

When testing probabilistic models, it's crucial to:

1. Calculate theoretical expectations:
```python
# Example: Quit attempts over 3 steps
population = 1000
quit_prob = 0.2
steps = 3
expected_mean = population * quit_prob * steps  # 600 attempts
```

2. Allow for reasonable variation:
```python
# Example: Setting bounds around expected mean
expected_min = expected_mean * 0.75  # 450 attempts
expected_max = expected_mean * 1.25  # 750 attempts
```

3. Consider compounding effects:
```python
# Example: Relapse calculation over steps
remaining = initial_population
total_relapses = 0
for step in range(3):
    relapses = remaining * relapse_prob
    total_relapses += relapses
    remaining -= relapses
```

## Best Practices

1. Test Setup:
   - Use small populations for faster tests
   - Control randomness through seeds
   - Isolate specific behaviors being tested

2. Assertions:
   - Check intermediate states, not just final results
   - Use appropriate tolerances for floating-point comparisons
   - Include descriptive error messages
   - Verify trends over time, not just final values

3. Documentation:
   - Document timing assumptions
   - Explain why tests are structured certain ways
   - Include examples of failure cases
   - Show calculations for expected values

## Common Pitfalls

1. Timing Issues:
   - Assuming effects are visible immediately in collected data
   - Not accounting for the step delay
   - Checking data at wrong points in the simulation

2. Probability Testing:
   - Over-specific assertions about random outcomes
   - Not accounting for valid random variation
   - Using too few samples for statistical validity

3. State Management:
   - Not resetting state between test runs
   - Allowing effects to accumulate unexpectedly
   - Not controlling all relevant parameters

4. Accumulation Effects:
   - Not running enough steps to see full behavior
   - Not tracking intermediate states
   - Not accounting for compounding probabilities
