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
import copy
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
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
class MediaPlayerState:
    """Saved media player state for restoration.

    Story 7.3: Captures current playback state before game starts so it can be
    restored after game ends (Story 7.6). Stored in-memory in game_config.

    Attributes:
        entity_id: The media player entity ID being used for the game.
        source: Active source before game (e.g., "Spotify"). Optional.
        media_title: Currently playing track title. Optional.
        media_artist: Artist name of current track. Optional.
        volume_level: Volume level (0.0-1.0) at time of capture.
        position: Playback position in seconds. Optional.
        state: Player state ("playing", "paused", "idle", etc.).
        saved_at: Timestamp when state was captured.
    """

    entity_id: str
    source: Optional[str]
    media_title: Optional[str]
    media_artist: Optional[str]
    volume_level: float
    position: Optional[float]
    state: str
    saved_at: datetime

    def is_valid(self) -> bool:
        """Check if state has enough info for restoration.

        Returns:
            True if state has at least source or media_title populated.
        """
        return self.source is not None or self.media_title is not None


@dataclass
class RoundState:
    """Current round state.

    Story 5.2: Represents the active round with song metadata, timer, and player guesses.
    Story 7.5: Added retry_count for playback error handling.
    Server-side authoritative state for timed gameplay window.
    """

    round_number: int
    song: dict[str, Any]  # Story 11.9 AC-6: {id, uri, title, artist, year, fun_fact, cover_url} - NO album
    started_at: float
    timer_duration: int  # seconds (from config, default 30)
    status: str = "active"  # active, ended
    guesses: list[dict[str, Any]] = field(default_factory=list)  # List of {player_name, year, bet, submitted_at}
    retry_count: int = 0  # Story 7.5: Track playback retry attempts


@dataclass
class BeatsyGameState:
    """Complete game state structure.

    This is the root state object stored in hass.data[DOMAIN][entry_id].
    All game state is accessed through this object.
    """

    entry_id: str = ""  # Story 11.1: Config entry ID for persistence operations
    game_config: GameConfig = field(default_factory=dict)
    players: list[Player] = field(default_factory=list)
    current_round: Optional[RoundState] = None
    played_songs: list[dict[str, Any]] = field(default_factory=list)  # Story 5.1: Full song dicts, not just URIs
    available_songs: list[dict[str, Any]] = field(default_factory=list)
    original_playlist: list[dict[str, Any]] = field(default_factory=list)  # Story 5.7: Deep copy of loaded playlist for reset
    websocket_connections: dict[str, Any] = field(default_factory=dict)
    game_started: bool = False
    game_started_at: Optional[float] = None
    game_status: str = "setup"  # Story 5.7: Game status (setup, active, ended)
    spotify: dict[str, Any] = field(default_factory=dict)
    round_timer_task: Optional[asyncio.Task] = None  # Story 5.4: Timer task for automatic round end
    saved_player_state: Optional[MediaPlayerState] = None  # Story 7.3: Saved media player state for restoration


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

    # Story 11.1: Store entry_id for persistence operations
    state.entry_id = entry_id

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

    if "points_wrong" in config:
        if config["points_wrong"] < 0:
            raise ValueError("points_wrong cannot be negative")

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

    _LOGGER.debug(
        "Round %d started: %s",
        round_state.round_number,
        round_state.song.get("title", "Unknown"),
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

    Story 5.2: Uses list-based guesses structure for round state.

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

    # Check if player already has a guess (update if exists)
    existing_guess = next(
        (g for g in round_state.guesses if g.get("player_name") == player_name), None
    )

    if existing_guess:
        # Update existing guess
        existing_guess["year"] = year_guess
        existing_guess["bet"] = bet_placed
        existing_guess["submitted_at"] = time.time()
    else:
        # Add new guess (atomic operation - list.append is thread-safe in async context)
        round_state.guesses.append({
            "player_name": player_name,
            "year": year_guess,
            "bet": bet_placed,
            "submitted_at": time.time(),
        })

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

    Story 5.2: Uses list-based guesses structure for round state.

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

    # Find existing guess for this player
    existing_guess = next(
        (g for g in round_state.guesses if g.get("player_name") == player_name), None
    )

    if existing_guess:
        # Update bet in existing guess
        existing_guess["bet"] = bet
        existing_guess["updated_at"] = time.time()
    else:
        # Create placeholder guess with bet status
        round_state.guesses.append({
            "player_name": player_name,
            "year": None,
            "bet": bet,
            "updated_at": time.time(),
        })

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


# ============================================================================
# Game Reset Functions (Story 5.7, Story 7.6)
# ============================================================================


async def reset_game_async(hass: HomeAssistant, entry_id: Optional[str] = None) -> None:
    """Reset all game state to initial setup conditions (async version).

    Story 5.7: Clears all ephemeral game state (players, rounds, song history) and
    resets available songs to original playlist. Preserves game configuration for
    next session. This function is idempotent - safe to call multiple times.

    Story 7.6: Restores media player state before clearing game state.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Side Effects:
        - Restores media player to previous state (Story 7.6)
        - Clears saved_player_state after restoration
        - Clears players list
        - Clears current_round
        - Clears played_songs
        - Resets available_songs to original_playlist (deep copy)
        - Sets game_status to "setup"
        - Resets game_started to False
        - Cancels any active round timer task
        - Preserves game_config (admin settings)

    AC-1: Clear all ephemeral state (players, current_round, played_songs)
    AC-2: Set game_status to "setup"
    AC-5: Preserve game_config
    AC-7: Idempotent operation (safe to call multiple times)
    Story 7.6 AC-1: Restore media player state before reset
    Story 7.6 AC-3: If no saved state, leave player idle
    """
    state = get_game_state(hass, entry_id)

    # Story 7.6: Restore media player state BEFORE clearing game state
    if state.saved_player_state:
        from .spotify_service import restore_player_state

        _LOGGER.info(
            "Restoring media player state for: %s",
            state.saved_player_state.entity_id,
        )

        try:
            result = await restore_player_state(hass, state.saved_player_state, entry_id)

            if result["success"]:
                _LOGGER.info(
                    "Successfully restored media player: %s",
                    state.saved_player_state.entity_id,
                )
            else:
                _LOGGER.warning(
                    "Partial restoration for %s: %s",
                    state.saved_player_state.entity_id,
                    result["errors"],
                )
        except Exception as e:
            # Story 7.6 AC-2: Best-effort - log error but don't block game reset
            _LOGGER.error(
                "Failed to restore media player state for %s: %s (continuing with reset)",
                state.saved_player_state.entity_id,
                str(e),
            )

        # Clear saved state after restoration attempt
        state.saved_player_state = None
        _LOGGER.debug("Cleared saved_player_state after restoration attempt")
    else:
        # Story 7.6 AC-3: No saved state - leave player idle
        _LOGGER.info("No media player state to restore")

    # Store reference to original playlist for restoration
    original_playlist = state.original_playlist

    # Count current state for logging (before clearing)
    players_count = len(state.players)
    played_songs_count = len(state.played_songs)
    current_round_active = state.current_round is not None

    # AC-1: Clear ephemeral state
    state.players.clear()
    state.current_round = None
    state.played_songs.clear()

    # AC-1: Reset available_songs to original playlist (deep copy to prevent mutations)
    if original_playlist:
        state.available_songs = copy.deepcopy(original_playlist)
        _LOGGER.debug(
            "Available songs restored: %d songs from original_playlist",
            len(state.available_songs),
        )
    else:
        # No original playlist available - log warning and set to empty
        state.available_songs = []
        _LOGGER.warning(
            "No original_playlist found during reset, available_songs set to empty list"
        )

    # AC-2: Set game status to "setup"
    state.game_status = "setup"

    # Reset game_started flag
    state.game_started = False
    state.game_started_at = None

    # Cancel any active round timer task
    if state.round_timer_task is not None and not state.round_timer_task.done():
        state.round_timer_task.cancel()
        _LOGGER.debug("Round timer task cancelled during game reset")
    state.round_timer_task = None

    # AC-5: game_config is NOT cleared - preserves admin settings

    # Comprehensive logging
    _LOGGER.info(
        "Game reset: All state cleared, game_status set to 'setup' "
        "(cleared %d players, %d played songs, round_active=%s)",
        players_count,
        played_songs_count,
        current_round_active,
    )


def reset_game(hass: HomeAssistant, entry_id: Optional[str] = None) -> None:
    """Reset all game state to initial setup conditions (synchronous version).

    DEPRECATED: Use reset_game_async() instead for proper async support with
    media player state restoration (Story 7.6).

    This synchronous wrapper is kept for backward compatibility with existing code
    that cannot easily be migrated to async. Does NOT restore media player state.

    Story 5.7: Clears all ephemeral game state (players, rounds, song history) and
    resets available songs to original playlist. Preserves game configuration for
    next session. This function is idempotent - safe to call multiple times.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Side Effects:
        - Clears players list
        - Clears current_round
        - Clears played_songs
        - Resets available_songs to original_playlist (deep copy)
        - Sets game_status to "setup"
        - Resets game_started to False
        - Cancels any active round timer task
        - Preserves game_config (admin settings)
        - NOTE: Does NOT restore media player state (use reset_game_async for that)

    AC-1: Clear all ephemeral state (players, current_round, played_songs)
    AC-2: Set game_status to "setup"
    AC-5: Preserve game_config
    AC-7: Idempotent operation (safe to call multiple times)
    """
    state = get_game_state(hass, entry_id)

    # Store reference to original playlist for restoration
    original_playlist = state.original_playlist

    # Count current state for logging (before clearing)
    players_count = len(state.players)
    played_songs_count = len(state.played_songs)
    current_round_active = state.current_round is not None

    # AC-1: Clear ephemeral state
    state.players.clear()
    state.current_round = None
    state.played_songs.clear()

    # AC-1: Reset available_songs to original playlist (deep copy to prevent mutations)
    if original_playlist:
        state.available_songs = copy.deepcopy(original_playlist)
        _LOGGER.debug(
            "Available songs restored: %d songs from original_playlist",
            len(state.available_songs),
        )
    else:
        # No original playlist available - log warning and set to empty
        state.available_songs = []
        _LOGGER.warning(
            "No original_playlist found during reset, available_songs set to empty list"
        )

    # AC-2: Set game status to "setup"
    state.game_status = "setup"

    # Reset game_started flag
    state.game_started = False
    state.game_started_at = None

    # Cancel any active round timer task
    if state.round_timer_task is not None and not state.round_timer_task.done():
        state.round_timer_task.cancel()
        _LOGGER.debug("Round timer task cancelled during game reset")
    state.round_timer_task = None

    # AC-5: game_config is NOT cleared - preserves admin settings

    # Comprehensive logging
    _LOGGER.info(
        "Game reset: All state cleared, game_status set to 'setup' "
        "(cleared %d players, %d played songs, round_active=%s)",
        players_count,
        played_songs_count,
        current_round_active,
    )


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
        Story 11.9 AC-6: {id, uri, title, artist, year, fun_fact, cover_url} - NO album

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
        # Story 11.9 AC-6: Removed album from required fields
        required_fields = ["id", "uri", "title", "artist", "year", "cover_url"]
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


async def initialize_round(
    hass: HomeAssistant, selected_song: dict[str, Any], entry_id: Optional[str] = None
) -> RoundState:
    """Initialize a new round with song metadata, timer, and empty guesses.

    Story 5.2: Creates authoritative server-side round state for timed gameplay window.
    Story 7.4: Integrates playback initiation and runtime metadata enrichment.
    Increments round_number continuously (1, 2, 3...) based on played_songs history.

    Args:
        hass: The Home Assistant instance.
        selected_song: Song dict from select_random_song() with all required fields:
            Story 11.9 AC-6: {id, uri, title, artist, year, fun_fact, cover_url} - NO album
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        Initialized RoundState object stored in game state.

    Raises:
        ValueError: If game config is missing timer settings.

    AC-1: Creates RoundState with round_number, song, started_at, timer_duration, status, guesses
    AC-2: Round number increments continuously (first round = 1, then 2, 3, 4...)
    Story 7.4 AC-1: Initiates playback on configured media player
    Story 7.4 AC-2: Playback starts within 2 seconds
    Story 7.4 AC-4: Handles playback failures gracefully
    """
    from .spotify_helper import play_track, get_media_player_metadata
    from homeassistant.exceptions import HomeAssistantError
    from .websocket_handler import broadcast_event

    state = get_game_state(hass, entry_id)

    # AC-2: Calculate round number from played songs count
    # Round 1 is first song played, round 2 is second, etc.
    new_round_number = len(state.played_songs)
    if new_round_number == 0:
        new_round_number = 1  # First round starts at 1

    # AC-1: Load timer_duration from game config (default 30 seconds)
    timer_duration = state.game_config.get("round_timer_seconds", 30)

    # Story 7.4 Task 2: Get media player entity_id from game config
    media_player_entity_id = state.game_config.get("media_player_entity_id")

    # Story 7.5: Retry logic with automatic song selection (max 3 attempts)
    playback_start_time = time.time()
    playback_success = False
    retry_count = 0
    max_retries = 3
    current_song = selected_song

    while retry_count < max_retries and not playback_success:
        if media_player_entity_id and current_song.get("uri"):
            try:
                _LOGGER.debug(
                    "Story 7.5: Initiating playback (attempt %d/%d): %s on %s",
                    retry_count + 1,
                    max_retries,
                    current_song.get("uri"),
                    media_player_entity_id,
                )

                # Call play_track() - non-blocking service call
                playback_success = await play_track(
                    hass, media_player_entity_id, current_song["uri"]
                )

                if playback_success:
                    playback_latency = time.time() - playback_start_time
                    _LOGGER.info(
                        "Story 7.5: Playback successful on attempt %d: '%s' by '%s' (%s) - initiated in %.2fs",
                        retry_count + 1,
                        current_song.get("title"),
                        current_song.get("artist"),
                        current_song.get("year"),
                        playback_latency,
                    )

                    # Warn if playback initiation took too long
                    if playback_latency > 2.0:
                        _LOGGER.warning(
                            "Story 7.5: Playback latency high: %.2fs (target: < 2s)",
                            playback_latency,
                        )
                    break  # Success, exit retry loop

            except HomeAssistantError as e:
                retry_count += 1
                error_message = str(e)

                _LOGGER.error(
                    "Story 7.5: Playback failed (attempt %d/%d): %s - %s",
                    retry_count,
                    max_retries,
                    current_song.get("uri"),
                    error_message,
                )

                if retry_count < max_retries:
                    # Story 7.5 Task 6: Automatic retry with new song
                    _LOGGER.info(
                        "Story 7.5: Retrying with different song (attempt %d/%d)",
                        retry_count + 1,
                        max_retries,
                    )

                    # Select new random song for retry
                    try:
                        current_song = await select_random_song(hass, entry_id)
                        _LOGGER.info(
                            "Story 7.5: Selected new song for retry: '%s' by '%s'",
                            current_song.get("title"),
                            current_song.get("artist"),
                        )
                    except PlaylistExhaustedError:
                        _LOGGER.error("Story 7.5: Playlist exhausted during retry, cannot continue")
                        break
                else:
                    # Story 7.5 Task 5: Max retries exhausted
                    _LOGGER.critical(
                        "Story 7.5: Max retries exhausted (%d attempts). Game paused.",
                        max_retries,
                    )

                    # Broadcast critical error to admin using helper function
                    from .events import broadcast_playback_error
                    await broadcast_playback_error(
                        hass,
                        error_message=f"Failed to play songs after {max_retries} attempts. Check Spotify connection and media player.",
                        track_title=current_song.get("title", "Unknown Track"),
                        track_artist=current_song.get("artist", "Unknown Artist"),
                        retry_count=retry_count,
                        max_retries=max_retries,
                        can_retry=False,
                    )
        else:
            _LOGGER.warning(
                "Story 7.5: Skipping playback - media_player_entity_id or track URI missing"
            )
            break

    # AC-1: Create RoundState with all required fields
    # Story 7.5: Use current_song (may be different from selected_song if retries occurred)
    # Story 11.9 AC-6: Song structure: {id, uri, title, artist, year, fun_fact, cover_url} - NO album
    round_state = RoundState(
        round_number=new_round_number,
        song=current_song,  # Story 11.9 AC-6: {id, uri, title, artist, year, fun_fact, cover_url} - NO album
        started_at=time.time(),  # UTC timestamp
        timer_duration=timer_duration,
        status="active",
        guesses=[],  # Empty list, will be populated by Story 5.3
        retry_count=retry_count,  # Story 7.5: Track retry attempts
    )

    # AC-1: Store round state in game state (authoritative server state)
    state.current_round = round_state

    # Story 7.4 Task 7: Runtime metadata enrichment
    # Wait 2 seconds for HA media player state to update, then enrich metadata
    if playback_success and media_player_entity_id:
        _LOGGER.debug(
            "Story 7.5: Waiting 2 seconds for media player state to update..."
        )
        await asyncio.sleep(2.0)

        try:
            # Fetch runtime metadata from media player
            metadata = await get_media_player_metadata(hass, media_player_entity_id)

            # Enrich song metadata with runtime data (optional - fallback to existing)
            if metadata.get("media_title"):
                round_state.song["title"] = metadata["media_title"]
            if metadata.get("media_artist"):
                round_state.song["artist"] = metadata["media_artist"]
            # Story 11.9 AC-6: Removed album field from song structure
            if metadata.get("entity_picture"):
                round_state.song["cover_url"] = metadata["entity_picture"]
                _LOGGER.debug("Story 11.9 AC-5: Cover URL overridden with media player entity_picture")
            else:
                _LOGGER.debug("Story 11.9 AC-5: Using placeholder cover URL (media player entity_picture not available)")

            _LOGGER.debug(
                "Story 7.5: Enriched metadata from media player: title='%s', artist='%s'",
                metadata.get("media_title"),
                metadata.get("media_artist"),
            )
        except HomeAssistantError as e:
            _LOGGER.warning(
                "Story 7.5: Failed to fetch runtime metadata (using original): %s",
                str(e),
            )
            # Continue with original metadata - don't fail round

    # Story 5.4 AC-1: Create and store timer task for automatic round end
    # Timer duration + grace period (2 seconds to absorb network latency)
    grace_period = 2.0
    total_duration = timer_duration + grace_period

    # Create background timer task (non-blocking)
    timer_task = asyncio.create_task(
        _round_timer_task(hass, round_state.round_number, total_duration, entry_id)
    )

    # Store task reference for cancellation (manual round end support)
    state.round_timer_task = timer_task

    # Logging handled in separate task (Task 6)
    _LOGGER.debug(
        "Round %d initialized: '%s' by %s (%ds timer + %ds grace = %ds total, retries: %d)",
        round_state.round_number,
        current_song.get("title"),
        current_song.get("artist"),
        timer_duration,
        int(grace_period),
        int(total_duration),
        retry_count,
    )

    return round_state


def prepare_round_started_payload(round_state: RoundState) -> dict[str, Any]:
    """Prepare round_started WebSocket event payload, excluding year field.

    Story 5.2: Builds broadcast payload for all connected clients. CRITICAL: year field
    is explicitly removed to prevent cheating - players must guess the year, not see it.

    Args:
        round_state: The initialized RoundState object.

    Returns:
        Payload dict ready for WebSocket broadcast with structure:
        {
            "type": "round_started",
            "song": {id, uri, title, artist, cover_url, fun_fact},  # year EXCLUDED, NO album
            "timer_duration": int,
            "started_at": float,
            "round_number": int
        }

    AC-3: Payload includes type, song (WITHOUT year), timer_duration, started_at, round_number
    AC-3: Song.year field MUST be excluded (security requirement)
    Story 11.9 AC-6: Song does NOT include album field
    AC-7: Provides all data needed for Epic 8 active round UI
    """
    # AC-3: Copy song dict and explicitly remove year field (CRITICAL for game integrity)
    payload_song = round_state.song.copy()
    payload_song.pop("year", None)  # Remove year - players are guessing it!

    # AC-3: Build payload with all required fields
    # Story 11.9 AC-6: Song includes id, uri, title, artist, cover_url, fun_fact (NO year, NO album)
    payload = {
        "type": "round_started",
        "song": payload_song,  # id, uri, title, artist, cover_url, fun_fact (NO year, NO album)
        "timer_duration": round_state.timer_duration,
        "started_at": round_state.started_at,
        "round_number": round_state.round_number,
    }

    # Verification: Ensure year is not in payload (double-check for security)
    assert "year" not in payload["song"], "SECURITY VIOLATION: year field found in round_started payload"

    return payload


# ============================================================================
# Round End & Scoring Functions (Stories 5.4, 5.5)
# ============================================================================


def calculate_score(
    actual_year: int, guess_year: int, bet_placed: bool, config: dict[str, Any]
) -> int:
    """Calculate points for a single guess based on proximity and bet.

    Story 5.5: Pure function implementing proximity-based scoring algorithm.
    Deterministic, no side effects, fully testable.

    Args:
        actual_year: The actual year of the song.
        guess_year: The player's guessed year.
        bet_placed: Whether the player placed a bet on this guess.
        config: Game configuration dict with scoring values.

    Returns:
        Integer points earned for this guess (0 or positive).

    AC-1: Exact match (proximity == 0) → points_exact (default 10)
    AC-2: Close proximity (±2 years) → points_close (default 5)
    AC-3: Near proximity (±5 years) → points_near (default 2)
    AC-4: Wrong (beyond ±5 years) → points_wrong (default 0)
    AC-5: Bet multiplier applied to all proximity tiers (default 2.0x)
    """
    # Calculate absolute proximity (distance between guess and actual)
    proximity = abs(actual_year - guess_year)

    # Determine base points from proximity using if/elif chain
    if proximity == 0:
        # AC-1: Exact year match
        base_points = config.get("points_exact", 10)
    elif proximity <= 2:
        # AC-2: Close proximity (within ±2 years)
        base_points = config.get("points_close", 5)
    elif proximity <= 5:
        # AC-3: Near proximity (within ±5 years, but beyond ±2)
        base_points = config.get("points_near", 2)
    else:
        # AC-4: Wrong guess (beyond ±5 years)
        base_points = config.get("points_wrong", 0)

    # AC-5: Apply bet multiplier if bet was placed
    if bet_placed:
        # Multiply by bet_multiplier (default 2.0), convert to int
        bet_multiplier = config.get("points_bet_multiplier", 2.0)
        return int(base_points * bet_multiplier)
    else:
        return base_points


async def calculate_round_scores(hass: HomeAssistant, entry_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Calculate scores for all guesses in current round.

    Story 5.5: Batch scoring function that processes all guesses, updates player totals,
    and returns results structure sorted by points_earned descending.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        List of results dicts sorted by points_earned (descending):
        [{player_name, year_guess, bet_placed, points_earned, proximity}, ...]

    AC-6: Update each player's total_points atomically
    AC-7: Generate results structure with all required fields, sorted by points descending
    AC-8: Performance requirement <500ms for 50 players (O(n) complexity)
    """
    scoring_start = time.time()

    state = get_game_state(hass, entry_id)

    # Verify current_round exists
    if state.current_round is None:
        _LOGGER.warning("calculate_round_scores called but no current_round exists")
        return []

    round_state = state.current_round

    # Load game config for scoring parameters
    config = state.game_config

    # Extract actual year from song
    actual_year = round_state.song.get("year")
    if actual_year is None:
        _LOGGER.error("Song missing year field, cannot calculate scores")
        return []

    # Initialize empty results list
    results = []

    # AC-8: O(n) iteration through guesses
    for guess in round_state.guesses:
        player_name = guess.get("player_name")
        year_guess = guess.get("year")
        bet_placed = guess.get("bet", False)

        # Skip invalid guesses (no player name or year)
        if player_name is None or year_guess is None:
            _LOGGER.warning(
                "Invalid guess in round %d: player_name=%s, year=%s (skipping)",
                round_state.round_number,
                player_name,
                year_guess,
            )
            continue

        # Calculate points earned for this guess
        points_earned = calculate_score(actual_year, year_guess, bet_placed, config)

        # Store points_earned in guess object for future reference
        guess["points_earned"] = points_earned

        # Calculate proximity for results structure
        proximity = abs(actual_year - year_guess)

        # AC-6: Update player total_points in players array
        player = get_player(hass, player_name, entry_id)
        if player is not None:
            player.score += points_earned
            _LOGGER.debug(
                "Player %s scored %d (guess: %d, actual: %d, proximity: %d, bet: %s)",
                player_name,
                points_earned,
                year_guess,
                actual_year,
                proximity,
                bet_placed,
            )
        else:
            _LOGGER.warning(
                "Player %s not found in players array, cannot update total_points",
                player_name,
            )

        # AC-7: Append to results structure
        results.append({
            "player_name": player_name,
            "year_guess": year_guess,
            "bet_placed": bet_placed,
            "points_earned": points_earned,
            "proximity": proximity,
        })

    # AC-7: Sort results by points_earned descending (highest scores first)
    results.sort(key=lambda r: r["points_earned"], reverse=True)

    # Calculate scoring duration for performance monitoring
    scoring_time_ms = (time.time() - scoring_start) * 1000

    # AC-8: Log INFO message with scoring details
    _LOGGER.info(
        "Round %d scoring complete: %d guesses scored in %.1fms",
        round_state.round_number,
        len(results),
        scoring_time_ms,
    )

    # AC-8: Log WARNING if scoring took longer than 500ms
    if scoring_time_ms > 500:
        _LOGGER.warning(
            "Scoring performance degraded: %.1fms for %d players (threshold: 500ms)",
            scoring_time_ms,
            len(results),
        )

    return results


def get_leaderboard(
    hass: HomeAssistant,
    entry_id: Optional[str] = None,
    current_player_name: Optional[str] = None
) -> list[dict[str, Any]]:
    """Calculate leaderboard with ranks from player scores.

    Story 5.6: Pure function that sorts players by total points descending,
    assigns ranks with proper tie handling (same score = same rank, next rank skips),
    and optionally highlights a specific player.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.
        current_player_name: Optional player name to mark with is_current_player flag.

    Returns:
        List of leaderboard entries sorted by total_points descending:
        [
            {
                "rank": int,              # Position (1-based, ties get same rank)
                "player_name": str,       # Player's display name
                "total_points": int,      # Cumulative points across all rounds
                "is_current_player": bool # True if matches current_player_name param
            },
            ...
        ]
        Returns empty list [] if no players exist.

    AC-1: Sort players by total_points descending (stable sort)
    AC-2: Assign ranks with tie handling (same score = same rank, skip numbers)
    AC-3: Return structured entries with all required fields
    AC-4: Mark current_player_name with is_current_player=true
    AC-5: Handle empty players gracefully (return [])
    AC-6: Performance <100ms for 50 players (O(n log n) sorting)
    """
    leaderboard_start = time.time()

    state = get_game_state(hass, entry_id)

    # AC-5: Handle empty players case
    players = state.players
    if not players or len(players) == 0:
        _LOGGER.debug("get_leaderboard called with no players, returning empty list")
        return []

    # AC-1: Sort players by score (total_points) descending
    # Use stable sort to maintain deterministic order for ties
    sorted_players = sorted(players, key=lambda p: p.score, reverse=True)

    # AC-2 & AC-3: Assign ranks with tie handling
    leaderboard = []
    current_rank = 1
    previous_score = None

    for position, player in enumerate(sorted_players, start=1):
        # Check if score changed from previous player
        if player.score != previous_score:
            # New score tier - update rank to current position
            current_rank = position
            previous_score = player.score

        # AC-4: Mark current player if name matches
        is_current = (
            current_player_name is not None
            and player.name == current_player_name
        )

        # AC-3: Create leaderboard entry with all required fields
        entry = {
            "rank": current_rank,
            "player_name": player.name,
            "total_points": player.score,  # Using score field (same as total_points)
            "is_current_player": is_current,
        }

        leaderboard.append(entry)

    # AC-6: Calculate performance metrics
    leaderboard_time_ms = (time.time() - leaderboard_start) * 1000

    # Logging: DEBUG level with leaderboard details
    _LOGGER.debug(
        "Leaderboard calculated: %d players, top score: %d, time: %.1fms",
        len(leaderboard),
        leaderboard[0]["total_points"] if leaderboard else 0,
        leaderboard_time_ms,
    )

    # AC-6: WARNING if performance degrades beyond threshold
    if leaderboard_time_ms > 100:
        _LOGGER.warning(
            "Leaderboard performance degraded: %.1fms for %d players (threshold: 100ms)",
            leaderboard_time_ms,
            len(leaderboard),
        )

    return leaderboard


async def end_round(hass: HomeAssistant, entry_id: Optional[str] = None) -> dict[str, Any]:
    """End current round, calculate scores, broadcast results to all clients.

    Story 5.4: Automatic round end when timer expires or manual admin override.
    Changes round status from "active" to "ended", preventing new guess submissions.
    Calls scoring and leaderboard functions, then broadcasts round_ended event.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        The round_ended payload dict that was broadcast.
        Returns empty dict if no current_round exists.

    AC-3: Set current_round.status = "ended" (prevents new guess submissions)
    AC-5: Call calculate_round_scores() to get results
    AC-6: Call get_leaderboard() to get sorted standings
    AC-7: Broadcast round_ended event with full payload
    AC-8: Comprehensive logging (INFO, WARNING, ERROR levels)
    AC-10: Graceful error handling (scoring/leaderboard/broadcast failures)
    """
    # Import broadcast_event - try relative import first, fallback to global namespace for tests
    try:
        from .websocket_api import broadcast_event
    except ImportError:
        # Fallback for test environment - use global broadcast_event if available
        try:
            broadcast_event = globals()['broadcast_event']
        except KeyError:
            # If still not available, create a no-op mock
            async def broadcast_event(*args, **kwargs):
                pass

    state = get_game_state(hass, entry_id)

    # AC-10: Check if current_round exists
    if state.current_round is None:
        _LOGGER.warning("end_round called but no current_round exists (already ended or not started)")
        return {}

    round_state = state.current_round

    # AC-10: Check if already ended (idempotent)
    if round_state.status == "ended":
        _LOGGER.info("Round %d already ended, skipping duplicate end_round call", round_state.round_number)
        return {}

    # AC-3: Set status to "ended" (atomic state transition)
    round_state.status = "ended"

    # Calculate elapsed time for logging
    elapsed = time.time() - round_state.started_at

    # AC-8: Log round end with timing
    _LOGGER.info(
        "Round %d ended: %d guesses submitted, elapsed time: %.1fs",
        round_state.round_number,
        len(round_state.guesses),
        elapsed,
    )

    # AC-5: Calculate scores for all guesses (Story 5.5 dependency)
    results = []
    try:
        scoring_start = time.time()
        results = await calculate_round_scores(hass, entry_id)
        scoring_time_ms = (time.time() - scoring_start) * 1000

        # AC-8: Log scoring completion
        _LOGGER.info(
            "Scoring completed: %d results calculated in %.1fms",
            len(results),
            scoring_time_ms,
        )

        # AC-8: DEBUG level logging with full results
        _LOGGER.debug("Round %d results: %s", round_state.round_number, results)
    except Exception as exc:
        # AC-10: Graceful degradation - scoring failure doesn't block game state
        _LOGGER.error(
            "Scoring calculation failed for round %d: %s (continuing with empty results)",
            round_state.round_number,
            exc,
            exc_info=True,
        )
        results = []

    # AC-6: Get leaderboard (Story 5.6 dependency)
    leaderboard = []
    try:
        leaderboard = get_leaderboard(hass, entry_id)

        # AC-8: DEBUG level logging with full leaderboard
        _LOGGER.debug("Round %d leaderboard: %s", round_state.round_number, leaderboard)
    except Exception as exc:
        # AC-10: Graceful degradation - leaderboard failure doesn't block game state
        _LOGGER.error(
            "Leaderboard calculation failed for round %d: %s (continuing with empty leaderboard)",
            round_state.round_number,
            exc,
            exc_info=True,
        )
        leaderboard = []

    # AC-7: Extract actual year from song (round_ended includes year, unlike round_started)
    actual_year = round_state.song.get("year")

    # AC-7: Prepare round_ended payload
    # Story 11.9 AC-6: Song includes ALL metadata (id, uri, title, artist, year, cover_url, fun_fact) - NO album
    payload = {
        "type": "round_ended",
        "round_number": round_state.round_number,
        "actual_year": actual_year,
        "song": round_state.song,  # Include ALL song metadata (id, uri, title, artist, year, cover_url, fun_fact) - NO album
        "results": results,  # Results from calculate_round_scores()
        "leaderboard": leaderboard,  # Leaderboard from get_leaderboard()
    }

    # AC-7: Broadcast round_ended event to ALL connected clients
    try:
        await broadcast_event(hass, "round_ended", payload, entry_id=entry_id)

        # AC-8: Log broadcast completion
        client_count = len(state.websocket_connections)
        _LOGGER.info(
            "round_ended broadcast sent to %d clients for round %d",
            client_count,
            round_state.round_number,
        )
    except Exception as exc:
        # AC-10: Graceful degradation - broadcast failure logged but doesn't crash component
        _LOGGER.error(
            "round_ended broadcast failed for round %d: %s (game state still transitioned)",
            round_state.round_number,
            exc,
            exc_info=True,
        )
        # Could retry once here if needed, but for now just log and continue

    return payload


async def _round_timer_task(
    hass: HomeAssistant, round_number: int, duration: float, entry_id: Optional[str] = None
) -> None:
    """Background timer task that triggers round end after duration.

    Story 5.4: Server-side asyncio timer for authoritative round expiration.
    Sleeps for duration seconds (timer_duration + grace_period), then calls end_round().
    Handles cancellation gracefully for manual round end (admin override).

    Args:
        hass: The Home Assistant instance.
        round_number: Round number to verify we're ending the correct round.
        duration: Sleep duration in seconds (timer_duration + grace_period).
        entry_id: The config entry ID. If None, uses first entry.

    AC-1: Background task created via asyncio.create_task()
    AC-2: Sleeps for timer_duration + 2 seconds (grace period)
    AC-2: After expiration, triggers end_round() automatically
    AC-8: Comprehensive logging (INFO for expiration/cancellation)
    AC-9: Handles asyncio.CancelledError for manual round end
    AC-10: Verifies round still active before ending (race condition protection)
    """
    try:
        # AC-2: Sleep for full duration (timer_duration + grace_period)
        await asyncio.sleep(duration)

        # AC-10: Verify current_round still exists and matches our round_number
        state = get_game_state(hass, entry_id)

        if state.current_round is None:
            _LOGGER.info(
                "Timer expired for round %d, but no current_round exists (already ended manually)",
                round_number,
            )
            return

        if state.current_round.round_number != round_number:
            _LOGGER.info(
                "Timer expired for round %d, but current round is now %d (already moved to next round)",
                round_number,
                state.current_round.round_number,
            )
            return

        if state.current_round.status != "active":
            _LOGGER.info(
                "Timer expired for round %d, but round status is '%s' (already ended)",
                round_number,
                state.current_round.status,
            )
            return

        # Calculate actual elapsed time for logging
        elapsed = time.time() - state.current_round.started_at

        # AC-8: Log timer expiration at INFO level
        _LOGGER.info(
            "Round %d timer expired at %.1fs (duration: %.1fs)",
            round_number,
            elapsed,
            duration,
        )

        # AC-2: Trigger end_round() automatically
        await end_round(hass, entry_id)

    except asyncio.CancelledError:
        # AC-9: Graceful cancellation handling (admin manual override)
        _LOGGER.info("Timer task cancelled for round %d (manual round end)", round_number)
        # Don't re-raise - this is expected behavior for manual round end
    except Exception as exc:
        # AC-10: Unexpected errors logged but don't crash component
        _LOGGER.error(
            "Timer task failed for round %d: %s",
            round_number,
            exc,
            exc_info=True,
        )


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
