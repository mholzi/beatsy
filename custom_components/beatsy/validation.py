"""Input validation and sanitization for Beatsy.

This module provides validation functions for all user inputs to prevent:
- XSS attacks via HTML/script injection
- Invalid data types and ranges
- Malformed Spotify URIs
- Out-of-bounds numeric values

All validation functions return ValidationResult with:
- valid: bool (True if input passes validation)
- error_message: Optional[str] (Human-readable error if validation fails)
- sanitized_value: Optional[Any] (Cleaned/normalized value ready for storage)

Security principles:
- Server-side validation is authoritative (never trust client)
- HTML escape all user content before storage
- Reject dangerous patterns (script tags, HTML entities)
- Normalize inputs to canonical format
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class ValidationResult:
    """Result of input validation.

    Attributes:
        valid: True if input passes validation rules
        error_message: Human-readable error message (None if valid)
        sanitized_value: Cleaned/normalized value ready for storage (None if invalid)
    """
    valid: bool
    error_message: Optional[str] = None
    sanitized_value: Optional[Any] = None


def sanitize_html(input_str: str) -> str:
    """Escape HTML entities to prevent XSS attacks.

    Converts dangerous characters to HTML entities:
    - < becomes &lt;
    - > becomes &gt;
    - & becomes &amp;
    - " becomes &quot;
    - ' becomes &#x27;

    Args:
        input_str: User-provided string that may contain HTML

    Returns:
        HTML-escaped string safe for storage and display

    Example:
        >>> sanitize_html("<script>alert('XSS')</script>")
        "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
    """
    return html.escape(input_str, quote=True)


def validate_player_name(name: str) -> ValidationResult:
    """Validate and sanitize player name input.

    Validation rules:
    - Length: 1-20 characters (after stripping whitespace)
    - Characters: Alphanumeric, spaces, hyphens, underscores only
    - No HTML tags: Reject strings containing < > &
    - No script content: Reject strings containing 'script' or 'javascript' (case-insensitive)

    Args:
        name: Raw player name from user input

    Returns:
        ValidationResult with:
        - valid=True and sanitized_value=cleaned name if passes
        - valid=False and error_message if fails

    Examples:
        >>> validate_player_name("Alice")
        ValidationResult(valid=True, error_message=None, sanitized_value="Alice")

        >>> validate_player_name("<script>alert('XSS')</script>")
        ValidationResult(valid=False, error_message="Player name contains invalid characters", sanitized_value=None)

        >>> validate_player_name("A" * 25)
        ValidationResult(valid=False, error_message="Player name must be between 1 and 20 characters", sanitized_value=None)
    """
    # Strip leading/trailing whitespace
    name = name.strip()

    # Check length (1-20 characters)
    if not name or len(name) > 20:
        return ValidationResult(
            valid=False,
            error_message="Player name must be between 1 and 20 characters",
            sanitized_value=None,
        )

    # Check for HTML tags (< > &)
    if any(char in name for char in ['<', '>', '&']):
        return ValidationResult(
            valid=False,
            error_message="Player name contains invalid characters",
            sanitized_value=None,
        )

    # Check for script content (case-insensitive)
    name_lower = name.lower()
    if 'script' in name_lower or 'javascript' in name_lower:
        return ValidationResult(
            valid=False,
            error_message="Player name contains invalid content",
            sanitized_value=None,
        )

    # Check for allowed characters: alphanumeric, spaces, hyphens, underscores
    # Pattern: ^[a-zA-Z0-9 _-]+$
    if not re.match(r'^[a-zA-Z0-9 _-]+$', name):
        return ValidationResult(
            valid=False,
            error_message="Player name can only contain letters, numbers, spaces, hyphens, and underscores",
            sanitized_value=None,
        )

    # Sanitize: HTML escape for additional safety
    sanitized = sanitize_html(name)

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=sanitized,
    )


def validate_year_guess(year: Any, min_year: int, max_year: int) -> ValidationResult:
    """Validate year guess input.

    Validation rules:
    - Type: Must be integer (or convertible to integer)
    - Range: Between min_year and max_year (inclusive)

    Args:
        year: User-provided year guess (may be int, str, or other)
        min_year: Minimum allowed year (from game config)
        max_year: Maximum allowed year (from game config)

    Returns:
        ValidationResult with:
        - valid=True and sanitized_value=int(year) if passes
        - valid=False and error_message if fails

    Examples:
        >>> validate_year_guess(1995, 1950, 2024)
        ValidationResult(valid=True, error_message=None, sanitized_value=1995)

        >>> validate_year_guess("2000", 1950, 2024)
        ValidationResult(valid=True, error_message=None, sanitized_value=2000)

        >>> validate_year_guess(2050, 1950, 2024)
        ValidationResult(valid=False, error_message="Year must be between 1950 and 2024", sanitized_value=None)

        >>> validate_year_guess("abc", 1950, 2024)
        ValidationResult(valid=False, error_message="Year must be a valid integer", sanitized_value=None)
    """
    # Try to convert to integer
    try:
        year_int = int(year)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            error_message="Year must be a valid integer",
            sanitized_value=None,
        )

    # Check range
    if year_int < min_year or year_int > max_year:
        return ValidationResult(
            valid=False,
            error_message=f"Year must be between {min_year} and {max_year}",
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=year_int,
    )


def validate_spotify_uri(uri: str) -> ValidationResult:
    """Validate and normalize Spotify playlist URI.

    Accepts two formats:
    1. Spotify URI: spotify:playlist:xxxxx
    2. HTTPS URL: https://open.spotify.com/playlist/xxxxx

    Normalizes to: spotify:playlist:ID

    Validation rules:
    - Must match one of the two formats
    - Playlist ID must contain only alphanumeric characters
    - Final URI must match pattern: ^spotify:playlist:[a-zA-Z0-9]+$

    Args:
        uri: Raw Spotify playlist URI or URL from user input

    Returns:
        ValidationResult with:
        - valid=True and sanitized_value=normalized URI if passes
        - valid=False and error_message if fails

    Examples:
        >>> validate_spotify_uri("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
        ValidationResult(valid=True, error_message=None, sanitized_value="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")

        >>> validate_spotify_uri("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        ValidationResult(valid=True, error_message=None, sanitized_value="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")

        >>> validate_spotify_uri("invalid")
        ValidationResult(valid=False, error_message="Invalid Spotify playlist URI format", sanitized_value=None)
    """
    uri = uri.strip()

    # Try to parse as Spotify URI format
    if uri.startswith("spotify:playlist:"):
        playlist_id = uri.replace("spotify:playlist:", "")
    # Try to parse as HTTPS URL format
    elif uri.startswith("https://open.spotify.com/playlist/"):
        # Extract playlist ID from URL
        # Format: https://open.spotify.com/playlist/ID or https://open.spotify.com/playlist/ID?...
        playlist_id = uri.replace("https://open.spotify.com/playlist/", "")
        # Remove query parameters if present
        if "?" in playlist_id:
            playlist_id = playlist_id.split("?")[0]
    else:
        return ValidationResult(
            valid=False,
            error_message="Invalid Spotify playlist URI format. Use 'spotify:playlist:ID' or 'https://open.spotify.com/playlist/ID'",
            sanitized_value=None,
        )

    # Validate playlist ID contains only alphanumeric characters
    if not re.match(r'^[a-zA-Z0-9]+$', playlist_id):
        return ValidationResult(
            valid=False,
            error_message="Invalid Spotify playlist ID. Must contain only letters and numbers",
            sanitized_value=None,
        )

    # Construct normalized URI
    normalized_uri = f"spotify:playlist:{playlist_id}"

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=normalized_uri,
    )


def validate_timer_duration(duration: Any) -> ValidationResult:
    """Validate timer duration setting.

    Validation rules:
    - Type: Must be integer (or convertible to integer)
    - Range: 10-120 seconds

    Args:
        duration: Timer duration in seconds

    Returns:
        ValidationResult with valid=True/False and error message
    """
    try:
        duration_int = int(duration)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            error_message="Timer duration must be a valid integer",
            sanitized_value=None,
        )

    if duration_int < 10 or duration_int > 120:
        return ValidationResult(
            valid=False,
            error_message="Timer duration must be between 10 and 120 seconds",
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=duration_int,
    )


def validate_year_range(min_year: Any, max_year: Any) -> ValidationResult:
    """Validate year range settings.

    Validation rules:
    - Type: Both must be integers (or convertible to integer)
    - Range: Both between 1900 and current year
    - Logic: max_year must be > min_year

    Args:
        min_year: Minimum year for game
        max_year: Maximum year for game

    Returns:
        ValidationResult with valid=True/False and error message
    """
    current_year = datetime.now().year

    try:
        min_int = int(min_year)
        max_int = int(max_year)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            error_message="Year range values must be valid integers",
            sanitized_value=None,
        )

    if min_int < 1900 or min_int > current_year:
        return ValidationResult(
            valid=False,
            error_message=f"Minimum year must be between 1900 and {current_year}",
            sanitized_value=None,
        )

    if max_int < 1900 or max_int > current_year:
        return ValidationResult(
            valid=False,
            error_message=f"Maximum year must be between 1900 and {current_year}",
            sanitized_value=None,
        )

    if max_int <= min_int:
        return ValidationResult(
            valid=False,
            error_message="Maximum year must be greater than minimum year",
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=(min_int, max_int),
    )


def validate_scoring_points(points: Any, points_type: str) -> ValidationResult:
    """Validate scoring points setting.

    Validation rules:
    - Type: Must be integer (or convertible to integer)
    - Range: Must be > 0

    Args:
        points: Points value (exact_points, close_points, near_points)
        points_type: Type of points for error message (e.g., "exact", "close", "near")

    Returns:
        ValidationResult with valid=True/False and error message
    """
    try:
        points_int = int(points)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            error_message=f"{points_type.capitalize()} points must be a valid integer",
            sanitized_value=None,
        )

    if points_int <= 0:
        return ValidationResult(
            valid=False,
            error_message=f"{points_type.capitalize()} points must be greater than 0",
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=points_int,
    )


def validate_bet_multiplier(multiplier: Any) -> ValidationResult:
    """Validate bet multiplier setting.

    Validation rules:
    - Type: Must be integer or float (or convertible)
    - Range: Must be > 1

    Args:
        multiplier: Bet multiplier value

    Returns:
        ValidationResult with valid=True/False and error message
    """
    try:
        # Try float first (accepts both int and float)
        multiplier_float = float(multiplier)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            error_message="Bet multiplier must be a valid number",
            sanitized_value=None,
        )

    if multiplier_float <= 1:
        return ValidationResult(
            valid=False,
            error_message="Bet multiplier must be greater than 1",
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=multiplier_float,
    )


def validate_game_settings(config: dict) -> ValidationResult:
    """Validate all game settings in config dictionary.

    Validates:
    - timer_duration: 10-120 seconds
    - year_range_min: 1900-2024
    - year_range_max: 1900-2024, > year_range_min
    - exact_points: > 0
    - close_points: > 0
    - near_points: > 0
    - bet_multiplier: > 1

    Args:
        config: Game configuration dictionary

    Returns:
        ValidationResult with:
        - valid=True and sanitized_value=validated config dict if all pass
        - valid=False and error_message listing all errors if any fail
    """
    errors = []
    sanitized_config = {}

    # Validate timer duration
    if "timer_duration" in config:
        result = validate_timer_duration(config["timer_duration"])
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["timer_duration"] = result.sanitized_value

    # Validate year range
    if "year_range_min" in config and "year_range_max" in config:
        result = validate_year_range(config["year_range_min"], config["year_range_max"])
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["year_range_min"], sanitized_config["year_range_max"] = result.sanitized_value

    # Validate scoring points
    if "exact_points" in config:
        result = validate_scoring_points(config["exact_points"], "exact")
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["exact_points"] = result.sanitized_value

    if "close_points" in config:
        result = validate_scoring_points(config["close_points"], "close")
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["close_points"] = result.sanitized_value

    if "near_points" in config:
        result = validate_scoring_points(config["near_points"], "near")
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["near_points"] = result.sanitized_value

    # Validate bet multiplier
    if "bet_multiplier" in config:
        result = validate_bet_multiplier(config["bet_multiplier"])
        if not result.valid:
            errors.append(result.error_message)
        else:
            sanitized_config["bet_multiplier"] = result.sanitized_value

    if errors:
        return ValidationResult(
            valid=False,
            error_message="; ".join(errors),
            sanitized_value=None,
        )

    return ValidationResult(
        valid=True,
        error_message=None,
        sanitized_value=sanitized_config,
    )
