"""Rate limiting module for Beatsy component.

Implements rate limiting for player actions to prevent spam and abuse.

Story 10.6: Rate Limiting & Spam Prevention
- Join game: 1 per 5 seconds per IP
- Submit guess: 1 per 2 seconds per player
- Place bet: 5 per second per player
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

_LOGGER = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration.

    Attributes:
        max_attempts: Maximum number of attempts allowed
        window_seconds: Time window in seconds
    """

    max_attempts: int
    window_seconds: float


# Rate limit configurations per tech spec (Story 10.6)
RATE_LIMITS = {
    "join_game": RateLimit(max_attempts=1, window_seconds=5.0),
    "submit_guess": RateLimit(max_attempts=1, window_seconds=2.0),
    "place_bet": RateLimit(max_attempts=5, window_seconds=1.0),
}


class RateLimiter:
    """Rate limiter using sliding window algorithm.

    Tracks action timestamps in memory and enforces rate limits.
    Implements automatic cleanup to prevent memory leaks.
    """

    def __init__(self):
        """Initialize rate limiter with empty tracking map."""
        # Maps: {action_key: [timestamp1, timestamp2, ...]}
        self._rate_limit_map: Dict[str, list[float]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._logger = _LOGGER

    def check_limit(self, key: str, limit: RateLimit) -> tuple[bool, Optional[float]]:
        """Check if action is within rate limit using sliding window.

        Algorithm:
        1. Get current timestamp
        2. Clean up old timestamps outside window
        3. Count attempts in current window
        4. If count >= max_attempts: Reject with retry_after
        5. Otherwise: Allow and record timestamp

        Args:
            key: Unique identifier for rate limiting (e.g., IP address, player name)
            limit: RateLimit configuration for this action

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if action is allowed, False if rate limited
            - retry_after_seconds: Time to wait before retrying (None if allowed)
        """
        current_time = time.time()

        # Get existing timestamps for this key
        if key not in self._rate_limit_map:
            self._rate_limit_map[key] = []

        timestamps = self._rate_limit_map[key]

        # Clean up timestamps outside the current window
        # Keep only timestamps within [current_time - window_seconds, current_time]
        cutoff_time = current_time - limit.window_seconds
        timestamps[:] = [ts for ts in timestamps if ts > cutoff_time]

        # Check if rate limit exceeded
        if len(timestamps) >= limit.max_attempts:
            # Calculate retry_after: time until oldest timestamp expires
            oldest_timestamp = timestamps[0]
            retry_after = limit.window_seconds - (current_time - oldest_timestamp)

            self._logger.warning(
                "Rate limit exceeded: key=%s, attempts=%d/%d, retry_after=%.1fs",
                key,
                len(timestamps),
                limit.max_attempts,
                retry_after,
            )

            return False, retry_after

        # Allow action and record timestamp
        timestamps.append(current_time)

        self._logger.debug(
            "Rate limit check passed: key=%s, attempts=%d/%d",
            key,
            len(timestamps),
            limit.max_attempts,
        )

        return True, None

    async def start_cleanup_task(self) -> None:
        """Start background cleanup task to prevent memory leaks.

        Runs every 10 minutes and removes entries older than 5 minutes.
        Should be called during component initialization.
        """
        if self._cleanup_task is not None:
            self._logger.warning("Cleanup task already running")
            return

        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._logger.info("Rate limiter cleanup task started")

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task.

        Should be called during component shutdown.
        """
        if self._cleanup_task is None:
            return

        self._cleanup_task.cancel()
        try:
            await self._cleanup_task
        except asyncio.CancelledError:
            pass

        self._cleanup_task = None
        self._logger.info("Rate limiter cleanup task stopped")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop (runs every 10 minutes).

        Removes entries where all timestamps are older than 5 minutes.
        Prevents memory leaks from tracking state.
        """
        try:
            while True:
                await asyncio.sleep(600)  # 10 minutes
                self._cleanup_old_entries()
        except asyncio.CancelledError:
            self._logger.debug("Cleanup task cancelled")
            raise

    def _cleanup_old_entries(self) -> None:
        """Remove entries with timestamps older than 5 minutes.

        Called periodically by cleanup task to prevent memory leaks.
        """
        current_time = time.time()
        cleanup_threshold = 300  # 5 minutes

        keys_to_remove = []

        for key, timestamps in self._rate_limit_map.items():
            # Remove timestamps older than 5 minutes
            timestamps[:] = [
                ts for ts in timestamps if current_time - ts < cleanup_threshold
            ]

            # If no recent timestamps, mark key for removal
            if not timestamps:
                keys_to_remove.append(key)

        # Remove keys with no recent activity
        for key in keys_to_remove:
            del self._rate_limit_map[key]

        if keys_to_remove:
            self._logger.debug(
                "Cleaned up %d inactive rate limit entries", len(keys_to_remove)
            )

    def get_stats(self) -> dict:
        """Get rate limiter statistics for monitoring.

        Returns:
            Dictionary with:
            - total_keys: Number of tracked keys
            - total_timestamps: Total number of timestamps tracked
        """
        total_timestamps = sum(len(ts) for ts in self._rate_limit_map.values())
        return {
            "total_keys": len(self._rate_limit_map),
            "total_timestamps": total_timestamps,
        }
