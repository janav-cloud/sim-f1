class TrackState:
    # Manages the state of the track surface, including rubber level and grip.
    def __init__(self):
        self.rubber_level = 0.0  # Range from 0.0 to 1.0
        self.max_grip_bonus = 0.015 # Max time reduction from full rubber

    def update_rubber(self, num_cars_on_track):
        # Increases the rubber on track each lap. Effect diminishes as track gets fully rubbered in.
        if self.rubber_level < 1.0:
            rubber_increase = (num_cars_on_track / 20) * 0.01 * (1.0 - self.rubber_level)
            self.rubber_level = min(1.0, self.rubber_level + rubber_increase)

    def handle_weather_change(self, weather_name):
        # Rain washes away the rubber on the track.
        if 'Rain' in weather_name:
            self.rubber_level *= 0.1 # Heavy rain washes most of it away
        elif weather_name == 'Light Rain':
            self.rubber_level *= 0.5 # Light rain has a smaller effect

    def get_grip_bonus(self):
        # Calculates the current grip bonus based on the rubber level.
        # This bonus is effectively a multiplier on grip, reducing lap time.
        return self.rubber_level * self.max_grip_bonus