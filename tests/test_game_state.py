"""Tests for game_state.py module.

This module tests the type-safe in-memory game state management system,
including state initialization, accessor functions, and config persistence.

NOTE: These tests are standalone and simulate Home Assistant functionality
without requiring the full HA installation.
"""
import sys
from pathlib import Path
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import dataclass, field
from typing import Any, TypedDict, Optional

# Create mock Home Assistant classes
class MockHomeAssistant:
    """Mock HomeAssistant class for testing."""
    def __init__(self):
        self.data = {}

class MockStore:
    """Mock Store class for testing."""
    def __init__(self, hass, version, key):
        self.hass = hass
        self.version = version
        self.key = key
        self._data = {}

    async def async_load(self):
        return self._data.get(self.key)

    async def async_save(self, data):
        self._data[self.key] = data

# Define constants from const.py
DOMAIN = "beatsy"

# Define types from game_state.py (copied to avoid import issues)
class GameConfig(TypedDict, total=False):
    """Game configuration settings."""
    playlist_uri: str
    media_player_entity_id: str
    round_timer_seconds: int
    points_exact: int
    points_close: int
    points_near: int
    points_bet_multiplier: float


@dataclass
class Player:
    """Player data model."""
    name: str
    session_id: str = ""
    score: int = 0
    is_admin: bool = False
    guesses: list[int] = field(default_factory=list)
    bets_placed: list[bool] = field(default_factory=list)
    joined_at: float = field(default_factory=time.time)


@dataclass
class RoundState:
    """Current round state."""
    round_number: int
    track_uri: str
    track_name: str
    track_artist: str
    correct_year: int
    guesses: dict[str, dict[str, Any]] = field(default_factory=dict)
    status: str = "active"
    timer_started_at: Optional[float] = None
    started_at: float = field(default_factory=time.time)


@dataclass
class BeatsyGameState:
    """Complete game state structure."""
    game_config: GameConfig = field(default_factory=dict)
    players: list[Player] = field(default_factory=list)
    current_round: Optional[RoundState] = None
    played_songs: list[str] = field(default_factory=list)
    available_songs: list[dict[str, Any]] = field(default_factory=list)
    websocket_connections: dict[str, Any] = field(default_factory=dict)
    game_started: bool = False
    game_started_at: Optional[float] = None
    spotify: dict[str, Any] = field(default_factory=dict)

# Load the actual game_state module code
game_state_file = Path(__file__).parent.parent / "home-assistant-config" / "custom_components" / "beatsy" / "game_state.py"
game_state_code = game_state_file.read_text()

# Execute game_state code in a controlled namespace
namespace = {
    '__name__': 'game_state',
    'logging': __import__('logging'),
    'time': time,
    'dataclass': dataclass,
    'field': field,
    'Any': Any,
    'TypedDict': TypedDict,
    'HomeAssistant': MockHomeAssistant,
    'Store': MockStore,
    'DOMAIN': DOMAIN,
}

# Parse and skip imports
lines = game_state_code.split('\n')
filtered_lines = []
skip_imports = False
for line in lines:
    if line.startswith('from __future__'):
        continue
    if line.startswith('import ') or line.startswith('from '):
        if 'homeassistant' in line or 'const' in line:
            continue
    filtered_lines.append(line)

# Execute the filtered code
exec('\n'.join(filtered_lines), namespace)

# Extract functions AND classes we need (use the ones from game_state module, not our copies)
init_game_state = namespace['init_game_state']
get_game_state = namespace['get_game_state']
get_game_config = namespace['get_game_config']
update_game_config = namespace['update_game_config']
get_players = namespace['get_players']
add_player = namespace['add_player']
get_player = namespace['get_player']
update_player_score = namespace['update_player_score']
reset_players = namespace['reset_players']
get_current_round = namespace['get_current_round']
set_current_round = namespace['set_current_round']
clear_current_round = namespace['clear_current_round']
add_guess = namespace['add_guess']
update_bet = namespace['update_bet']
get_played_songs = namespace['get_played_songs']
add_played_song = namespace['add_played_song']
is_song_played = namespace['is_song_played']
clear_played_songs = namespace['clear_played_songs']
initialize_game = namespace['initialize_game']
load_config = namespace['load_config']
save_config = namespace['save_config']

# Override our class definitions with the ones from game_state module
BeatsyGameState = namespace['BeatsyGameState']
Player = namespace['Player']
RoundState = namespace['RoundState']
GameConfig = namespace['GameConfig']


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def hass():
    """Create a mock Home Assistant instance."""
    return MockHomeAssistant()


@pytest.fixture
def entry_id():
    """Return a test entry ID."""
    return "test_entry_123"


@pytest.fixture
def initialized_hass(hass, entry_id):
    """Create a hass instance with initialized game state."""
    init_game_state(hass, entry_id)
    return hass


# ============================================================================
# Test State Initialization
# ============================================================================


def test_init_game_state(hass, entry_id):
    """Test state initialization creates BeatsyGameState instance."""
    state = init_game_state(hass, entry_id)

    # Verify state is correct type
    assert isinstance(state, BeatsyGameState)

    # Verify state stored in hass.data
    assert DOMAIN in hass.data
    assert entry_id in hass.data[DOMAIN]
    assert hass.data[DOMAIN][entry_id] is state

    # Verify default field values
    assert state.players == []
    assert state.current_round is None
    assert state.played_songs == []
    assert state.available_songs == []
    assert state.websocket_connections == {}
    assert state.game_started is False
    assert state.game_started_at is None
    assert state.game_config == {}
    assert state.spotify == {}


def test_get_game_state(initialized_hass, entry_id):
    """Test getting game state for an entry."""
    state = get_game_state(initialized_hass, entry_id)

    assert isinstance(state, BeatsyGameState)
    assert state is initialized_hass.data[DOMAIN][entry_id]


def test_get_game_state_without_entry_id(initialized_hass):
    """Test getting game state without specifying entry_id."""
    state = get_game_state(initialized_hass, None)

    assert isinstance(state, BeatsyGameState)


def test_get_game_state_not_initialized():
    """Test getting state when not initialized raises ValueError."""
    hass = MockHomeAssistant()

    with pytest.raises(ValueError, match="not initialized"):
        get_game_state(hass, "nonexistent_entry")


def test_get_game_state_migration_from_dict(hass, entry_id):
    """Test migration from legacy dict state to BeatsyGameState."""
    # Create legacy dict state
    hass.data[DOMAIN] = {
        entry_id: {
            "game_config": {"playlist_uri": "spotify:playlist:123"},
            "players": [{"name": "Alice", "score": 10, "session_id": "s1", "is_admin": False}],
            "current_round": None,
            "played_songs": ["spotify:track:1"],
            "available_songs": [],
            "websocket_connections": {},
            "game_started": True,
            "game_started_at": 1234567890.0,
            "spotify": {},
        }
    }

    # Get state should migrate it
    state = get_game_state(hass, entry_id)

    # Verify migration
    assert isinstance(state, BeatsyGameState)
    assert state.game_config["playlist_uri"] == "spotify:playlist:123"
    assert len(state.players) == 1
    assert isinstance(state.players[0], Player)
    assert state.players[0].name == "Alice"
    assert state.players[0].score == 10
    assert state.played_songs == ["spotify:track:1"]
    assert state.game_started is True


# ============================================================================
# Test Config Accessor Functions
# ============================================================================


def test_get_game_config(initialized_hass, entry_id):
    """Test getting game configuration."""
    config = get_game_config(initialized_hass, entry_id)

    assert isinstance(config, dict)
    assert config == {}


def test_update_game_config(initialized_hass, entry_id):
    """Test updating game configuration."""
    config: GameConfig = {
        "playlist_uri": "spotify:playlist:abc123",
        "media_player_entity_id": "media_player.spotify",
        "round_timer_seconds": 30,
        "points_exact": 10,
        "points_close": 5,
        "points_near": 2,
        "points_bet_multiplier": 2.0,
    }

    update_game_config(initialized_hass, config, entry_id)

    retrieved_config = get_game_config(initialized_hass, entry_id)
    assert retrieved_config["playlist_uri"] == "spotify:playlist:abc123"
    assert retrieved_config["round_timer_seconds"] == 30
    assert retrieved_config["points_exact"] == 10


def test_update_game_config_validates_timer(initialized_hass, entry_id):
    """Test that update_game_config validates round_timer_seconds."""
    config: GameConfig = {"round_timer_seconds": 0}

    with pytest.raises(ValueError, match="round_timer_seconds must be positive"):
        update_game_config(initialized_hass, config, entry_id)


def test_update_game_config_validates_points(initialized_hass, entry_id):
    """Test that update_game_config validates point values."""
    with pytest.raises(ValueError, match="points_exact cannot be negative"):
        update_game_config(initialized_hass, {"points_exact": -1}, entry_id)

    with pytest.raises(ValueError, match="points_close cannot be negative"):
        update_game_config(initialized_hass, {"points_close": -1}, entry_id)

    with pytest.raises(ValueError, match="points_near cannot be negative"):
        update_game_config(initialized_hass, {"points_near": -1}, entry_id)


def test_update_game_config_validates_multiplier(initialized_hass, entry_id):
    """Test that update_game_config validates bet multiplier."""
    with pytest.raises(ValueError, match="points_bet_multiplier must be positive"):
        update_game_config(initialized_hass, {"points_bet_multiplier": 0}, entry_id)

    with pytest.raises(ValueError, match="points_bet_multiplier must be positive"):
        update_game_config(initialized_hass, {"points_bet_multiplier": -1.5}, entry_id)


# ============================================================================
# Test Player Accessor Functions
# ============================================================================


def test_get_players_empty(initialized_hass, entry_id):
    """Test getting players when list is empty."""
    players = get_players(initialized_hass, entry_id)

    assert players == []


def test_add_player(initialized_hass, entry_id):
    """Test adding a player."""
    add_player(initialized_hass, "Alice", "session123", False, entry_id)

    players = get_players(initialized_hass, entry_id)
    assert len(players) == 1
    assert players[0].name == "Alice"
    assert players[0].session_id == "session123"
    assert players[0].score == 0
    assert players[0].is_admin is False


def test_add_player_duplicate_raises(initialized_hass, entry_id):
    """Test that adding duplicate player raises ValueError."""
    add_player(initialized_hass, "Alice", "s1", False, entry_id)

    with pytest.raises(ValueError, match="already exists"):
        add_player(initialized_hass, "Alice", "s2", False, entry_id)


def test_get_player(initialized_hass, entry_id):
    """Test getting player by name."""
    add_player(initialized_hass, "Alice", "s1", False, entry_id)
    add_player(initialized_hass, "Bob", "s2", False, entry_id)

    player = get_player(initialized_hass, "Alice", entry_id)
    assert player is not None
    assert player.name == "Alice"
    assert player.session_id == "s1"


def test_get_player_not_found(initialized_hass, entry_id):
    """Test getting non-existent player returns None."""
    player = get_player(initialized_hass, "NonExistent", entry_id)
    assert player is None


def test_update_player_score(initialized_hass, entry_id):
    """Test updating player score."""
    add_player(initialized_hass, "Alice", "s1", False, entry_id)

    # Add points
    update_player_score(initialized_hass, "Alice", 10, entry_id)
    player = get_player(initialized_hass, "Alice", entry_id)
    assert player.score == 10

    # Add more points
    update_player_score(initialized_hass, "Alice", 5, entry_id)
    assert player.score == 15

    # Subtract points
    update_player_score(initialized_hass, "Alice", -3, entry_id)
    assert player.score == 12


def test_update_player_score_not_found(initialized_hass, entry_id):
    """Test updating score for non-existent player raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        update_player_score(initialized_hass, "NonExistent", 10, entry_id)


def test_reset_players(initialized_hass, entry_id):
    """Test resetting players clears the list."""
    add_player(initialized_hass, "Alice", "s1", False, entry_id)
    add_player(initialized_hass, "Bob", "s2", False, entry_id)

    assert len(get_players(initialized_hass, entry_id)) == 2

    reset_players(initialized_hass, entry_id)

    assert len(get_players(initialized_hass, entry_id)) == 0


# ============================================================================
# Test Round Accessor Functions
# ============================================================================


def test_get_current_round_none(initialized_hass, entry_id):
    """Test getting current round when no round active."""
    current_round = get_current_round(initialized_hass, entry_id)
    assert current_round is None


def test_set_current_round(initialized_hass, entry_id):
    """Test setting current round."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:abc123",
        track_name="Test Song",
        track_artist="Test Artist",
        correct_year=1995,
    )

    set_current_round(initialized_hass, round_state, entry_id)

    retrieved_round = get_current_round(initialized_hass, entry_id)
    assert retrieved_round is not None
    assert retrieved_round.round_number == 1
    assert retrieved_round.track_name == "Test Song"
    assert retrieved_round.correct_year == 1995
    assert retrieved_round.status == "active"
    assert retrieved_round.timer_started_at is not None


def test_clear_current_round(initialized_hass, entry_id):
    """Test clearing current round."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    )
    set_current_round(initialized_hass, round_state, entry_id)

    assert get_current_round(initialized_hass, entry_id) is not None

    clear_current_round(initialized_hass, entry_id)

    assert get_current_round(initialized_hass, entry_id) is None


def test_add_guess(initialized_hass, entry_id):
    """Test adding player guess to current round."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    )
    set_current_round(initialized_hass, round_state, entry_id)

    add_guess(initialized_hass, "Alice", 1998, False, entry_id)

    retrieved_round = get_current_round(initialized_hass, entry_id)
    assert "Alice" in retrieved_round.guesses
    assert retrieved_round.guesses["Alice"]["year"] == 1998
    assert retrieved_round.guesses["Alice"]["bet"] is False


def test_add_guess_with_bet(initialized_hass, entry_id):
    """Test adding guess with bet placed."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    )
    set_current_round(initialized_hass, round_state, entry_id)

    add_guess(initialized_hass, "Alice", 2001, True, entry_id)

    retrieved_round = get_current_round(initialized_hass, entry_id)
    assert retrieved_round.guesses["Alice"]["bet"] is True


def test_add_guess_no_active_round(initialized_hass, entry_id):
    """Test adding guess when no active round raises ValueError."""
    with pytest.raises(ValueError, match="No active round"):
        add_guess(initialized_hass, "Alice", 2000, False, entry_id)


def test_add_guess_round_not_active(initialized_hass, entry_id):
    """Test adding guess when round ended raises ValueError."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
        status="ended",
    )
    set_current_round(initialized_hass, round_state, entry_id)

    with pytest.raises(ValueError, match="Round is not active"):
        add_guess(initialized_hass, "Alice", 2000, False, entry_id)


def test_update_bet(initialized_hass, entry_id):
    """Test updating player bet status."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    )
    set_current_round(initialized_hass, round_state, entry_id)

    # Add initial guess without bet
    add_guess(initialized_hass, "Alice", 2001, False, entry_id)

    # Update bet status
    update_bet(initialized_hass, "Alice", True, entry_id)

    retrieved_round = get_current_round(initialized_hass, entry_id)
    assert retrieved_round.guesses["Alice"]["bet"] is True


def test_update_bet_no_round(initialized_hass, entry_id):
    """Test updating bet when no active round raises ValueError."""
    with pytest.raises(ValueError, match="No active round"):
        update_bet(initialized_hass, "Alice", True, entry_id)


# ============================================================================
# Test Song History Functions
# ============================================================================


def test_get_played_songs_empty(initialized_hass, entry_id):
    """Test getting played songs when list is empty."""
    played_songs = get_played_songs(initialized_hass, entry_id)
    assert played_songs == []


def test_add_played_song(initialized_hass, entry_id):
    """Test adding song to played history."""
    add_played_song(initialized_hass, "spotify:track:abc123", entry_id)

    played_songs = get_played_songs(initialized_hass, entry_id)
    assert len(played_songs) == 1
    assert "spotify:track:abc123" in played_songs


def test_add_played_song_prevents_duplicates(initialized_hass, entry_id):
    """Test that adding same song twice doesn't create duplicate."""
    add_played_song(initialized_hass, "spotify:track:abc123", entry_id)
    add_played_song(initialized_hass, "spotify:track:abc123", entry_id)

    played_songs = get_played_songs(initialized_hass, entry_id)
    assert len(played_songs) == 1


def test_is_song_played(initialized_hass, entry_id):
    """Test checking if song has been played."""
    assert is_song_played(initialized_hass, "spotify:track:123", entry_id) is False

    add_played_song(initialized_hass, "spotify:track:123", entry_id)

    assert is_song_played(initialized_hass, "spotify:track:123", entry_id) is True
    assert is_song_played(initialized_hass, "spotify:track:456", entry_id) is False


def test_clear_played_songs(initialized_hass, entry_id):
    """Test clearing played songs history."""
    add_played_song(initialized_hass, "spotify:track:1", entry_id)
    add_played_song(initialized_hass, "spotify:track:2", entry_id)

    assert len(get_played_songs(initialized_hass, entry_id)) == 2

    clear_played_songs(initialized_hass, entry_id)

    assert len(get_played_songs(initialized_hass, entry_id)) == 0


# ============================================================================
# Test Game Initialization (backward compatibility)
# ============================================================================


def test_initialize_game(initialized_hass, entry_id):
    """Test initializing game with config."""
    config = {
        "playlist_uri": "spotify:playlist:123",
        "media_player_entity_id": "media_player.spotify",
    }

    initialize_game(initialized_hass, config, entry_id)

    state = get_game_state(initialized_hass, entry_id)
    assert state.game_started is True
    assert state.game_started_at is not None
    assert state.game_config["playlist_uri"] == "spotify:playlist:123"


# ============================================================================
# Test Config Persistence
# ============================================================================


@pytest.mark.asyncio
async def test_load_config_no_file(hass, entry_id):
    """Test loading config when no file exists returns empty dict."""
    with patch.object(MockStore, "async_load", new_callable=AsyncMock) as mock_load:
        mock_load.return_value = None

        config = await load_config(hass, entry_id)

        assert config == {}


@pytest.mark.asyncio
async def test_load_config_with_data(hass, entry_id):
    """Test loading config from storage."""
    stored_data = {
        "playlist_uri": "spotify:playlist:abc",
        "round_timer_seconds": 45,
    }

    with patch.object(MockStore, "async_load", new_callable=AsyncMock) as mock_load:
        mock_load.return_value = stored_data

        config = await load_config(hass, entry_id)

        assert config["playlist_uri"] == "spotify:playlist:abc"
        assert config["round_timer_seconds"] == 45


@pytest.mark.asyncio
async def test_save_config(hass, entry_id):
    """Test saving config to storage."""
    config: GameConfig = {
        "playlist_uri": "spotify:playlist:xyz",
        "points_exact": 15,
    }

    with patch.object(MockStore, "async_save", new_callable=AsyncMock) as mock_save:
        await save_config(hass, config, entry_id)

        mock_save.assert_called_once_with(config)


# ============================================================================
# Test Integration - Full State Lifecycle
# ============================================================================


def test_full_game_lifecycle(hass, entry_id):
    """Test complete game state lifecycle."""
    # 1. Initialize state
    state = init_game_state(hass, entry_id)
    assert isinstance(state, BeatsyGameState)

    # 2. Configure game
    config: GameConfig = {
        "playlist_uri": "spotify:playlist:test",
        "media_player_entity_id": "media_player.spotify",
        "round_timer_seconds": 30,
        "points_exact": 10,
        "points_close": 5,
    }
    update_game_config(hass, config, entry_id)

    # 3. Add players
    add_player(hass, "Alice", "session1", True, entry_id)
    add_player(hass, "Bob", "session2", False, entry_id)
    add_player(hass, "Charlie", "session3", False, entry_id)

    assert len(get_players(hass, entry_id)) == 3

    # 4. Start first round
    round1 = RoundState(
        round_number=1,
        track_uri="spotify:track:song1",
        track_name="Great Song",
        track_artist="Famous Artist",
        correct_year=1985,
    )
    set_current_round(hass, round1, entry_id)

    # 5. Add song to history
    add_played_song(hass, "spotify:track:song1", entry_id)

    # 6. Players submit guesses
    add_guess(hass, "Alice", 1985, True, entry_id)
    add_guess(hass, "Bob", 1987, False, entry_id)
    add_guess(hass, "Charlie", 1990, False, entry_id)

    current_round = get_current_round(hass, entry_id)
    assert len(current_round.guesses) == 3

    # 7. Update scores
    update_player_score(hass, "Alice", 20, entry_id)  # Exact + bet
    update_player_score(hass, "Bob", 5, entry_id)  # Close

    # 8. End round
    clear_current_round(hass, entry_id)
    assert get_current_round(hass, entry_id) is None

    # 9. Verify final state
    players = get_players(hass, entry_id)
    alice = next(p for p in players if p.name == "Alice")
    bob = next(p for p in players if p.name == "Bob")
    charlie = next(p for p in players if p.name == "Charlie")

    assert alice.score == 20
    assert bob.score == 5
    assert charlie.score == 0

    assert len(get_played_songs(hass, entry_id)) == 1
    assert is_song_played(hass, "spotify:track:song1", entry_id)

    # 10. Start second round
    round2 = RoundState(
        round_number=2,
        track_uri="spotify:track:song2",
        track_name="Another Song",
        track_artist="Another Artist",
        correct_year=2005,
    )
    set_current_round(hass, round2, entry_id)

    assert get_current_round(hass, entry_id).round_number == 2


# ============================================================================
# Test Performance - In-Memory Speed
# ============================================================================


def test_state_access_performance(initialized_hass, entry_id):
    """Test that state access is fast (<1ms)."""
    # Add test data
    for i in range(10):
        add_player(initialized_hass, f"Player{i}", f"s{i}", False, entry_id)

    # Measure get_players call time
    start = time.time()
    result = get_players(initialized_hass, entry_id)
    elapsed = time.time() - start

    assert len(result) == 10
    # We expect <1ms for in-memory operations
    assert elapsed < 0.001, f"get_players took {elapsed*1000:.2f}ms, expected <1ms"


def test_player_operations_performance(initialized_hass, entry_id):
    """Test that 1000 player operations complete quickly."""
    start = time.time()

    # Perform 1000 operations
    for i in range(100):
        add_player(initialized_hass, f"Player{i}", f"s{i}", False, entry_id)

    for i in range(100):
        get_player(initialized_hass, f"Player{i}", entry_id)

    for i in range(100):
        update_player_score(initialized_hass, f"Player{i}", 10, entry_id)

    elapsed = time.time() - start

    # 300 operations should complete in well under 100ms
    assert elapsed < 0.1, f"Operations took {elapsed*1000:.2f}ms, expected <100ms"


def test_round_operations_performance(initialized_hass, entry_id):
    """Test round operations are fast."""
    start = time.time()

    # Create and set 100 rounds
    for i in range(100):
        round_state = RoundState(
            round_number=i,
            track_uri=f"spotify:track:{i}",
            track_name=f"Song {i}",
            track_artist=f"Artist {i}",
            correct_year=2000 + i,
        )
        set_current_round(initialized_hass, round_state, entry_id)
        get_current_round(initialized_hass, entry_id)
        clear_current_round(initialized_hass, entry_id)

    elapsed = time.time() - start

    # 300 operations (set + get + clear) should be fast
    assert elapsed < 0.1, f"Operations took {elapsed*1000:.2f}ms, expected <100ms"


# ============================================================================
# Test Type Safety
# ============================================================================


def test_player_dataclass_types():
    """Test Player dataclass has correct types."""
    player = Player(name="Test", session_id="s1", is_admin=True)

    assert isinstance(player.name, str)
    assert isinstance(player.session_id, str)
    assert isinstance(player.score, int)
    assert isinstance(player.is_admin, bool)
    assert isinstance(player.guesses, list)
    assert isinstance(player.bets_placed, list)


def test_round_state_dataclass_types():
    """Test RoundState dataclass has correct types."""
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    )

    assert isinstance(round_state.round_number, int)
    assert isinstance(round_state.track_uri, str)
    assert isinstance(round_state.track_name, str)
    assert isinstance(round_state.track_artist, str)
    assert isinstance(round_state.correct_year, int)
    assert isinstance(round_state.guesses, dict)
    assert isinstance(round_state.status, str)


def test_beatsy_game_state_types():
    """Test BeatsyGameState dataclass has correct types."""
    state = BeatsyGameState()

    assert isinstance(state.game_config, dict)
    assert isinstance(state.players, list)
    assert state.current_round is None or isinstance(state.current_round, RoundState)
    assert isinstance(state.played_songs, list)
    assert isinstance(state.available_songs, list)
    assert isinstance(state.websocket_connections, dict)
    assert isinstance(state.game_started, bool)
    assert isinstance(state.spotify, dict)
