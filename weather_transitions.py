WEATHER_TRANSITIONS = {
    "Dry": {"Light Rain": 0.1, "Hot": 0.05, "Cold": 0.05},
    "Light Rain": {"Dry": 0.4, "Heavy Rain": 0.3, "Light Rain": 0.3}, # Can stay Light Rain
    "Heavy Rain": {"Light Rain": 0.6, "Dry": 0.1},
    "Hot": {"Dry": 0.2, "Hot": 0.8}, # Tends to stay Hot
    "Cold": {"Dry": 0.2, "Cold": 0.8} # Tends to stay Cold
}