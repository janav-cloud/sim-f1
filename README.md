# 🏎️ Advanced F1 Race Simulation & Championship Engine

A high-fidelity, physically calibrated Formula 1 race simulation engine and championship tracker. Built with Monte Carlo probabilistic modeling, modular race physics, and authentic Grand Prix dynamics—including tire thermal degradation, dirty air aerodynamic wash, dynamic track evolution, wet-weather crossovers, pit stop undercuts, and automated World Championship tracking.

---

## 🚀 Key Features

* **Balanced Multi-Factor Physics**:
  * **Car vs. Driver Balance**: Moderated car pace weighting ensures constructor tiers remain authentic while granting elite drivers the agency to challenge for victories and podiums.
  * **Circuit Trait Specialization**: High-speed power tracks (Monza, Spa, Baku) reward low aerodynamic drag and horsepower; technical tracks (Monaco, Singapore, Hungaroring) reward downforce, stability, and curb agility.
  * **Weather & Track Temperatures**: In rain, mechanical car differences compress by 55%, elevating driver wet-weather ability. Hot tracks ($\ge 38^\circ\text{C}$) cause soft compound thermal blistering and reward hard tires; cold tracks ($\le 18^\circ\text{C}$) introduce hard compound warm-up lag.
  * **Track Evolution & Drying Lines**: Racing lines rubber in over time ($-0.32$s/lap permanent, $-0.55$s/lap street). Clearing standing water creates drying lines that trigger dramatic slick crossover windows.
  * **Strategic Pits & Undercuts**: Out-lap fresh tire surges ($-0.95$s lap 1, $-0.50$s lap 2) enable tactical undercuts. Pit crew speeds and errors mirror real-world pit wall execution.
  * **Neutralizations (VSC & Full Safety Car)**: Incidents branch into Virtual Safety Cars (delta-paced, discounted pit stops) or Full Safety Cars (field bunching).
* **Automated Championship Tracking ([`WDC.csv`](WDC.csv) & [`WCC.csv`](WCC.csv))**:
  * Automatically records points after every completed Grand Prix.
  * Appends a new column per circuit, recalculates total points, and sorts the championship table descending.
  * Saved exclusively at the project root directory.
* **100% Data-Driven (Zero Hardcoding)**:
  * No driver or team has hardcoded favoritism or scripts. All performance is calculated dynamically from your CSV data files.
* **Arbitrary Grid Size Support ($>20$ Drivers)**:
  * Seamlessly simulates, classifies, and awards points for any grid size ($20, 21, 22, 24+$ drivers) without truncation.
* **Interactive Next.js Telemetry Dashboard**:
  * Replay race telemetry lap-by-lap with live leaderboards, tire compound stints, interval gaps, and event feeds.

---

## 📁 Project Structure

```bash
sim-f1-5.0/
│
├── race_sim_adv.py         # Advanced Monte Carlo race simulation & physics engine
├── circuit_data.py         # Circuit metadata (length, cornering, wear, overtaking difficulty)
├── weather_conditions.py   # Environmental parameters (grip, temperatures, wear modifiers)
├── weather_transitions.py  # Markov transition probabilities for dynamic weather shifts
├── race_strategy.py        # Strategic archetypes (1-Stop, 2-Stop, 3-Stop, Undercut, SC gamble)
├── ers_management.py       # ERS deployment & braking-demand harvesting logic
├── track_evolution.py      # Surface rubbering-in, water clearance & drying line mechanics
├── team_orders.py          # Intra-team yielding, alternate strategy & morale logic
├── race_logger.py          # Structured event logging (overtakes, pits, errors, safety cars)
│
├── DRIVERS DATA.csv        # Driver attributes (skill, consistency, tire save, wet mastery)
├── TEAM DATA.csv           # Constructor attributes (pit stop speed, strategy acumen)
├── CALCULATIONS.csv        # 15 vehicle engineering metrics & final car performance scores
│
├── WDC.csv                 # World Drivers' Championship standings (auto-updated)
├── WCC.csv                 # World Constructors' Championship standings (auto-updated)
│
├── outputs/                # Structured simulation outputs folder
│   ├── results/
│   │   ├── aggregated/     # Aggregated Monte Carlo summary & classification tables
│   │   └── races/          # Detailed CSV classifications per circuit and weather
│   ├── logs/               # Lap-by-lap race commentary and event text logs
│   └── replays/            # JSON telemetry replay files for the web dashboard
│
├── dashboard/              # Next.js interactive race replay visualization dashboard
└── README.md               # Project documentation
```

---

## 📦 Requirements & Installation

### Simulation Engine
- Python 3.8+
- pandas

Install required Python packages:
```bash
pip install pandas
```

### Telemetry Dashboard (Optional)
- Node.js 18+
- npm

Install dashboard dependencies:
```bash
cd dashboard
npm install
cd ..
```

---

## ▶️ Running the Simulation

Ensure `DRIVERS DATA.csv`, `TEAM DATA.csv`, and `CALCULATIONS.csv` are in the project root directory.

Run the simulation engine:
```powershell
python race_sim_adv.py
```

### Interactive Prompts:
1. **Choose a circuit number (1–24)**: Select any Grand Prix on the calendar (e.g. Monza, Monaco, Spa, Silverstone).
2. **Total number of Monte Carlo simulations**:
   * Enter `1` for a single live race.
   * Enter `100`–`500` for statistical probability distributions.
3. **Use enhanced simulation features? (y/n)**:
   * Select `y` to enable ERS, dynamic track rubbering, tire thermal blistering, pit undercuts, dirty air, and VSC/SC.
4. **Save individual race results & logs? (y/n)**:
   * Select `y` to export race classifications and lap commentary to `outputs/`.
5. **Show detailed race logs? (y/n)**:
   * Select `y` to stream live lap-by-lap racing events directly into the console.

---

## 🏆 World Championship Tracking

Every time a Grand Prix finishes, the engine automatically updates the championship tables in the project root:

* **[`WDC.csv`](WDC.csv)**: Driver Name, Team Name, `[Circuit 1]`, `[Circuit 2]`..., `Total Points`
* **[`WCC.csv`](WCC.csv)**: Team Name, `[Circuit 1]`, `[Circuit 2]`..., `Total Points`

You can run consecutive races across the season (Bahrain $\to$ Jeddah $\to$ Albert Park $\to$ Suzuka...), watching points accumulate dynamically as title fights unfold.

---

## 💻 Running the Web Telemetry Dashboard

To visualize race replays with interactive lap charts and event feeds:

1. Launch the local dev server:
   ```bash
   cd dashboard
   npm run dev
   ```
2. Open [http://localhost:3000](http://localhost:3000) in your browser.
3. Select and load any generated replay file from `outputs/replays/<Circuit>/<Weather>/Sim_X_Replay.json`.
4. Inspect:
   * Lap-by-lap interval gaps and leaderboard positions
   * Tire compound stints and tire wear
   * Event feed (Overtakes, Pit stops, Safety Cars, VSC periods, Weather changes)

---

### 🧠 Credits
Developed for Formula 1 simulation, committee modeling, and race strategy analysis.

### Made with Love by Janav Dua! 💌
