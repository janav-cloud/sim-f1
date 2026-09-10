import pandas as pd
import random
import math
from collections import Counter
import os
import json

# --- 1. Modular Data Imports ---
from circuit_data import CIRCUIT_DATA
from weather_conditions import WEATHER_CONDITIONS
from race_strategy import RACE_STRATEGY_TYPES
from weather_transitions import WEATHER_TRANSITIONS
# NEW: Import new modules for enhanced features
from ers_management import ERS_MODES, manage_ers 
from track_evolution import TrackState
from team_orders import check_for_team_orders
# NEW: Import the race logger
from race_logger import RaceLogger

# --- 2. Data Loading Function ---
def load_csv_data(filepath):
    """
    Loads data from a specified CSV file into a list of dictionaries.
    Handles potential FileNotFoundError and other exceptions.
    """
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
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
        self.car_overall_score = car_scores.get('Overall_Car_Score', 80.0)
        self.car_engine_hp_final = car_scores.get('Engine_HP_Final', 8.0)
        self.car_engine_fe_final = car_scores.get('Engine_FE_Final', 7.5)
        self.car_engine_rel_final = car_scores.get('Engine_REL_Final', 7.0)
        self.car_chassis_aero_df_final = car_scores.get('ChassisAero_DF_Final', 8.0)
        self.car_chassis_aero_dr_final = car_scores.get('ChassisAero_DR_Final', 5.5)
        self.car_chassis_aero_cs_final = car_scores.get('ChassisAero_CS_Final', 8.0)
        self.car_suspension_hdl_final = car_scores.get('Suspension_HDL_Final', 8.0)
        self.car_suspension_twm_final = car_scores.get('Suspension_TWM_Final', 8.0)
        self.car_suspension_rc_final = car_scores.get('Suspension_RC_Final', 8.0)
        self.car_brakes_sp_final = car_scores.get('Brakes_SP_Final', 8.0)
        self.car_brakes_hd_final = car_scores.get('Brakes_HD_Final', 8.0)
        self.car_brakes_dur_final = car_scores.get('Brakes_DUR_Final', 8.0)
        self.car_tires_grp_final = car_scores.get('Tires_GRP_Final', 8.0)
        self.car_tires_wr_final = car_scores.get('Tires_WR_Final', 5.5)
        self.car_tires_con_final = car_scores.get('Tires_CON_Final', 8.0)
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
        self.ers_charge = 1.0
        self.ers_mode = ERS_MODES['Standard']
        self.ers_deployment_lap = 0
        self.morale = 1.0
        self.fuel_load_kg = 110.0
        self.drs_active = False
        self.in_dirty_air = False
        self.compounds_used = []

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
    """
    Calculates a realistic reference F1 lap time in seconds based on circuit length and characteristics.
    """
    straight_weight = circuit.get('straight_speed_importance', 0.7)
    cornering_weight = circuit.get('cornering_importance', 0.7)
    # Calibrated speed model: high straight speed lowers seconds per km; high cornering increases seconds per km
    sec_per_km = 17.2 - (straight_weight * 3.2) + (cornering_weight * 4.2)
    if circuit.get('track_type') == 'Street Circuit' and circuit.get('length_km', 5.0) < 4.0:
        sec_per_km += 3.5  # Monaco slow-speed twisty street adjustment
    return circuit['length_km'] * sec_per_km

def calculate_lap_time(entry, circuit, weather, enhanced_simulation=False, weather_changed=False, track_grip_bonus=0.0, ers_power_boost=0.0):
    """
    Calculates the realistic lap time for a single lap for a given entry.
    """
    base_time = calculate_base_lap_time(circuit)
    speed_weight = circuit['straight_speed_importance']
    cornering_weight = circuit['cornering_importance']
    braking_weight = circuit['braking_demands']
    downforce_sens = circuit.get('downforce_sensitivity', 0.7)
    
    # 1. Dynamic Circuit Trait Emphasis:
    # High-speed circuits amplify straight power & low drag; technical circuits amplify downforce & corner stability
    straight_emphasis = (speed_weight / 0.70) ** 1.45
    corner_emphasis = (cornering_weight / 0.70) ** 1.45 * (downforce_sens / 0.70)
    w_straight = speed_weight * straight_emphasis
    w_corner = cornering_weight * corner_emphasis
    w_brake = braking_weight * 0.22
    total_weight = w_straight + w_corner + w_brake

    # Scale ERS power boost
    scaled_ers = (ers_power_boost * 0.12) if enhanced_simulation else 0.0
    effective_hp = (entry.car_engine_hp_final + scaled_ers) * weather['hp_multiplier']

    # DRS straight speed surge (magnified on high-speed circuits)
    drs_speed_bonus = 0.0
    if enhanced_simulation and entry.drs_active:
        drs_speed_bonus = 0.45 * (speed_weight / 0.70)

    # Aerodynamic downforce & dirty air
    effective_downforce = entry.car_chassis_aero_df_final * weather['downforce_multiplier']
    if enhanced_simulation and entry.in_dirty_air:
        effective_downforce *= 0.86  # 14% front downforce loss in wake

    # DR (Drag): LOWER is better! On high-speed circuits, drag efficiency gives huge straight speed
    drag_efficiency = max(0.0, 10.0 - entry.car_chassis_aero_dr_final)
    straight_line_performance = (effective_hp * 0.65) + (drag_efficiency * 0.35) + drs_speed_bonus

    # Cornering performance integrates DF (Downforce), CS (Cornering Stability), and HDL (Handling)
    cornering_performance = (effective_downforce * 0.65) + (entry.car_chassis_aero_cs_final * 0.20) + (entry.car_suspension_hdl_final * 0.15)

    # Normalized braking with Heat Dissipation (HD) to reflect brake fade
    brake_norm = 7.0 + (entry.car_brakes_sp_final - 7.0) * 0.30 + (entry.car_brakes_hd_final - 7.5) * 0.15

    perf_score = (
        (straight_line_performance * w_straight) +
        (cornering_performance * w_corner) +
        (brake_norm * w_brake)
    ) / total_weight

    # 2. Car Pace vs Driver Skill Balance:
    # Lowered slightly on raw car (0.068) so car alone does not decide the race
    car_pace_delta = -(perf_score - 8.2) * 0.068 * (circuit['length_km'] / 5.0)

    # Wet weather equalizer: in rain, car mechanical differences are compressed by 55% (traction limited)
    if weather.get('grip_multiplier', 1.0) < 0.90:
        car_pace_delta *= 0.45

    adjusted_time = base_time + car_pace_delta

    # Driver skill delta: elevated to 1.35 so driver talent has authentic race-winning agency
    driver_skill_delta = -(entry.driver_skill - 0.85) * 1.35 * (circuit['length_km'] / 5.0)
    adjusted_time += driver_skill_delta

    # Street Circuit Agility & Curb Riding (Handling + Ride Comfort)
    if circuit.get('track_type') == 'Street Circuit':
        curb_agility = ((entry.car_suspension_hdl_final + entry.car_suspension_rc_final - 16.0) / 10.0) * 0.22
        adjusted_time -= curb_agility

    # Standing start / Lap 1 launch physics
    if entry.laps_completed == 0:
        standing_start_delta = 6.2
        if enhanced_simulation:
            if entry.current_tire_compound == 'soft':
                standing_start_delta -= 0.50
            elif entry.current_tire_compound == 'hard':
                standing_start_delta += 0.50
            driver_launch_reaction = (entry.driver_skill - 0.85) * 0.60 + (entry.driver_consistency - 0.5) * 0.35
            standing_start_delta -= driver_launch_reaction
        adjusted_time += standing_start_delta

    # 3. Weather & Rain Mastery:
    grip_penalty = max(0.0, 1.0 - weather['grip_multiplier'])
    # In rain, elite wet weather drivers mitigate up to 75% of lost grip
    mitigation = grip_penalty * (entry.driver_wet_weather_ability * 0.75)
    effective_grip_multiplier = weather['grip_multiplier'] + mitigation + track_grip_bonus
    
    # Grip loss lap time penalty
    effective_grip_loss = max(0.0, 1.0 - effective_grip_multiplier)
    adjusted_time += base_time * (effective_grip_loss * 0.40)

    # 4. Track Evolution (Rubbering in):
    if track_grip_bonus > 0:
        adjusted_time -= base_time * (track_grip_bonus * 0.32)

    if enhanced_simulation and weather_changed:
        adaptability = entry.assigned_strategy_type.get('weather_adaptability', 0.0)
        adaptability_modifier = weather.get('adaptability_modifier', 0.2)
        adjusted_time *= (1.0 - (adaptability * adaptability_modifier * 0.08))

    # 5. Tire Degradation Model (Circuit Wear Severity + Driver Tire Management):
    normalized_tires_wr = entry.car_tires_wr_final / 10.0
    twm_factor = 1.0 - ((entry.car_suspension_twm_final - 8.0) * 0.04)
    car_wear_factor = max(0.35, (0.40 + normalized_tires_wr) * twm_factor)
    
    laps_factor = max(40, circuit.get('laps', 55))
    circuit_wear_mult = (circuit['tire_wear_severity'] / 0.70)
    base_wear_per_lap = (circuit['tire_wear_severity'] / laps_factor) * 2.2 * car_wear_factor * circuit_wear_mult
    # Driver tire management has increased impact (0.55 factor)
    driver_wear_effect = base_wear_per_lap * (1.0 - (entry.driver_tire_management * 0.55))
    final_wear_this_lap = driver_wear_effect + (weather['tire_wear_modifier'] * 0.006)

    # Compound effects on pace and wear
    weather_rec = weather.get('tire_type_recommendation', 'dry')
    if enhanced_simulation and entry.current_tire_compound:
        if entry.current_tire_compound == 'soft':
            final_wear_this_lap *= 1.45
            adjusted_time -= 0.58  # Soft tire initial pace burst
        elif entry.current_tire_compound == 'medium':
            final_wear_this_lap *= 1.00
            # baseline pace
        elif entry.current_tire_compound == 'hard':
            final_wear_this_lap *= 0.68
            adjusted_time += 0.42
        elif entry.current_tire_compound == 'intermediate':
            final_wear_this_lap *= 0.90
            if weather_rec != 'intermediate':
                adjusted_time += 3.5 if weather_rec == 'dry' else 4.5
        elif entry.current_tire_compound == 'wet':
            final_wear_this_lap *= 0.70
            if weather_rec != 'wet':
                adjusted_time += 8.0 if weather_rec == 'dry' else 3.0

        # Heavy penalty for slicks in rain
        if entry.current_tire_compound in ['soft', 'medium', 'hard']:
            if weather_rec == 'intermediate':
                adjusted_time += 10.0
            elif weather_rec == 'wet':
                adjusted_time += 28.0

        # 6. Thermal Effects (Track Temperature):
        track_temp = weather.get('track_temp_celsius', 25)
        if track_temp >= 38:
            # Hot track thermal degradation: soft tires blister severely; hard tires excel
            if entry.current_tire_compound == 'soft':
                final_wear_this_lap *= 1.30
                if entry.laps_on_current_tires > 5:
                    adjusted_time += 0.42  # Blistering pace penalty
            elif entry.current_tire_compound == 'hard':
                adjusted_time -= 0.30  # Hard tire operating window advantage
            # Brake thermal fade in high temperatures
            if entry.car_brakes_hd_final < 8.0:
                adjusted_time += 0.16
        elif track_temp <= 18:
            # Cold track warm-up lag on hard compound
            if entry.current_tire_compound == 'hard' and entry.laps_on_current_tires <= 4:
                adjusted_time += 0.55
            elif entry.current_tire_compound in ['soft', 'medium']:
                adjusted_time -= 0.25

        # 7. Out-lap fresh tire surge (Powerful Undercut Advantage):
        if entry.laps_on_current_tires <= 2 and entry.pit_stops_made > 0:
            adjusted_time -= (0.95 if entry.laps_on_current_tires == 1 else 0.50)

    # Dirty air wear acceleration:
    if enhanced_simulation and entry.in_dirty_air:
        final_wear_this_lap *= 1.18  # 18% more wear sliding in dirty air

    entry.tire_wear = min(1.0, max(0.0, entry.tire_wear + final_wear_this_lap))
    entry.laps_on_current_tires += 1

    # Progressive tire wear penalty (the "cliff"):
    if entry.tire_wear > 0.80:
        tire_wear_penalty = (entry.tire_wear ** 3) * 6.5
    elif entry.tire_wear > 0.50:
        tire_wear_penalty = (entry.tire_wear ** 2.5) * 4.8
    else:
        tire_wear_penalty = (entry.tire_wear ** 2) * 2.5
    adjusted_time += tire_wear_penalty

    # Graining
    if enhanced_simulation and not entry.has_graining:
        graining_chance = 0.0
        if entry.current_tire_compound in ['soft', 'medium'] and entry.tire_wear > 0.4 and entry.laps_on_current_tires > 8:
            graining_chance = (entry.tire_wear - 0.4) * 0.05
            graining_chance += (1.0 - entry.driver_tire_management) * 0.02
            graining_chance += weather.get('track_temp_celsius', 25) / 1000.0

        if random.random() < graining_chance:
            entry.has_graining = True
            adjusted_time += random.uniform(1.0, 2.5)

    if entry.has_graining:
        adjusted_time += 1.2

    # Driver consistency variance modulated by Suspension_RC (Ride Comfort) and Tires_CON (Consistency)
    dampener = max(0.7, 1.0 - ((entry.car_suspension_rc_final - 8.0) * 0.02) - ((entry.car_tires_con_final - 7.5) * 0.02))
    deviation_range = max(0.08, (1.0 - entry.driver_consistency) * 0.45 * dampener)
    random_deviation = random.uniform(-deviation_range, deviation_range)
    adjusted_time += random_deviation
    
    # Strategy acumen bonus: neutral at 0.70
    strategy_bonus = (entry.effective_strategy_acumen - 0.70) * 0.08
    adjusted_time -= strategy_bonus

    if entry.has_minor_damage:
        adjusted_time *= entry.damage_penalty_factor

    if enhanced_simulation:
        weather_variability_lap_jitter = weather.get('variability', 0.0) * 0.5
        if random.random() < weather_variability_lap_jitter:
            adjusted_time *= random.uniform(0.997, 1.003)
            
        fuel_burn_rate = circuit['length_km'] * 0.35
        # Engine_FE_Final (Fuel Efficiency): Higher is better (burns fuel more efficiently)
        fe_factor = 1.0 - ((entry.car_engine_fe_final - 7.5) * 0.03)
        fuel_burn_rate *= max(0.85, fe_factor)
        if entry.ers_mode['name'] in ['Overtake', 'Hotlap']:
            fuel_burn_rate *= 1.1
        elif entry.ers_mode['name'] == 'Charge':
            fuel_burn_rate *= 0.9
            
        entry.fuel_load_kg = max(0.0, entry.fuel_load_kg - fuel_burn_rate)
        # Weight penalty: ~0.3s per 10kg
        weight_penalty = (entry.fuel_load_kg / 10.0) * 0.30
        adjusted_time += weight_penalty
        
        if entry.morale > 1.0:
            adjusted_time *= (1.0 - min(0.015, (entry.morale - 1.0) * 0.01))
        elif entry.morale < 1.0:
            adjusted_time *= (1.0 + min(0.015, (1.0 - entry.morale) * 0.01))

    # Sanity guard: minimum realistic time is 75% of base_time
    return max(base_time * 0.75, adjusted_time)

def decide_pit_stop(entry, circuit, lap, is_safety_car, is_vsc=False, enhanced_simulation=False, current_weather_name='Dry', track_state=None, teams_pitting_this_lap=None):
    """Determines if a car should make a pit stop on the current lap based on strategy and TEAM DATA acumen."""
    # Under green flag conditions, teams avoid double stacking by staggering stops by 1 lap unless tire wear is critical
    if enhanced_simulation and not is_safety_car and not is_vsc and teams_pitting_this_lap and entry.team_name in teams_pitting_this_lap:
        if entry.tire_wear < 0.80:
            return False

    strategy_name = entry.assigned_strategy_type['name']
    total_laps = circuit['laps']

    # 1. Safety Car / VSC Opportunism driven by team_strategy_acumen from TEAM DATA.csv
    if (is_safety_car or is_vsc) and lap > 5 and lap < total_laps - 5:
        # High acumen teams need lower wear to seize free pit stop; low acumen teams hesitate
        base_thresh = 0.20 if entry.assigned_strategy_type['name'] == "Safety Car Optimization (Opportunistic)" else 0.35
        if is_vsc:
            base_thresh += 0.05
        # Teams with higher strategy acumen react decisively; lower acumen teams need more wear before pitting
        acumen_thresh = base_thresh if entry.effective_strategy_acumen > 0.78 else (base_thresh + 0.12)
        if entry.tire_wear > acumen_thresh:
            return True

    # 2. Critical tire wear failure threshold
    if entry.tire_wear > 0.85:
        return True

    # 3. Dynamic Undercut Trigger driven by strategy acumen:
    # High acumen teams notice rival within 1.4s near scheduled window and pit 1-2 laps early to jump them
    if enhanced_simulation and not is_safety_car and not is_vsc:
        time_to_front = getattr(entry, 'current_time_to_front', float('inf'))
        if time_to_front < 1.4 and entry.tire_wear > 0.40 and entry.effective_strategy_acumen > 0.82:
            num_stops = 2 if "2-Stop" in strategy_name else (3 if "3-Stop" in strategy_name else 1)
            target_lap = int((total_laps / (num_stops + 1)) * (entry.pit_stops_made + 1))
            if abs(lap - target_lap) <= 3 and entry.pit_stops_made < num_stops:
                return True

    # 4. Drying line crossover trigger: if racing line is drying out, ditch wet/inters for slicks!
    if enhanced_simulation and track_state and track_state.has_dry_line:
        if entry.current_tire_compound in ['intermediate', 'wet'] and current_weather_name in ['Dry', 'Hot', 'Cold']:
            if entry.effective_strategy_acumen > 0.55 or lap > 8:
                return True

    # 5. Weather transitions driven by acumen:
    if enhanced_simulation:
        tire_type_rec = WEATHER_CONDITIONS[current_weather_name].get('tire_type_recommendation', 'dry')
        if tire_type_rec != entry.current_tire_compound:
            if current_weather_name == 'Heavy Rain' and entry.current_tire_compound != 'wet':
                return True
            elif current_weather_name == 'Light Rain' and entry.current_tire_compound not in ['intermediate', 'wet']:
                if entry.effective_strategy_acumen > 0.68 or entry.assigned_strategy_type['name'] == "Weather Dependent (Wet/Intermediate Play)":
                    return True
            elif current_weather_name in ['Dry', 'Hot', 'Cold'] and entry.current_tire_compound in ['intermediate', 'wet']:
                if not track_state or track_state.wetness_level < 0.20:
                    return True

    num_stops = 1
    if "2-Stop" in strategy_name: num_stops = 2
    elif "3-Stop" in strategy_name: num_stops = 3

    if lap > total_laps - 3: return False

    pit_window_size = 5
    for i in range(1, num_stops + 1):
        target_lap = int((total_laps / (num_stops + 1)) * i)
        if entry.pit_stops_made == (i - 1) and lap in range(max(1, target_lap - pit_window_size), min(total_laps + 1, target_lap + pit_window_size + 1)):
            # High acumen teams time stop when tire wear hits sweet spot; low acumen teams wait longer
            wear_threshold = 0.45 - (entry.effective_strategy_acumen - 0.75) * 0.12
            if entry.tire_wear > wear_threshold or \
               (entry.laps_on_current_tires >= int(total_laps / (num_stops + 1) * 0.75) and entry.tire_wear > 0.25) or \
               lap >= target_lap:
                return True

    # Mandatory FIA stop in dry races: if driver hasn't stopped yet, enforce stop before race ends
    if current_weather_name in ['Dry', 'Hot', 'Cold'] and entry.pit_stops_made == 0 and lap >= total_laps - 8:
        return True

    if enhanced_simulation:
        if entry.current_tire_compound == 'soft' and entry.tire_wear > 0.58 and \
           entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive push'):
            return True
        # Smart pit walls with high acumen protect tires from falling off the cliff
        cliff_protect = 0.72 if entry.effective_strategy_acumen > 0.80 else 0.80
        if entry.tire_wear > cliff_protect:
            return True

    return False

CIRCUIT_PIT_DELTAS = {
    "Bahrain International Circuit": 21.5,
    "Jeddah Corniche Circuit": 20.0,
    "Albert Park Circuit": 20.0,
    "Baku City Circuit": 20.5,
    "Miami International Autodrome": 20.0,
    "Circuit de Monaco": 19.5,
    "Circuit de Barcelona-Catalunya": 22.0,
    "Circuit Gilles Villeneuve": 18.5,
    "Red Bull Ring": 20.0,
    "Silverstone Circuit": 19.5,
    "Hungaroring": 20.5,
    "Circuit de Spa-Francorchamps": 22.5,
    "Circuit Zandvoort": 19.0,
    "Autodromo Nazionale Monza": 23.5,
    "Marina Bay Street Circuit": 28.0,
    "Suzuka International Racing Course": 22.0,
    "Losail International Circuit": 22.5,
    "Circuit of the Americas": 20.5,
    "Autódromo Hermanos Rodríguez": 21.0,
    "Autódromo José Carlos Pace": 20.5,
    "Las Vegas Strip Circuit": 20.0,
    "Yas Marina Circuit": 21.5,
}

def simulate_pit_stop(entry, lap, logger, is_safety_car, is_vsc=False, enhanced_simulation=False, current_weather_name='Dry', circuit=None, teams_pitting_this_lap=None, track_state=None):
    """Simulates a pit stop, adding time, resetting tire wear, and choosing new tires."""
    circuit_name = circuit.get('name', '') if circuit else ''
    total_pit_lane_loss = circuit.get('pit_lane_delta') or CIRCUIT_PIT_DELTAS.get(circuit_name, 21.0)
    # The pit lane driving time excluding stationary tire change (total pit loss minus baseline 2.4s)
    pit_lane_delta = max(15.0, total_pit_lane_loss - 2.4)

    # 1. Base stationary stop derived from team_pit_stop_speed in TEAM DATA.csv:
    # Top crews (0.95 Red Bull) -> ~2.18s; Midfield (0.85 Ferrari) -> ~2.33s; Backmarkers (0.68 Sauber) -> ~2.58s
    base_stationary_time = 3.6
    time_reduction = entry.team_pit_stop_speed * 1.5
    stationary_time = base_stationary_time - time_reduction
    if enhanced_simulation:
        # 2. Double-stack delay scaled by team_pit_stop_speed:
        # Elite crews service second car quickly (2.0 - 2.6s), slower crews take longer (3.4 - 4.5s)
        if teams_pitting_this_lap is not None:
            if entry.team_name in teams_pitting_this_lap:
                base_double_stack_delay = 5.2 - (entry.team_pit_stop_speed * 3.0)
                double_stack_delay = base_double_stack_delay + random.uniform(-0.25, 0.35)
                stationary_time += double_stack_delay
                logger.log_double_stack(lap, entry, double_stack_delay)
            else:
                teams_pitting_this_lap.add(entry.team_name)

        # 3. Pit stop error chance and duration scaled by team_pit_stop_speed:
        pit_error_chance = 0.04 * (1.0 - entry.team_pit_stop_speed)
        if random.random() < pit_error_chance:
            error_time = random.uniform(1.8, 4.2 + (1.0 - entry.team_pit_stop_speed) * 2.5)
            stationary_time += error_time
            logger.log_pit_error(lap, entry, error_time)
        else:
            pit_stop_variability = random.uniform(-0.35, 0.35) * (1.4 - entry.team_pit_stop_speed * 0.5)
            stationary_time += pit_stop_variability
            
    if is_safety_car:
        # Safety Car bunches field and cars move at ~50% speed past pit exit
        pit_stop_time = (pit_lane_delta * 0.5) + stationary_time
    elif is_vsc:
        # Under VSC, on-track cars are limited by delta time (~38% slower), reducing net pit loss by ~35%
        pit_stop_time = (pit_lane_delta * 0.65) + stationary_time
    else:
        pit_stop_time = pit_lane_delta + stationary_time
        
    entry.total_race_time_s += pit_stop_time
    entry.pit_stops_made += 1
    entry.tire_wear = 0.0
    entry.laps_on_current_tires = 0
    entry.has_graining = False

    new_compound = None
    tire_type_rec = WEATHER_CONDITIONS[current_weather_name].get('tire_type_recommendation', 'dry')
    
    # Check if drying line allows switching to dry compound even if weather is damp
    if enhanced_simulation and track_state and track_state.has_dry_line and current_weather_name in ['Dry', 'Hot', 'Cold']:
        tire_type_rec = 'dry'

    if tire_type_rec == 'intermediate':
        new_compound = 'intermediate'
    elif tire_type_rec == 'wet':
        new_compound = 'wet'
    else:
        compounds = ['soft', 'medium', 'hard']
        strategy_pref = entry.assigned_strategy_type.get('tire_compound_preference', {'soft': 0.33, 'medium': 0.33, 'hard': 0.34})
        
        # FIA Rule: in dry races, drivers must use at least two different dry compounds
        used_so_far = getattr(entry, 'compounds_used', [])
        # If only 1 compound used so far, require a different dry compound
        if len(set(used_so_far)) == 1 and entry.current_tire_compound in compounds:
            different_compounds = [c for c in compounds if c != entry.current_tire_compound]
        else:
            different_compounds = compounds

        if circuit:
            remaining_laps = circuit['laps'] - entry.laps_completed
            if remaining_laps < 12:
                candidates = [c for c in ['soft', 'medium'] if c in different_compounds] or ['soft', 'medium']
                new_compound = random.choices(candidates, weights=[0.65, 0.35] if len(candidates) == 2 else [1.0], k=1)[0]
            elif remaining_laps > 28:
                candidates = [c for c in ['medium', 'hard'] if c in different_compounds] or ['medium', 'hard']
                new_compound = random.choices(candidates, weights=[0.55, 0.45] if len(candidates) == 2 else [1.0], k=1)[0]
            else:
                candidates = different_compounds
                weights = [strategy_pref.get(c, 0.33) for c in candidates]
                total_w = sum(weights) or 1.0
                new_compound = random.choices(candidates, weights=[w / total_w for w in weights], k=1)[0]
        else:
            candidates = different_compounds
            weights = [strategy_pref.get(c, 0.33) for c in candidates]
            total_w = sum(weights) or 1.0
            new_compound = random.choices(candidates, weights=[w / total_w for w in weights], k=1)[0]

    entry.current_tire_compound = new_compound
    if not hasattr(entry, 'compounds_used'):
        entry.compounds_used = []
    entry.compounds_used.append(new_compound)
    
    logger.log_pit_stop(lap, entry, stationary_time, new_compound, total_pit_loss=pit_stop_time)
    
    return pit_stop_time

def simulate_event(entry, lap, logger, weather, enhanced_simulation=False):
    """Simulates random events like mechanical failures and driver errors."""
    if entry.is_dnf: return

    # CALCULATIONS.csv metrics: Engine_REL_Final (Higher=better), Brakes_DUR_Final (Higher=better), Brakes_HD_Final (Higher=better)
    rel_normalized = max(0.1, min(1.0, entry.car_engine_rel_final / 10.0))
    # Combined brake health from Durability and Heat Dissipation
    brake_health = (entry.car_brakes_dur_final * 0.65) + (entry.car_brakes_hd_final * 0.35)
    dur_normalized = max(0.1, min(1.0, brake_health / 10.0))
    
    engine_reliability_penalty_factor = (1.0 - rel_normalized) * 2.0
    brakes_durability_penalty_factor = (1.0 - dur_normalized) * 1.5
    
    failure_chance = 0.00015 + (engine_reliability_penalty_factor * 0.0008) + (brakes_durability_penalty_factor * 0.0006)

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
        logger.log_dnf(lap, entry)
        return

    # Driver error chance mitigated by wet weather ability in the rain
    rain_error_mod = weather.get('driver_error_chance_modifier', 0.0) * (1.0 - entry.driver_wet_weather_ability * 0.5)
    error_chance = 0.0008 * (1.5 - entry.driver_consistency) + (rain_error_mod * 0.20)
    if enhanced_simulation:
        error_chance += weather.get('variability', 0.0) * 0.0005
        if entry.tire_wear > 0.8:
            error_chance *= (1 + (entry.tire_wear - 0.8) * 0.5)
        if entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            error_chance *= 1.1

    if random.random() < error_chance:
        if enhanced_simulation:
            entry.morale = max(0.8, entry.morale - 0.1)
        incident_type_roll = random.random()
        if incident_type_roll < 0.06:
            entry.is_dnf = True
            entry.dnf_reason = "Driver Error (Crash)"
            logger.log_dnf(lap, entry)
        elif incident_type_roll < 0.22:
            entry.total_race_time_s += random.uniform(4.0, 9.0)
        else:
            entry.total_race_time_s += random.uniform(1.0, 2.5)


def check_for_overtake(front_entry, rear_entry, circuit, time_diff, enhanced_simulation=False):
    """Calculates the probability of an overtake attempt being successful."""
    # Moderated car advantage (0.008) so raw car does not overpower driver racecraft
    pace_advantage = (rear_entry.car_overall_score - front_entry.car_overall_score) * 0.008
    # Elevated driver racecraft (overtaking vs defending skill)
    skill_advantage = (rear_entry.driver_overtaking_skill - front_entry.driver_defending_skill) * 0.45
    # Circuit track difficulty (high at Monaco/Singapore, low at Monza/Spa)
    track_difficulty = circuit['overtaking_difficulty'] * 0.42
    
    overtake_prob = 0.22 + pace_advantage + skill_advantage - track_difficulty

    if enhanced_simulation:
        if front_entry.current_position <= 5:
            overtake_prob -= 0.05
        
        tire_wear_diff = front_entry.tire_wear - rear_entry.tire_wear
        overtake_prob += tire_wear_diff * 0.24

        if circuit['straight_speed_importance'] > 0.7 and circuit.get('downforce_sensitivity', 0.5) < 0.7:
            if time_diff < 0.8:
                overtake_prob += 0.16
            elif time_diff < 1.0:
                overtake_prob += 0.06

        overtake_prob += (rear_entry.driver_consistency - 0.5) * 0.05 
        
        # Elite defending driver holding position on healthy tires
        if front_entry.driver_defending_skill > rear_entry.driver_overtaking_skill and front_entry.tire_wear < 0.70:
            overtake_prob -= 0.06
        
        if rear_entry.assigned_strategy_type.get('name', '').lower().startswith('aggressive'):
            overtake_prob += 0.03
            
        if rear_entry.ers_mode['name'] == 'Overtake':
            overtake_prob += 0.18
        if front_entry.ers_mode['name'] == 'Defend':
            overtake_prob -= 0.12
            
        if rear_entry.drs_active:
            if front_entry.drs_active:
                overtake_prob += 0.05  # DRS train resistance: defending car also has DRS open
            else:
                overtake_prob += 0.26
            
        overtake_prob += (rear_entry.morale - 1.0) * 0.1
        overtake_prob -= (front_entry.morale - 1.0) * 0.1

    return random.random() < max(0.02, min(0.95, overtake_prob))


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
        entry.ers_charge = 1.0
        entry.ers_mode = ERS_MODES['Standard']
        entry.ers_deployment_lap = 0
        entry.morale = 1.0
        entry.fuel_load_kg = 110.0
        entry.drs_active = False
        entry.in_dirty_air = False

    safety_car_laps = 0
    safety_car_end_lap = -10
    vsc_laps = 0
    vsc_end_lap = -10
    current_weather = weather.copy()
    current_weather_name = weather['name']
    
    track_state = TrackState(track_type=circuit.get('track_type', 'Permanent'), initial_weather=current_weather_name)
    logger = RaceLogger()
    
    replay_data = {
        'circuit': circuit['name'],
        'total_laps': circuit['laps'],
        'initial_weather': current_weather_name,
        'starting_grid': [],
        'laps_data': [],
        'events': []
    }
    for entry in entries:
        entry.compounds_used = [entry.current_tire_compound] if entry.current_tire_compound else []
        replay_data['starting_grid'].append({
            'driver': entry.driver_name,
            'team': entry.team_name,
            'position': entry.initial_position
        })

    print(f"\n--- Simulating Race at {circuit['name']} with initial {current_weather_name} conditions ---")

    for lap in range(1, circuit['laps'] + 1):
        is_safety_car_deployed_this_lap = False
        if safety_car_laps == 0 and vsc_laps == 0 and lap > 2 and lap < circuit['laps'] - 5:
            non_dnf_incident_chance = 0.006 
            dnf_occurred_last_lap = any(e.laps_completed == lap - 1 and e.is_dnf for e in entries)
            if dnf_occurred_last_lap or random.random() < non_dnf_incident_chance:
                is_street = circuit.get('track_type') == 'Street Circuit'
                incident_severity_roll = random.random()
                full_sc_prob = 0.65 if is_street else 0.40
                if incident_severity_roll < full_sc_prob:
                    is_safety_car_deployed_this_lap = True
                    safety_car_laps = random.randint(2, 4)
                    logger.log_safety_car(lap)
                else:
                    vsc_laps = random.randint(1, 2)
                    logger.log_vsc(lap)

        is_safety_car_active = safety_car_laps > 0
        is_vsc_active = (vsc_laps > 0) and not is_safety_car_active
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
                        track_state.handle_weather_change(current_weather_name)
                        logger.log_weather_change(lap, new_weather_name)

        track_state.update_rubber(len([e for e in entries if not e.is_dnf]), current_weather=current_weather_name, total_cars=len(entries))
        track_grip_bonus = track_state.get_grip_bonus() if enhanced_simulation else 0.0

        live_race_order = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)

        for i, entry in enumerate(live_race_order):
            if entry.is_dnf: continue
            
            temp_front_car = live_race_order[i-1] if i > 0 else None
            entry.current_time_to_front = entry.total_race_time_s - temp_front_car.total_race_time_s if temp_front_car else float('inf')
            
            if enhanced_simulation:
                front_car = live_race_order[i-1] if i > 0 else None
                rear_car = live_race_order[i+1] if i < len(live_race_order) - 1 else None
                time_to_front = entry.total_race_time_s - front_car.total_race_time_s if front_car else float('inf')
                time_to_rear = rear_car.total_race_time_s - entry.total_race_time_s if rear_car else float('inf')
                manage_ers(entry, lap, time_to_front, time_to_rear, circuit=circuit)
                
                # FIA Rule: DRS enabled only after 2 green flag racing laps (at start and after restarts)
                drs_legal = (lap > 2) and (not is_safety_car_active) and (not is_vsc_active) and (lap > safety_car_end_lap + 2) and (lap > vsc_end_lap + 1)
                entry.drs_active = drs_legal and (time_to_front < 1.0)
                entry.in_dirty_air = time_to_front < 2.0

        teams_pitting_this_lap = set()
        for entry in entries:
            if entry.is_dnf: continue

            simulate_event(entry, lap, logger, current_weather, enhanced_simulation)
            if entry.is_dnf: continue

            if decide_pit_stop(entry, circuit, lap, is_safety_car_active, is_vsc=is_vsc_active, enhanced_simulation=enhanced_simulation, current_weather_name=current_weather_name, track_state=track_state, teams_pitting_this_lap=teams_pitting_this_lap):
                simulate_pit_stop(entry, lap, logger, is_safety_car_active, is_vsc=is_vsc_active, enhanced_simulation=enhanced_simulation, current_weather_name=current_weather_name, circuit=circuit, teams_pitting_this_lap=teams_pitting_this_lap, track_state=track_state)

            ers_boost = entry.ers_mode['power_boost'] if enhanced_simulation else 0.0
            lap_time = calculate_lap_time(entry, circuit, current_weather, enhanced_simulation, weather_changed_this_lap, track_grip_bonus, ers_boost)
            
            leader_laps = max(e.laps_completed for e in entries)
            if entry.laps_completed < leader_laps - 1:
                time_to_leader = entry.total_race_time_s - live_race_order[0].total_race_time_s
                if 0 < time_to_leader < 5: 
                    lap_time *= 1.015 
                    logger.log_blue_flag(lap, entry)
                    if len(live_race_order) > 0:
                        live_race_order[0].total_race_time_s += random.uniform(0.1, 0.25)

            if is_safety_car_active:
                sc_base = calculate_base_lap_time(circuit) * 1.35
                if hasattr(entry, 'current_time_to_front') and entry.current_time_to_front > 1.2:
                    lap_time = sc_base * 0.95 + random.uniform(-0.2, 0.2)
                else:
                    lap_time = sc_base + random.uniform(-0.2, 0.2)
            elif is_vsc_active:
                # Under VSC, delta pacing preserves on-track gaps without physical safety car bunching
                vsc_base = calculate_base_lap_time(circuit) * 1.38
                lap_time = vsc_base + random.uniform(-0.25, 0.25)

            entry.total_race_time_s += lap_time
            entry.laps_completed += 1

        if is_safety_car_active:
            safety_car_laps -= 1
            if safety_car_laps == 0:
                safety_car_end_lap = lap
                logger.log_safety_car_ends(lap)
        elif is_vsc_active:
            vsc_laps -= 1
            if vsc_laps == 0:
                vsc_end_lap = lap
                logger.log_vsc_ends(lap)

        live_race_order = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)
        for i, entry in enumerate(live_race_order):
            entry.current_position = i + 1
            
        if enhanced_simulation and not is_safety_car_active and not is_vsc_active:
            teams = {e.team_name for e in live_race_order}
            for team in teams:
                team_drivers = [e for e in live_race_order if e.team_name == team]
                if len(team_drivers) == 2:
                    team_drivers.sort(key=lambda x: x.current_position)
                    if check_for_team_orders(team_drivers[0], team_drivers[1], lap, circuit['laps'], logger):
                        time_swap_diff = team_drivers[1].total_race_time_s - team_drivers[0].total_race_time_s
                        team_drivers[0].total_race_time_s += time_swap_diff + 0.1
                        live_race_order.sort(key=lambda x: x.total_race_time_s)

        overtakes_this_lap = 0
        max_overtakes_per_lap = 4
        if not is_safety_car_active and not is_vsc_active:
            for i in range(len(live_race_order) - 1, 0, -1):
                if overtakes_this_lap >= max_overtakes_per_lap:
                    break
                rear_entry, front_entry = live_race_order[i], live_race_order[i-1]
                time_difference = rear_entry.total_race_time_s - front_entry.total_race_time_s
                
                if 0 < time_difference < 1.2: 
                    if check_for_overtake(front_entry, rear_entry, circuit, time_difference, enhanced_simulation):
                        logger.log_overtake(lap, rear_entry, front_entry)
                        front_entry.total_race_time_s = rear_entry.total_race_time_s + random.uniform(0.12, 0.25)
                        
                        if enhanced_simulation:
                            rear_entry.morale = min(1.2, rear_entry.morale + 0.05)
                            front_entry.morale = max(0.8, front_entry.morale - 0.05)
                        
                        overtakes_this_lap += 1

        live_race_order.sort(key=lambda x: x.total_race_time_s) 

        for idx, entry_sorted in enumerate(live_race_order):
            entry_sorted.current_position = idx + 1
            
        lap_state = []
        current_standings = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s) + sorted([e for e in entries if e.is_dnf], key=lambda x: (-x.laps_completed, x.total_race_time_s))
        for e in current_standings:
            lap_state.append({
                'driver': e.driver_name,
                'team': e.team_name,
                'position': e.current_position,
                'gap': e.total_race_time_s - current_standings[0].total_race_time_s if not e.is_dnf and len(current_standings) > 0 else -1,
                'tire': e.current_tire_compound,
                'tire_laps': e.laps_on_current_tires,
                'pits': e.pit_stops_made,
                'dnf': e.is_dnf,
                'dnf_reason': e.dnf_reason if e.is_dnf else '',
                'time': round(e.total_race_time_s, 3)
            })
        replay_data['laps_data'].append({
            'lap': lap,
            'weather': current_weather_name,
            'safety_car': is_safety_car_active or is_vsc_active,
            'vsc': is_vsc_active,
            'standings': lap_state
        })

    non_dnf = sorted([e for e in entries if not e.is_dnf], key=lambda x: x.total_race_time_s)
    dnf = sorted([e for e in entries if e.is_dnf], key=lambda x: (-x.laps_completed, x.total_race_time_s))
    
    final_results = non_dnf + dnf
    for i, entry in enumerate(final_results):
        entry.current_position = i + 1
        
    replay_data['events'] = logger.logs
        
    return final_results, logger.logs, replay_data

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

def calculate_circuit_quali_pace(entry, circuit, weather):
    """
    Calculates single-lap qualifying pace considering:
    - Circuit straight speed and low drag efficiency (power circuits like Monza, Spa, Vegas)
    - Circuit cornering importance, downforce sensitivity, and handling (Monaco, Hungaroring, Suzuka)
    - Weather grip & wet weather ability (rain masters excel in wet qualifying)
    - Driver raw skill and consistency (consistency controls clean banker lap vs mistakes)
    """
    speed_w = circuit.get('straight_speed_importance', 0.7)
    corner_w = circuit.get('cornering_importance', 0.7)
    downforce_sens = circuit.get('downforce_sensitivity', 0.7)
    
    # Drag efficiency (lower drag = higher straight speed)
    drag_eff = max(0.0, 10.0 - entry.car_chassis_aero_dr_final)
    straight_perf = (entry.car_engine_hp_final * 0.65) + (drag_eff * 0.35)
    corner_perf = (entry.car_chassis_aero_df_final * 0.60) + (entry.car_chassis_aero_cs_final * 0.25) + (entry.car_suspension_hdl_final * 0.15)
    
    car_circuit_perf = (straight_perf * speed_w + corner_perf * corner_w * downforce_sens) / (speed_w + corner_w * downforce_sens)
    
    # Driver talent in qualifying
    driver_quali = entry.driver_skill * 10.0
    
    # In wet qualifying, wet mastery is decisive & car differences are compressed
    grip_mult = weather.get('grip_multiplier', 1.0)
    if grip_mult < 0.90:
        wet_bonus = (entry.driver_wet_weather_ability - 0.80) * 8.0
        driver_quali += wet_bonus
        car_circuit_perf = 8.0 + (car_circuit_perf - 8.0) * 0.45
        
    # Consistency controls qualifying mistake / flyer variance
    consistency_range = max(0.15, (1.0 - entry.driver_consistency) * 1.4)
    driver_variance = random.uniform(-consistency_range, consistency_range)
    
    # Balanced weighting: 35% car circuit suitability, 65% driver prowess + variance
    final_quali_pace = (car_circuit_perf * 0.35) + (driver_quali * 0.65) + driver_variance
    return final_quali_pace

def run_monte_carlo_simulation(num_simulations, circuit, weather, race_entries_template, enhanced_simulation=False, race_results_output_dir=None, show_logs=False, save_logs=False, save_individual_races=False):
    """Runs the race simulation multiple times for a specific weather condition."""
    print(f"\n--- Running {num_simulations} simulations for {weather['name']} conditions at {circuit['name']} ---")
    all_simulation_results = []
    
    for sim_num in range(num_simulations):
        sim_entries = []
        for entry_template in race_entries_template:
            driver_data_copy = {
                'driver_name': entry_template.driver_name, 'skill': entry_template.driver_skill,
                'consistency': entry_template.driver_consistency, 'tire_management': entry_template.driver_tire_management,
                'wet_weather_ability': entry_template.driver_wet_weather_ability, 'overtaking_skill': entry_template.driver_overtaking_skill,
                'defending_skill': entry_template.driver_defending_skill, 'team_name': entry_template.team_name
            }
            team_data_copy = {
                'team_name': entry_template.team_name, 'team_pit_stop_speed': entry_template.team_pit_stop_speed,
                'team_strategy_acumen': entry_template.team_strategy_acumen_base, 'strategy_aggressive_acumen': entry_template.strategy_aggressive_acumen,
                'strategy_balanced_acumen': entry_template.strategy_balanced_acumen, 'strategy_conservative_acumen': entry_template.strategy_conservative_acumen
            }
            car_scores_copy = {
                'Overall_Car_Score': entry_template.car_overall_score,
                'Engine_HP_Final': entry_template.car_engine_hp_final,
                'Engine_FE_Final': entry_template.car_engine_fe_final,
                'Engine_REL_Final': entry_template.car_engine_rel_final,
                'ChassisAero_DF_Final': entry_template.car_chassis_aero_df_final,
                'ChassisAero_DR_Final': entry_template.car_chassis_aero_dr_final,
                'ChassisAero_CS_Final': entry_template.car_chassis_aero_cs_final,
                'Suspension_HDL_Final': entry_template.car_suspension_hdl_final,
                'Suspension_TWM_Final': entry_template.car_suspension_twm_final,
                'Suspension_RC_Final': entry_template.car_suspension_rc_final,
                'Brakes_SP_Final': entry_template.car_brakes_sp_final,
                'Brakes_HD_Final': entry_template.car_brakes_hd_final,
                'Brakes_DUR_Final': entry_template.car_brakes_dur_final,
                'Tires_GRP_Final': entry_template.car_tires_grp_final,
                'Tires_WR_Final': entry_template.car_tires_wr_final,
                'Tires_CON_Final': entry_template.car_tires_con_final
            }
            assigned_strategy = random.choice(RACE_STRATEGY_TYPES)
            new_entry = RaceEntry(driver_data_copy, team_data_copy, car_scores_copy, 0, assigned_strategy)
            sim_entries.append(new_entry)

        # Seed starting grid based on qualifying pace (circuit fit, weather, driver talent, consistency)
        for entry in sim_entries:
            entry.temp_quali = calculate_circuit_quali_pace(entry, circuit, weather)
        sim_entries.sort(key=lambda x: -x.temp_quali)
        for grid_pos, entry in enumerate(sim_entries):
            entry.initial_position = grid_pos + 1
            entry.current_position = grid_pos + 1
            entry.total_race_time_s = grid_pos * 0.25  # Grid row separation on race start

        for i, entry in enumerate(sim_entries):
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

        simulation_results, race_logs, replay_data = simulate_race(circuit, weather, sim_entries, enhanced_simulation)
        race_result_df = generate_final_race_result(simulation_results)
        
        base_output_dir = race_results_output_dir if race_results_output_dir else os.path.join(os.getcwd(), "outputs")
        circuit_folder_name = circuit['name'].replace(' ', '_')
        weather_folder_name = weather['name'].replace(' ', '_')

        # Always save race replays into outputs/replays/
        replay_dir = os.path.join(base_output_dir, "replays", circuit_folder_name, weather_folder_name)
        os.makedirs(replay_dir, exist_ok=True)
        replay_filepath = os.path.join(replay_dir, f"Sim_{sim_num + 1}_Replay.json")
        with open(replay_filepath, 'w') as f:
            json.dump(replay_data, f)
        print(f"Replay saved to {replay_filepath}")
        
        print(f"\n--- Race Result for Simulation {sim_num + 1} ({weather['name']} conditions) ---")
        print(race_result_df.to_string(index=False))

        if show_logs:
            print("\n--- Race Log ---")
            for log_entry in race_logs:
                print(f"Lap {log_entry['lap']:>2}: [{log_entry['type']:<12}] {log_entry['message']}")

        if save_individual_races:
            race_csv_dir = os.path.join(base_output_dir, "results", "races", circuit_folder_name, weather_folder_name)
            os.makedirs(race_csv_dir, exist_ok=True)
            race_filename = f"Race_{circuit_folder_name}_{weather_folder_name}_Sim_{sim_num + 1}.csv"
            race_filepath = os.path.join(race_csv_dir, race_filename)
            race_result_df.to_csv(race_filepath, index=False)
            print(f"Individual race result saved to {race_filepath}")

        if save_logs:
            log_dir = os.path.join(base_output_dir, "logs", "races", circuit_folder_name, weather_folder_name)
            os.makedirs(log_dir, exist_ok=True)
            log_filename = f"Race_{circuit_folder_name}_{weather_folder_name}_Sim_{sim_num + 1}_Log.txt"
            log_filepath = os.path.join(log_dir, log_filename)
            with open(log_filepath, 'w') as f:
                for log_entry in race_logs:
                    f.write(f"Lap {log_entry['lap']:>2}: [{log_entry['type']:<12}] {log_entry['message']}\n")
            print(f"Individual race log saved to {log_filepath}")

        all_simulation_results.append([e.__dict__.copy() for e in simulation_results])
    return all_simulation_results

def aggregate_results(all_simulation_results, all_drivers):
    """Aggregates results from all simulations into a final summary DataFrame."""
    driver_stats = {d['driver_name']: {
        'total_points': 0, 'dnf_count': 0,
        'finishing_positions': {pos: 0 for pos in range(1, len(all_drivers) + 2)}, 
        'team_name': d.get('team_name', 'N/A'), 'position_counts': []
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
            'Driver': driver_name, 'Team': stats['team_name'],
            'Mode Position': mode_position, 'Mode Count': mode_count,
            'Avg Points': avg_points, 'DNF Rate (%)': f"{dnf_rate:.2f}"
        }
        for pos in range(1, len(all_drivers) + 1):
            result[f'P{pos}_Prob'] = (stats['finishing_positions'].get(pos, 0) / num_sims) * 100
        result['DNF_Prob (%)'] = (stats['finishing_positions'].get(len(all_drivers) + 1, 0) / num_sims) * 100
        
        final_data.append(result)
    
    results_df = pd.DataFrame(final_data).sort_values(by=['Mode Position', 'Mode Count', 'Avg Points'], ascending=[True, False, False])
    return results_df

def generate_final_classification(aggregated_df, num_drivers=None):
    """Generates a final classification list with Position, Driver, Team, and Points based on sorted position (supports any number of drivers)."""
    final_list = aggregated_df[['Driver', 'Team', 'Mode Position', 'Avg Points']].copy()
    final_list = final_list.sort_values(by=['Avg Points', 'Mode Position'], ascending=[False, True]).reset_index(drop=True)
    final_list['Position'] = final_list.index + 1
    final_list['Points'] = final_list['Position'].apply(assign_points) 
    final_list = final_list[['Position', 'Driver', 'Team', 'Points']]
    if num_drivers is not None:
        final_list = final_list.head(num_drivers)
    return final_list

# Backwards compatibility alias
generate_final_p1_p20_list = generate_final_classification

def update_championship_standings(final_classification, circuit_name, all_drivers=None, all_teams=None):
    """
    Updates or creates two championship tracking CSVs ONLY at the project root:
    1. WDC.csv (World Drivers' Championship): Driver Name, Team Name, [Circuit 1], [Circuit 2]..., Total Points
    2. WCC.csv (World Constructors' Championship): Team Name, [Circuit 1], [Circuit 2]..., Total Points
    Appends a new column for each completed circuit and recalculates Total Points.
    Saves ONLY to the workspace root directory.
    """
    circuit_col = circuit_name.strip()
    base_dir = os.getcwd()

    driver_points = {}
    driver_team_map = {}
    team_points = {}

    for _, row in final_classification.iterrows():
        d_name = str(row['Driver']).strip()
        t_name = str(row['Team']).strip()
        pts = int(row['Points'])
        driver_points[d_name] = pts
        driver_team_map[d_name] = t_name
        team_points[t_name] = team_points.get(t_name, 0) + pts

    if all_drivers:
        for d in all_drivers:
            d_name = d.get('driver_name', '').strip()
            t_name = d.get('team_name', '').strip()
            if d_name:
                driver_team_map.setdefault(d_name, t_name)
                driver_points.setdefault(d_name, 0)

    if all_teams:
        for t in all_teams:
            t_name = t.get('team_name', '').strip()
            if t_name:
                team_points.setdefault(t_name, 0)

    # 1. Update WDC.csv (World Drivers' Championship) - ONLY in project root
    wdc_path = os.path.join(base_dir, "WDC.csv")
    if os.path.exists(wdc_path):
        try:
            wdc_df = pd.read_csv(wdc_path)
            wdc_df.columns = wdc_df.columns.str.strip()
        except Exception:
            wdc_df = pd.DataFrame()
    else:
        wdc_df = pd.DataFrame()

    if wdc_df.empty or 'Driver Name' not in wdc_df.columns:
        driver_list = list(driver_team_map.keys())
        wdc_df = pd.DataFrame({
            'Driver Name': driver_list,
            'Team Name': [driver_team_map.get(d, 'N/A') for d in driver_list]
        })

    existing_drivers = set(wdc_df['Driver Name'].astype(str).str.strip())
    new_driver_rows = []
    for d_name, t_name in driver_team_map.items():
        if d_name not in existing_drivers:
            new_driver_rows.append({'Driver Name': d_name, 'Team Name': t_name})
    if new_driver_rows:
        wdc_df = pd.concat([wdc_df, pd.DataFrame(new_driver_rows)], ignore_index=True)

    wdc_df['Team Name'] = wdc_df['Driver Name'].astype(str).str.strip().apply(
        lambda d: driver_team_map.get(d, wdc_df.loc[wdc_df['Driver Name'] == d, 'Team Name'].values[0])
    )
    wdc_df[circuit_col] = wdc_df['Driver Name'].astype(str).str.strip().apply(lambda d: driver_points.get(d, 0))

    circuit_cols_wdc = [c for c in wdc_df.columns if c not in {'Driver Name', 'Team Name', 'Total Points'}]
    for c in circuit_cols_wdc:
        wdc_df[c] = pd.to_numeric(wdc_df[c], errors='coerce').fillna(0).astype(int)

    wdc_df['Total Points'] = wdc_df[circuit_cols_wdc].sum(axis=1)
    wdc_df = wdc_df.sort_values(by=['Total Points', circuit_col], ascending=[False, False]).reset_index(drop=True)
    ordered_wdc_cols = ['Driver Name', 'Team Name'] + circuit_cols_wdc + ['Total Points']
    wdc_df = wdc_df[ordered_wdc_cols]

    # Save ONLY at project root
    wdc_df.to_csv(wdc_path, index=False)

    # 2. Update WCC.csv (World Constructors' Championship) - ONLY in project root
    wcc_path = os.path.join(base_dir, "WCC.csv")
    if os.path.exists(wcc_path):
        try:
            wcc_df = pd.read_csv(wcc_path)
            wcc_df.columns = wcc_df.columns.str.strip()
        except Exception:
            wcc_df = pd.DataFrame()
    else:
        wcc_df = pd.DataFrame()

    if wcc_df.empty or 'Team Name' not in wcc_df.columns:
        team_list = list(team_points.keys())
        wcc_df = pd.DataFrame({
            'Team Name': team_list
        })

    existing_teams = set(wcc_df['Team Name'].astype(str).str.strip())
    new_team_rows = []
    for t_name in team_points.keys():
        if t_name not in existing_teams:
            new_team_rows.append({'Team Name': t_name})
    if new_team_rows:
        wcc_df = pd.concat([wcc_df, pd.DataFrame(new_team_rows)], ignore_index=True)

    wcc_df[circuit_col] = wcc_df['Team Name'].astype(str).str.strip().apply(lambda t: team_points.get(t, 0))

    circuit_cols_wcc = [c for c in wcc_df.columns if c not in {'Team Name', 'Total Points'}]
    for c in circuit_cols_wcc:
        wcc_df[c] = pd.to_numeric(wcc_df[c], errors='coerce').fillna(0).astype(int)

    wcc_df['Total Points'] = wcc_df[circuit_cols_wcc].sum(axis=1)
    wcc_df = wcc_df.sort_values(by=['Total Points', circuit_col], ascending=[False, False]).reset_index(drop=True)
    ordered_wcc_cols = ['Team Name'] + circuit_cols_wcc + ['Total Points']
    wcc_df = wcc_df[ordered_wcc_cols]

    # Save ONLY at project root
    wcc_df.to_csv(wcc_path, index=False)

    print("\n" + "="*70)
    print(f"--- WORLD DRIVERS' CHAMPIONSHIP (WDC) STANDINGS AFTER {circuit_col.upper()} ---")
    print("="*70)
    print(wdc_df.to_string(index=False))

    print("\n" + "="*70)
    print(f"--- WORLD CONSTRUCTORS' CHAMPIONSHIP (WCC) STANDINGS AFTER {circuit_col.upper()} ---")
    print("="*70)
    print(wcc_df.to_string(index=False))

    print(f"\nChampionship Standings successfully updated (saved to project root):")
    print(f"  - WDC: {wdc_path}")
    print(f"  - WCC: {wcc_path}")

    return wdc_df, wcc_df

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
            use_enhanced = input("Use enhanced simulation features? (y/n): ").strip().lower() == 'y'
            
            save_individual_races = input("Save individual race results to CSVs? (y/n): ").strip().lower() == 'y'
            save_logs = input("Save detailed race logs to text files? (y/n): ").strip().lower() == 'y'
            
            race_results_output_dir = os.path.join(os.getcwd(), "outputs")
            print(f"All simulation outputs, logs, and replays will be saved under: {race_results_output_dir}/")

            show_logs = input("Show detailed race logs for each simulation? (y/n): ").strip().lower() == 'y'


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
                
                results_for_this_weather = run_monte_carlo_simulation(
                    current_weather_sims, chosen_circuit, weather_for_sim, 
                    race_entries_template, use_enhanced, race_results_output_dir, 
                    show_logs, save_logs, save_individual_races
                )
                all_sim_results_across_weathers.extend(results_for_this_weather)
            
            if all_sim_results_across_weathers:
                final_df = aggregate_results(all_sim_results_across_weathers, valid_drivers)
                print("\n" + "="*50)
                print("--- FINAL AGGREGATED RACE RESULTS (ALL WEATHER CONDITIONS) ---")
                print("="*50)
                print(final_df.to_string())
                
                agg_output_dir = os.path.join(race_results_output_dir, "results", "aggregated")
                os.makedirs(agg_output_dir, exist_ok=True)

                output_filename = f"SimResult_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs_AllWeather.csv"
                output_filepath = os.path.join(agg_output_dir, output_filename)
                final_df.to_csv(output_filepath, index=False)
                print(f"\nAggregated results saved to {output_filepath}")

                final_classification = generate_final_classification(final_df, len(valid_drivers))
                num_racers = len(final_classification)
                print("\n" + "="*50)
                print(f"--- FINAL P1-P{num_racers} RACE CLASSIFICATION ---")
                print("="*50)
                print(final_classification.to_string(index=False))
                
                classification_filename = f"Final_Classification_{chosen_circuit['name'].replace(' ', '')}_{total_simulations}runs.csv"
                classification_filepath = os.path.join(agg_output_dir, classification_filename)
                final_classification.to_csv(classification_filepath, index=False)
                print(f"\nFinal race classification saved to {classification_filepath}")

                # Update WDC and WCC Championship CSVs (Only at project root)
                update_championship_standings(final_classification, chosen_circuit['name'], valid_drivers, teams_data)