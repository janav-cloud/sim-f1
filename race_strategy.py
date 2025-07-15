RACE_STRATEGY_TYPES = [
    {
        "name": "Aggressive Push (2-Stop)",
        "description": "Push hard from the start, prioritizing track position. Likely a 2-stop race on softer compounds. High risk of tire degradation but potential for strong pace.",
        "applies_acumen": "strategy_aggressive_acumen",
        "tire_compound_preference": {"soft": 0.6, "medium": 0.3, "hard": 0.1},  # Favor soft for speed
        "weather_adaptability": 0.3  # Moderate adaptability to weather changes
    },
    {
        "name": "Balanced Approach (2-Stop)",
        "description": "A standard 2-stop strategy aiming for consistent pace and managing tires. Adapts to race conditions. Best general approach.",
        "applies_acumen": "strategy_balanced_acumen",
        "tire_compound_preference": {"soft": 0.3, "medium": 0.5, "hard": 0.2},  # Balanced, medium-focused
        "weather_adaptability": 0.5  # Good adaptability
    },
    {
        "name": "Conservative Tire Save (1-Stop)",
        "description": "Focus on extreme tire preservation to attempt a 1-stop race. Sacrifices some pace for track position and fewer pit stops. High risk of being undercut or caught out by Safety Cars.",
        "applies_acumen": "strategy_conservative_acumen",
        "tire_compound_preference": {"soft": 0.1, "medium": 0.3, "hard": 0.6},  # Favor hard for durability
        "weather_adaptability": 0.2  # Low adaptability, focused on tire management
    },
    {
        "name": "Sprint to the Finish (3-Stop Aggressive)",
        "description": "An ultra-aggressive strategy with 3 or more pit stops. Push tires to their absolute limit, aiming for maximum pace. High risk of traffic and pit stop time loss.",
        "applies_acumen": "strategy_aggressive_acumen",
        "tire_compound_preference": {"soft": 0.7, "medium": 0.2, "hard": 0.1},  # Heavily favor soft
        "weather_adaptability": 0.3  # Moderate adaptability
    },
    {
        "name": "Underdog Gamble (Offset Strategy)",
        "description": "Attempting an unconventional pit stop window or tire compound choice to gain an advantage. High risk, but high reward potential for teams out of position.",
        "applies_acumen": "strategy_balanced_acumen",
        "tire_compound_preference": {"soft": 0.4, "medium": 0.3, "hard": 0.3},  # Flexible compound choice
        "weather_adaptability": 0.4  # Moderate adaptability for flexibility
    },
    {
        "name": "Safety Car Optimization (Opportunistic)",
        "description": "A strategy heavily reliant on reacting to Safety Car or Virtual Safety Car periods. Teams aim to pit during these periods to minimize time loss in the pits. Requires quick decision-making and preparedness.",
        "applies_acumen": "strategy_balanced_acumen",
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3},  # Flexible for opportunistic pits
        "weather_adaptability": 0.4  # Moderate adaptability
    },
    {
        "name": "Track Position Focus (Undercut/Overcut Play)",
        "description": "Primarily focused on gaining or maintaining track position through strategic pit stop timing relative to rivals. Involves either pitting earlier (undercut) or staying out longer (overcut) to gain time on fresh/older tires. Requires precise execution and understanding of tire warm-up/degradation.",
        "applies_acumen": "strategy_aggressive_acumen",
        "tire_compound_preference": {"soft": 0.5, "medium": 0.3, "hard": 0.2},  # Softer tires for undercut speed
        "weather_adaptability": 0.3  # Moderate adaptability
    },
    {
        "name": "Weather Dependent (Wet/Intermediate Play)",
        "description": "A flexible strategy designed for races with changing weather conditions (e.g., dry to wet, or vice-versa). Involves making timely calls for intermediate or full wet tires, which can dramatically alter race outcomes. High risk if the call is wrong.",
        "applies_acumen": "strategy_balanced_acumen",  # Changed to balanced for adaptive decision-making
        "tire_compound_preference": {"soft": 0.3, "medium": 0.4, "hard": 0.3},  # Flexible, weather-driven
        "weather_adaptability": 0.8  # High adaptability to weather changes
    },
    {
        "name": "Damage Limitation (Reactive)",
        "description": "When a car has sustained minor damage or the driver is struggling with pace/tires, this strategy focuses on minimizing loss of positions. May involve an earlier-than-planned pit stop, switching to harder compounds, or simply holding position. Reactive rather than proactive.",
        "applies_acumen": "strategy_conservative_acumen",
        "tire_compound_preference": {"soft": 0.1, "medium": 0.3, "hard": 0.6},  # Hard tires for reliability
        "weather_adaptability": 0.2  # Low adaptability, focused on survival
    },
    {
        "name": "Qualifying Tire Sacrifice (Strategic Start)",
        "description": "Deliberately sacrificing a strong qualifying performance (e.g., by not using the softest available tire in Q2) to start the race on a more durable tire compound, aiming for a longer first stint and potentially a different pit strategy. High risk of losing initial track position.",
        "applies_acumen": "strategy_conservative_acumen",
        "tire_compound_preference": {"soft": 0.1, "medium": 0.3, "hard": 0.6},  # Hard tires for long stints
        "weather_adaptability": 0.3  # Moderate adaptability
    },
]