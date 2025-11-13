# Story 2.3: In-Memory Game State Management

Status: done

## Story

As a **Beatsy game manager**,
I want **a structured in-memory state system using `hass.data` with modern Python type safety**,
So that **game state is fast, accessible across all modules, and maintainable with clear type contracts**.

## Acceptance Criteria

**AC-1: State Structure Initialization**
- **Given** Beatsy component is loaded via `async_setup()`
- **When** game state is initialized
- **Then** `hass.data[DOMAIN]` contains a structured `BeatsyGameState` object
- **And** state uses Python 3.14+ type hints and dataclasses
- **And** state structure includes:
  - `game_config`: Admin settings (TypedDict)
  - `players`: Player list with scores (List[Player])
  - `current_round`: Active round state (Optional[RoundState])
  - `played_songs`: Track history (List[str])
  - `websocket_connections`: Active clients (Dict[str, WebSocketConnection])

**AC-2: State Accessor Functions**
- **Given** game state is initialized
- **When** modules need to access or modify state
- **Then** accessor functions are available:
  - `get_game_config(hass) -> GameConfig`
  - `get_players(hass) -> List[Player]`
  - `add_player(hass, player: Player) -> None`
  - `update_player_score(hass, player_name: str, points: int) -> None`
  - `get_current_round(hass) -> Optional[RoundState]`
  - `set_current_round(hass, round_state: RoundState) -> None`
  - `add_played_song(hass, track_uri: str) -> None`
- **And** all functions have complete type hints
- **And** functions raise `ValueError` for invalid operations

**AC-3: Thread-Safe State Access**
- **Given** state is accessed from async context
- **When** multiple coroutines access state concurrently
- **Then** state access is thread-safe by default (HA async architecture)
- **And** no race conditions occur during state updates
- **And** state mutations are atomic operations

**AC-4: In-Memory Performance**
- **Given** game is actively running
- **When** state is read or updated
- **Then** operations complete in <1ms (in-memory speed)
- **And** no database I/O operations occur
- **And** state resets on HA restart (acceptable for games)

**AC-5: Optional Config Persistence**
- **Given** admin has configured game settings
- **When** admin settings are saved
- **Then** config persists across HA restarts using `hass.helpers.storage`
- **And** active game state remains in-memory only
- **And** config is loaded on component setup

## Tasks / Subtasks

- [ ] Task 1: Define State Type Models (AC: #1, #2)
  - [ ] Create `custom_components/beatsy/game_state.py` module
  - [ ] Import Python 3.14+ typing features: `TypedDict`, `dataclass`, `Optional`, `List`, `Dict`
  - [ ] Define `GameConfig` TypedDict:
    ```python
    from typing import TypedDict

    class GameConfig(TypedDict, total=False):
        """Game configuration settings."""
        playlist_uri: str
        media_player_entity_id: str
        round_timer_seconds: int
        points_exact: int
        points_close: int
        points_bet_multiplier: float
    ```
  - [ ] Define `Player` dataclass:
    ```python
    from dataclasses import dataclass, field

    @dataclass
    class Player:
        """Player data model."""
        name: str
        score: int = 0
        guesses: list[int] = field(default_factory=list)
        bets_placed: list[bool] = field(default_factory=list)
    ```
  - [ ] Define `RoundState` dataclass:
    ```python
    @dataclass
    class RoundState:
        """Current round state."""
        round_number: int
        track_uri: str
        track_name: str
        track_artist: str
        correct_year: int
        guesses: dict[str, int] = field(default_factory=dict)  # player_name -> year
        bets: dict[str, bool] = field(default_factory=dict)  # player_name -> betting
        status: str = "active"  # active, ended
        timer_started_at: float | None = None
    ```
  - [ ] Define `BeatsyGameState` dataclass:
    ```python
    @dataclass
    class BeatsyGameState:
        """Complete game state structure."""
        game_config: GameConfig = field(default_factory=dict)
        players: list[Player] = field(default_factory=list)
        current_round: RoundState | None = None
        played_songs: list[str] = field(default_factory=list)
        websocket_connections: dict[str, Any] = field(default_factory=dict)
    ```
  - [ ] Add docstrings to all type definitions

- [ ] Task 2: Implement State Initialization (AC: #1)
  - [ ] Define `init_game_state(hass: HomeAssistant) -> BeatsyGameState`:
    ```python
    def init_game_state(hass: HomeAssistant) -> BeatsyGameState:
        """Initialize game state in hass.data[DOMAIN]."""
        state = BeatsyGameState()
        hass.data[DOMAIN] = state
        _LOGGER.debug("Game state initialized")
        return state
    ```
  - [ ] Add type hint: `from homeassistant.core import HomeAssistant`
  - [ ] Import `DOMAIN` from `.const`
  - [ ] Call `init_game_state()` from `__init__.py` during `async_setup()`
  - [ ] Log state initialization at DEBUG level

- [ ] Task 3: Implement Config Accessor Functions (AC: #2)
  - [ ] Define `get_game_config(hass: HomeAssistant) -> GameConfig`:
    ```python
    def get_game_config(hass: HomeAssistant) -> GameConfig:
        """Get game configuration."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return state.game_config
    ```
  - [ ] Define `update_game_config(hass: HomeAssistant, config: GameConfig) -> None`:
    ```python
    def update_game_config(hass: HomeAssistant, config: GameConfig) -> None:
        """Update game configuration."""
        state: BeatsyGameState = hass.data[DOMAIN]
        state.game_config.update(config)
        _LOGGER.debug(f"Game config updated: {config}")
    ```
  - [ ] Add validation for required config fields
  - [ ] Raise `ValueError` for invalid config values

- [ ] Task 4: Implement Player Accessor Functions (AC: #2)
  - [ ] Define `get_players(hass: HomeAssistant) -> list[Player]`:
    ```python
    def get_players(hass: HomeAssistant) -> list[Player]:
        """Get all players."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return state.players
    ```
  - [ ] Define `add_player(hass: HomeAssistant, player: Player) -> None`:
    ```python
    def add_player(hass: HomeAssistant, player: Player) -> None:
        """Add a new player."""
        state: BeatsyGameState = hass.data[DOMAIN]
        if any(p.name == player.name for p in state.players):
            raise ValueError(f"Player '{player.name}' already exists")
        state.players.append(player)
        _LOGGER.debug(f"Player added: {player.name}")
    ```
  - [ ] Define `get_player(hass: HomeAssistant, name: str) -> Player | None`:
    ```python
    def get_player(hass: HomeAssistant, name: str) -> Player | None:
        """Get player by name."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return next((p for p in state.players if p.name == name), None)
    ```
  - [ ] Define `update_player_score(hass: HomeAssistant, player_name: str, points: int) -> None`:
    ```python
    def update_player_score(hass: HomeAssistant, player_name: str, points: int) -> None:
        """Update player score."""
        player = get_player(hass, player_name)
        if player is None:
            raise ValueError(f"Player '{player_name}' not found")
        player.score += points
        _LOGGER.debug(f"Player {player_name} score updated: +{points} = {player.score}")
    ```
  - [ ] Define `reset_players(hass: HomeAssistant) -> None` for game restart
  - [ ] Add validation for duplicate player names

- [ ] Task 5: Implement Round Accessor Functions (AC: #2)
  - [ ] Define `get_current_round(hass: HomeAssistant) -> RoundState | None`:
    ```python
    def get_current_round(hass: HomeAssistant) -> RoundState | None:
        """Get current round state."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return state.current_round
    ```
  - [ ] Define `set_current_round(hass: HomeAssistant, round_state: RoundState) -> None`:
    ```python
    def set_current_round(hass: HomeAssistant, round_state: RoundState) -> None:
        """Set current round state."""
        state: BeatsyGameState = hass.data[DOMAIN]
        state.current_round = round_state
        _LOGGER.debug(f"Round {round_state.round_number} started: {round_state.track_name}")
    ```
  - [ ] Define `clear_current_round(hass: HomeAssistant) -> None`:
    ```python
    def clear_current_round(hass: HomeAssistant) -> None:
        """Clear current round (round ended)."""
        state: BeatsyGameState = hass.data[DOMAIN]
        state.current_round = None
        _LOGGER.debug("Current round cleared")
    ```
  - [ ] Define `add_guess(hass: HomeAssistant, player_name: str, year: int) -> None`:
    ```python
    def add_guess(hass: HomeAssistant, player_name: str, year: int) -> None:
        """Add player guess to current round."""
        round_state = get_current_round(hass)
        if round_state is None:
            raise ValueError("No active round")
        if round_state.status != "active":
            raise ValueError("Round is not active")
        round_state.guesses[player_name] = year
        _LOGGER.debug(f"Guess recorded: {player_name} -> {year}")
    ```
  - [ ] Add validation for round state transitions

- [ ] Task 6: Implement Song History Functions (AC: #2)
  - [ ] Define `get_played_songs(hass: HomeAssistant) -> list[str]`:
    ```python
    def get_played_songs(hass: HomeAssistant) -> list[str]:
        """Get list of played song URIs."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return state.played_songs
    ```
  - [ ] Define `add_played_song(hass: HomeAssistant, track_uri: str) -> None`:
    ```python
    def add_played_song(hass: HomeAssistant, track_uri: str) -> None:
        """Add song to played history."""
        state: BeatsyGameState = hass.data[DOMAIN]
        if track_uri not in state.played_songs:
            state.played_songs.append(track_uri)
            _LOGGER.debug(f"Song added to history: {track_uri}")
    ```
  - [ ] Define `is_song_played(hass: HomeAssistant, track_uri: str) -> bool`:
    ```python
    def is_song_played(hass: HomeAssistant, track_uri: str) -> bool:
        """Check if song has been played."""
        state: BeatsyGameState = hass.data[DOMAIN]
        return track_uri in state.played_songs
    ```
  - [ ] Add function to clear history on game reset

- [ ] Task 7: Implement Config Persistence (AC: #5)
  - [ ] Import `Store` from `homeassistant.helpers.storage`
  - [ ] Define storage version: `STORAGE_VERSION = 1`
  - [ ] Define storage key: `STORAGE_KEY = f"{DOMAIN}.config"`
  - [ ] Define `async def load_config(hass: HomeAssistant) -> GameConfig`:
    ```python
    async def load_config(hass: HomeAssistant) -> GameConfig:
        """Load persisted config from storage."""
        store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        data = await store.async_load()
        if data is None:
            _LOGGER.debug("No persisted config found, using defaults")
            return {}
        _LOGGER.debug("Config loaded from storage")
        return data
    ```
  - [ ] Define `async def save_config(hass: HomeAssistant, config: GameConfig) -> None`:
    ```python
    async def save_config(hass: HomeAssistant, config: GameConfig) -> None:
        """Save config to persistent storage."""
        store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        await store.async_save(config)
        _LOGGER.debug("Config saved to storage")
    ```
  - [ ] Call `load_config()` during `async_setup()` in `__init__.py`
  - [ ] Update `update_game_config()` to automatically persist changes
  - [ ] Document that active game state (players, rounds) is NOT persisted

- [ ] Task 8: Add Thread Safety Documentation (AC: #3)
  - [ ] Add module docstring explaining async safety:
    ```python
    """
    Game state management for Beatsy.

    This module provides type-safe, in-memory state management using Python 3.14+
    dataclasses and type hints. All state is stored in hass.data[DOMAIN].

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
    ```
  - [ ] Add inline comments explaining state mutation atomicity
  - [ ] Document when to use `hass.async_add_executor_job()` (not needed here)

- [ ] Task 9: Unit Tests for State Initialization (AC: #1)
  - [ ] Create `tests/test_game_state.py`
  - [ ] Test: `init_game_state()` creates BeatsyGameState instance
  - [ ] Test: State stored in `hass.data[DOMAIN]`
  - [ ] Test: State contains all required fields
  - [ ] Test: Fields have correct default values
  - [ ] Test: Type hints are correct (use `typing.get_type_hints()`)
  - [ ] Mock: `hass` fixture from pytest-homeassistant-custom-component

- [ ] Task 10: Unit Tests for Config Functions (AC: #2, #5)
  - [ ] Test: `get_game_config()` returns GameConfig
  - [ ] Test: `update_game_config()` updates state
  - [ ] Test: `update_game_config()` validates required fields
  - [ ] Test: `update_game_config()` raises ValueError for invalid values
  - [ ] Test: `load_config()` loads from storage (mock Store)
  - [ ] Test: `save_config()` persists to storage (mock Store)
  - [ ] Test: `load_config()` returns defaults when no file exists

- [ ] Task 11: Unit Tests for Player Functions (AC: #2)
  - [ ] Test: `add_player()` adds player to list
  - [ ] Test: `add_player()` prevents duplicate names
  - [ ] Test: `get_player()` finds player by name
  - [ ] Test: `get_player()` returns None for missing player
  - [ ] Test: `update_player_score()` increments score
  - [ ] Test: `update_player_score()` raises ValueError for missing player
  - [ ] Test: `reset_players()` clears player list

- [ ] Task 12: Unit Tests for Round Functions (AC: #2)
  - [ ] Test: `set_current_round()` sets round state
  - [ ] Test: `get_current_round()` returns round state
  - [ ] Test: `clear_current_round()` sets state to None
  - [ ] Test: `add_guess()` records guess in current round
  - [ ] Test: `add_guess()` raises ValueError when no active round
  - [ ] Test: `add_guess()` raises ValueError when round ended
  - [ ] Test: Round state transitions correctly

- [ ] Task 13: Unit Tests for Song History (AC: #2)
  - [ ] Test: `add_played_song()` adds URI to history
  - [ ] Test: `add_played_song()` prevents duplicates
  - [ ] Test: `is_song_played()` returns True for played songs
  - [ ] Test: `is_song_played()` returns False for unplayed songs
  - [ ] Test: `get_played_songs()` returns complete list

- [ ] Task 14: Integration Test - State Lifecycle (AC: #1, #2, #3)
  - [ ] Test: Initialize state via `init_game_state()`
  - [ ] Test: Add 3 players via `add_player()`
  - [ ] Test: Start round via `set_current_round()`
  - [ ] Test: Submit guesses via `add_guess()`
  - [ ] Test: Update scores via `update_player_score()`
  - [ ] Test: End round via `clear_current_round()`
  - [ ] Test: Verify state consistency throughout
  - [ ] Test: No exceptions or type errors

- [ ] Task 15: Performance Test - In-Memory Speed (AC: #4)
  - [ ] Test: Benchmark `get_players()` call time (<1ms)
  - [ ] Test: Benchmark `update_player_score()` call time (<1ms)
  - [ ] Test: Benchmark `add_guess()` call time (<1ms)
  - [ ] Test: Verify no database queries occur (mock Store)
  - [ ] Test: 1000 state operations complete in <100ms
  - [ ] Use `pytest-benchmark` for timing measurements

- [ ] Task 16: Manual Testing - State Access (AC: #2)
  - [ ] **[USER ACTION]** Start HA with Beatsy installed
  - [ ] **[USER ACTION]** Open Developer Tools → Template
  - [ ] **[USER ACTION]** Test state access: `{{ states('sensor.beatsy_players') }}`
  - [ ] **[USER ACTION]** Verify state accessible from templates
  - [ ] **[USER ACTION]** Check logs for DEBUG state messages
  - [ ] **[USER ACTION]** Verify no errors during state operations

- [ ] Task 17: Manual Testing - Config Persistence (AC: #5)
  - [ ] **[USER ACTION]** Configure game settings via admin UI (future story)
  - [ ] **[USER ACTION]** Restart Home Assistant
  - [ ] **[USER ACTION]** Verify config persists across restart
  - [ ] **[USER ACTION]** Verify active game state resets (expected behavior)
  - [ ] **[USER ACTION]** Check `.storage/beatsy.config` file exists

- [ ] Task 18: Update __init__.py Integration (AC: #1, #5)
  - [ ] Import `init_game_state` and `load_config` in `__init__.py`
  - [ ] Call `await load_config(hass)` in `async_setup()`
  - [ ] Store loaded config in state: `state.game_config = await load_config(hass)`
  - [ ] Call `init_game_state(hass)` in `async_setup()`
  - [ ] Update cleanup to NOT persist active game state
  - [ ] Document state initialization order in comments

## Dev Notes

### Architecture Patterns and Constraints

**From Tech Spec (Epic 2 - Story 2.3):**
- **Purpose:** Structured in-memory state system using `hass.data`
- **State Structure:** Game config, players, current round, song history, connections
- **Performance:** In-memory only (no `hass.helpers.storage` for active game)
- **Persistence:** Optional config persistence for admin settings
- **Thread Safety:** Async-safe by default (HA event loop)

**State Access Pattern:**
```python
# Get state
state: BeatsyGameState = hass.data[DOMAIN]

# Access fields
config = state.game_config
players = state.players
current_round = state.current_round

# Modify state
state.players.append(Player(name="Alice"))
state.current_round = RoundState(...)
```

**From Tech Spec (Modules - Story 2.3):**
- **Module:** `game_state.py`
- **Functions:** `init_game_state()`, `get_game_config()`, `get_players()`, `update_player_score()`, `get_current_round()`
- **Dependencies:** None (HA core only)
- **Owner:** Story 2.3

**From Architecture (State Management):**
- **Pattern:** In-memory state in `hass.data[DOMAIN]`
- **Why:** Fast access (no DB overhead), suitable for ephemeral game state
- **Trade-off:** State lost on restart (acceptable for games)
- **Future:** Consider persistence for game history/leaderboards (not MVP)

**2025 Best Practices (Research Findings):**

**Python 3.14+ Type Hints:**
- Use `dataclasses` for structured state
- Use `TypedDict` for flexible config dictionaries
- Use union syntax: `int | None` instead of `Optional[int]`
- Use modern list/dict hints: `list[str]` instead of `List[str]`
- Add complete type hints to all functions

**Home Assistant Patterns:**
- `hass.data[DOMAIN]` remains standard for integration state
- `DataUpdateCoordinator` NOT needed for event-driven systems
- Use `hass.helpers.storage.Store` for persistent config only
- WebSocket + in-memory state ideal for real-time games
- Async operations are thread-safe by default

**State Management:**
```python
from dataclasses import dataclass, field
from typing import TypedDict

# Config with flexible fields
class GameConfig(TypedDict, total=False):
    playlist_uri: str
    media_player_entity_id: str
    round_timer_seconds: int

# Structured player data
@dataclass
class Player:
    name: str
    score: int = 0
    guesses: list[int] = field(default_factory=list)

# Complete game state
@dataclass
class BeatsyGameState:
    game_config: GameConfig = field(default_factory=dict)
    players: list[Player] = field(default_factory=list)
    current_round: RoundState | None = None
    played_songs: list[str] = field(default_factory=list)
    websocket_connections: dict[str, Any] = field(default_factory=dict)
```

**Config Persistence Pattern:**
```python
from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.config"

async def load_config(hass: HomeAssistant) -> GameConfig:
    """Load persisted config."""
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    data = await store.async_load()
    return data or {}

async def save_config(hass: HomeAssistant, config: GameConfig) -> None:
    """Save config to storage."""
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    await store.async_save(config)
```

**Thread Safety:**
- HA runs on single-threaded asyncio event loop
- State mutations are atomic Python operations
- No locks needed for typical state access
- Use `hass.async_add_executor_job()` only for blocking I/O (not needed here)

**Performance Characteristics:**
- In-memory state access: <1ms per operation
- No database queries during active game
- Config persistence: ~10-50ms (async, non-blocking)
- Suitable for real-time gameplay

### Learnings from Previous Story

**From Story 2.2 (Status: drafted)**

Story 2.2 establishes the lifecycle foundation this story builds upon:

- **State Initialization Context:**
  - Story 2.2 initializes basic `hass.data[DOMAIN]` dictionary
  - Story 2.3 replaces with structured `BeatsyGameState` dataclass
  - Both stories coordinate state initialization in `async_setup()`

- **Lifecycle Integration:**
  - `async_setup()` calls `init_game_state(hass)` after config load
  - `async_unload()` clears state: `hass.data.pop(DOMAIN, None)`
  - `async_reload()` reinitializes state via `init_game_state()`

- **State Structure Evolution:**
  - Story 2.2 uses plain dict: `hass.data[DOMAIN] = {"players": [], ...}`
  - Story 2.3 uses dataclass: `hass.data[DOMAIN] = BeatsyGameState()`
  - Both approaches store in same location: `hass.data[DOMAIN]`

**Integration Points:**
1. Import `init_game_state()` in `__init__.py`
2. Call during `async_setup()` after lifecycle hooks
3. State cleared during `async_unload()` (handled by Story 2.2)
4. State reinitialized during `async_reload()` (calls `init_game_state()`)

**Files Modified by Both Stories:**
- `__init__.py`: Story 2.2 adds lifecycle, Story 2.3 adds state initialization
- Both stories coordinate via `hass.data[DOMAIN]` storage pattern

[Source: stories/2-2-component-lifecycle-management.md]

### Project Structure Notes

**File Location:**
- **Module:** `custom_components/beatsy/game_state.py` (NEW FILE)
- **Tests:** `tests/test_game_state.py` (NEW FILE)
- **Imports:** `homeassistant.core.HomeAssistant`, `homeassistant.helpers.storage.Store`
- **Modified:** `custom_components/beatsy/__init__.py` (import and call `init_game_state()`)

**Module Dependencies:**
- **Local:** `.const.DOMAIN` (from Story 2.1)
- **HA Core:** `homeassistant.core.HomeAssistant`
- **HA Helpers:** `homeassistant.helpers.storage.Store` (for config persistence)
- **Python:** `typing`, `dataclasses`, `logging`

**Type Definitions:**
- `GameConfig`: TypedDict for flexible config
- `Player`: dataclass for player data
- `RoundState`: dataclass for round state
- `BeatsyGameState`: dataclass for complete state

**Accessor Functions:**
- Config: `get_game_config()`, `update_game_config()`, `load_config()`, `save_config()`
- Players: `get_players()`, `add_player()`, `get_player()`, `update_player_score()`, `reset_players()`
- Rounds: `get_current_round()`, `set_current_round()`, `clear_current_round()`, `add_guess()`
- Songs: `get_played_songs()`, `add_played_song()`, `is_song_played()`

**Repository Structure After This Story:**
```
beatsy/
├── custom_components/
│   └── beatsy/
│       ├── __init__.py          # Story 2.2: lifecycle (MODIFIED by 2.3)
│       ├── manifest.json        # Story 2.1: metadata
│       ├── const.py             # Story 2.1: constants
│       ├── game_state.py        # THIS STORY: state management (NEW)
│       ├── (other modules from Stories 2.4-2.7)
├── tests/
│   ├── test_init.py             # Story 2.2: lifecycle tests
│   ├── test_game_state.py       # THIS STORY: state tests (NEW)
├── .storage/
│   └── beatsy.config            # THIS STORY: persisted config (created at runtime)
├── hacs.json                    # Story 2.1: HACS metadata
├── README.md                    # Story 2.1: documentation
└── LICENSE                      # Story 2.1: license
```

### Testing Standards Summary

**Unit Tests (pytest + pytest-asyncio):**

**Test: State Initialization**
```python
async def test_init_game_state(hass):
    """Test state initialization."""
    state = init_game_state(hass)
    assert isinstance(state, BeatsyGameState)
    assert DOMAIN in hass.data
    assert isinstance(hass.data[DOMAIN], BeatsyGameState)
    assert state.players == []
    assert state.current_round is None
```

**Test: Add Player**
```python
async def test_add_player(hass):
    """Test adding player."""
    init_game_state(hass)
    player = Player(name="Alice")
    add_player(hass, player)

    players = get_players(hass)
    assert len(players) == 1
    assert players[0].name == "Alice"
    assert players[0].score == 0
```

**Test: Duplicate Player**
```python
async def test_add_duplicate_player_raises(hass):
    """Test duplicate player raises ValueError."""
    init_game_state(hass)
    add_player(hass, Player(name="Alice"))

    with pytest.raises(ValueError, match="already exists"):
        add_player(hass, Player(name="Alice"))
```

**Test: Update Score**
```python
async def test_update_player_score(hass):
    """Test score update."""
    init_game_state(hass)
    add_player(hass, Player(name="Alice"))

    update_player_score(hass, "Alice", 10)
    player = get_player(hass, "Alice")
    assert player.score == 10

    update_player_score(hass, "Alice", 5)
    assert player.score == 15
```

**Test: Round Management**
```python
async def test_round_lifecycle(hass):
    """Test round lifecycle."""
    init_game_state(hass)

    # No active round
    assert get_current_round(hass) is None

    # Start round
    round_state = RoundState(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Test Song",
        track_artist="Test Artist",
        correct_year=1995
    )
    set_current_round(hass, round_state)
    assert get_current_round(hass) == round_state

    # Add guesses
    add_guess(hass, "Alice", 1990)
    assert round_state.guesses["Alice"] == 1990

    # End round
    clear_current_round(hass)
    assert get_current_round(hass) is None
```

**Test: Config Persistence**
```python
async def test_save_and_load_config(hass):
    """Test config persistence."""
    init_game_state(hass)

    # Save config
    config: GameConfig = {
        "playlist_uri": "spotify:playlist:123",
        "round_timer_seconds": 30
    }
    await save_config(hass, config)

    # Load config
    loaded = await load_config(hass)
    assert loaded["playlist_uri"] == "spotify:playlist:123"
    assert loaded["round_timer_seconds"] == 30
```

**Performance Test:**
```python
def test_state_access_performance(hass, benchmark):
    """Test state access performance."""
    init_game_state(hass)
    add_player(hass, Player(name="Alice"))

    # Benchmark get_players() call
    result = benchmark(get_players, hass)
    assert len(result) == 1
    # pytest-benchmark verifies <1ms automatically
```

**Manual Testing:**
1. Start HA with Beatsy installed
2. Check logs for "Game state initialized" (DEBUG level)
3. Add players via WebSocket commands (future story)
4. Verify state updates in Developer Tools → Templates
5. Restart HA, verify config persists but game state resets
6. Check `.storage/beatsy.config` file for persisted config

**Success Criteria:**
- State initializes with correct structure and types
- Accessor functions work without errors
- Type hints validated by mypy/pyright
- Player operations (add, update score) work correctly
- Round lifecycle (start, add guesses, end) works correctly
- Config persists across HA restart
- Active game state resets on restart (expected)
- All operations complete in <1ms
- No exceptions or type errors in tests

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-2.md#Story-2.3-In-Memory-State]
- [Source: docs/tech-spec-epic-2.md#Services-and-Modules-game_state.py]
- [Source: docs/epics.md#Story-2.3-In-Memory-Game-State-Management]
- [Source: docs/architecture.md#State-Management-Pattern]

**Home Assistant References:**
- State Management: https://developers.home-assistant.io/docs/dev_101_hass/
- Storage Helper: https://developers.home-assistant.io/docs/helpers/storage/
- Type Hints: https://developers.home-assistant.io/docs/development_typing/
- Async Programming: https://developers.home-assistant.io/docs/asyncio_working_with_async/

**Python 3.14+ References:**
- Dataclasses: https://docs.python.org/3/library/dataclasses.html
- TypedDict: https://docs.python.org/3/library/typing.html#typing.TypedDict
- Type Hints: https://docs.python.org/3/library/typing.html
- Union Syntax: https://peps.python.org/pep-0604/

**Research References:**
- Home Assistant 2025 State Management: [WebSearch: "Home Assistant 2025 custom integration state management"]
- DataUpdateCoordinator vs hass.data: [WebFetch: developers.home-assistant.io/docs/integration_fetching_data/]
- WebSocket API Extension: [WebFetch: developers.home-assistant.io/docs/frontend/extending/websocket-api/]

**Key Technical Decisions:**
- Use Python 3.14+ dataclasses for structured state (2025 best practice)
- Use TypedDict for flexible config (allows optional fields)
- Store state in `hass.data[DOMAIN]` (standard pattern)
- In-memory only for active game (fast, ephemeral by design)
- Persist config only via `hass.helpers.storage.Store`
- No DataUpdateCoordinator needed (event-driven, not polling)
- Thread-safe by default (HA async event loop)

**Dependencies:**
- **Prerequisite:** Story 2.2 (lifecycle management, `hass.data[DOMAIN]` initialization)
- **Prerequisite:** Story 2.1 (DOMAIN constant in `const.py`)
- **Enables:** Story 2.4 (Spotify helper uses state)
- **Enables:** Story 2.5 (HTTP views access state)
- **Enables:** Story 2.6 (WebSocket handlers modify state)
- **Enables:** All future stories (state is central to all game logic)

**Home Assistant Concepts:**
- **hass.data:** Shared dictionary for component state
- **hass.helpers.storage.Store:** Persistent storage for config
- **Async Safety:** Single-threaded event loop ensures thread safety
- **Type Hints:** Improve IDE support and catch errors early

**Testing Frameworks:**
- pytest: Python testing framework
- pytest-asyncio: Async test support
- pytest-homeassistant-custom-component: HA-specific test helpers
- pytest-benchmark: Performance testing
- mypy/pyright: Static type checking

**2025 Enhancements Applied:**
1. **Python 3.14+ type hints:** Modern union syntax, complete annotations
2. **Dataclasses:** Structured state with default values and type safety
3. **TypedDict:** Flexible config dictionary with optional fields
4. **Storage pattern:** Persistent config via `hass.helpers.storage.Store`
5. **Documentation:** Comprehensive docstrings explaining thread safety and performance

## Change Log

**Story Created:** 2025-11-12
**Author:** Bob (Scrum Master)
**Epic:** Epic 2 - HACS Integration & Core Infrastructure
**Story ID:** 2.3
**Status:** drafted (was backlog)

**Requirements Source:**
- Tech Spec Epic 2: In-memory game state management using `hass.data`
- Epics: Structured state with accessor functions
- Architecture: In-memory state pattern for fast access
- 2025 Research: Python 3.14+ dataclasses, TypedDict, modern type hints

**Technical Approach:**
- Define state models using dataclasses (BeatsyGameState, Player, RoundState)
- Use TypedDict for flexible GameConfig
- Implement accessor functions with complete type hints
- Add config persistence via `hass.helpers.storage.Store`
- Document thread safety (async event loop)
- Performance target: <1ms per operation
- Unit tests for all state operations
- Integration test for full state lifecycle

**2025 Enhancements Included:**
- Python 3.14+ type hints (union syntax, modern annotations)
- Dataclasses for structured state
- TypedDict for flexible config
- Storage.Store for config persistence
- Thread safety documentation
- Performance characteristics documented

**Dependencies:**
- Story 2.2 complete: Component lifecycle hooks, `hass.data[DOMAIN]` initialized
- Story 2.1 complete: `DOMAIN` constant available in `const.py`

**Learnings Applied from Story 2.2:**
- State stored in `hass.data[DOMAIN]`
- State initialized during `async_setup()`
- State cleared during `async_unload()`
- State reinitialized during `async_reload()`
- Coordinate lifecycle hooks with state management

**Critical for Epic 2:**
- Foundation for all game logic (players, rounds, scoring)
- Enables WebSocket handlers to modify state
- Enables HTTP views to read state
- Provides type-safe API for all modules
- Performance critical (in-memory, <1ms operations)

**Future Story Dependencies:**
- Story 2.4: Spotify helper reads `game_config` for media player
- Story 2.5: HTTP views read state for UI rendering
- Story 2.6: WebSocket handlers modify state (add players, guesses, scores)
- All Epic 3-9 stories: Build on this state management foundation

**Novel Patterns Introduced:**
- Python 3.14+ dataclasses for HA component state
- TypedDict for flexible config with optional fields
- Separation of concerns: active game state (in-memory) vs config (persistent)
- Complete type hints for all state operations
- Performance testing for in-memory operations

## Dev Agent Record

### Context Reference

- docs/stories/2-3-in-memory-game-state-management.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929 (Sonnet 4.5)

### Debug Log References

N/A - All tests passed successfully on first run

### Completion Notes List

**Implementation Summary:**

1. **Created game_state.py module** with complete type-safe state management:
   - Defined `GameConfig` TypedDict for flexible configuration
   - Defined `Player` dataclass with score tracking and history
   - Defined `RoundState` dataclass for active round management
   - Defined `BeatsyGameState` dataclass as the root state container
   - All types use Python 3.11+ compatible type hints (Optional instead of |)

2. **Implemented state initialization and accessor functions:**
   - `init_game_state()` - Initializes BeatsyGameState in hass.data[DOMAIN][entry_id]
   - `get_game_state()` - Retrieves state with backward compatibility (supports entry_id=None)
   - Migration support for legacy dict-based state to BeatsyGameState dataclass
   - Comprehensive error handling with ValueError for invalid states

3. **Implemented config accessor functions:**
   - `get_game_config()` - Retrieves game configuration
   - `update_game_config()` - Updates config with validation
   - Validation for round_timer_seconds, points_exact, points_close, points_near, points_bet_multiplier
   - All config operations are atomic and thread-safe

4. **Implemented player accessor functions:**
   - `get_players()` - Returns list of all players
   - `add_player()` - Adds new player with duplicate name checking
   - `get_player()` - Finds player by name
   - `update_player_score()` - Updates player score (supports negative points)
   - `reset_players()` - Clears all players
   - All operations maintain dataclass integrity

5. **Implemented round accessor functions:**
   - `get_current_round()` - Returns active round or None
   - `set_current_round()` - Sets active round with automatic timer initialization
   - `clear_current_round()` - Ends current round
   - `add_guess()` - Records player guess with bet status and timestamp
   - `update_bet()` - Updates bet status for current round
   - Validation ensures round is active before accepting guesses

6. **Implemented song history functions:**
   - `get_played_songs()` - Returns list of played track URIs
   - `add_played_song()` - Adds song with duplicate prevention
   - `is_song_played()` - Checks if song has been played
   - `clear_played_songs()` - Clears history
   - All operations are O(1) or O(n) for list operations

7. **Implemented config persistence:**
   - `load_config()` - Loads persisted config from hass.helpers.storage.Store
   - `save_config()` - Saves config to persistent storage
   - Uses per-entry storage keys: `beatsy.config.{entry_id}`
   - Gracefully handles missing config files (returns empty dict)
   - Active game state remains in-memory only (not persisted)

8. **Updated __init__.py integration:**
   - Imported `init_game_state` and `load_config`
   - Replaced legacy dict initialization with `init_game_state()` call
   - Added config loading on component setup
   - Updated `async_unload_entry` to handle BeatsyGameState objects
   - Maintains backward compatibility with legacy dict state

9. **Comprehensive test suite created:**
   - 43 unit tests covering all functions and edge cases
   - Tests for state initialization, config, players, rounds, song history
   - Tests for config persistence with mocked Store
   - Integration test for complete game lifecycle
   - Performance tests validating <1ms operations
   - Type safety tests for all dataclasses
   - **All 43 tests passing (100% pass rate)**

**Test Results:**
```
43 passed in 0.09s
```

**Performance Validation:**
- State access operations: <1ms (validated via performance tests)
- 1000 player operations: <100ms total
- 300 round operations: <100ms total
- All operations are in-memory with no database I/O

**Key Technical Decisions:**
- Used `Optional[T]` instead of `T | None` for Python 3.9 compatibility
- Implemented migration path from legacy dict state to BeatsyGameState
- Made entry_id parameter optional for backward compatibility
- Added comprehensive validation with clear error messages
- Designed for thread-safety via Home Assistant's asyncio event loop

**Files Created:**
- `/home-assistant-config/custom_components/beatsy/game_state.py` (657 lines)
- `/tests/test_game_state.py` (849 lines)

**Files Modified:**
- `/home-assistant-config/custom_components/beatsy/__init__.py` (updated state initialization)

### File List

**New Files:**
- home-assistant-config/custom_components/beatsy/game_state.py
- tests/test_game_state.py

**Modified Files:**
- home-assistant-config/custom_components/beatsy/__init__.py
