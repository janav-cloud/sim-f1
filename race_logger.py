class RaceLogger:
    # A simple class to handle logging of race events.
    def __init__(self):
        self.logs = []

    def log(self, lap, event_type, message):
        # Generic log method to append a new log entry.
        self.logs.append({'lap': lap, 'type': event_type, 'message': message})

    def log_overtake(self, lap, overtaking_driver, overtaken_driver):
        # Logs a successful overtake.
        self.log(lap, 'Overtake', f"{overtaking_driver.driver_name} has overtaken {overtaken_driver.driver_name} for P{overtaken_driver.current_position}.")

    def log_pit_stop(self, lap, entry, stationary_time, new_tires, total_pit_loss=None):
        # Logs a pit stop event with realistic stationary stop time and total pit lane loss.
        if total_pit_loss is not None:
            self.log(lap, 'Pit Stop', f"{entry.driver_name} pits from P{entry.current_position}. Stop: {stationary_time:.2f}s ({total_pit_loss:.1f}s pit loss). New tires: {new_tires.capitalize()}.")
        else:
            self.log(lap, 'Pit Stop', f"{entry.driver_name} pits from P{entry.current_position}. Stop: {stationary_time:.2f}s. New tires: {new_tires.capitalize()}.")

    def log_pit_error(self, lap, entry, duration):
        # Logs a pit stop event.
        self.log(lap, 'Pit Stop Error', f"{entry.driver_name} pits from P{entry.current_position}. Error time: {duration:.2f}s.")

    def log_dnf(self, lap, entry):
        # Logs a driver not finishing the race.
        self.log(lap, 'DNF', f"{entry.driver_name} is out of the race from P{entry.current_position}. Reason: {entry.dnf_reason}.")

    def log_safety_car(self, lap, reason="an incident"):
        # Logs the deployment of the Safety Car.
        self.log(lap, 'Safety Car', f"Safety Car deployed due to {reason}.")
        
    def log_safety_car_ends(self, lap):
        # Logs when the Safety Car is coming into the pits.
        self.log(lap, 'Safety Car', "Safety Car in this lap. Racing will resume next lap.")

    def log_vsc(self, lap, reason="an incident"):
        # Logs Virtual Safety Car deployment.
        self.log(lap, 'Virtual Safety Car', f"Virtual Safety Car (VSC) deployed due to {reason}. Delta times active.")

    def log_vsc_ends(self, lap):
        # Logs when Virtual Safety Car ends.
        self.log(lap, 'Virtual Safety Car', "Track clear. Virtual Safety Car ending. Track is green.")

    def log_blue_flag(self, lap, entry):
        # Logs when a backmarker is shown blue flags to let leaders through.
        self.log(lap, 'Blue Flag', f"{entry.driver_name} (P{entry.current_position}) shown blue flags for approaching leader.")

    def log_double_stack(self, lap, entry, wait_time):
        # Logs when a driver has to wait for a teammate in a double stack pit stop.
        self.log(lap, 'Pit Stop Error', f"{entry.driver_name} double-stacked behind teammate! Delayed by {wait_time:.2f}s in pit box.")

    def log_weather_change(self, lap, new_weather):
        # Logs a change in weather conditions.
        self.log(lap, 'Weather', f"The weather has changed to {new_weather}.")
        
    def log_team_order(self, lap, team_name, front_driver, rear_driver):
        # Logs a team order instruction.
        self.log(lap, 'Team Order', f"Team {team_name} has instructed {front_driver.driver_name} to let {rear_driver.driver_name} pass.")