"""Event type definitions and schema documentation for Beatsy WebSocket events.

This module serves as the single source of truth for all real-time events broadcast
from backend to frontend via WebSocket. It provides:

1. Event type constants - prevent typos and enable IDE autocomplete
2. Comprehensive schema documentation - data types and required fields
3. Usage examples - help frontend developers integrate events
4. Event envelope format - consistent message structure across all events
5. Broadcast helper functions - convenience wrappers for common events

Architecture:
-----------
This module implements the Generic WebSocket Event Bus (Epic 6, Story 6.1).
All events follow a standardized envelope format and are broadcast using the
broadcast_event() function from websocket_handler.py.

Event Envelope Format:
--------------------
All events are wrapped in a standardized envelope:

.. code-block:: python

    {
        "type": "beatsy/event",          # Fixed constant for all Beatsy events
        "event_type": "player_joined",   # Matches one of the EVENT_* constants below
        "data": {                        # Event-specific payload (see schemas below)
            "player_name": "Sarah",
            "total_players": 8
        },
        "timestamp": "2025-11-14T10:30:00Z"  # ISO 8601 UTC timestamp (optional)
    }

Frontend Integration:
--------------------
JavaScript/TypeScript example for handling events:

.. code-block:: javascript

    websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "beatsy/event") {
            switch (message.event_type) {
                case "player_joined":
                    handlePlayerJoined(message.data);
                    break;
                case "bet_placed":
                    handleBetPlaced(message.data);
                    break;
                case "round_started":
                    handleRoundStarted(message.data);
                    break;
                case "round_ended":
                    handleRoundEnded(message.data);
                    break;
                case "leaderboard_updated":
                    handleLeaderboardUpdated(message.data);
                    break;
                case "game_reset":
                    handleGameReset(message.data);
                    break;
                default:
                    console.warn("Unknown event type:", message.event_type);
            }
        }
    };

Backend Usage (Recommended - Use Helper Functions):
--------------------------------------------------
Instead of calling broadcast_event() directly, use the convenience helpers
defined in this module. They ensure consistent schemas and reduce coupling:

.. code-block:: python

    from custom_components.beatsy.events import broadcast_player_joined

    # Helper handles schema construction automatically
    await broadcast_player_joined(hass, "Sarah", 8)

    # Compare to manual broadcast_event (more verbose, schema can drift):
    # await broadcast_event(hass, EVENT_PLAYER_JOINED, {"player_name": "Sarah", "total_players": 8})

See Also:
--------
- websocket_handler.py: broadcast_event() implementation
- websocket_api.py: WebSocket command handlers that trigger events
- docs/tech-spec-epic-6.md: Detailed event schemas and architecture

References:
----------
- Epic 6, Story 6.1: Generic WebSocket Event Bus
- Epic 6, Story 6.3: Event Type Definitions & Schema
- Epic 6, Story 6.4: Broadcast Helpers for Common Events
- Epic 4-9: Features that emit these events
"""

import time
from typing import Any

from homeassistant.core import HomeAssistant

# Event Type Constants
# ====================
# These constants are used as the event_type field in the broadcast_event() function.
# Always use these constants instead of hardcoded strings to prevent typos.

EVENT_PLAYER_JOINED = "player_joined"
"""Player successfully registered and joined the game.

Broadcast when a player completes registration via join_game command.
Used by Epic 4 (Player Registration) to update lobby UI for all clients.

Schema:
    .. code-block:: python

        {
            "player_name": str,      # Name of player who joined (unique, may have (N) suffix)
            "total_players": int     # Total number of players in game (including new player)
        }

Example:
    .. code-block:: python

        {
            "player_name": "Sarah",
            "total_players": 8
        }

When Broadcast:
    - After successful player registration (websocket_api.handle_join_game)
    - Typically excluded from joining player's connection (they get full player list in join response)
    - Other players receive this event to update their lobby views

Frontend Actions:
    - Add new player to lobby player list
    - Update player count display
    - Play join notification sound (optional)
    - Show "Sarah joined!" toast message (optional)

Related Events:
    - game_reset: Clears all players from lobby
"""

EVENT_BET_PLACED = "bet_placed"
"""Player toggled bet status during active round.

Broadcast when a player places or removes a bet via place_bet command.
Used by Epic 8 (Active Round UI) to show bet indicators next to player names.

Schema:
    .. code-block:: python

        {
            "player_name": str      # Name of player who placed/removed bet
        }

Example:
    .. code-block:: python

        {
            "player_name": "Sarah"
        }

When Broadcast:
    - When player calls place_bet with bet=True or bet=False
    - Only during active round (round.status == "active")
    - Broadcast to ALL clients (including betting player)

Frontend Actions:
    - Toggle bet indicator icon next to player name (e.g., star, chip, flame)
    - Update bet counter ("3/8 players betting")
    - Play bet sound effect (optional)
    - Animate bet placement (optional)

Notes:
    - Event does NOT include bet status (true/false) - frontend must track state
    - Alternative: Use bet_updated event with explicit bet field (see websocket_api.py)
    - Original schema simplified to match Story 6.3 specification

Related Events:
    - round_started: Resets all bet indicators
    - round_ended: Shows which players won bet bonus
"""

EVENT_ROUND_STARTED = "round_started"
"""New round started with song and timer information.

Broadcast when admin triggers next_song command and round initializes.
Used by Epic 8 (Active Round UI) to display song info, album art, and countdown timer.

Schema:
    .. code-block:: python

        {
            "song": {
                "title": str,       # Song title (e.g., "Billie Jean")
                "artist": str,      # Primary artist name (e.g., "Michael Jackson")
                "album": str,       # Album name (e.g., "Thriller")
                "cover_url": str,   # Album art URL (Spotify CDN, 640x640px)
                "uri": str          # Spotify track URI (spotify:track:...)
                # NOTE: year field is intentionally EXCLUDED (game logic!)
            },
            "timer_duration": int,  # Round duration in seconds (e.g., 30)
            "started_at": float     # Server UTC timestamp when round started (for client sync)
        }

Example:
    .. code-block:: python

        {
            "song": {
                "title": "Billie Jean",
                "artist": "Michael Jackson",
                "album": "Thriller",
                "cover_url": "https://i.scdn.co/image/abc123...",
                "uri": "spotify:track:5ChkMS8OtdzJeqyybCc9R5"
            },
            "timer_duration": 30,
            "started_at": 1731600000.0
        }

When Broadcast:
    - After song selection and round initialization (Story 5.2)
    - Broadcast to ALL clients (admin AND players)
    - Triggers transition from lobby/results to active round UI

Frontend Actions:
    - Display song title, artist, album info
    - Show album cover art
    - Start countdown timer (sync with started_at timestamp)
    - Enable year guess input slider/buttons
    - Reset bet indicator to off
    - Clear any previous round results

Timer Synchronization:
    - Use started_at timestamp to calculate elapsed time on client
    - elapsed = (client_time - started_at)
    - remaining = timer_duration - elapsed
    - Prevents timer drift from network latency

Security Note:
    - Song year is INTENTIONALLY excluded from this event
    - Backend must strip year field before broadcasting (prepare_round_started_payload)
    - Year is only revealed in round_ended event

Related Events:
    - round_ended: Reveals correct year and shows results
    - bet_placed: Players toggle bet during active round
"""

EVENT_ROUND_ENDED = "round_ended"
"""Round timer expired and results calculated.

Broadcast when round timer expires or admin manually ends round.
Used by Epic 9 (Results & Leaderboards) to display guesses, scores, and correct year.

Schema:
    .. code-block:: python

        {
            "correct_year": int,    # Actual year of the song (revealed answer)
            "results": [            # Array of player results (all guesses for this round)
                {
                    "player_name": str,     # Player who submitted guess
                    "year_guess": int,      # Year the player guessed
                    "points_earned": int,   # Points awarded for this round (0-15)
                    "bet_placed": bool,     # Whether player placed bet (affects points)
                    "proximity": int        # abs(year_guess - correct_year)
                },
                # ... more results
            ]
        }

Example:
    .. code-block:: python

        {
            "correct_year": 1983,
            "results": [
                {
                    "player_name": "Sarah",
                    "year_guess": 1985,
                    "points_earned": 5,
                    "bet_placed": False,
                    "proximity": 2
                },
                {
                    "player_name": "Alex",
                    "year_guess": 1983,
                    "points_earned": 15,
                    "bet_placed": True,
                    "proximity": 0
                },
                {
                    "player_name": "Jordan",
                    "year_guess": 1990,
                    "points_earned": 0,
                    "bet_placed": False,
                    "proximity": 7
                }
            ]
        }

When Broadcast:
    - Automatically when round timer expires (Story 5.4)
    - Manually when admin triggers next_song during active round (Story 5.4)
    - After score calculation completes

Frontend Actions:
    - Display correct year with reveal animation
    - Show all player guesses and how many points they earned
    - Highlight perfect guesses (proximity = 0)
    - Show bet bonus indicators (bet_placed = True)
    - Sort results by points_earned descending
    - Play sound effects for different accuracy levels
    - Transition to results view

Scoring Algorithm (for frontend visualization):
    - proximity 0: 10 points base (perfect guess)
    - proximity 1: 7 points base
    - proximity 2: 5 points base
    - proximity 3: 3 points base
    - proximity 4-5: 1 point base
    - proximity 6+: 0 points
    - bet bonus: +5 points if bet_placed=True AND proximity <= 2

Related Events:
    - leaderboard_updated: Overall standings after round ends
    - round_started: Next round begins after results shown
"""

EVENT_LEADERBOARD_UPDATED = "leaderboard_updated"
"""Overall game leaderboard updated with cumulative scores.

Broadcast after round_ended event with updated total scores for all players.
Used by Epic 9 (Results & Leaderboards) to display overall standings.

Schema:
    .. code-block:: python

        {
            "leaderboard": [        # Array of player standings (sorted by total_points desc)
                {
                    "rank": int,            # Leaderboard position (1-indexed)
                    "player_name": str,     # Player name
                    "total_points": int,    # Cumulative score across all rounds
                    "is_current_player": bool  # Optional: True if this is viewing player
                },
                # ... more entries
            ]
        }

Example:
    .. code-block:: python

        {
            "leaderboard": [
                {
                    "rank": 1,
                    "player_name": "Alex",
                    "total_points": 50,
                    "is_current_player": False
                },
                {
                    "rank": 2,
                    "player_name": "Sarah",
                    "total_points": 45,
                    "is_current_player": True
                },
                {
                    "rank": 3,
                    "player_name": "Jordan",
                    "total_points": 40,
                    "is_current_player": False
                }
            ]
        }

When Broadcast:
    - After round_ended event (when scores update)
    - After each round completes
    - Broadcast to ALL clients

Frontend Actions:
    - Display overall leaderboard table or podium
    - Highlight current player's position
    - Show rank changes from previous round (optional)
    - Animate rank movements (optional)
    - Show crown/medal for top 3 players (optional)
    - Play fanfare sound for leader (optional)

Notes:
    - Leaderboard is sorted by total_points descending
    - Ties are handled by maintaining sort stability (first to reach score wins tiebreaker)
    - is_current_player field may be omitted if not available

Related Events:
    - round_ended: Individual round results
    - game_reset: Clears leaderboard back to zero
"""

EVENT_GAME_RESET = "game_reset"
"""Game state reset by admin - return to lobby.

Broadcast when admin triggers reset_game command to clear all game state.
Used by all epics to reset UI to initial lobby state.

Schema:
    .. code-block:: python

        {}  # Empty payload - this is a signal-only event

Example:
    .. code-block:: python

        {}

When Broadcast:
    - When admin calls reset_game via WebSocket command
    - Clears all players, rounds, scores, and game state
    - Resets available_songs from original_playlist

Frontend Actions:
    - Navigate to lobby/registration view
    - Clear all player data from UI
    - Reset leaderboard display
    - Clear current round info
    - Clear round history
    - Show "Game reset by admin" notification
    - Prompt players to re-register (optional)

Backend State Changes:
    - Clears state.players list
    - Clears state.current_round
    - Clears state.played_songs
    - Restores state.available_songs from original_playlist
    - Preserves game_config (timer_duration, year_range, etc.)

Notes:
    - This is a signal-only event (no data payload needed)
    - All clients must handle this event to prevent UI desync
    - Players must re-register via join_game after reset

Related Events:
    - player_joined: Players re-register after reset
"""

EVENT_PLAYBACK_ERROR = "playback_error"
"""Music playback error occurred on Spotify media player.

Broadcast when Spotify media player fails to play track during active round.
Used by Epic 7 (Story 7.5) for admin error handling and player notification.

Schema:
    .. code-block:: python

        {
            "error_message": str,   # Human-readable error description
            "track_uri": str,       # Spotify URI that failed to play
            "timestamp": float      # UTC timestamp when error occurred
        }

Example:
    .. code-block:: python

        {
            "error_message": "Spotify media player not available",
            "track_uri": "spotify:track:5ChkMS8OtdzJeqyybCc9R5",
            "timestamp": 1731600000.0
        }

When Broadcast:
    - When play_track() fails in spotify_helper.py
    - During round start if media player unavailable
    - If Spotify API returns error
    - If track URI is invalid or restricted

Frontend Actions:
    - Show error notification to admin
    - Display "Music playback failed" message to players
    - Optionally pause round timer
    - Allow admin to skip to next song
    - Log error for debugging

Admin Recovery Options:
    - Skip to next song (trigger next_song command)
    - Check media player configuration
    - Verify Spotify integration status
    - Check track availability in region

Notes:
    - This event is defined for Epic 7 Story 7.5 (Playback Error Handling)
    - Implementation deferred to Epic 7
    - Schema defined now for consistency with Story 6.3

Related Events:
    - round_started: Successful playback after error recovery
"""


# Event Schema Type Definitions (for type checking and validation)
# =================================================================
# These type hints can be used with mypy or runtime validation libraries
# like pydantic, marshmallow, or jsonschema (future enhancement)

# Type definitions for each event's data payload
# Note: These are comments for now, will be converted to TypedDict or dataclasses if needed

# PlayerJoinedData = {
#     "player_name": str,
#     "total_players": int,
# }

# BetPlacedData = {
#     "player_name": str,
# }

# RoundStartedData = {
#     "song": {
#         "title": str,
#         "artist": str,
#         "album": str,
#         "cover_url": str,
#         "uri": str,
#     },
#     "timer_duration": int,
#     "started_at": float,
# }

# RoundEndedData = {
#     "correct_year": int,
#     "results": list[{
#         "player_name": str,
#         "year_guess": int,
#         "points_earned": int,
#         "bet_placed": bool,
#         "proximity": int,
#     }],
# }

# LeaderboardUpdatedData = {
#     "leaderboard": list[{
#         "rank": int,
#         "player_name": str,
#         "total_points": int,
#         "is_current_player": bool,  # optional
#     }],
# }

# GameResetData = {}  # Empty payload

# PlaybackErrorData = {
#     "error_message": str,
#     "track_uri": str,
#     "timestamp": float,
# }


# ============================================================================
# Broadcast Helper Functions (Epic 6, Story 6.4)
# ============================================================================
# These convenience functions reduce coupling between business logic and event
# schemas. If schemas change, only helpers need updating (not all calling code).


async def broadcast_player_joined(
    hass: HomeAssistant,
    player_name: str,
    total_players: int
) -> None:
    """Broadcast player_joined event when new player registers.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_PLAYER_JOINED constant.

    Args:
        hass: Home Assistant instance.
        player_name: Name of player who joined (may have (N) suffix for duplicates).
        total_players: Total number of players in game (including new player).

    Example:
        .. code-block:: python

            # In websocket_api.py after player registration
            await broadcast_player_joined(hass, "Sarah", 8)

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "player_joined",
            #     "data": {
            #         "player_name": "Sarah",
            #         "total_players": 8
            #     }
            # }

    References:
        - Epic 4 (Player Registration): Calls this after successful join_game
        - EVENT_PLAYER_JOINED schema documentation (lines 113-148)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_PLAYER_JOINED,
        {
            "player_name": player_name,
            "total_players": total_players
        }
    )


async def broadcast_bet_placed(
    hass: HomeAssistant,
    player_name: str
) -> None:
    """Broadcast bet_placed event when player toggles bet status.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_BET_PLACED constant.

    Args:
        hass: Home Assistant instance.
        player_name: Name of player who placed/removed bet.

    Example:
        .. code-block:: python

            # In websocket_api.py when player places bet
            await broadcast_bet_placed(hass, "Sarah")

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "bet_placed",
            #     "data": {
            #         "player_name": "Sarah"
            #     }
            # }

    References:
        - Epic 8 (Active Round UI): Calls this when player toggles bet
        - EVENT_BET_PLACED schema documentation (lines 150-189)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_BET_PLACED,
        {
            "player_name": player_name
        }
    )


async def broadcast_round_started(
    hass: HomeAssistant,
    song: dict[str, Any],
    timer_duration: int,
    started_at: float
) -> None:
    """Broadcast round_started event with song info and timer.

    CRITICAL: This helper removes the 'year' field from song metadata before
    broadcasting to prevent client-side cheating. The year is only revealed
    in the round_ended event.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_ROUND_STARTED constant.

    Args:
        hass: Home Assistant instance.
        song: Song metadata dict including year (will be stripped).
        timer_duration: Round duration in seconds (e.g., 30).
        started_at: Server UTC timestamp when round started.

    Example:
        .. code-block:: python

            # In game_manager.py when round starts
            song = {
                "title": "Billie Jean",
                "artist": "Michael Jackson",
                "album": "Thriller",
                "cover_url": "https://i.scdn.co/image/abc123...",
                "uri": "spotify:track:5ChkMS8OtdzJeqyybCc9R5",
                "year": 1983  # Will be removed before broadcasting!
            }
            await broadcast_round_started(hass, song, 30, time.time())

            # Broadcasts this payload (year removed):
            # {
            #     "type": "beatsy/event",
            #     "event_type": "round_started",
            #     "data": {
            #         "song": {
            #             "title": "Billie Jean",
            #             "artist": "Michael Jackson",
            #             "album": "Thriller",
            #             "cover_url": "https://i.scdn.co/image/abc123...",
            #             "uri": "spotify:track:5ChkMS8OtdzJeqyybCc9R5"
            #             # Note: year field is missing
            #         },
            #         "timer_duration": 30,
            #         "started_at": 1731600000.0
            #     }
            # }

    Security Note:
        The year field is intentionally removed to prevent cheating. Players
        should not be able to see the correct answer in their browser DevTools.

    References:
        - Epic 5 (Game Mechanics): Calls this when admin triggers next_song
        - EVENT_ROUND_STARTED schema documentation (lines 191-255)
    """
    from .websocket_handler import broadcast_event

    # Remove year from song metadata before broadcasting (security!)
    song_without_year = {k: v for k, v in song.items() if k != "year"}

    await broadcast_event(
        hass,
        EVENT_ROUND_STARTED,
        {
            "song": song_without_year,
            "timer_duration": timer_duration,
            "started_at": started_at
        }
    )


async def broadcast_round_ended(
    hass: HomeAssistant,
    correct_year: int,
    results: list[dict[str, Any]]
) -> None:
    """Broadcast round_ended event with scoring results.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_ROUND_ENDED constant.

    Args:
        hass: Home Assistant instance.
        correct_year: Actual year of the song (revealed answer).
        results: Array of player results with guesses and points earned.

    Example:
        .. code-block:: python

            # In game_manager.py when round timer expires
            results = [
                {
                    "player_name": "Sarah",
                    "year_guess": 1985,
                    "points_earned": 5,
                    "bet_placed": False,
                    "proximity": 2
                },
                {
                    "player_name": "Alex",
                    "year_guess": 1983,
                    "points_earned": 15,
                    "bet_placed": True,
                    "proximity": 0
                }
            ]
            await broadcast_round_ended(hass, 1983, results)

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "round_ended",
            #     "data": {
            #         "correct_year": 1983,
            #         "results": [...]
            #     }
            # }

    References:
        - Epic 5 (Game Mechanics): Calls this when round completes
        - Epic 9 (Results & Leaderboards): Displays these results
        - EVENT_ROUND_ENDED schema documentation (lines 257-336)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_ROUND_ENDED,
        {
            "correct_year": correct_year,
            "results": results
        }
    )


async def broadcast_leaderboard_updated(
    hass: HomeAssistant,
    leaderboard: list[dict[str, Any]]
) -> None:
    """Broadcast leaderboard_updated event with overall standings.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_LEADERBOARD_UPDATED constant.

    Args:
        hass: Home Assistant instance.
        leaderboard: Array of player standings sorted by total_points descending.

    Example:
        .. code-block:: python

            # In game_manager.py after round scoring
            leaderboard = [
                {
                    "rank": 1,
                    "player_name": "Alex",
                    "total_points": 50,
                    "is_current_player": False
                },
                {
                    "rank": 2,
                    "player_name": "Sarah",
                    "total_points": 45,
                    "is_current_player": True
                }
            ]
            await broadcast_leaderboard_updated(hass, leaderboard)

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "leaderboard_updated",
            #     "data": {
            #         "leaderboard": [...]
            #     }
            # }

    References:
        - Epic 9 (Results & Leaderboards): Calls this after score calculation
        - EVENT_LEADERBOARD_UPDATED schema documentation (lines 338-406)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_LEADERBOARD_UPDATED,
        {
            "leaderboard": leaderboard
        }
    )


async def broadcast_game_reset(hass: HomeAssistant) -> None:
    """Broadcast game_reset event (signal-only, no payload).

    This helper function calls broadcast_event() with an empty payload dict
    and the EVENT_GAME_RESET constant.

    Args:
        hass: Home Assistant instance.

    Example:
        .. code-block:: python

            # In websocket_api.py when admin triggers reset_game
            await broadcast_game_reset(hass)

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "game_reset",
            #     "data": {}
            # }

    References:
        - Epic 5 (Game Mechanics): Calls this when admin resets game
        - All Epics: Reset UI to lobby state on this event
        - EVENT_GAME_RESET schema documentation (lines 408-452)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_GAME_RESET,
        {}
    )


async def broadcast_playback_error(
    hass: HomeAssistant,
    error_message: str,
    track_title: str = "Unknown Track",
    track_artist: str = "Unknown Artist",
    retry_count: int = 0,
    max_retries: int = 3,
    can_retry: bool = True
) -> None:
    """Broadcast playback_error event when Spotify fails to play track.

    This helper function constructs the correct payload schema and calls
    broadcast_event() with the EVENT_PLAYBACK_ERROR constant.

    Args:
        hass: Home Assistant instance.
        error_message: Human-readable error description.
        track_title: Title of the track that failed to play.
        track_artist: Artist of the track that failed to play.
        retry_count: Number of retry attempts made so far.
        max_retries: Maximum number of retries allowed.
        can_retry: Whether automatic retry is possible.

    Example:
        .. code-block:: python

            # Story 7.5: Max retries exhausted
            await broadcast_playback_error(
                hass,
                "Failed to play songs after 3 attempts. Check Spotify connection.",
                track_title="Bad Song",
                track_artist="Test Artist",
                retry_count=3,
                max_retries=3,
                can_retry=False
            )

            # Broadcasts this payload to all clients:
            # {
            #     "type": "beatsy/event",
            #     "event_type": "playback_error",
            #     "data": {
            #         "error_message": "Failed to play songs after 3 attempts...",
            #         "track_title": "Bad Song",
            #         "track_artist": "Test Artist",
            #         "retry_count": 3,
            #         "max_retries": 3,
            #         "can_retry": false
            #     }
            # }

    References:
        - Epic 7, Story 7.5: Playback Error Handling & Retry
        - EVENT_PLAYBACK_ERROR schema documentation (lines 454-504)
    """
    from .websocket_handler import broadcast_event

    await broadcast_event(
        hass,
        EVENT_PLAYBACK_ERROR,
        {
            "error_message": error_message,
            "track_title": track_title,
            "track_artist": track_artist,
            "retry_count": retry_count,
            "max_retries": max_retries,
            "can_retry": can_retry,
        }
    )
