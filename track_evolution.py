class TrackState:
    """
    Manages the state of the track surface:
    - Rubber level & grip evolution (faster on green street circuits)
    - Surface wetness & drying line dynamics (cars displace water, enabling crossover)
    - Track grip multiplier
    """
    def __init__(self, track_type="Permanent", initial_weather="Dry"):
        # Green track starts with lower rubber; street circuits are very green initially
        if track_type == "Street Circuit":
            self.rubber_level = 0.08
            self.evolution_multiplier = 1.8  # Street circuits rubber in rapidly
        else:
            self.rubber_level = 0.20
            self.evolution_multiplier = 1.0  # Permanent circuits have more baseline rubber

        self.max_grip_bonus = 0.025  # Up to 2.5% time reduction as rubber builds
        
        # Surface wetness: 0.0 = bone dry, 0.4 = damp/drying, 0.7 = intermediate, 1.0 = heavy wet
        if initial_weather == "Heavy Rain":
            self.wetness_level = 1.0
        elif initial_weather == "Light Rain":
            self.wetness_level = 0.55
        else:
            self.wetness_level = 0.0

        self.has_dry_line = False

    def update_rubber(self, num_cars_on_track, current_weather="Dry", total_cars=None):
        """
        Increases rubber on track in dry conditions and clears standing water as cars circulate.
        Dynamically scales with any grid size (20, 22, 24, etc.).
        """
        grid_scale = max(1, total_cars) if total_cars else max(20, num_cars_on_track)
        # Rubber builds up in dry conditions
        if self.wetness_level < 0.15:
            if self.rubber_level < 1.0:
                rubber_increase = (num_cars_on_track / float(grid_scale)) * 0.015 * self.evolution_multiplier * (1.0 - self.rubber_level)
                self.rubber_level = min(1.0, self.rubber_level + rubber_increase)

        # Water clearing / drying line: cars circulating displace standing water
        if current_weather in ["Dry", "Hot", "Cold"]:
            if self.wetness_level > 0.0:
                water_cleared = (num_cars_on_track / float(grid_scale)) * 0.05
                self.wetness_level = max(0.0, self.wetness_level - water_cleared)
                self.has_dry_line = (0.05 < self.wetness_level < 0.35)
        elif current_weather == "Light Rain":
            self.wetness_level = min(0.65, self.wetness_level + 0.08)
            self.has_dry_line = False
        elif current_weather == "Heavy Rain":
            self.wetness_level = 1.0
            self.has_dry_line = False

    def handle_weather_change(self, weather_name):
        """Adjusts rubber and wetness levels when dynamic weather shifts occur."""
        if weather_name == 'Light Rain':
            self.rubber_level *= 0.5
            self.wetness_level = max(self.wetness_level, 0.50)
            self.has_dry_line = False
        elif 'Rain' in weather_name:
            self.rubber_level *= 0.1  # Heavy rain washes rubber off the racing line
            self.wetness_level = 1.0
            self.has_dry_line = False
        elif weather_name in ['Dry', 'Hot', 'Cold']:
            if self.wetness_level > 0.5:
                self.wetness_level = 0.45

    def get_grip_bonus(self):
        """
        Calculates the current grip bonus based on rubber level and track dampness.
        """
        if self.wetness_level > 0.25:
            return 0.0  # Wet track nullifies rubber grip bonus
        return self.rubber_level * self.max_grip_bonus * (1.0 - self.wetness_level)