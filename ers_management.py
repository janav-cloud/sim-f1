import random

# Defines the different ERS modes available to a car.
ERS_MODES = {
    'Standard': {'name': 'Standard', 'power_boost': 0, 'energy_drain': -0.02, 'duration_laps': 1}, # Negative drain is charging
    'Hotlap': {'name': 'Hotlap', 'power_boost': 8, 'energy_drain': 0.15, 'duration_laps': 1},
    'Overtake': {'name': 'Overtake', 'power_boost': 12, 'energy_drain': 0.25, 'duration_laps': 1},
    'Defend': {'name': 'Defend', 'power_boost': 6, 'energy_drain': 0.10, 'duration_laps': 2},
    'Charge': {'name': 'Charge', 'power_boost': -5, 'energy_drain': -0.10, 'duration_laps': 3}
}

def manage_ers(entry, current_lap, time_to_front, time_to_rear, circuit=None):
    # Manages ERS deployment strategy for a driver on a given lap.

    # If a special mode is active, check if its duration is over
    if entry.ers_mode['name'] != 'Standard' and current_lap > entry.ers_deployment_lap + entry.ers_mode['duration_laps']:
        entry.ers_mode = ERS_MODES['Standard']

    # Drain/charge battery based on current mode
    drain = entry.ers_mode['energy_drain']
    # If circuit has high braking demands, MGU-K energy harvesting (recharge) is slightly faster
    if circuit and drain < 0:
        drain *= (1.0 + (circuit.get('braking_demands', 0.7) - 0.5) * 0.4)

    entry.ers_charge = max(0.0, min(1.0, entry.ers_charge - drain))

    # Only make a new decision if in Standard mode
    if entry.ers_mode['name'] == 'Standard':
        # Recharge battery if it's low
        if entry.ers_charge < 0.25 and random.random() < 0.8:
            entry.ers_mode = ERS_MODES['Charge']
            entry.ers_deployment_lap = current_lap
            return

        # High chance to use Overtake mode if within DRS / passing range of car ahead
        if time_to_front < 0.8 and entry.ers_charge > 0.35 and random.random() < 0.75:
            entry.ers_mode = ERS_MODES['Overtake']
            entry.ers_deployment_lap = current_lap
            return
            
        # High chance to use Defend mode if car behind is right on gearbox
        if time_to_rear < 0.8 and entry.ers_charge > 0.30 and random.random() < 0.75:
            entry.ers_mode = ERS_MODES['Defend']
            entry.ers_deployment_lap = current_lap
            return

        # Use Hotlap mode if in clear air to build a gap
        if time_to_front > 2.5 and time_to_rear > 2.5 and entry.ers_charge > 0.65 and random.random() < 0.15:
            entry.ers_mode = ERS_MODES['Hotlap']
            entry.ers_deployment_lap = current_lap
            return