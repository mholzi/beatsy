"""State stress test module for Beatsy POC validation.

This module validates that Home Assistant's in-memory storage can handle rapid
game state updates. Tests both legacy hass.data and modern entry.runtime_data
patterns to compare performance and validate migration path.

STORAGE STRATEGY (HA 2025 Best Practice):
==========================================

Two storage patterns are tested:

1. LEGACY PATTERN - hass.data[DOMAIN]:
   - Traditional Home Assistant data storage
   - Dictionary-based, untyped access
   - Manual cleanup required
   - Used in older integrations
   - Performance: Fast (in-memory)
   - Use case: Backward compatibility

2. MODERN PATTERN - entry.runtime_data (RECOMMENDED):
   - Introduced in Home Assistant 2024.6+
   - Type-safe storage with dataclasses
   - Automatic cleanup on unload
   - Better IDE support and type checking
   - Performance: Fast (in-memory, similar to hass.data)
   - Use case: NEW integrations, production code

RECOMMENDATION FOR PRODUCTION (Epic 2+):
========================================
Use entry.runtime_data pattern for the following reasons:
- Type safety: Full IDE autocomplete and type checking
- Cleaner code: Direct dataclass access vs dict operations
- Automatic cleanup: HA handles cleanup on unload
- Better maintainability: Typed structures prevent bugs
- HA 2025 best practice: Official recommendation from HA core team

STORAGE APPROACH FOR BEATSY:
=============================
- Active game state: In-memory (entry.runtime_data) - Fast, ephemeral
- Game configuration: Persistent (hass.helpers.storage) - Survives restarts
- Rationale: Games are ephemeral by nature, players expect reset on restart
- Performance: In-memory eliminates I/O latency during rapid updates

This test validates that in-memory storage (both patterns) meets performance
targets for rapid game state updates during active gameplay.

Reference: https://developers.home-assistant.io/blog/2024/04/30/store-runtime-data-inside-config-entry/
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# 2025 Pattern: Typed dataclasses for structured game state


@dataclass
class Player:
    """Player data structure."""

    name: str
    score: int


@dataclass
class Guess:
    """Player guess data structure."""

    player: str
    year: int
    bet: bool


@dataclass
class Round:
    """Game round data structure."""

    song_uri: str
    started_at: int
    timer_duration: int
    guesses: list[Guess]


@dataclass
class GameStateData:
    """
    Complete game state data structure for HA 2025 pattern.

    This typed dataclass is used with entry.runtime_data for type-safe storage.
    For legacy hass.data pattern, convert to dict with asdict().
    """

    players: list[Player]
    current_round: Round
    played_songs: list[str]


@dataclass
class PerformanceMetrics:
    """Performance metrics for POC validation."""

    test_type: str
    storage_pattern: str  # "hass.data" or "entry.runtime_data"
    total_operations: int
    duration_seconds: float
    success_count: int
    failure_count: int
    avg_latency_ms: float
    max_latency_ms: float
    errors: list[str] = field(default_factory=list)


# Type alias for typed ConfigEntry (HA 2025 pattern)
BeatsyConfigEntry: TypeAlias = "ConfigEntry[GameStateData]"


def _create_initial_game_state() -> GameStateData:
    """Create initial game state with 10 players and realistic data."""
    players = [
        Player(name=f"Player{i+1}", score=i * 5)  # 0, 5, 10, 15, ...
        for i in range(10)
    ]

    current_round = Round(
        song_uri="spotify:track:mock_uri_12345",
        started_at=int(time.time()),
        timer_duration=30,
        guesses=[
            Guess(player="Player1", year=1985, bet=True),
            Guess(player="Player2", year=1987, bet=False),
        ],
    )

    played_songs = [
        "spotify:track:song1",
        "spotify:track:song2",
        "spotify:track:song3",
    ]

    return GameStateData(
        players=players,
        current_round=current_round,
        played_songs=played_songs,
    )


async def run_state_stress_test(
    hass: HomeAssistant,
    use_runtime_data: bool = False,
) -> PerformanceMetrics:
    """
    Run state stress test with 100 write+read cycles.

    Args:
        hass: Home Assistant instance
        use_runtime_data: If True, use entry.runtime_data pattern (2025)
                         If False, use hass.data pattern (legacy)

    Returns:
        PerformanceMetrics with results and storage pattern used
    """
    from .const import DOMAIN

    storage_pattern = "entry.runtime_data" if use_runtime_data else "hass.data"
    _LOGGER.info(
        "Starting state stress test with %s pattern (100 write+read cycles)",
        storage_pattern,
    )

    # Initialize game state
    initial_state = _create_initial_game_state()

    # Setup storage based on pattern
    if use_runtime_data:
        # Create mock config entry for runtime_data pattern
        # In production, this would be a real ConfigEntry
        from homeassistant.config_entries import ConfigEntry

        mock_entry = ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Beatsy Test",
            data={},
            source="test",
        )
        mock_entry.runtime_data = initial_state
        storage_ref = mock_entry
    else:
        # Legacy hass.data pattern
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN]["game_state"] = asdict(initial_state)
        storage_ref = hass

    # Performance tracking
    latencies: list[float] = []
    success_count = 0
    failure_count = 0
    errors: list[str] = []

    start_time = time.perf_counter()

    # Run 100 write+read cycles
    for i in range(100):
        cycle_start = time.perf_counter()

        try:
            # Write: Increment random player's score
            player_idx = i % 10  # Cycle through all 10 players
            expected_score = initial_state.players[player_idx].score + (i // 10) + 1

            if use_runtime_data:
                # entry.runtime_data pattern: Direct dataclass access
                storage_ref.runtime_data.players[player_idx].score = expected_score
            else:
                # hass.data pattern: Dict access
                storage_ref.data[DOMAIN]["game_state"]["players"][player_idx][
                    "score"
                ] = expected_score

            # Read: Retrieve and validate score
            if use_runtime_data:
                actual_score = storage_ref.runtime_data.players[player_idx].score
            else:
                actual_score = storage_ref.data[DOMAIN]["game_state"]["players"][
                    player_idx
                ]["score"]

            # Data integrity validation
            if actual_score != expected_score:
                error_msg = (
                    f"Data corruption at cycle {i}: "
                    f"expected {expected_score}, got {actual_score}"
                )
                _LOGGER.error(error_msg)
                errors.append(error_msg)
                failure_count += 1
            else:
                success_count += 1

            cycle_end = time.perf_counter()
            latency_ms = (cycle_end - cycle_start) * 1000
            latencies.append(latency_ms)

        except Exception as e:
            error_msg = f"Error at cycle {i}: {e!s}"
            _LOGGER.error(error_msg)
            errors.append(error_msg)
            failure_count += 1

            # Record latency even for failures
            cycle_end = time.perf_counter()
            latency_ms = (cycle_end - cycle_start) * 1000
            latencies.append(latency_ms)

    end_time = time.perf_counter()
    duration_seconds = end_time - start_time

    # Calculate metrics
    avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0
    max_latency_ms = max(latencies) if latencies else 0

    metrics = PerformanceMetrics(
        test_type="state_writes",
        storage_pattern=storage_pattern,
        total_operations=100,
        duration_seconds=round(duration_seconds, 2),
        success_count=success_count,
        failure_count=failure_count,
        avg_latency_ms=round(avg_latency_ms, 2),
        max_latency_ms=round(max_latency_ms, 2),
        errors=errors,
    )

    _LOGGER.info(
        "Beatsy: State test completed - %d ops in %.2fs (pattern: %s)",
        metrics.total_operations,
        metrics.duration_seconds,
        storage_pattern,
    )
    _LOGGER.info(
        "Performance: avg %.2fms, max %.2fms, success rate: %d/%d",
        metrics.avg_latency_ms,
        metrics.max_latency_ms,
        success_count,
        metrics.total_operations,
    )

    return metrics
