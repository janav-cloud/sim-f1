import pandas as pd
import random
import math
from collections import Counter
import os # NEW: Import os module for path operations

# --- 1. Modular Data Imports ---
from circuit_data import CIRCUIT_DATA
from weather_conditions import WEATHER_CONDITIONS
from race_strategy import RACE_STRATEGY_TYPES
from weather_transitions import WEATHER_TRANSITIONS

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
        self.current_tire_compound = None
        self.laps_on_current_tires = 0
        self.has_graining = False
        self.has_minor_damage = False
        self.damage_penalty_factor = 1.0

        acumen_map = {
            "strategy_aggressive_acumen": self.strategy_aggressive_acumen,
            "strategy_balanced_acumen": self.strategy_balanced_acumen,
            "strategy_conservative_acumen": self.strategy_conservative_acumen
        }
        self.effective_strategy_acumen = self.team_strategy_acumen_base
        found_strategy = next((s_type for s_type in RACE_STRATEGY_TYPES if s_type['name'] == self.assigned_strategy_type['name']), None)
        if found_strategy:
            self.effective_strategy_acumen = acumen_map.get(found_strategy['applies_acumen'], self.team_strategy_acumen_base)
        else:
            self.effective_strategy_acumen = self.team_strategy_acumen_base

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

    if enhanced_simulation:
        if weather_changed:
            adaptability = entry.assigned_strategy_type.get('weather_adaptability', 0.0)
            adaptability_modifier = weather.get('adaptability_modifier', 0.2)
            adjusted_time *= (1.0 - (adaptability * adaptability_modifier * 0.1))

    adjusted_time /= effective_grip_multiplier

    base_wear_per_lap = circuit['tire_wear_severity'] * (1.1 - entry.car_tires_wr_final)
    driver_wear_effect = base_wear_per_lap * (1.0 - (entry.driver_tire_management * 0.5))
    final_wear_this_lap = (driver_wear_effect + weather['tire_wear_modifier']) / 100.0

    if enhanced_simulation and entry.current_tire_compound:
        if entry.current_tire_compound == 'soft':
            final_wear_this_lap *= 1.2
            adjusted_time *= 0.98
        elif entry.current_tire_compound == 'hard':
            final_wear_this_lap *= 0.8
            adjusted_time *= 1.02
        elif entry.current_tire_compound == 'intermediate':
            adjusted_time *= 0.95 if weather.get('tire_type_recommendation', 'dry') == 'intermediate' else 1.05
            final_wear_this_lap *= 1.0
        elif entry.current_tire_compound == 'wet':
            adjusted_time *= 0.90 if weather.get('tire_type_recommendation', 'dry') == 'wet' else 1.10
            final_wear_this_lap *= 0.7

    entry.tire_wear = min(1.0, entry.tire_wear + final_wear_this_lap)
    entry.laps_on_current_tires += 1

    if entry.tire_wear > 0.8:
        tire_wear_penalty = (entry.tire_wear ** 3) * 10.0
    elif entry.tire_wear > 0.5:
        tire_wear_penalty = (entry.tire_wear ** 2.5) * 7.5
    else:
        tire_wear_penalty = (entry.tire_wear ** 2) * 5.0
    adjusted_time += tire_wear_penalty

    if enhanced_simulation and not entry.has_graining:
        graining_chance = 0.0
        if entry.current_tire_compound in ['soft', 'medium'] and entry.tire_wear > 0.4 and entry.laps_on_current_tires > 8:
            graining_chance = (entry.tire_wear - 0.4) * 0.05
            graining_chance += (1.0 - entry.driver_tire_management) * 0.02
            graining_chance += weather.get('track_temp_celsius', 25) / 1000.0

        if random.random() < graining_chance:
            entry.has_graining = True
            adjusted_time += random.uniform(1.0, 3.0)

    if entry.has_graining:
        adjusted_time += 1.5

    deviation_range = (1.0 - entry.driver_consistency) * 0.5
    random_deviation = random.uniform(-deviation_range, deviation_range)
    adjusted_time += random_deviation
    
    strategy_bonus = (entry.effective_strategy_acumen - 0.7) * 0.1
    adjusted_time -= strategy_bonus

    if entry.has_minor_damage:
        adjusted_time *= entry.damage_penalty_factor

    if enhanced_simulation:
        weather_variability_lap_jitter = weather.get('variability', 0.0) * 0.5
        if random.random() < weather_variability_lap_jitter:
            adjusted_time *= random.uniform(0.995, 1.005)

    return max(base_time * 0.8, adjusted_time)

def decide_pit_stop(entry, circuit, lap, is_safety_car, enhanced_simulation=False, current_weather_name='Dry'):
    """Determines if a car should make a pit stop on the current lap."""
    strategy_name = entry.assigned_strategy_type['name']
    total_laps = circuit['laps']

    if is_safety_car and lap > 5 and lap < total_laps - 5:
        if (entry.assigned_strategy_type['name'] == "Safety Car Optimization (Opportunistic)" and entry.tire_wear > 0.2) or \
           (entry.effective_strategy_acumen > 0.75 and entry.tire_wear > 0.4):
            return True

    if entry.tire_wear > 0.95:
        return True

    if enhanced_simulation:
        tire_type_rec = WEATHER_CONDITIONS[current_weather_name].get('tire_type_recommendation', 'dry')
        if tire_type_rec != entry.current_tire_compound:
            if current_weather_name == 'Heavy Rain' and entry.current_tire_compound != 'wet':
                return True
            elif current_weather_name == 'Light Rain' and entry.current_tire_compound not in ['intermediate', 'wet']:
                if entry.effective_strategy_acumen > 0.6 or entry.assigned_strategy_type['name'] == "Weather Dependent (Wet/Intermediate Play)":
                    return True
            elif current_weather_name == 'Dry' and entry.current_tire_compound in ['intermediate', 'wet']:
                return True
            elif current_weather_name == 'Hot' and entry.current_tire_compound in ['intermediate', 'wet']:
                return True
            elif current_weather_name == 'Cold' and entry.current_tire_compound in ['intermediate', 'wet']:
                return True

    num_stops = 1
    if "2-Stop" in strategy_name: num_stops = 2
    elif "3-Stop" in strategy_name: num_stops = 3

    if lap > total_laps - 5: return False

    pit_window_size = 5
    for i in range(1, num_stops + 1):
        target_lap = int((total_laps / (num_stops + 1)) * i)
        if entry.pit_stops_made == (i - 1) and lap in range(max(1, target_lap - pit_window_size), min(total_laps + 1, target_lap + pit_window_size + 1)):
            if entry.tire_wear > 0.5 or \
               (entry.laps_on_current_tires > (total_laps / (num_stops + 1) * 0.8) and entry.tire_wear > 0.3):
                return True

    if enhanced_simulation:
        if entry.current_tire_compound == 'soft' and entry.tire_wear > 0.65 and \
           entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive push'):
            return True

    return False

def simulate_pit_stop(entry, enhanced_simulation=False, current_weather_name='Dry', circuit=None):
    """Simulates a pit stop, adding time and resetting tire wear, and choosing new tires."""
    base_time = 23.0
    time_reduction = entry.team_pit_stop_speed * 2.0
    pit_stop_time = base_time - time_reduction
    if enhanced_simulation:
        pit_stop_variability = random.uniform(-0.5, 0.5)
        pit_stop_time += pit_stop_variability
    entry.total_race_time_s += pit_stop_time
    entry.pit_stops_made += 1
    entry.tire_wear = 0.0
    entry.laps_on_current_tires = 0
    entry.has_graining = False

    new_compound = None
    tire_type_rec = WEATHER_CONDITIONS[current_weather_name].get('tire_type_recommendation', 'dry')
    
    if tire_type_rec == 'intermediate':
        new_compound = 'intermediate'
    elif tire_type_rec == 'wet':
        new_compound = 'wet'
    else:
        compounds = ['soft', 'medium', 'hard']
        strategy_pref = entry.assigned_strategy_type.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
        
        if circuit:
            remaining_laps = circuit['laps'] - entry.laps_completed
            if remaining_laps < 10:
                new_compound = random.choices(['soft', 'medium'], weights=[0.7, 0.3], k=1)[0]
            elif remaining_laps > 30 and entry.tire_wear < 0.2:
                 new_compound = random.choices(['medium', 'hard'], weights=[0.6, 0.4], k=1)[0]
            elif entry.tire_wear > 0.7:
                new_compound = random.choices(['medium', 'hard'], weights=[0.6, 0.4], k=1)[0]
            else:
                new_compound = random.choices(compounds, weights=[strategy_pref[c] for c in compounds], k=1)[0]
        else:
            new_compound = random.choices(compounds, weights=[strategy_pref[c] for c in compounds], k=1)[0]

    entry.current_tire_compound = new_compound
    return pit_stop_time

def simulate_event(entry, weather, enhanced_simulation=False):
    """Simulates random events like mechanical failures and driver errors."""
    if entry.is_dnf: return

    engine_reliability_penalty_factor = (1.0 - entry.car_engine_rel_final) * 2
    brakes_durability_penalty_factor = (1.0 - entry.car_brakes_dur_final) * 1.5
    
    failure_chance = 0.0002 + (engine_reliability_penalty_factor * 0.001) + (brakes_durability_penalty_factor * 0.0008)

    if enhanced_simulation:
        if entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            failure_chance *= 1.25
        
        minor_damage_chance_base = 0.0002 + (engine_reliability_penalty_factor * 0.0005) + (brakes_durability_penalty_factor * 0.0003)
        if entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            minor_damage_chance_base *= 1.5
        if entry.tire_wear > 0.8:
            minor_damage_chance_base *= (1 + (entry.tire_wear - 0.8) * 0.5)

        if random.random() < minor_damage_chance_base and not entry.has_minor_damage:
            entry.has_minor_damage = True
            entry.damage_penalty_factor = random.uniform(1.005, 1.02)

    if random.random() < failure_chance:
        total_penalty = engine_reliability_penalty_factor + brakes_durability_penalty_factor
        if total_penalty > 0 and random.random() < (engine_reliability_penalty_factor / total_penalty):
            entry.dnf_reason = "Mechanical Failure (Engine)"
        elif total_penalty > 0:
            entry.dnf_reason = "Mechanical Failure (Brakes/Chassis)"
        else:
            entry.dnf_reason = "Mechanical Failure"
        entry.is_dnf = True
        return

    error_chance = 0.001 * (1.5 - entry.driver_consistency) + weather['driver_error_chance_modifier']
    if enhanced_simulation:
        error_chance += weather.get('variability', 0.0) * 0.0005
        if entry.tire_wear > 0.8:
            error_chance *= (1 + (entry.tire_wear - 0.8) * 0.5)
        if entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            error_chance *= 1.1

    if random.random() < error_chance:
        incident_type_roll = random.random()
        if incident_type_roll < 0.05:
            entry.is_dnf = True
            entry.dnf_reason = "Driver Error (Crash)"
        elif incident_type_roll < 0.2:
            entry.total_race_time_s += random.uniform(5.0, 10.0)
        else:
            entry.total_race_time_s += random.uniform(1.0, 3.0)


def check_for_overtake(front_entry, rear_entry, circuit, time_diff, enhanced_simulation=False):
    """Calculates the probability of an overtake attempt being successful."""
    pace_advantage = (rear_entry.car_overall_score - front_entry.car_overall_score) * 0.2
    skill_advantage = (rear_entry.driver_overtaking_skill - front_entry.driver_defending_skill) * 0.3
    track_difficulty = circuit['overtaking_difficulty'] * 0.4
    
    overtake_prob = 0.3 + pace_advantage + skill_advantage - track_difficulty

    if enhanced_simulation:
        if front_entry.current_position <= 5:
            overtake_prob -= 0.05
        
        tire_wear_diff = front_entry.tire_wear - rear_entry.tire_wear
        overtake_prob += tire_wear_diff * 0.15

        if circuit['straight_speed_importance'] > 0.7 and circuit.get('downforce_sensitivity', 0.5) < 0.7:
            if time_diff < 0.8:
                overtake_prob += 0.15
            elif time_diff < 1.0:
                overtake_prob += 0.05

        overtake_prob += (rear_entry.driver_consistency - 0.5) * 0.05 
        
        if front_entry.driver_defending_skill > rear_entry.driver_overtaking_skill and front_entry.tire_wear < 0.7:
            overtake_prob -= 0.03
        
        if rear_entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            overtake_prob += 0.02

    return random.random() < max(0.0, min(1.0, overtake_prob))


def simulate_race(circuit, weather, entries, enhanced_simulation=False):
    """The main function to simulate an entire race from start to finish."""
    for entry in entries:
        entry.total_race_time_s = 0.0
        entry.laps_completed = 0
        entry.is_dnf = False
        entry.dnf_reason = ""
        entry.pit_stops_made = 0
        entry.tire_wear = 0.0
        entry.laps_on_current_tires = 0
        entry.has_graining = False
        entry.has_minor_damage = False
        entry.damage_penalty_factor = 1.0

    safety_car_laps = 0
    current_weather = weather.copy()
    current_weather_name = weather['name']

    print(f"\n--- Simulating Race at {circuit['name']} with initial {current_weather_name} conditions ---")

    for lap in range(1, circuit['laps'] + 1):
        is_safety_car_deployed_this_lap = False
        if safety_car_laps == 0 and lap > 2 and lap < circuit['laps'] - 5:
            dnf_occurred_last_lap = any(e.laps_completed == lap - 1 and e.is_dnf for e in entries)
            if dnf_occurred_last_lap:
                sc_probability = 0.6 if circuit.get('track_type') == 'Street Circuit' else 0.4
                if random.random() < sc_probability:
                    is_safety_car_deployed_this_lap = True
                    safety_car_laps = random.randint(2, 4)

        is_safety_car_active = safety_car_laps > 0
        weather_changed_this_lap = False

        if enhanced_simulation:
            weather_susceptibility = circuit.get('weather_susceptibility', 0.1)
            if random.random() < current_weather.get('variability', 0.0) * weather_susceptibility:
                possible_transitions = WEATHER_TRANSITIONS.get(current_weather_name, {})
                if possible_transitions:
                    next_weather_names = list(possible_transitions.keys())
                    transition_weights = list(possible_transitions.values())
                    
                    total_weight = sum(transition_weights)
                    if total_weight == 0:
                        new_weather_name = current_weather_name
                    else:
                        normalized_weights = [w / total_weight for w in transition_weights]
                        new_weather_name = random.choices(next_weather_names, weights=normalized_weights, k=1)[0]
                    
                    if new_weather_name != current_weather_name:
                        current_weather = WEATHER_CONDITIONS[new_weather_name].copy()
                        current_weather_name = new_weather_name
                        weather_changed_this_lap = True

        for entry in entries:
            if entry.is_dnf: continue

            simulate_event(entry, current_weather, enhanced_simulation)
            if entry.is_dnf: continue

            if decide_pit_stop(entry, circuit, lap, is_safety_car_active, enhanced_simulation, current_weather_name):
                simulate_pit_stop(entry, enhanced_simulation, current_weather_name, circuit)

            lap_time = calculate_lap_time(entry, circuit, current_weather, enhanced_simulation, weather_changed_this_lap)
            
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
                        car.total_race_time_s = leader_time + (i * 0.8)

        live_race_order = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)
        for i, entry in enumerate(live_race_order):
            entry.current_position = i + 1

        for i in range(len(live_race_order) - 1, 0, -1):
            rear_entry, front_entry = live_race_order[i], live_race_order[i-1]
            time_difference = rear_entry.total_race_time_s - front_entry.total_race_time_s
            
            if 0 < time_difference < 1.2: 
                if check_for_overtake(front_entry, rear_entry, circuit, time_difference, enhanced_simulation):
                    overtake_time_swing = random.uniform(0.1, 0.3)
                    
                    rear_entry.total_race_time_s = front_entry.total_race_time_s - overtake_time_swing
                    front_entry.total_race_time_s = front_entry.total_race_time_s + overtake_time_swing
                    
                    live_race_order.sort(key=lambda x: x.total_race_time_s)
                    for idx, entry_sorted in enumerate(live_race_order):
                        entry_sorted.current_position = idx + 1
                    i = len(live_race_order)

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

def run_monte_carlo_simulation(num_simulations, circuit, weather, race_entries_template, enhanced_simulation=False, race_results_output_dir=None):
    """Runs the race simulation multiple times for a specific weather condition."""
    print(f"\n--- Running {num_simulations} simulations for {weather['name']} conditions at {circuit['name']} ---")
    all_simulation_results = []
    
    if race_results_output_dir:
        # Create circuit-specific subdirectory
        circuit_specific_dir = os.path.join(race_results_output_dir, circuit['name'].replace(' ', '_')) # Replace spaces for valid folder name
        os.makedirs(circuit_specific_dir, exist_ok=True)
        print(f"Individual race results for {circuit['name']} will be saved to: {circuit_specific_dir}")


    for sim_num in range(num_simulations):
        sim_entries = []
        for entry_template in race_entries_template:
            driver_data_copy = {
                'driver_name': entry_template.driver_name,
                'skill': entry_template.driver_skill,
                'consistency': entry_template.driver_consistency,
                'tire_management': entry_template.driver_tire_management,
                'wet_weather_ability': entry_template.driver_wet_weather_ability,
                'overtaking_skill': entry_template.driver_overtaking_skill,
                'defending_skill': entry_template.driver_defending_skill,
                'team_name': entry_template.team_name
            }
            team_data_copy = {
                'team_name': entry_template.team_name,
                'team_pit_stop_speed': entry_template.team_pit_stop_speed,
                'team_strategy_acumen': entry_template.team_strategy_acumen_base,
                'strategy_aggressive_acumen': entry_template.strategy_aggressive_acumen,
                'strategy_balanced_acumen': entry_template.strategy_balanced_acumen,
                'strategy_conservative_acumen': entry_template.strategy_conservative_acumen
            }
            car_scores_copy = {
                'Overall_Car_Score': entry_template.car_overall_score,
                'Engine_HP_Final': entry_template.car_engine_hp_final,
                'Engine_REL_Final': entry_template.car_engine_rel_final,
                'ChassisAero_DF_Final': entry_template.car_chassis_aero_df_final,
                'ChassisAero_DR_Final': entry_template.car_chassis_aero_dr_final,
                'Brakes_SP_Final': entry_template.car_brakes_sp_final,
                'Brakes_DUR_Final': entry_template.car_brakes_dur_final,
                'Tires_WR_Final': entry_template.car_tires_wr_final
            }
            
            assigned_strategy = random.choice(RACE_STRATEGY_TYPES)
            
            new_entry = RaceEntry(driver_data_copy, team_data_copy, car_scores_copy, 0, assigned_strategy)
            sim_entries.append(new_entry)


        initial_grid_positions = list(range(1, len(sim_entries) + 1))
        random.shuffle(initial_grid_positions)

        for i, entry in enumerate(sim_entries):
            entry.initial_position = initial_grid_positions[i]
            entry.current_position = initial_grid_positions[i]
            
            if enhanced_simulation:
                compounds = ['soft', 'medium', 'hard']
                tire_type = weather.get('tire_type_recommendation', 'dry')
                if tire_type in ['intermediate', 'wet']:
                    entry.current_tire_compound = tire_type
                else:
                    circuit_weights = circuit.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
                    strategy_weights = entry.assigned_strategy_type.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
                    combined_weights = [(circuit_weights[c] + strategy_weights[c]) / 2 for c in compounds]
                    entry.current_tire_compound = random.choices(compounds, weights=combined_weights, k=1)[0]
            else:
                entry.current_tire_compound = 'medium'

        simulation_results = simulate_race(circuit, weather, sim_entries, enhanced_simulation)
        race_result_df = generate_final_race_result(simulation_results)
        
        print(f"\n--- Race Result for Simulation {sim_num + 1} ({weather['name']} conditions) ---")
        print(race_result_df.to_string(index=False))

        # NEW: Save individual race result CSV to circuit-specific subdirectory
        if race_results_output_dir:
            circuit_folder_name = circuit['name'].replace(' ', '_')
            race_filename = f"Race_{circuit_folder_name}_{weather['name'].replace(' ', '')}_Sim_{sim_num + 1}.csv"
            race_filepath = os.path.join(race_results_output_dir, circuit_folder_name, race_filename)
            race_result_df.to_csv(race_filepath, index=False)
            print(f"Individual race result saved to {race_filepath}")

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
            stats = driver_stats.get(entry_data['driver_name'])
            if stats:
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
        mode_position = min(position_counts.items(), key=lambda x: (-x[1], x[0]))[0] if position_counts else len(all_drivers) + 1
        mode_count = position_counts[mode_position] if position_counts else 0

        result = {
            'Driver': driver_name,
            'Team': stats['team_name'],
            'Mode Position': mode_position,
            'Mode Count': mode_count,
            'Avg Points': avg_points,
            'DNF Rate (%)': f"{dnf_rate:.2f}"
        }
        for pos in range(1, len(all_drivers) + 1):
            result[f'P{pos}_Prob'] = (stats['finishing_positions'].get(pos, 0) / num_sims) * 100
        result['DNF_Prob (%)'] = (stats['finishing_positions'].get(len(all_drivers) + 1, 0) / num_sims) * 100
        
        final_data.append(result)
    
    results_df = pd.DataFrame(final_data).sort_values(by=['Mode Position', 'Mode Count', 'Avg Points'], ascending=[True, False, False])
    return results_df

def generate_final_p1_p20_list(aggregated_df, num_drivers):
    """Generates a final P1-P20 list with Position, Driver, Team, and Points based on sorted position."""
    final_list = aggregated_df[['Driver', 'Team', 'Mode Position', 'Avg Points']].copy()
    final_list = final_list.sort_values(by=['Mode Position', 'Avg Points'], ascending=[True, False]).reset_index(drop=True)
    final_list['Position'] = final_list.index + 1
    final_list['Points'] = final_list['Position'].apply(assign_points) 
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
            for i, c in enumerate(CIRCUIT_DATA):
                print(f"  {i+1}: {c['name']}")
            circuit_choice = int(input(f"Choose a circuit number (1-{len(CIRCUIT_DATA)}): ")) - 1
            chosen_circuit = CIRCUIT_DATA[circuit_choice]
            
            total_simulations = int(input("\nEnter total number of Monte Carlo simulations to run (e.g., 5000): "))
            use_enhanced = input("\nUse enhanced simulation features? (y/n): ").strip().lower() == 'y'
            
            save_individual_races = input("Save individual race results to CSVs? (y/n): ").strip().lower() == 'y'
            race_results_output_dir = None
            if save_individual_races:
                # Base directory for all individual race results
                base_output_folder_name = "individual_results"
                race_results_output_dir = os.path.join(os.getcwd(), base_output_folder_name)
                # The circuit-specific subdirectory will be created inside run_monte_carlo_simulation
                print(f"Individual race results will be saved under: {race_results_output_dir}/{{Circuit Name}}/")

        except (ValueError, IndexError):
            print("Invalid input. Exiting.")
            exit()
        
        valid_drivers = []
        for d in drivers_data:
            team_name = d.get('team_name', '').strip()
            team_exists = any(t['team_name'].strip() == team_name for t in teams_data)
            car_data_exists = any(cs.get('Team Name', '').strip() == team_name for cs in car_calculations_data)
            if team_exists and car_data_exists:
                valid_drivers.append(d)
            else:
                print(f"Skipping driver {d.get('driver_name', 'N/A')}: Team '{team_name}' not found in TEAM DATA or CALCULATIONS.")

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
                initial_strategy_for_template = random.choice(RACE_STRATEGY_TYPES)
                entry = RaceEntry(driver_data, team_info, car_score_info, 0, initial_strategy_for_template)
                race_entries_template.append(entry)

            all_weather_conditions_list = list(WEATHER_CONDITIONS.items())
            num_weathers = len(all_weather_conditions_list)
            
            sims_per_weather = total_simulations // num_weathers
            remainder_sims = total_simulations % num_weathers
            
            all_sim_results_across_weathers = []
            for i, (weather_name, weather_data) in enumerate(all_weather_conditions_list):
                current_weather_sims = sims_per_weather + (1 if i < remainder_sims else 0)
                if current_weather_sims == 0: continue

                weather_for_sim = weather_data.copy()
                weather_for_sim["name"] = weather_name
                if use_enhanced:
                    weather_for_sim['variability'] = weather_data.get('variability', 0.1 if weather_name != 'Dry' else 0.05)
                
                results_for_this_weather = run_monte_carlo_simulation(current_weather_sims, chosen_circuit, weather_for_sim, race_entries_template, use_enhanced, race_results_output_dir)
                all_sim_results_across_weathers.extend(results_for_this_weather)
            
            if all_sim_results_across_weathers:
                final_df = aggregate_results(all_sim_results_across_weathers, valid_drivers)
                print("\n" + "="*50)
                print("--- FINAL AGGREGATED RACE RESULTS (ALL WEATHER CONDITIONS) ---")
                print("="*50)
                print(final_df.to_string())
                
                output_filename = f"SimResult_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs_AllWeather.csv"
                final_df.to_csv(output_filename, index=False)
                print(f"\nAggregated results saved to {output_filename}")

                final_p1_p20 = generate_final_p1_p20_list(final_df, len(valid_drivers))
                print("\n" + "="*50)
                print("--- FINAL P1-P20 RACE RESULT ---")
                print("="*50)
                print(final_p1_p20.to_string(index=False))
                
                p1_p20_filename = f"Final_P1_P20_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs.csv"
                final_p1_p20.to_csv(p1_p20_filename, index=False)
                print(f"\nFinal P1-P20 race result saved to {p1_p20_filename}")