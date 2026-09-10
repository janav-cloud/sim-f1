import random

def check_for_team_orders(front_driver, rear_driver, lap, total_laps, logger):
    # Decides if a team should issue a team order to swap driver positions.
    # No team orders in the first 4 laps or last 3 laps
    if lap < 4 or lap > total_laps - 3:
        return False

    time_diff = rear_driver.total_race_time_s - front_driver.total_race_time_s
    
    # Only consider if cars are in immediate proximity
    if time_diff > 2.0 or time_diff < 0:
        return False

    should_swap = False

    # Scenario 1: Front driver has sustained damage and is holding up teammate
    if front_driver.has_minor_damage and not rear_driver.has_minor_damage:
        if rear_driver.effective_strategy_acumen > 0.55 and random.random() < 0.90:
            should_swap = True

    # Scenario 2: Rear driver is significantly faster (better tire wear or softer compound)
    elif (rear_driver.tire_wear < front_driver.tire_wear - 0.15) or \
         (rear_driver.current_tire_compound == 'soft' and front_driver.current_tire_compound != 'soft'):
        if rear_driver.effective_strategy_acumen > 0.65 and random.random() < 0.80:
            should_swap = True

    # Scenario 3: Drivers are on different strategies and holding each other up
    elif time_diff < 1.0:
        front_stops = 1 if "1-Stop" in front_driver.assigned_strategy_type['name'] else 2
        rear_stops = 1 if "1-Stop" in rear_driver.assigned_strategy_type['name'] else 2
        if front_stops != rear_stops and rear_driver.effective_strategy_acumen > 0.60 and random.random() < 0.60:
            should_swap = True

    if should_swap:
        logger.log_team_order(lap, rear_driver.team_name, front_driver, rear_driver)
        # Morale adjustments: front driver is slightly dejected, rear driver is motivated
        front_driver.morale = max(0.85, front_driver.morale - 0.03)
        rear_driver.morale = min(1.15, rear_driver.morale + 0.03)
        return True
            
    return False