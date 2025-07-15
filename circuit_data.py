CIRCUIT_DATA = [
    {
        "name": "Bahrain International Circuit",
        "track_type": "Permanent",
        "straight_speed_importance": 0.8,
        "cornering_importance": 0.6,
        "braking_demands": 0.9,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.6,
        "overtaking_difficulty": 0.7,
        "length_km": 5.412,
        "laps": 57,
        "weather_susceptibility": 0.2,  # Desert climate, low weather variability
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2}  # Medium preferred due to tire wear
    },
    {
        "name": "Jeddah Corniche Circuit",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.9,
        "cornering_importance": 0.7,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.6,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.6,
        "length_km": 6.174,
        "laps": 50,
        "weather_susceptibility": 0.1,  # Stable coastal climate
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}  # Softer tires viable due to lower wear
    },
    {
        "name": "Albert Park Circuit",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.6,
        "cornering_importance": 0.7,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.5,
        "length_km": 5.278,
        "laps": 58,
        "weather_susceptibility": 0.4,  # Melbourne can have variable weather
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2}
    },
    {
        "name": "Suzuka Circuit",
        "track_type": "Technical",
        "straight_speed_importance": 0.6,
        "cornering_importance": 0.9,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.9,
        "overtaking_difficulty": 0.4,
        "length_km": 5.807,
        "laps": 53,
        "weather_susceptibility": 0.5,  # Japan can have rain during race season
        "tire_compound_preference": {"soft": 0.2, "medium": 0.4, "hard": 0.4}  # Harder tires for high wear
    },
    {
        "name": "Shanghai International Circuit",
        "track_type": "Mixed",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.7,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.6,
        "length_km": 5.451,
        "laps": 56,
        "weather_susceptibility": 0.3,  # Moderate weather variability
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2}
    },
    {
        "name": "Miami International Autodrome",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.6,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.6,
        "downforce_sensitivity": 0.6,
        "overtaking_difficulty": 0.6,
        "length_km": 5.412,
        "laps": 57,
        "weather_susceptibility": 0.4,  # Florida's humid, variable weather
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}
    },
    {
        "name": "Autodromo Enzo e Dino Ferrari (Imola)",
        "track_type": "Technical",
        "straight_speed_importance": 0.5,
        "cornering_importance": 0.8,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.8,
        "overtaking_difficulty": 0.3,
        "length_km": 4.909,
        "laps": 63,
        "weather_susceptibility": 0.4,  # European circuit with some variability
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Circuit de Monaco",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.2,
        "cornering_importance": 0.9,
        "braking_demands": 0.5,
        "tire_wear_severity": 0.5,
        "downforce_sensitivity": 0.9,
        "overtaking_difficulty": 0.9,
        "length_km": 3.337,
        "laps": 78,
        "weather_susceptibility": 0.2,  # Mediterranean climate, stable
        "tire_compound_preference": {"soft": 0.5, "medium": 0.3, "hard": 0.2}  # Soft tires due to low wear
    },
    {
        "name": "Circuit Gilles Villeneuve",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.8,
        "cornering_importance": 0.6,
        "braking_demands": 0.8,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.5,
        "overtaking_difficulty": 0.7,
        "length_km": 4.361,
        "laps": 70,
        "weather_susceptibility": 0.5,  # Canada can have unpredictable weather
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2}
    },
    {
        "name": "Circuit de Barcelona-Catalunya",
        "track_type": "Technical",
        "straight_speed_importance": 0.6,
        "cornering_importance": 0.8,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.9,
        "overtaking_difficulty": 0.5,
        "length_km": 4.657,
        "laps": 66,
        "weather_susceptibility": 0.3,  # Stable Spanish climate
        "tire_compound_preference": {"soft": 0.2, "medium": 0.4, "hard": 0.4}
    },
    {
        "name": "Red Bull Ring",
        "track_type": "High-Speed",
        "straight_speed_importance": 0.8,
        "cornering_importance": 0.5,
        "braking_demands": 0.8,
        "tire_wear_severity": 0.6,
        "downforce_sensitivity": 0.5,
        "overtaking_difficulty": 0.7,
        "length_km": 4.318,
        "laps": 71,
        "weather_susceptibility": 0.4,  # Alpine region, some variability
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}
    },
    {
        "name": "Silverstone Circuit",
        "track_type": "High-Speed",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.7,
        "braking_demands": 0.8,
        "tire_wear_severity": 0.9,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.5,
        "length_km": 5.891,
        "laps": 52,
        "weather_susceptibility": 0.6,  # UK weather, highly variable
        "tire_compound_preference": {"soft": 0.2, "medium": 0.3, "hard": 0.5}  # Hard tires for high wear
    },
    {
        "name": "Hungaroring",
        "track_type": "Technical",
        "straight_speed_importance": 0.4,
        "cornering_importance": 0.9,
        "braking_demands": 0.6,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.9,
        "overtaking_difficulty": 0.3,
        "length_km": 4.381,
        "laps": 70,
        "weather_susceptibility": 0.4,  # Moderate variability in Hungary
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Circuit de Spa-Francorchamps",
        "track_type": "High-Speed",
        "straight_speed_importance": 0.9,
        "cornering_importance": 0.7,
        "braking_demands": 0.6,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.6,
        "overtaking_difficulty": 0.7,
        "length_km": 7.004,
        "laps": 44,
        "weather_susceptibility": 0.7,  # Notoriously variable Ardennes weather
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Circuit Zandvoort",
        "track_type": "Technical",
        "straight_speed_importance": 0.5,
        "cornering_importance": 0.9,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.8,
        "overtaking_difficulty": 0.3,
        "length_km": 4.259,
        "laps": 72,
        "weather_susceptibility": 0.5,  # Coastal, variable Dutch weather
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Autodromo Nazionale Monza",
        "track_type": "High-Speed",
        "straight_speed_importance": 0.9,
        "cornering_importance": 0.3,
        "braking_demands": 0.6,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.4,
        "overtaking_difficulty": 0.6,
        "length_km": 5.793,
        "laps": 53,
        "weather_susceptibility": 0.4,  # Northern Italy, some variability
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}
    },
    {
        "name": "Baku City Circuit",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.9,
        "cornering_importance": 0.5,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.5,
        "downforce_sensitivity": 0.6,
        "overtaking_difficulty": 0.8,
        "length_km": 6.003,
        "laps": 51,
        "weather_susceptibility": 0.3,  # Stable but occasional wind
        "tire_compound_preference": {"soft": 0.5, "medium": 0.3, "hard": 0.2}
    },
    {
        "name": "Marina Bay Street Circuit",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.3,
        "cornering_importance": 0.9,
        "braking_demands": 0.8,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.9,
        "overtaking_difficulty": 0.4,
        "length_km": 4.940,
        "laps": 62,
        "weather_susceptibility": 0.5,  # Tropical, rain possible
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Circuit of the Americas (COTA)",
        "track_type": "Mixed",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.8,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.8,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.6,
        "length_km": 5.513,
        "laps": 56,
        "weather_susceptibility": 0.4,  # Texas weather can vary
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Autodromo Hermanos Rodriguez",
        "track_type": "Permanent",
        "straight_speed_importance": 0.8,
        "cornering_importance": 0.6,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.6,
        "downforce_sensitivity": 0.5,
        "overtaking_difficulty": 0.6,
        "length_km": 4.304,
        "laps": 71,
        "weather_susceptibility": 0.3,  # High altitude, stable weather
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}
    },
    {
        "name": "Autodromo Jose Carlos Pace (Interlagos)",
        "track_type": "Mixed",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.7,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.7,
        "length_km": 4.309,
        "laps": 71,
        "weather_susceptibility": 0.6,  # Brazil, prone to rain
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3}
    },
    {
        "name": "Las Vegas Strip Circuit",
        "track_type": "Street Circuit",
        "straight_speed_importance": 0.9,
        "cornering_importance": 0.4,
        "braking_demands": 0.6,
        "tire_wear_severity": 0.5,
        "downforce_sensitivity": 0.4,
        "overtaking_difficulty": 0.7,
        "length_km": 6.201,
        "laps": 50,
        "weather_susceptibility": 0.2,  # Desert, stable weather
        "tire_compound_preference": {"soft": 0.5, "medium": 0.3, "hard": 0.2}
    },
    {
        "name": "Lusail International Circuit",
        "track_type": "High-Speed",
        "straight_speed_importance": 0.8,
        "cornering_importance": 0.6,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.7,
        "downforce_sensitivity": 0.6,
        "overtaking_difficulty": 0.6,
        "length_km": 5.419,
        "laps": 57,
        "weather_susceptibility": 0.2,  # Desert, stable weather
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2}
    },
    {
        "name": "Yas Marina Circuit",
        "track_type": "Mixed",
        "straight_speed_importance": 0.7,
        "cornering_importance": 0.7,
        "braking_demands": 0.7,
        "tire_wear_severity": 0.6,
        "downforce_sensitivity": 0.7,
        "overtaking_difficulty": 0.6,
        "length_km": 5.281,
        "laps": 58,
        "weather_susceptibility": 0.1,  # Desert, very stable
        "tire_compound_preference": {"soft": 0.4, "medium": 0.4, "hard": 0.2}
    },
]