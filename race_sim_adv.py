import pandas as pd
import random
import math
from collections import Counter

# --- 1. Modular Data Imports ---
from circuit_data import CIRCUIT_DATA
from weather_conditions import WEATHER_CONDITIONS
from race_strategy import RACE_STRATEGY_TYPES

# --- 2. Data Loading Function ---
def load_csv_data(filepath):
    """
    Loads data from a specified CSV file into a list of dictionaries.
    Handles potential FileNotFoundError and other exceptions.
    """
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        print(f"Successfully loaded data from {filepath}")
        return df.to_dict(orient='records')
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found. Please ensure it's in the same directory as the script.")
        return None
    except Exception as e:
        print(f"An error occurred while loading {filepath}: {e}")
        return None

# --- 3. Race Entry Class ---
class RaceEntry:
    """
    Represents a single driver and their car in the race.
    Holds all dynamic and static attributes for a participant.
    """
    def __init__(self, driver_data, team_data, car_scores, initial_position, assigned_strategy_type):
        self.driver_name = driver_data['driver_name']
        self.team_name = driver_data['team_name']
        self.driver_skill = driver_data['skill']
        self.driver_consistency = driver_data['consistency']
        self.driver_tire_management = driver_data['tire_management']
        self.driver_wet_weather_ability = driver_data['wet_weather_ability']
        self.driver_overtaking_skill = driver_data['overtaking_skill']
        self.driver_defending_skill = driver_data['defending_skill']
        self.team_pit_stop_speed = team_data['team_pit_stop_speed']
        self.team_strategy_acumen_base = team_data['team_strategy_acumen']
        self.strategy_aggressive_acumen = team_data['strategy_aggressive_acumen']
        self.strategy_balanced_acumen = team_data['strategy_balanced_acumen']
        self.strategy_conservative_acumen = team_data['strategy_conservative_acumen']
        self.car_overall_score = car_scores['Overall_Car_Score']
        self.car_engine_hp_final = car_scores['Engine_HP_Final']
        self.car_engine_rel_final = car_scores['Engine_REL_Final']
        self.car_chassis_aero_df_final = car_scores['ChassisAero_DF_Final']
        self.car_chassis_aero_dr_final = car_scores['ChassisAero_DR_Final']
        self.car_brakes_sp_final = car_scores['Brakes_SP_Final']
        self.car_brakes_dur_final = car_scores['Brakes_DUR_Final']
        self.car_tires_wr_final = car_scores['Tires_WR_Final']
        self.initial_position = initial_position
        self.current_position = initial_position
        self.total_race_time_s = 0.0
        self.laps_completed = 0
        self.is_dnf = False
        self.dnf_reason = ""
        self.pit_stops_made = 0
        self.tire_wear = 0.0
        self.assigned_strategy_type = assigned_strategy_type
        acumen_map = {
            "strategy_aggressive_acumen": self.strategy_aggressive_acumen,
            "strategy_balanced_acumen": self.strategy_balanced_acumen,
            "strategy_conservative_acumen": self.strategy_conservative_acumen
        }
        self.effective_strategy_acumen = self.team_strategy_acumen_base
        for s_type in RACE_STRATEGY_TYPES:
            if s_type['name'] == self.assigned_strategy_type['name']:
                self.effective_strategy_acumen = acumen_map.get(s_type['applies_acumen'], self.team_strategy_acumen_base)
                break

    def __repr__(self):
        status = f"DNF ({self.dnf_reason})" if self.is_dnf else f"Time: {self.total_race_time_s:.2f}s"
        return f"P{self.current_position} {self.driver_name} ({self.team_name}) - {status}"

# --- 4. Simulation Core Logic ---
def calculate_base_lap_time(circuit):
    """Calculates a reference lap time based on circuit length."""
    return circuit['length_km'] * 38

def calculate_lap_time(entry, circuit, weather, enhanced_simulation=False, weather_changed=False):
    """
    Calculates the time for a single lap for a given entry.
    Enhanced simulation adds dynamic weather effects, tire compound impact, and adaptability.
    """
    base_time = calculate_base_lap_time(circuit)
    speed_weight = circuit['straight_speed_importance']
    cornering_weight = circuit['cornering_importance']
    braking_weight = circuit['braking_demands']
    total_weight = speed_weight + cornering_weight + braking_weight
    effective_hp = entry.car_engine_hp_final * weather['hp_multiplier']
    effective_downforce = entry.car_chassis_aero_df_final * weather['downforce_multiplier']
    straight_line_performance = (effective_hp * 0.7) + (entry.car_chassis_aero_dr_final * 0.3)
    perf_score = (
        (straight_line_performance * speed_weight) +
        (effective_downforce * cornering_weight) +
        (entry.car_brakes_sp_final * braking_weight)
    ) / total_weight
    adjusted_time = base_time / (perf_score + 0.5)
    driver_skill_modifier = 1.0 - (entry.driver_skill * 0.05)
    adjusted_time *= driver_skill_modifier
    grip_penalty = 1.0 - weather['grip_multiplier']
    mitigation = grip_penalty * (entry.driver_wet_weather_ability * 0.5)
    effective_grip_multiplier = weather['grip_multiplier'] + mitigation
    if enhanced_simulation and weather_changed:
        adaptability = entry.assigned_strategy_type.get('weather_adaptability', 0.0)
        adaptability_modifier = weather.get('adaptability_modifier', 0.2)
        effective_grip_multiplier += adaptability * adaptability_modifier * 0.1
    adjusted_time /= effective_grip_multiplier
    base_wear_per_lap = circuit['tire_wear_severity'] * (1.1 - entry.car_tires_wr_final)
    driver_wear_effect = base_wear_per_lap * (1.0 - (entry.driver_tire_management * 0.5))
    final_wear_this_lap = (driver_wear_effect + weather['tire_wear_modifier']) / 100.0
    entry.tire_wear = min(1.0, entry.tire_wear + final_wear_this_lap)
    tire_wear_penalty = (entry.tire_wear ** 2) * 5.0
    adjusted_time += tire_wear_penalty
    deviation_range = (1.0 - entry.driver_consistency) * 0.5
    random_deviation = random.uniform(-deviation_range, deviation_range)
    adjusted_time += random_deviation
    strategy_bonus = (entry.effective_strategy_acumen - 0.7) * 0.1
    adjusted_time -= strategy_bonus
    if enhanced_simulation:
        tire_compound = entry.assigned_strategy_type.get('tire_compound', 'medium')
        if tire_compound in ['soft', 'medium', 'hard']:
            if tire_compound == 'soft':
                adjusted_time *= 0.98
                entry.tire_wear += final_wear_this_lap * 0.2
            elif tire_compound == 'hard':
                adjusted_time *= 1.02
                entry.tire_wear -= final_wear_this_lap * 0.1
        elif tire_compound == 'intermediate':
            adjusted_time *= 0.95 if weather.get('tire_type_recommendation', 'dry') == 'intermediate' else 1.05
            entry.tire_wear += final_wear_this_lap * 0.1
        elif tire_compound == 'wet':
            adjusted_time *= 0.90 if weather.get('tire_type_recommendation', 'dry') == 'wet' else 1.10
            entry.tire_wear += final_wear_this_lap * 0.05
        weather_variability = weather.get('variability', 0.0)
        if random.random() < weather_variability:
            adjusted_time *= random.uniform(0.99, 1.01)
    return max(base_time * 0.8, adjusted_time)

def decide_pit_stop(entry, circuit, lap, is_safety_car, enhanced_simulation=False):
    """Determines if a car should make a pit stop on the current lap."""
    strategy_name = entry.assigned_strategy_type['name']
    total_laps = circuit['laps']
    if is_safety_car and entry.tire_wear > 0.4 and lap > 5 and lap < total_laps - 5:
        return True
    if entry.tire_wear > 0.95:
        return True
    num_stops = 1
    if "2-Stop" in strategy_name: num_stops = 2
    elif "3-Stop" in strategy_name: num_stops = 3
    if lap > total_laps - 5: return False
    pit_window_size = 5
    for i in range(1, num_stops + 1):
        target_lap = int((total_laps / (num_stops + 1)) * i)
        if entry.pit_stops_made == i - 1 and lap in range(target_lap - pit_window_size, target_lap + pit_window_size):
            if entry.tire_wear > 0.5:
                return True
    if enhanced_simulation:
        if entry.tire_wear > 0.7 and entry.assigned_strategy_type.get('tire_compound') == 'soft':
            return True
    return False

def simulate_pit_stop(entry, enhanced_simulation=False):
    """Simulates a pit stop, adding time and resetting tire wear."""
    base_time = 23.0
    time_reduction = entry.team_pit_stop_speed * 2.0
    pit_stop_time = base_time - time_reduction
    if enhanced_simulation:
        pit_stop_variability = random.uniform(-0.5, 0.5)
        pit_stop_time += pit_stop_variability
    entry.total_race_time_s += pit_stop_time
    entry.pit_stops_made += 1
    entry.tire_wear = 0.0
    return pit_stop_time

def simulate_event(entry, weather, enhanced_simulation=False):
    """Simulates random events like mechanical failures and driver errors."""
    if entry.is_dnf: return
    reliability_penalty = (1 - entry.car_engine_rel_final) + (1 - entry.car_brakes_dur_final)
    failure_chance = 0.0005 + (reliability_penalty * 0.001)
    if enhanced_simulation:
        if entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            failure_chance *= 1.2
    if random.random() < failure_chance:
        entry.is_dnf = True
        entry.dnf_reason = "Mechanical Failure"
        return
    error_chance = 0.001 * (1.5 - entry.driver_consistency) + weather['driver_error_chance_modifier']
    if enhanced_simulation:
        error_chance += weather.get('variability', 0.0) * 0.0005
    if random.random() < error_chance:
        if random.random() < 0.1:
            entry.is_dnf = True
            entry.dnf_reason = "Driver Error"
        else:
            entry.total_race_time_s += random.uniform(2.0, 5.0)

def check_for_overtake(front_entry, rear_entry, circuit, enhanced_simulation=False):
    """Calculates the probability of an overtake attempt being successful."""
    pace_advantage = (rear_entry.car_overall_score - front_entry.car_overall_score) * 0.2
    skill_advantage = (rear_entry.driver_overtaking_skill - front_entry.driver_defending_skill) * 0.3
    track_difficulty = circuit['overtaking_difficulty'] * 0.4
    overtake_prob = 0.3 + pace_advantage + skill_advantage - track_difficulty
    if enhanced_simulation:
        position_factor = (front_entry.current_position / len(CIRCUIT_DATA)) * 0.1
        overtake_prob -= position_factor
        tire_wear_diff = front_entry.tire_wear - rear_entry.tire_wear
        overtake_prob += tire_wear_diff * 0.1
    return random.random() < max(0.0, min(1.0, overtake_prob))

def simulate_race(circuit, weather, entries, enhanced_simulation=False):
    """The main function to simulate an entire race from start to finish."""
    for entry in entries:
        entry.current_position = entry.initial_position
        entry.total_race_time_s = 0.0
        entry.laps_completed = 0
        entry.is_dnf = False
        entry.dnf_reason = ""
        entry.pit_stops_made = 0
        entry.tire_wear = 0.0
    safety_car_laps = 0
    current_weather = weather.copy()
    for lap in range(1, circuit['laps'] + 1):
        is_safety_car_deployed_this_lap = False
        if safety_car_laps == 0 and lap > 2 and lap < circuit['laps'] - 5:
            if any(e.laps_completed == lap - 1 and e.is_dnf for e in entries):
                if random.random() < 0.5:
                    is_safety_car_deployed_this_lap = True
                    safety_car_laps = random.randint(2, 3)
        is_safety_car_active = safety_car_laps > 0
        weather_changed = False
        if enhanced_simulation:
            weather_susceptibility = circuit.get('weather_susceptibility', 0.1)
            if random.random() < current_weather.get('variability', 0.0) * weather_susceptibility:
                new_weather = random.choice(list(WEATHER_CONDITIONS.values()))
                current_weather.update({
                    'hp_multiplier': new_weather['hp_multiplier'],
                    'downforce_multiplier': new_weather['downforce_multiplier'],
                    'grip_multiplier': new_weather['grip_multiplier'],
                    'tire_wear_modifier': new_weather['tire_wear_modifier'],
                    'driver_error_chance_modifier': new_weather['driver_error_chance_modifier'],
                    'variability': new_weather.get('variability', 0.0),
                    'tire_type_recommendation': new_weather.get('tire_type_recommendation', 'dry'),
                    'adaptability_modifier': new_weather.get('adaptability_modifier', 0.2)
                })
                weather_changed = True
        for entry in entries:
            if entry.is_dnf: continue
            simulate_event(entry, current_weather, enhanced_simulation)
            if entry.is_dnf: continue
            if decide_pit_stop(entry, circuit, lap, is_safety_car_active, enhanced_simulation):
                simulate_pit_stop(entry, enhanced_simulation)
            lap_time = calculate_lap_time(entry, circuit, current_weather, enhanced_simulation, weather_changed)
            if is_safety_car_active:
                lap_time = calculate_base_lap_time(circuit) * 1.4 + random.uniform(-0.5, 0.5)
            entry.total_race_time_s += lap_time
            entry.laps_completed += 1
        if is_safety_car_active:
            safety_car_laps -= 1
            if safety_car_laps == 0:
                active_cars = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)
                if active_cars:
                    leader_time = active_cars[0].total_race_time_s
                    for i, car in enumerate(active_cars):
                        car.total_race_time_s = leader_time + (i * 1.5)
        live_race_order = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)
        for i in range(len(live_race_order) - 1, 0, -1):
            rear_entry, front_entry = live_race_order[i], live_race_order[i-1]
            if rear_entry.total_race_time_s - front_entry.total_race_time_s < 1.0:
                if check_for_overtake(front_entry, rear_entry, circuit, enhanced_simulation):
                    front_time, rear_time = front_entry.total_race_time_s, rear_entry.total_race_time_s
                    rear_entry.total_race_time_s, front_entry.total_race_time_s = front_time - 0.1, rear_time + 0.1
    final_results = sorted(entries, key=lambda x: (x.is_dnf, -x.laps_completed, x.total_race_time_s))
    for i, entry in enumerate(final_results):
        entry.current_position = i + 1
    return final_results

def assign_points(position):
    """Assigns F1 points based on finishing position."""
    points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    return points_system.get(position, 0)

def generate_final_race_result(final_results):
    """Generates a P1-P20 race result list with Position, Driver, Team Name, Points, and Status."""
    result_data = []
    for entry in final_results:
        points = 0 if entry.is_dnf else assign_points(entry.current_position)
        status = entry.dnf_reason if entry.is_dnf else "Finished"
        result_data.append({
            'Position': entry.current_position,
            'Driver': entry.driver_name,
            'Team': entry.team_name,
            'Points': points,
            'Status': status
        })
    result_df = pd.DataFrame(result_data)
    return result_df

def run_monte_carlo_simulation(num_simulations, circuit, weather, race_entries_template, enhanced_simulation=False):
    """Runs the race simulation multiple times for a specific weather condition."""
    print(f"\n--- Running {num_simulations} simulations for {weather['name']} conditions ---")
    all_simulation_results = []
    for sim_num in range(num_simulations):
        initial_grid_positions = list(range(1, len(race_entries_template) + 1))
        random.shuffle(initial_grid_positions)
        for i, entry in enumerate(race_entries_template):
            entry.initial_position = initial_grid_positions[i]
            entry.assigned_strategy_type = random.choice(RACE_STRATEGY_TYPES)
            if enhanced_simulation:
                compounds = ['soft', 'medium', 'hard']
                tire_type = weather.get('tire_type_recommendation', 'dry')
                if tire_type in ['intermediate', 'wet']:
                    entry.assigned_strategy_type['tire_compound'] = tire_type
                else:
                    circuit_weights = circuit.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
                    strategy_weights = entry.assigned_strategy_type.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
                    combined_weights = [(circuit_weights[c] + strategy_weights[c]) / 2 for c in compounds]
                    entry.assigned_strategy_type['tire_compound'] = random.choices(compounds, weights=combined_weights, k=1)[0]
        simulation_results = simulate_race(circuit, weather, race_entries_template, enhanced_simulation)
        race_result_df = generate_final_race_result(simulation_results)
        print(f"\n--- Race Result for Simulation {sim_num + 1} ---")
        print(race_result_df.to_string(index=False))
        all_simulation_results.append([e.__dict__.copy() for e in simulation_results])
    return all_simulation_results

def aggregate_results(all_simulation_results, all_drivers):
    """Aggregates results from all simulations into a final summary DataFrame."""
    driver_stats = {d['driver_name']: {
        'total_points': 0,
        'dnf_count': 0,
        'finishing_positions': {pos: 0 for pos in range(1, len(all_drivers) + 2)},
        'team_name': d.get('team_name', 'N/A'),
        'position_counts': []
    } for d in all_drivers}
    num_sims = len(all_simulation_results)
    if num_sims == 0: return pd.DataFrame()
    for sim_results in all_simulation_results:
        for entry_data in sim_results:
            stats = driver_stats[entry_data['driver_name']]
            position = len(all_drivers) + 1 if entry_data['is_dnf'] else entry_data['current_position']
            stats['position_counts'].append(position)
            if entry_data['is_dnf']:
                stats['dnf_count'] += 1
                stats['finishing_positions'][len(all_drivers) + 1] += 1
            else:
                stats['total_points'] += assign_points(entry_data['current_position'])
                stats['finishing_positions'][entry_data['current_position']] += 1
    final_data = []
    for driver_name, stats in driver_stats.items():
        avg_points = stats['total_points'] / num_sims
        dnf_rate = (stats['dnf_count'] / num_sims) * 100
        position_counts = Counter(stats['position_counts'])
        mode_position = min(position_counts.items(), key=lambda x: (x[0], -x[1]))[0] if position_counts else len(all_drivers) + 1
        mode_count = position_counts[mode_position] if position_counts else 0
        result = {
            'Driver': driver_name,
            'Team': stats['team_name'],
            'Mode Position': mode_position,
            'Mode Count': mode_count,
            'Avg Points': avg_points,  # Changed to numeric for sorting
            'DNF Rate (%)': f"{dnf_rate:.2f}"
        }
        for pos in range(1, len(all_drivers) + 1):
            result[f'P{pos}_Prob'] = (stats['finishing_positions'][pos] / num_sims) * 100
        final_data.append(result)
    results_df = pd.DataFrame(final_data).sort_values(by=['Mode Position', 'Mode Count', 'Avg Points'], ascending=[True, False, False])
    return results_df

def generate_final_p1_p20_list(aggregated_df, num_drivers):
    """Generates a final P1-P20 list with Position, Driver, Team, and Points based on sorted position."""
    final_list = aggregated_df[['Driver', 'Team', 'Mode Position', 'Mode Count', 'Avg Points']].copy()
    final_list = final_list.sort_values(by=['Mode Position', 'Mode Count', 'Avg Points'], ascending=[True, False, False]).reset_index(drop=True)
    final_list['Position'] = final_list.index + 1
    final_list['Points'] = final_list['Position'].apply(assign_points)  # Assign points based on final Position
    final_list = final_list[['Position', 'Driver', 'Team', 'Points']]
    final_list = final_list.head(min(num_drivers, 20))
    return final_list

# --- 5. Main Execution Block ---
if __name__ == "__main__":
    print("--- F1 Race Simulator Initializing ---")
    teams_data = load_csv_data('TEAM DATA.csv')
    drivers_data = load_csv_data('DRIVERS DATA.csv')
    car_calculations_data = load_csv_data('CALCULATIONS.csv')
    if any(data is None for data in [teams_data, drivers_data, car_calculations_data]):
        print("\nExiting due to data loading errors. Please check file paths and integrity.")
    else:
        try:
            print("\nAvailable Circuits:")
            for i, c in enumerate(CIRCUIT_DATA): print(f"  {i+1}: {c['name']}")
            circuit_choice = int(input(f"Choose a circuit number (1-{len(CIRCUIT_DATA)}): ")) - 1
            chosen_circuit = CIRCUIT_DATA[circuit_choice]
            total_simulations = int(input("\nEnter total number of Monte Carlo simulations to run (e.g., 5000): "))
            use_enhanced = input("\nUse enhanced simulation features? (y/n): ").strip().lower() == 'y'
        except (ValueError, IndexError):
            print("Invalid input. Exiting."); exit()
        valid_drivers = []
        for d in drivers_data:
            team_name = d.get('team_name', '').strip()
            if team_name and any(t['team_name'].strip() == team_name for t in teams_data) and any(cs.get('Team Name', '').strip() == team_name for cs in car_calculations_data):
                valid_drivers.append(d)
        if len(valid_drivers) < len(drivers_data):
            print(f"\nWarning: Simulating for {len(valid_drivers)} of {len(drivers_data)} drivers with complete data.")
        if not valid_drivers:
            print("No valid drivers found. Please check team assignments in your CSVs.")
        else:
            race_entries_template = []
            for driver_data in valid_drivers:
                team_name = driver_data['team_name'].strip()
                team_info = next(t for t in teams_data if t['team_name'].strip() == team_name)
                car_score_info = next(cs for cs in car_calculations_data if cs['Team Name'].strip() == team_name)
                entry = RaceEntry(driver_data, team_info, car_score_info, 0, RACE_STRATEGY_TYPES[0])
                race_entries_template.append(entry)
            all_weather_conditions = list(WEATHER_CONDITIONS.items())
            num_weathers = len(all_weather_conditions)
            sims_per_weather = total_simulations // num_weathers
            remainder_sims = total_simulations % num_weathers
            all_sim_results_across_weathers = []
            for i, (weather_name, weather_data) in enumerate(all_weather_conditions):
                current_weather_sims = sims_per_weather + (1 if i < remainder_sims else 0)
                if current_weather_sims == 0: continue
                weather_data["name"] = weather_name
                if use_enhanced:
                    weather_data['variability'] = WEATHER_CONDITIONS[weather_name].get('variability', 0.1 if weather_name != 'Dry' else 0.05)
                results_for_this_weather = run_monte_carlo_simulation(current_weather_sims, chosen_circuit, weather_data, race_entries_template, use_enhanced)
                all_sim_results_across_weathers.extend(results_for_this_weather)
            if all_sim_results_across_weathers:
                final_df = aggregate_results(all_sim_results_across_weathers, valid_drivers)
                print("\n--- Final Aggregated Race Results (All Weather Conditions) ---")
                print(final_df.to_string())
                output_filename = f"SimResult_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs_AllWeather.csv"
                final_df.to_csv(output_filename, index=False)
                print(f"\nAggregated results saved to {output_filename}")
                final_p1_p20 = generate_final_p1_p20_list(final_df, len(valid_drivers))
                print("\n--- Final P1-P20 Race Result ---")
                print(final_p1_p20.to_string(index=False))
                p1_p20_filename = f"Final_P1_P20_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs.csv"
                final_p1_p20.to_csv(p1_p20_filename, index=False)
                print(f"\nFinal P1-P20 race result saved to {p1_p20_filename}")