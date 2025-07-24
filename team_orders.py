import random

def check_for_team_orders(front_driver, rear_driver, lap, total_laps, logger):
    # Decides if a team should issue a team order to swap driver positions.
    # No team orders in the first 5 laps or last 5 laps
    if lap < 5 or lap > total_laps - 5:
        return False

    time_diff = rear_driver.total_race_time_s - front_driver.total_race_time_s
    
    # Only consider if they are close
    if time_diff > 2.0:
        return False

    # Scenario 1: Rear driver is significantly faster (better tire wear or compound)
    rear_is_faster = (rear_driver.tire_wear < front_driver.tire_wear - 0.2) or \
                     (rear_driver.current_tire_compound == 'soft' and front_driver.current_tire_compound != 'soft')

    if rear_is_faster:
        # Higher acumen teams are more likely to make the call
        if rear_driver.effective_strategy_acumen > 0.7 and random.random() < 0.8:
            # NEW: Log the team order
            logger.log_team_order(lap, rear_driver.team_name, front_driver, rear_driver)
            return True

    # Scenario 2: Drivers are on different strategies and holding each other up
    front_stops = 1 if "1-Stop" in front_driver.assigned_strategy_type['name'] else 2
    rear_stops = 1 if "1-Stop" in rear_driver.assigned_strategy_type['name'] else 2
    
    if front_stops != rear_stops and time_diff < 1.0:
        if rear_driver.effective_strategy_acumen > 0.6 and random.random() < 0.5:
            # NEW: Log the team order
            logger.log_team_order(lap, rear_driver.team_name, front_driver, rear_driver)
            return True
            
    return False