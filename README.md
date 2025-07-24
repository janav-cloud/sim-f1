# 🏎️ F1 Race Simulation Engine

A comprehensive Formula 1 race simulation engine that uses real-world-like driver, team, car, and circuit data to simulate race outcomes under various weather conditions using Monte Carlo methods. Includes enhanced features like weather variability, pit strategies, tire degradation, and overtaking logic.

## 🚀 Features

- Modular architecture with separate modules for circuits, weather, and strategies.
- Monte Carlo simulation support to evaluate performance over thousands of race iterations.
- Enhanced simulation logic for:
  - Tire wear and compound impact
  - Dynamic weather changes
  - Strategy adaptability
  - Pit stop decisions and safety car events
- Aggregated statistics like average position, DNF rate, and probability distributions for final positions.

## 📁 Project Structure

```bash
f1_race_simulator/
│
├── ers_management.py       # Defines ERS modes and management logic
├── track_evolution.py      # Manages track state, including rubbering-in and grip evolution
├── team_orders.py          # Contains the logic for team order decisions
├── race_logger.py          # Provides the RaceLogger class for capturing race events
├── circuit_data.py         # Circuit metadata (length, overtaking difficulty, etc.)
├── weather_conditions.py   # Weather effects on grip, engine performance, etc.
├── race_strategy.py        # Strategy types and their acumen
├── weather_transitions.py  # Defines probabilities of weather changing
├── TEAM DATA.csv           # Team attributes (pit stop speed, strategy acumen)
├── DRIVERS DATA.csv        # Driver skill profiles
├── CALCULATIONS.csv        # Car performance scores per team
├── main.py                 # The main simulation script that runs the race
└── README.md               # Project README file
```

## 📦 Requirements

- Python 3.7+
- pandas

Install dependencies:

```bash
pip install pandas
```

## ▶️ Running the Simulation
Ensure TEAM DATA.csv, DRIVERS DATA.csv, and CALCULATIONS.csv are in the root directory.

## 📊 Outputs
- Individual Race Results CSV: Includes detailed simulation results per race.
- Aggregated Summary CSV: Shows average positions, DNF rates, and probabilities of finishing in each position.
- Complete logs containing information about the race simulation circuit wise.

### 📌 Notes
- Only drivers with complete data across all three CSVs will be simulated.
- Strategies and tire compounds are randomly assigned but weighted based on circuit and strategy type.
- Weather may change dynamically during races in enhanced mode.

### 🧠 Credits
Developed for F1 simulation and strategy modeling. Data and structure are customizable for other motorsport formats.

### Made with Love by Janav Dua! 💌
