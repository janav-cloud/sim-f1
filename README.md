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
├── race_sim_adv.py         # Advanced Monte Carlo race simulation engine
├── TEAM DATA.csv           # Team attributes (pit stop speed, strategy acumen)
├── DRIVERS DATA.csv        # Driver skill profiles
├── CALCULATIONS.csv        # Car performance scores per team
├── outputs/                # Structured simulation outputs folder
│   ├── results/            # Race result CSVs
│   │   ├── aggregated/     # Aggregated summary & P1-P20 CSV results
│   │   └── races/          # Detailed race results per circuit and weather
│   ├── logs/               # Detailed lap-by-lap race logs per circuit and weather
│   └── replays/            # Lap-by-lap JSON replay telemetry files
└── README.md               # Project README file
```

## 📦 Requirements

- Python 3.7+
- pandas
- Next.js

Install dependencies:

```bash
pip install pandas
```

## ▶️ Running the Simulation
Ensure TEAM DATA.csv, DRIVERS DATA.csv, and CALCULATIONS.csv are in the root directory.

## 📊 Outputs
All outputs are organized under the `outputs/` directory:
- **Aggregated Summaries**: `outputs/results/aggregated/` (Overall multi-simulation statistics and P1-P20 position tables)
- **Individual Race Results**: `outputs/results/races/{Circuit}/{Weather}/` (Detailed CSV per race iteration)
- **Detailed Race Logs**: `outputs/logs/races/{Circuit}/{Weather}/` (Lap-by-lap text event logs)
- **Race Replays**: `outputs/replays/{Circuit}/{Weather}/` (BETA Feature: JSON telemetry for the web dashboard visualization)

### 📌 Notes
- Only drivers with complete data across all three CSVs will be simulated.
- Strategies and tire compounds are randomly assigned but weighted based on circuit and strategy type.
- Weather may change dynamically during races in enhanced mode.
- For the race replay, use the "dashboard" directory.
#### Steps are as follows:
1. Prerequisites
```bash
cd dashboard
npm install
npm run dev
```
2. As the website loads (localhost:3000), upload the JSON file in the replays directory.

### 🧠 Credits
Developed for F1 simulation and strategy modeling. Data and structure are customizable for other motorsport formats.

### Made with Love by Janav Dua! 💌
