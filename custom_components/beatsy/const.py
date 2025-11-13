"""Constants for the Beatsy integration."""

DOMAIN: str = "beatsy"

# Game Configuration Defaults
DEFAULT_TIMER_DURATION: int = 30  # seconds
DEFAULT_YEAR_RANGE_MIN: int = 1950
DEFAULT_YEAR_RANGE_MAX: int = 2024
DEFAULT_EXACT_POINTS: int = 10  # Points for exact year guess
DEFAULT_CLOSE_POINTS: int = 5  # Points for ±2 years
DEFAULT_NEAR_POINTS: int = 2  # Points for ±5 years
DEFAULT_BET_MULTIPLIER: int = 2  # Multiplier when player bets
