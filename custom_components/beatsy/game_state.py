"""
Game state management for Beatsy.

This module provides type-safe, in-memory state management using Python 3.11+
dataclasses and type hints. All state is stored in hass.data[DOMAIN][entry_id].

Thread Safety:
- Home Assistant runs on asyncio (single-threaded event loop)
- All state access is inherently thread-safe within async context
- State mutations are atomic Python operations (list.append, dict update)
- No locks required for typical game state operations

Performance:
- In-memory only (no database I/O)
- State operations complete in <1ms
- Active game state resets on HA restart (by design)
- Admin config persists via hass.helpers.storage
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Storage configuration for config persistence
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.config"

# Song selection concurrency lock (Story 5.1, AC-6)
_song_selection_lock = asyncio.Lock()


# ============================================================================
# Custom Exceptions
# ============================================================================


class PlaylistExhaustedError(Exception):
    """Raised when all songs have been played and available_songs is empty.

    This exception includes an error code for WebSocket error responses.
    Attributes:
        code: Error code "playlist_exhausted" for API responses.
        message: Human-readable error message.
    """

    def __init__(self, message: str = "All songs have been played. Please reset the game or load a new playlist."):
        self.code = "playlist_exhausted"
        self.message = message
        super().__init__(message)


# ============================================================================
# Type Definitions
# ============================================================================


class GameConfig(TypedDict, total=False):
    """Game configuration settings.

    TypedDict with total=False allows all fields to be optional,
    providing flexibility for partial configuration updates.
    """

    playlist_uri: str
    media_player_entity_id: str
    round_timer_seconds: int
    points_exact: int
    points_close: int
    points_near: int
    points_bet_multiplier: float


@dataclass
class Player:
    """Player data model.

    Represents a single player in the game with their score and history.
    """

    name: str
    original_name: str = ""  # Name as originally submitted by player
    session_id: str = ""
    score: int = 0
    is_admin: bool = False
    guesses: list[int] = field(default_factory=list)
    bets_placed: list[bool] = field(default_factory=list)
    joined_at: float = field(default_factory=time.time)
    connected: bool = True  # Story 4.4: Track connection status
    last_activity: float = field(default_factory=time.time)  # Story 4.4: For session expiration


@dataclass
class RoundState:
    """Current round state.

    Represents the active round with track information and player guesses.
    """

    round_number: int
    track_uri: str
    track_name: str
    track_artist: str
    correct_year: int
    guesses: dict[str, dict[str, Any]] = field(default_factory=dict)  # player_name -> {year, bet, submitted_at}
    status: str = "active"  # active, ended
    timer_started_at: Optional[float] = None
    started_at: float = field(default_factory=time.time)


@dataclass
class BeatsyGameState:
    """Complete game state structure.

    This is the root state object stored in hass.data[DOMAIN][entry_id].
    All game state is accessed through this object.
    """

    game_config: GameConfig = field(default_factory=dict)
    players: list[Player] = field(default_factory=list)
    current_round: Optional[RoundState] = None
    played_songs: list[dict[str, Any]] = field(default_factory=list)  # Story 5.1: Full song dicts, not just URIs
    available_songs: list[dict[str, Any]] = field(default_factory=list)
    websocket_connections: dict[str, Any] = field(default_factory=dict)
    game_started: bool = False
    game_started_at: Optional[float] = None
    spotify: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# State Initialization
# ============================================================================


def init_game_state(hass: HomeAssistant, entry_id: str) -> BeatsyGameState:
    """Initialize game state in hass.data[DOMAIN][entry_id].

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID for this Beatsy instance.

    Returns:
        The initialized BeatsyGameState object.
    """
    state = BeatsyGameState()

    # Ensure domain exists
    hass.data.setdefault(DOMAIN, {})

    # Store state for this entry
    hass.data[DOMAIN][entry_id] = state

    _LOGGER.debug("Game state initialized for entry %s", entry_id)
    return state


def get_game_state(hass: HomeAssistant, entry_id: Optional[str] = None) -> BeatsyGameState:
    """Get game state for a specific entry.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, returns first entry's state.

    Returns:
        The BeatsyGameState object for this entry.

    Raises:
        ValueError: If state is not initialized for this entry.
    """
    if DOMAIN not in hass.data:
        raise ValueError(f"{DOMAIN} not initialized in hass.data")

    # If no entry_id specified, get first entry (backward compatibility)
    if entry_id is None:
        entries = list(hass.data[DOMAIN].values())
        if not entries:
            raise ValueError(f"No {DOMAIN} entries found in hass.data")
        state = entries[0]
    else:
        if entry_id not in hass.data[DOMAIN]:
            raise ValueError(f"Game state not initialized for entry {entry_id}")
        state = hass.data[DOMAIN][entry_id]

    # Handle migration from dict to BeatsyGameState
    if isinstance(state, dict):
        entry_id_str = entry_id or list(hass.data[DOMAIN].keys())[0]
        _LOGGER.warning(
            "Migrating legacy dict state to BeatsyGameState for entry %s", entry_id_str
        )
        # Convert legacy dict state to BeatsyGameState
        new_state = BeatsyGameState(
            game_config=state.get("game_config", {}),
            players=[
                Player(
                    name=p.get("name", ""),
                    original_name=p.get("original_name", p.get("name", "")),
                    session_id=p.get("session_id", ""),
                    score=p.get("score", 0),
                    is_admin=p.get("is_admin", False),
                    guesses=p.get("guesses", []),
                    bets_placed=p.get("bets_placed", []),
                    joined_at=p.get("joined_at", time.time()),
                )
                if isinstance(p, dict)
                else p
                for p in state.get("players", [])
            ],
            current_round=state.get("current_round"),
            played_songs=state.get("played_songs", []),
            available_songs=state.get("available_songs", []),
            websocket_connections=state.get("websocket_connections", {}),
            game_started=state.get("game_started", False),
            game_started_at=state.get("game_started_at"),
            spotify=state.get("spotify", {}),
        )
        hass.data[DOMAIN][entry_id_str] = new_state
        return new_state

    return state


# ============================================================================
# Config Accessor Functions
# ============================================================================


def get_game_config(hass: HomeAssistant, entry_id: Optional[str] = None) -> GameConfig:
    """Get game configuration.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        The current game configuration.
    """
    state = get_game_state(hass, entry_id)
    return state.game_config


def update_game_config(
    hass: HomeAssistant, config: GameConfig, entry_id: Optional[str] = None
) -> None:
    """Update game configuration.

    Args:
        hass: The Home Assistant instance.
        config: The configuration updates to apply.
        entry_id: The config entry ID. If None, uses first entry.

    Raises:
        ValueError: If configuration values are invalid.
    """
    state = get_game_state(hass, entry_id)

    # Validate config values
    if "round_timer_seconds" in config:
        if config["round_timer_seconds"] < 1:
            raise ValueError("round_timer_seconds must be positive")

    if "points_exact" in config:
        if config["points_exact"] < 0:
            raise ValueError("points_exact cannot be negative")

    if "points_close" in config:
        if config["points_close"] < 0:
            raise ValueError("points_close cannot be negative")

    if "points_near" in config:
        if config["points_near"] < 0:
            raise ValueError("points_near cannot be negative")

    if "points_bet_multiplier" in config:
        if config["points_bet_multiplier"] <= 0:
            raise ValueError("points_bet_multiplier must be positive")

    # Update state (atomic operation - dict.update is thread-safe in async context)
    state.game_config.update(config)

    _LOGGER.debug("Game config updated: %s", config)


# ============================================================================
# Player Accessor Functions
# ============================================================================


def get_players(hass: HomeAssistant, entry_id: Optional[str] = None) -> list[Player]:
    """Get all players.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        List of all players.
    """
    state = get_game_state(hass, entry_id)
    return state.players


def add_player(
    hass: HomeAssistant,
    player_name: str,
    session_id: str = "",
    is_admin: bool = False,
    original_name: str = "",
    entry_id: Optional[str] = None,
) -> None:
    """Add a new player.

    Args:
        hass: The Home Assistant instance.
        player_name: The player's name (adjusted if duplicate).
        session_id: The player's session ID (optional).
        is_admin: Whether the player is an admin.
        original_name: The name as originally submitted by player.
        entry_id: The config entry ID. If None, uses first entry.

    Raises:
        ValueError: If player name already exists.
    """
    state = get_game_state(hass, entry_id)

    # Check for duplicate name
    if any(p.name == player_name for p in state.players):
        raise ValueError(f"Player '{player_name}' already exists")

    # Create player object
    player = Player(
        name=player_name,
        original_name=original_name if original_name else player_name,
        session_id=session_id,
        is_admin=is_admin,
    )

    # Add player (atomic operation - list.append is thread-safe in async context)
    state.players.append(player)

    _LOGGER.debug("Player added: %s (session: %s)", player_name, session_id)


def get_player(
    hass: HomeAssistant, name: str, entry_id: Optional[str] = None
) -> Optional[Player]:
    """Get player by name.

    Args:
        hass: The Home Assistant instance.
        name: The player name to find.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        The Player object if found, None otherwise.
    """
    state = get_game_state(hass, entry_id)
    return next((p for p in state.players if p.name == name), None)


def find_player_by_session(
    hass: HomeAssistant, session_id: str, entry_id: Optional[str] = None
) -> Optional[Player]:
    """Find player by session ID (Story 4.4).

    Used for reconnection flow to look up player by their session_id
    instead of name. Enables seamless reconnection without losing
    player identity and score.

    Args:
        hass: The Home Assistant instance.
        session_id: The player's session ID (UUID).
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        The Player object if found, None otherwise.
    """
    state = get_game_state(hass, entry_id)
    return next((p for p in state.players if p.session_id == session_id), None)


def update_player_score(
    hass: HomeAssistant,
    player_name: str,
    points: int,
    entry_id: Optional[str] = None,
) -> None:
    """Update player score.

    Args:
        hass: The Home Assistant instance.
        player_name: The name of the player to update.
        points: The points to add (can be negative).
        entry_id: The config entry ID. If None, uses first entry.

    Raises:
        ValueError: If player is not found.
    """
    player = get_player(hass, player_name, entry_id)
    if player is None:
        raise ValueError(f"Player '{player_name}' not found")

    # Update score (atomic operation - int assignment is thread-safe in async context)
    player.score += points

    _LOGGER.debug(
        "Player %s score updated: +%d = %d",
        player_name,
        points,
        player.score,
    )


def reset_players(hass: HomeAssistant, entry_id: Optional[str] = None) -> None:
    """Reset all players (clear player list).

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Clear players (atomic operation - list.clear is thread-safe in async context)
    state.players.clear()

    _LOGGER.debug("Players reset")


# ============================================================================
# Round Accessor Functions
# ============================================================================


def get_current_round(
    hass: HomeAssistant, entry_id: Optional[str] = None
) -> Optional[RoundState]:
    """Get current round state.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        The current RoundState if active, None otherwise.
    """
    state = get_game_state(hass, entry_id)
    return state.current_round


def set_current_round(
    hass: HomeAssistant, round_state: RoundState, entry_id: Optional[str] = None
) -> None:
    """Set current round state.

    Args:
        hass: The Home Assistant instance.
        round_state: The round state to set.
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Set round (atomic operation - object assignment is thread-safe in async context)
    state.current_round = round_state

    # Set timer start time if not already set
    if round_state.timer_started_at is None:
        round_state.timer_started_at = time.time()

    _LOGGER.debug(
        "Round %d started: %s",
        round_state.round_number,
        round_state.track_name,
    )


def clear_current_round(hass: HomeAssistant, entry_id: Optional[str] = None) -> None:
    """Clear current round (round ended).

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Clear round (atomic operation - assignment is thread-safe in async context)
    state.current_round = None

    _LOGGER.debug("Current round cleared")


def add_guess(
    hass: HomeAssistant,
    player_name: str,
    year_guess: int,
    bet_placed: bool = False,
    entry_id: Optional[str] = None,
) -> None:
    """Add player guess to current round.

    Args:
        hass: The Home Assistant instance.
        player_name: The name of the player making the guess.
        year_guess: The year being guessed.
        bet_placed: Whether the player placed a bet.
        entry_id: The config entry ID. If None, uses first entry.

    Raises:
        ValueError: If no active round or round is not active.
    """
    round_state = get_current_round(hass, entry_id)

    if round_state is None:
        raise ValueError("No active round")

    if round_state.status != "active":
        raise ValueError("Round is not active")

    # Add guess (atomic operation - dict assignment is thread-safe in async context)
    round_state.guesses[player_name] = {
        "year": year_guess,
        "bet": bet_placed,
        "submitted_at": time.time(),
    }

    _LOGGER.debug(
        "Guess recorded: %s -> %d (bet: %s)", player_name, year_guess, bet_placed
    )


def update_bet(
    hass: HomeAssistant,
    player_name: str,
    bet: bool,
    entry_id: Optional[str] = None,
) -> None:
    """Update player bet status for current round.

    Args:
        hass: The Home Assistant instance.
        player_name: The name of the player placing the bet.
        bet: Whether the player is betting on their guess.
        entry_id: The config entry ID. If None, uses first entry.

    Raises:
        ValueError: If no active round or round is not active.
    """
    round_state = get_current_round(hass, entry_id)

    if round_state is None:
        raise ValueError("No active round")

    if round_state.status != "active":
        raise ValueError("Round is not active")

    # Update or create guess entry with bet status
    if player_name in round_state.guesses:
        round_state.guesses[player_name]["bet"] = bet
    else:
        # Create placeholder guess with bet status
        round_state.guesses[player_name] = {
            "year": None,
            "bet": bet,
            "updated_at": time.time(),
        }

    _LOGGER.debug("Bet updated: %s -> %s", player_name, bet)


# ============================================================================
# Song History Functions
# ============================================================================


def get_played_songs(hass: HomeAssistant, entry_id: Optional[str] = None) -> list[str]:
    """Get list of played song URIs.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        List of played song URIs.
    """
    state = get_game_state(hass, entry_id)
    return state.played_songs


def add_played_song(
    hass: HomeAssistant, track_uri: str, entry_id: Optional[str] = None
) -> None:
    """Add song to played history.

    Args:
        hass: The Home Assistant instance.
        track_uri: The Spotify track URI to add.
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Only add if not already played (prevents duplicates)
    if track_uri not in state.played_songs:
        # Add to history (atomic operation - list.append is thread-safe in async context)
        state.played_songs.append(track_uri)
        _LOGGER.debug("Song added to history: %s", track_uri)


def is_song_played(
    hass: HomeAssistant, track_uri: str, entry_id: Optional[str] = None
) -> bool:
    """Check if song has been played.

    Args:
        hass: The Home Assistant instance.
        track_uri: The Spotify track URI to check.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        True if the song has been played, False otherwise.
    """
    state = get_game_state(hass, entry_id)
    return track_uri in state.played_songs


def clear_played_songs(hass: HomeAssistant, entry_id: Optional[str] = None) -> None:
    """Clear played songs history.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Clear history (atomic operation - list.clear is thread-safe in async context)
    state.played_songs.clear()

    _LOGGER.debug("Played songs cleared")


async def select_random_song(
    hass: HomeAssistant, entry_id: Optional[str] = None
) -> dict[str, Any]:
    """Select a random song from available songs without repeating.

    Story 5.1: Implements Fisher-Yates random selection using Python's
    random.choice() for O(1) selection. Moves selected song from available_songs
    to played_songs atomically. Protected by asyncio.Lock for concurrency safety.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        Selected song dictionary with all required fields:
        {uri, title, artist, album, year, cover_url}

    Raises:
        PlaylistExhaustedError: If available_songs list is empty (all songs played).
        ValueError: If selected song is missing required fields.

    AC-1: Random selection from available_songs using random.choice()
    AC-2: Validates song structure has all required fields
    AC-3: Atomically moves song from available to played
    AC-4: Raises PlaylistExhaustedError when empty
    AC-5: Prevents repeats by tracking played_songs
    AC-6: Uses asyncio.Lock() for concurrent request protection
    AC-7: Comprehensive logging (INFO, DEBUG, WARNING)
    """
    async with _song_selection_lock:
        state = get_game_state(hass, entry_id)

        # AC-4: Check if playlist is exhausted
        if not state.available_songs or len(state.available_songs) == 0:
            played_count = len(state.played_songs)
            _LOGGER.warning(
                "Playlist exhausted: %d songs played, no songs available",
                played_count,
            )
            raise PlaylistExhaustedError()

        # AC-1: Random selection using Fisher-Yates (via random.choice)
        # O(1) selection time, proper distribution
        selected_song = random.choice(state.available_songs)

        # AC-2: Validate song structure has all required fields
        required_fields = ["uri", "title", "artist", "album", "year", "cover_url"]
        missing_fields = [field for field in required_fields if field not in selected_song or not selected_song[field]]

        if missing_fields:
            _LOGGER.error(
                "Selected song missing required fields: %s. Song: %s",
                missing_fields,
                selected_song,
            )
            raise ValueError(f"Song missing required fields: {missing_fields}")

        # Get current round number for logging (if available)
        round_number = state.current_round.round_number if state.current_round else len(state.played_songs) + 1

        # AC-3: Atomic move from available to played
        # Remove from available (O(n) but acceptable for playlists <1000 songs)
        state.available_songs.remove(selected_song)

        # Add to played history
        state.played_songs.append(selected_song)

        # AC-7: Logging - INFO level with song details
        _LOGGER.info(
            "Selected song for round %d: '%s' by %s (%d)",
            round_number,
            selected_song["title"],
            selected_song["artist"],
            selected_song["year"],
        )

        # AC-7: Logging - DEBUG level with remaining count
        remaining_count = len(state.available_songs)
        _LOGGER.debug("Available songs remaining: %d", remaining_count)

        # AC-5: Verification - no song should be in both lists
        # This is guaranteed by the remove/append operations above
        assert selected_song not in state.available_songs, "Song still in available_songs after selection"
        assert selected_song in state.played_songs, "Song not in played_songs after selection"

        return selected_song


# ============================================================================
# Game Initialization (backward compatibility)
# ============================================================================


def initialize_game(
    hass: HomeAssistant, config: dict[str, Any], entry_id: Optional[str] = None
) -> None:
    """Initialize game with provided configuration.

    Args:
        hass: Home Assistant instance
        config: Game configuration dict
        entry_id: The config entry ID. If None, uses first entry.
    """
    state = get_game_state(hass, entry_id)

    # Store config
    state.game_config.update(config)

    # Set game as initialized
    state.game_started = True
    state.game_started_at = time.time()

    _LOGGER.info("Game initialized with config: %s", config)


# ============================================================================
# Config Persistence Functions
# ============================================================================


async def load_config(hass: HomeAssistant, entry_id: str) -> GameConfig:
    """Load persisted config from storage.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID.

    Returns:
        The loaded configuration, or empty dict if no config exists.
    """
    store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry_id}")
    data = await store.async_load()

    if data is None:
        _LOGGER.debug("No persisted config found for entry %s, using defaults", entry_id)
        return {}

    _LOGGER.debug("Config loaded from storage for entry %s", entry_id)
    return data


async def save_config(
    hass: HomeAssistant, config: GameConfig, entry_id: str
) -> None:
    """Save config to persistent storage.

    Args:
        hass: The Home Assistant instance.
        config: The configuration to save.
        entry_id: The config entry ID.
    """
    store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry_id}")
    await store.async_save(config)

    _LOGGER.debug("Config saved to storage for entry %s", entry_id)
