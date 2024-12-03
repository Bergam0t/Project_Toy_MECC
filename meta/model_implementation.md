# MECC Model Implementation Details

## Model Purpose
This agent-based simulation models the impact of Making Every Contact Count (MECC) training on health behavior changes in a population. The model specifically focuses on how MECC-trained government service workers can influence lifestyle changes through Very Brief Interventions (VBIs).

## Key Model Components

### Agents

1. **People**
   - Have lifestyle factors:
     - Smoking
     - Drinking
     - Physical inactivity
   - Can make quit attempts with varying probabilities of success
   - Interact randomly with government services

2. **Government Services**
   - Can receive MECC training
   - Interact with people randomly
   - Can deliver Very Brief Interventions when trained

## Key Parameters

### Smoking Intervention Parameters
Based on Cochrane Review evidence:
- Background quit rate: 2-3% at 12 months without intervention
- Brief advice intervention increases quit rate by 1-3 percentage points
- Offering support increases cessation attempts by 40-60%
- Current UK smoking prevalence: 11.9% (ONS 2023)

### MECC Training Implementation
- Services gain MECC training over time at a specified training rate
- Trained services have increased probability of delivering Very Brief Interventions
- VBIs increase probability of quit attempts for lifestyle factors

## Model Outputs
1. MECC Training Numbers
   - Tracks progression of MECC-trained service workers

2. Behavior Change Metrics
   - Number of quit attempts
   - Number of successful quits
   - Temporal tracking of changes

## Implementation Notes
- Built using Mesa framework for agent-based modeling
- Streamlit frontend for visualization and interaction
- Multiple agent types to represent different service providers and population segments
- Randomized interactions between people and services
- Probability-based intervention and success rates based on research evidence

## Research-Based Parameters
The model incorporates evidence from multiple studies:
- Cochrane Review findings on physician advice effectiveness
- ONS population statistics for baseline behaviors
- Research on brief intervention effectiveness in primary care
- Studies on opportunistic smoking cessation interventions

## Future Development Areas
1. Integration of additional lifestyle factors
2. Refinement of interaction patterns
3. Enhanced MECC training progression mechanics
4. Additional outcome metrics
