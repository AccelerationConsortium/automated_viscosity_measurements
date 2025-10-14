# Automated Viscosity Measurements

This project automates viscosity measurements using a viscometer, CNC machine for sample handling, and ESP32 for pump control. It supports single RPM, dynamic, and bisection analysis modes.

## Project Structure

```
src/
├── hardware/
│   ├── viscometer/  # Viscometer protocol and client
│   ├── cnc/         # CNC controller
│   └── pump/        # ESP32 pump control
├── motion/          # Sample handling and wash sequences
├── analysis/        # Analysis methods (single, dynamic, bisection)
└── runner/          # Main entry point and bridge to 32-bit worker

config/
├── default.yaml     # Main configuration (ports, modes, etc.)
└── locations.yaml   # CNC sample and wash station positions

results/             # Output CSV files per sample
```

## Installation

### Prerequisites

- Python 3.8+ (64-bit for main application)
- Python 3.8+ (32-bit for viscometer worker subprocess)
- Serial ports for viscometer (COM6), CNC (COM5), ESP32 pump (COM4)

### Setup Virtual Environments

1. Create 64-bit venv:
   ```bash
   python -m venv venv64
   venv64\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create 32-bit venv (if using separate Python installation):
   ```bash
   # Assuming python32.exe is available
   python32 -m venv venv32
   venv32\Scripts\activate
   pip install -r requirements.txt
   ```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config/default.yaml` to set:

- Serial ports and baud rates
- Analysis mode (`single`, `dynamic`, `bisection`)
- Sample rack and range
- Wash settings

Edit `config/locations.yaml` for CNC positions.

## Usage

1. Ensure hardware is connected and ports are correct.

2. Run the main application:
   ```bash
   python src/runner/main.py
   ```

   This will:
   - Load configuration
   - Initialize hardware
   - Move to samples, perform analysis, save CSVs to `results/`

3. Results are saved as CSV files in `results/sample_XXX/` directories.

## Analysis Modes

- **Single**: Spin at fixed RPM, log torque/temperature over time
- **Dynamic**: Test multiple RPMs, record steady-state values
- **Bisection**: Find RPM for target torque using binary search

## Troubleshooting

- Ensure serial ports are not in use by other applications
- Check virtual mode in config for testing without hardware
- 32-bit worker requires DVT_COM.dll in `src/hardware/viscometer/`

