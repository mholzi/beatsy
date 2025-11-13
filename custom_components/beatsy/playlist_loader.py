"""Playlist file loading and validation module.

This module provides functionality to:
- Scan playlists/ directory for JSON files
- Validate playlist JSON structure
- Return list of valid playlists for admin dropdown

Implemented in Story 3.3: Playlist Selection from JSON Files
"""
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def list_playlists(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Scan playlists/ directory and return valid playlists.

    Args:
        hass: Home Assistant instance (for future use if needed).

    Returns:
        List of playlist dictionaries with structure:
        [{"playlist_id": str, "name": str, "track_count": int, "file_path": str}]

    Note:
        Invalid playlists are excluded with warnings logged.
    """
    # Get playlists directory path
    module_dir = Path(__file__).parent
    playlists_dir = module_dir / "playlists"

    if not playlists_dir.exists():
        _LOGGER.warning("Playlists directory does not exist: %s", playlists_dir)
        return []

    playlists = []

    # Scan for *.json files
    for file_path in playlists_dir.glob("*.json"):
        try:
            # Load and parse JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate required fields
            errors = validate_playlist_json(data)
            if errors:
                _LOGGER.warning(
                    "Invalid playlist %s: %s", file_path.name, ", ".join(errors)
                )
                continue

            # Add to valid playlists list
            playlists.append(
                {
                    "playlist_id": data["playlist_id"],
                    "name": data["playlist_name"],
                    "track_count": len(data["songs"]),
                    "file_path": str(file_path.relative_to(module_dir)),
                }
            )
            _LOGGER.debug("Loaded valid playlist: %s (%d songs)", data["playlist_name"], len(data["songs"]))

        except json.JSONDecodeError as e:
            _LOGGER.error("Failed to parse JSON in %s: %s", file_path.name, str(e))
        except Exception as e:
            _LOGGER.error("Failed to load playlist %s: %s", file_path.name, str(e))

    _LOGGER.info("Found %d valid playlists in %s", len(playlists), playlists_dir)
    return playlists


def validate_playlist_json(data: dict[str, Any]) -> list[str]:
    """Validate playlist JSON structure.

    Args:
        data: Parsed JSON data from playlist file.

    Returns:
        List of error messages (empty list if valid).

    Validates:
        - Required playlist-level fields: playlist_name, playlist_id, songs
        - songs must be a list
        - Each song must have: spotify_uri, year
    """
    errors = []

    # Validate playlist-level fields
    if "playlist_name" not in data:
        errors.append("Missing field: playlist_name")
    elif not isinstance(data["playlist_name"], str):
        errors.append("playlist_name must be a string")

    if "playlist_id" not in data:
        errors.append("Missing field: playlist_id")
    elif not isinstance(data["playlist_id"], str):
        errors.append("playlist_id must be a string")

    if "songs" not in data:
        errors.append("Missing field: songs (must be array)")
    elif not isinstance(data["songs"], list):
        errors.append("songs must be an array")
    else:
        # Validate each song
        for i, song in enumerate(data["songs"]):
            if not isinstance(song, dict):
                errors.append(f"Song {i}: must be an object")
                continue

            if "spotify_uri" not in song:
                errors.append(f"Song {i}: Missing field: spotify_uri")
            elif not isinstance(song["spotify_uri"], str):
                errors.append(f"Song {i}: spotify_uri must be a string")

            if "year" not in song:
                errors.append(f"Song {i}: Missing field: year")
            elif not isinstance(song["year"], int):
                errors.append(f"Song {i}: year must be an integer")

    return errors


# ============================================================================
# Story 3.5: Additional Functions for Game Initialization
# ============================================================================


def load_playlist_file(playlists_dir: Path, playlist_id: str) -> dict[str, Any]:
    """
    Load and validate a specific playlist JSON file for game initialization.

    Story 3.5: Task 3 - Playlist Loading and Track Storage (AC-3)

    Args:
        playlists_dir: Path to directory containing playlist JSON files
        playlist_id: Playlist identifier (matches filename without .json extension)

    Returns:
        Parsed and validated playlist dict with structure:
        {
            "playlist_name": str,
            "playlist_id": str,
            "songs": list[dict] with each song having spotify_uri and year
        }

    Raises:
        FileNotFoundError: If playlist file doesn't exist at expected path
        ValueError: If playlist validation fails (missing fields, invalid JSON)

    Example:
        >>> playlist = load_playlist_file(Path("playlists"), "80s_hits")
        >>> print(f"{playlist['playlist_name']} has {len(playlist['songs'])} tracks")
        '80s Hits has 18 tracks'
    """
    # Construct file path
    playlist_path = playlists_dir / f"{playlist_id}.json"

    # Check file exists
    if not playlist_path.exists():
        _LOGGER.error("Playlist file not found: %s", playlist_path)
        raise FileNotFoundError(
            f"Playlist file '{playlist_id}.json' not found in {playlists_dir}"
        )

    # Read and parse JSON
    try:
        with playlist_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        _LOGGER.error("Invalid JSON in playlist %s: %s", playlist_id, e)
        raise ValueError(f"Playlist '{playlist_id}' contains invalid JSON: {e}")
    except Exception as e:
        _LOGGER.error("Error reading playlist %s: %s", playlist_id, e)
        raise ValueError(f"Failed to read playlist '{playlist_id}': {e}")

    # Validate playlist structure
    validation_errors = validate_playlist_json(data)
    if validation_errors:
        error_msg = f"Playlist '{playlist_id}' validation failed: {', '.join(validation_errors)}"
        _LOGGER.error(error_msg)
        raise ValueError(error_msg)

    _LOGGER.info(
        "Successfully loaded playlist '%s' with %d songs",
        data["playlist_name"],
        len(data["songs"]),
    )

    return data


def filter_songs_by_year(
    songs: list[dict[str, Any]], year_min: int, year_max: int
) -> list[dict[str, Any]]:
    """
    Filter songs to only include those within the specified year range (inclusive).

    Story 3.5: Task 3 - Playlist Loading and Track Storage (AC-3)
    Used during game initialization to apply year range filters from game settings.

    Args:
        songs: List of song dicts, each must have a 'year' field (integer)
        year_min: Minimum year (inclusive)
        year_max: Maximum year (inclusive)

    Returns:
        Filtered list of songs where year_min <= song['year'] <= year_max

    Note:
        Songs missing the 'year' field are excluded from results.
        Empty list is returned if no songs match the year range.

    Example:
        >>> songs = [
        ...     {"spotify_uri": "spotify:track:abc", "year": 1980},
        ...     {"spotify_uri": "spotify:track:def", "year": 1990},
        ...     {"spotify_uri": "spotify:track:ghi", "year": 2000}
        ... ]
        >>> filtered = filter_songs_by_year(songs, 1985, 1995)
        >>> len(filtered)
        1
        >>> filtered[0]['year']
        1990
    """
    # Filter songs within year range
    filtered = [
        song
        for song in songs
        if isinstance(song.get("year"), int) and year_min <= song["year"] <= year_max
    ]

    _LOGGER.info(
        "Filtered songs by year range [%d, %d]: %d total -> %d remaining",
        year_min,
        year_max,
        len(songs),
        len(filtered),
    )

    return filtered
