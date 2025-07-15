WEATHER_CONDITIONS = {
    "Dry": {
        "track_temp_celsius": 30,
        "air_temp_celsius": 25,
        "grip_multiplier": 1.0,
        "hp_multiplier": 1.0,
        "downforce_multiplier": 1.0,
        "tire_wear_modifier": 0.0,
        "driver_error_chance_modifier": 0.0,
        "variability": 0.05,  # Low chance of weather change
        "tire_type_recommendation": "dry",  # Standard dry tires (soft, medium, hard)
        "adaptability_modifier": 0.2  # Low benefit for adaptive strategies
    },
    "Light Rain": {
        "track_temp_celsius": 20,
        "air_temp_celsius": 18,
        "grip_multiplier": 0.7,
        "hp_multiplier": 0.95,
        "downforce_multiplier": 0.9,
        "tire_wear_modifier": -0.1,
        "driver_error_chance_modifier": 0.05,
        "variability": 0.3,  # Moderate chance of changing (e.g., to Heavy Rain or Dry)
        "tire_type_recommendation": "intermediate",  # Intermediate tires recommended
        "adaptability_modifier": 0.6  # Moderate benefit for adaptive strategies
    },
    "Heavy Rain": {
        "track_temp_celsius": 15,
        "air_temp_celsius": 15,
        "grip_multiplier": 0.4,
        "hp_multiplier": 0.8,
        "downforce_multiplier": 0.7,
        "tire_wear_modifier": -0.2,
        "driver_error_chance_modifier": 0.15,
        "variability": 0.4,  # High chance of weather shifts
        "tire_type_recommendation": "wet",  # Full wet tires required
        "adaptability_modifier": 0.8  # High benefit for adaptive strategies
    },
    "Hot": {
        "track_temp_celsius": 45,
        "air_temp_celsius": 35,
        "grip_multiplier": 0.95,
        "hp_multiplier": 0.98,
        "downforce_multiplier": 0.98,
        "tire_wear_modifier": 0.15,
        "driver_error_chance_modifier": 0.02,
        "variability": 0.1,  # Low to moderate chance of change
        "tire_type_recommendation": "dry",  # Dry tires, likely hard compounds
        "adaptability_modifier": 0.3  # Low to moderate benefit
    },
    "Cold": {
        "track_temp_celsius": 10,
        "air_temp_celsius": 8,
        "grip_multiplier": 0.9,
        "hp_multiplier": 1.0,
        "downforce_multiplier": 1.0,
        "tire_wear_modifier": -0.05,
        "driver_error_chance_modifier": 0.03,
        "variability": 0.2,  # Moderate chance of change
        "tire_type_recommendation": "dry",  # Dry tires, likely soft for grip
        "adaptability_modifier": 0.4  # Moderate benefit for adaptive strategies
    }
}