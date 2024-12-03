# Project Analysis: MECC Simulation

## Project Overview
This is a simulation project focused on Making Every Contact Count (MECC), implemented as a web application using Streamlit with underlying agent-based modeling using Mesa framework.

## Directory Structure Analysis

### Core Application (`streamlit_app/`)
- Main application components for the web interface and simulation logic
- Key files:
  - `app.py`: Main Streamlit application entry point
  - `homepage.py`: Homepage implementation
  - `logic_diagram.py`: Logic flow visualization
  - `parameters.py`: Simulation parameters configuration
  - `generic_mecc_model.py`: Core MECC model implementation
  - `mesa_abs_two_types_mecc.py`: Mesa agent-based simulation with two agent types
  - `model_two_types_mecc.py`: Two-type model implementation
  - `streamlit_model_functions.py`: Helper functions for Streamlit integration

### Resources
- Contains visual assets (`resources/`)
  - MECC.jpg and MECC2.png for application branding/visualization

### Data Management
- `downloads/` and `outputs/` directories for simulation results and exports
- Organized with .gitkeep files to maintain directory structure

### Environment Configuration
- `environment/environment.yml`: Conda environment specification
- `requirements.txt`: Python package dependencies

### Archive
Contains previous iterations and alternative implementations:
- `mesa_abs_two_types.py`
- `mesa_abs.py`
- `model_two_types.py`
- `model.py`
- `server.py`

## Technical Stack
1. **Frontend**: Streamlit framework for web interface
2. **Simulation Engine**: Mesa framework for agent-based modeling
3. **Documentation**: Quarto (`.qmd` file) for report generation
4. **Styling**: Custom CSS (NHS report theme)

## Project Purpose
The application appears to be designed for simulating and analyzing Making Every Contact Count (MECC) scenarios, likely in a healthcare context given the NHS theming. It uses agent-based modeling to simulate interactions and outcomes in healthcare settings.

## Development Patterns
- Modular architecture separating UI, simulation logic, and models
- Multiple model implementations suggesting iterative development
- Clear separation of concerns between simulation core and web interface
- Organized resource management for outputs and downloads
