"""Centralized error handling and response system for Beatsy.

Story 10.4: Error Handling Hardening

This module provides:
- Standardized error response format
- Error code definitions with user-friendly messages
- Helper functions for consistent error handling
- Logging utilities for debugging

Architecture:
- ErrorResponse dataclass for structured error data
- ERROR_CODES dictionary mapping codes to user-friendly messages
- Helper functions for creating error responses
- Integration with Home Assistant logging
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

_LOGGER = logging.getLogger(__name__)


# ============================================================================
# Error Response Data Models
# ============================================================================


@dataclass
class ErrorResponse:
    """Structured error response for consistent error handling.

    Attributes:
        error_code: Machine-readable error code (e.g., "playlist_not_found")
        message: User-friendly error message
        details: Optional dict with additional context for debugging
        timestamp: When the error occurred
        troubleshooting: Optional troubleshooting steps for users
    """

    error_code: str
    message: str
    details: Optional[dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    troubleshooting: Optional[list[str]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert ErrorResponse to dictionary for JSON serialization.

        Returns:
            Dictionary representation of error response
        """
        result = {
            "error": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp,
        }

        if self.details:
            result["details"] = self.details

        if self.troubleshooting:
            result["troubleshooting"] = self.troubleshooting

        return result


# ============================================================================
# Error Code Definitions
# ============================================================================


ERROR_CODES = {
    # Spotify Integration Errors
    "spotify_not_configured": {
        "message": "Spotify integration not configured. Please set up Spotify in Home Assistant first.",
        "troubleshooting": [
            "Go to Settings > Devices & Services",
            "Click 'Add Integration' and search for 'Spotify'",
            "Follow the setup instructions to connect your Spotify account",
        ],
    },
    "spotify_service_unavailable": {
        "message": "Spotify service is currently unavailable. Please try again later.",
        "troubleshooting": [
            "Check your internet connection",
            "Verify Spotify integration is loaded in HA",
            "Try reloading the Spotify integration",
        ],
    },
    "spotify_token_expired": {
        "message": "Spotify authentication has expired. Please reconnect your Spotify account.",
        "troubleshooting": [
            "Go to Settings > Devices & Services > Spotify",
            "Click 'Reconfigure' to refresh authentication",
        ],
    },
    "spotify_network_timeout": {
        "message": "Connection to Spotify timed out. Retrying...",
        "troubleshooting": [
            "Check your internet connection",
            "Wait a moment and try again",
        ],
    },

    # Playlist Errors
    "playlist_not_found": {
        "message": "Playlist not found. Please check your playlist URL.",
        "troubleshooting": [
            "Verify the playlist URL is correct",
            "Make sure the playlist is public or you have access",
            "Try copying the playlist link from Spotify again",
        ],
    },
    "playlist_invalid_uri": {
        "message": "Invalid playlist URI format.",
        "troubleshooting": [
            "Use format: spotify:playlist:XXXXX",
            "Or paste the full Spotify playlist URL",
            "Example: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        ],
    },
    "playlist_exhausted": {
        "message": "All songs have been played. End the game or reload the playlist.",
        "troubleshooting": [
            "Click 'Reset Game' to play again",
            "Or load a different playlist with more songs",
        ],
    },
    "playlist_empty": {
        "message": "Playlist is empty or has no valid songs in the year range.",
        "troubleshooting": [
            "Choose a different playlist with more songs",
            "Adjust the year range to include more songs",
            "Verify the playlist has tracks in Spotify",
        ],
    },
    "insufficient_tracks": {
        "message": "Not enough tracks available. At least 10 songs required.",
        "troubleshooting": [
            "Choose a playlist with more songs",
            "Widen the year range in game settings",
        ],
    },

    # Media Player Errors
    "no_media_players": {
        "message": "No Spotify players found. Please check your Home Assistant integration.",
        "troubleshooting": [
            "Ensure you have a Spotify-capable device (Chromecast, Sonos, etc.)",
            "Check that devices are powered on and connected",
            "Verify the Spotify integration is working in HA",
        ],
    },
    "media_player_unavailable": {
        "message": "Selected media player is currently unavailable.",
        "troubleshooting": [
            "Check that the device is powered on",
            "Verify the device is connected to your network",
            "Try selecting a different media player",
        ],
    },
    "playback_failed": {
        "message": "Failed to play track. Retrying...",
        "troubleshooting": [
            "Check that your media player is working",
            "Verify Spotify is accessible on the device",
            "Try skipping to the next song",
        ],
    },

    # WebSocket Errors
    "websocket_disconnected": {
        "message": "Connection lost. Reconnecting...",
        "troubleshooting": [
            "Check your internet connection",
            "Wait for automatic reconnection",
            "If it persists, refresh the page",
        ],
    },
    "websocket_connection_failed": {
        "message": "Failed to connect to game server.",
        "troubleshooting": [
            "Check your internet connection",
            "Verify Home Assistant is running",
            "Try refreshing the page",
        ],
    },
    "message_send_failed": {
        "message": "Failed to send message. Retrying...",
        "troubleshooting": [
            "Wait for reconnection",
            "If it persists, refresh the page",
        ],
    },

    # Game State Errors
    "no_active_game": {
        "message": "No active game found. Please start a game first.",
        "troubleshooting": [
            "Go to admin page and click 'Start Game'",
        ],
    },
    "no_active_round": {
        "message": "No active round. Wait for admin to start the next round.",
        "troubleshooting": [
            "Wait for the admin to click 'Next Song'",
        ],
    },
    "game_state_corrupted": {
        "message": "Game state is corrupted. Resetting...",
        "troubleshooting": [
            "The game has been automatically reset",
            "Please start a new game",
        ],
    },
    "timer_expired": {
        "message": "Time's up! Round has ended.",
        "troubleshooting": [],
    },
    "already_submitted": {
        "message": "You've already submitted a guess for this round.",
        "troubleshooting": [
            "Wait for the next round to guess again",
        ],
    },

    # Validation Errors
    "validation_error": {
        "message": "Invalid input. Please check your data.",
        "troubleshooting": [],
    },
    "insufficient_players": {
        "message": "At least 2 players required to start the game.",
        "troubleshooting": [
            "Wait for more players to join",
            "Share the player URL with friends",
        ],
    },
    "invalid_player_name": {
        "message": "Player name cannot be empty.",
        "troubleshooting": [
            "Enter a valid player name",
        ],
    },

    # Authentication Errors
    "unauthorized": {
        "message": "Only the admin can perform this action.",
        "troubleshooting": [
            "Make sure you're using the admin page",
            "Ask the game host to perform this action",
        ],
    },
    "session_not_found": {
        "message": "Session not found. Please rejoin the game.",
        "troubleshooting": [
            "Refresh the page and enter your name again",
        ],
    },
    "session_expired": {
        "message": "Session expired. Please rejoin the game.",
        "troubleshooting": [
            "Refresh the page and enter your name again",
        ],
    },

    # Generic Errors
    "internal_error": {
        "message": "An unexpected error occurred. Please try again.",
        "troubleshooting": [
            "Try refreshing the page",
            "If it persists, check Home Assistant logs",
        ],
    },
    "service_unavailable": {
        "message": "Service temporarily unavailable. Please try again.",
        "troubleshooting": [
            "Wait a moment and try again",
            "Check that Home Assistant is running properly",
        ],
    },
}


# ============================================================================
# Error Response Helper Functions
# ============================================================================


def create_error_response(
    error_code: str,
    details: Optional[dict[str, Any]] = None,
    custom_message: Optional[str] = None,
) -> ErrorResponse:
    """Create a standardized error response.

    Args:
        error_code: Error code from ERROR_CODES dictionary
        details: Optional additional context for debugging
        custom_message: Optional custom message (overrides default)

    Returns:
        ErrorResponse object with user-friendly message

    Example:
        >>> error = create_error_response("playlist_not_found",
        ...     details={"playlist_uri": "spotify:playlist:invalid"})
        >>> print(error.message)
        "Playlist not found. Please check your playlist URL."
    """
    error_info = ERROR_CODES.get(error_code, ERROR_CODES["internal_error"])

    message = custom_message or error_info["message"]
    troubleshooting = error_info.get("troubleshooting")

    return ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        troubleshooting=troubleshooting,
    )


def log_error(
    error_code: str,
    context: Optional[dict[str, Any]] = None,
    exception: Optional[Exception] = None,
    level: str = "error",
) -> None:
    """Log error with consistent formatting and context.

    Args:
        error_code: Error code from ERROR_CODES
        context: Additional context (player name, round number, etc.)
        exception: Optional exception object for stack trace
        level: Log level ("debug", "info", "warning", "error")

    Example:
        >>> log_error("playlist_not_found",
        ...     context={"playlist_uri": "spotify:playlist:123"},
        ...     level="warning")
    """
    log_func = getattr(_LOGGER, level, _LOGGER.error)

    error_info = ERROR_CODES.get(error_code, ERROR_CODES["internal_error"])
    message = error_info["message"]

    log_message = f"[{error_code}] {message}"

    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        log_message += f" | Context: {context_str}"

    if exception:
        log_func(log_message, exc_info=exception)
    else:
        log_func(log_message)


def handle_exception(
    exception: Exception,
    context: Optional[dict[str, Any]] = None,
    fallback_code: str = "internal_error",
) -> ErrorResponse:
    """Convert exception to standardized error response.

    Maps known exception types to appropriate error codes and logs with context.

    Args:
        exception: The exception to handle
        context: Additional context for logging
        fallback_code: Error code to use if exception type not recognized

    Returns:
        ErrorResponse object

    Example:
        >>> try:
        ...     # some operation
        ... except Exception as e:
        ...     error = handle_exception(e, context={"player": "Alice"})
        ...     return error.to_dict()
    """
    from .game_state import PlaylistExhaustedError
    from .spotify_helper import SpotifyPlaylistNotFound, SpotifyAPIError

    # Map exception types to error codes
    exception_map = {
        PlaylistExhaustedError: "playlist_exhausted",
        SpotifyPlaylistNotFound: "playlist_not_found",
        SpotifyAPIError: "spotify_service_unavailable",
        ValueError: "validation_error",
        TimeoutError: "spotify_network_timeout",
    }

    error_code = exception_map.get(type(exception), fallback_code)

    # Log the exception with context
    log_error(error_code, context=context, exception=exception, level="error")

    # Create error response
    details = {"exception_type": type(exception).__name__}
    if context:
        details.update(context)

    return create_error_response(error_code, details=details)


# ============================================================================
# Retry Logic Helper
# ============================================================================


async def retry_with_backoff(
    operation: callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    error_code: str = "internal_error",
    context: Optional[dict[str, Any]] = None,
):
    """Retry an async operation with exponential backoff.

    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds between retries
        backoff_factor: Multiplier for delay on each retry
        error_code: Error code for logging
        context: Additional context for logging

    Returns:
        Result of successful operation

    Raises:
        Last exception if all retries fail

    Example:
        >>> result = await retry_with_backoff(
        ...     lambda: spotify_api_call(),
        ...     max_retries=3,
        ...     error_code="spotify_service_unavailable"
        ... )
    """
    import asyncio

    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_exception = e

            if attempt < max_retries - 1:
                retry_context = {
                    **(context or {}),
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "delay": delay,
                }
                log_error(
                    error_code,
                    context=retry_context,
                    exception=e,
                    level="warning",
                )

                await asyncio.sleep(delay)
                delay *= backoff_factor

    # All retries failed
    log_error(
        error_code,
        context={**(context or {}), "attempts": max_retries, "status": "failed"},
        exception=last_exception,
        level="error",
    )

    raise last_exception
