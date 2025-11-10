# Architecture

## Executive Summary

Beatsy is a Home Assistant Custom Component that transforms smart homes into interactive party game platforms. The architecture uses the official HA integration blueprint structure with added web UI and WebSocket layers for real-time multiplayer gameplay. All components are HACS-compatible and designed for local network access without authentication requirements.

## Project Initialization

**First Implementation Story:**

Initialize the Beatsy integration structure from `ludeeus/integration_blueprint`:

```bash
# Create base structure
mkdir -p custom_components/beatsy
cd custom_components/beatsy

# Copy and adapt integration_blueprint structure:
# - __init__.py (integration initialization)
# - manifest.json (HA metadata, dependencies)
# - const.py (constants)
# - hacs.json (HACS metadata)
# - README.md (documentation)
```

**Development Setup:**
- Local VS Code development (no devcontainer)
- Test against live HA instance via API
- HA Connection: `http://192.168.0.191:8123`
- API Token: Configured in `.env` (10-year token, expires 2035)
- Deploy: Copy to `/config/custom_components/beatsy/` and restart HA

**This establishes:**
- HACS-compatible structure
- Standard HA integration patterns
- Python 3.11+ compatibility (HA 2024.x requirement)
- Base testing framework (pytest)

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Backend Framework | Python (HA Integration) | 3.11+ | All | Required by Home Assistant 2024.x |
| Frontend Framework | Static HTML + Tailwind CSS | Tailwind 3.4+ | FR-2, FR-3, FR-6 | UX spec requirement: no build process, mobile-first |
| Real-Time Communication | Custom aiohttp WebSocket | aiohttp (HA bundled) | FR-5 | Public access required, full control over game state broadcasts |
| Game State Storage | Hybrid (Memory + HA Registry) | - | FR-1, FR-4 | Fast in-memory gameplay, persistent config/scores |
| Spotify Integration | HA Service Calls (media_player) | - | FR-1 | Respect existing HA Spotify integration, avoid auth conflicts |
| Static File Serving | HA www/ folder mechanism | - | FR-2, FR-3 | Standard HA pattern, automatic public access at /local/beatsy/ |
| Frontend Architecture | ES6 Modules (native browser) | ES2020 | FR-2, FR-3, FR-5 | Clean code separation, no build process, modern browser support |
| Timer Synchronization | Hybrid (Client + Server sync) | - | FR-4, FR-5 | Smooth UX with server authority, resilient to network issues |
| Concurrency Control | Asyncio State Machine + Queue | asyncio (stdlib) | FR-4, FR-5 | Prevent race conditions, atomic state transitions |
| Error Handling | Auto-reconnect + Session persistence | - | FR-8, NFR-5 | Graceful degradation, 5-min timeout, visual feedback |

## Project Structure

```
beatsy/
├── custom_components/
│   └── beatsy/
│       ├── __init__.py              # Integration setup, register WebSocket endpoint
│       ├── manifest.json            # HA metadata: domain, dependencies, version
│       ├── hacs.json                # HACS metadata for distribution
│       ├── const.py                 # Constants (DOMAIN, default config values)
│       ├── config_flow.py           # Optional: HA UI config (may skip for MVP)
│       │
│       ├── game_manager.py          # Core game state machine
│       ├── game_state.py            # Game state data classes
│       ├── player.py                # Player model
│       ├── scoring.py               # Proximity scoring logic
│       │
│       ├── websocket_handler.py     # WebSocket connection manager
│       ├── websocket_api.py         # WebSocket message handlers
│       │
│       ├── spotify_service.py       # HA Spotify service call wrapper
│       ├── storage.py               # HA Registry read/write utilities
│       │
│       └── www/                     # Static web files (served at /local/beatsy/)
│           ├── admin.html           # Admin game setup interface
│           ├── start.html           # Player join & gameplay interface
│           │
│           ├── js/
│           │   ├── websocket-client.js   # Shared WebSocket connection
│           │   ├── game-state.js         # Client-side state management
│           │   ├── ui-admin.js           # Admin UI logic
│           │   ├── ui-player.js          # Player UI logic
│           │   └── utils.js              # Shared utilities
│           │
│           ├── css/
│           │   ├── tailwind.min.css      # Compiled Tailwind (production)
│           │   └── custom.css            # Custom overrides
│           │
│           └── assets/
│               └── logo.svg              # Beatsy logo
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_game_manager.py         # Game state machine tests
│   ├── test_scoring.py              # Scoring logic tests
│   └── test_websocket_api.py        # WebSocket handler tests
│
├── .devcontainer/                   # Optional: VS Code devcontainer config
├── .github/
│   └── workflows/
│       └── tests.yml                # CI/CD: Run tests on push
│
├── README.md                        # Installation & usage docs
├── LICENSE                          # License file
├── requirements.txt                 # Python dependencies (if any beyond HA)
└── info.md                          # HACS description & changelog
```

## Epic to Architecture Mapping

| Functional Requirement | Architecture Components | Primary Files |
|------------------------|------------------------|---------------|
| **FR-1: Home Assistant Integration** | HACS structure, HA integration setup | `manifest.json`, `hacs.json`, `__init__.py` |
| **FR-2: Admin Interface** | Admin web UI, WebSocket client | `www/admin.html`, `www/js/ui-admin.js` |
| **FR-3: Player Interface** | Player web UI, WebSocket client | `www/start.html`, `www/js/ui-player.js` |
| **FR-4: Game Mechanics** | Game state machine, scoring engine | `game_manager.py`, `scoring.py`, `player.py` |
| **FR-5: Real-Time Features** | WebSocket server, message handlers | `websocket_handler.py`, `websocket_api.py` |
| **FR-6: Mobile-First Design** | Tailwind CSS, responsive HTML | `www/css/tailwind.min.css`, HTML files |
| **FR-7: Admin Controls** | Admin WebSocket commands, game manager | `websocket_api.py`, `game_manager.py` |
| **FR-8: Error Handling** | Reconnection logic, error states | `websocket-client.js`, `game_manager.py` |

### Component Responsibilities

**Backend (Python):**
- `__init__.py` - Register integration with HA, set up WebSocket endpoint
- `game_manager.py` - State machine (SETUP → WAITING → ACTIVE → RESULTS)
- `game_state.py` - Data models for game, round, player state
- `player.py` - Player model with guess tracking
- `scoring.py` - Proximity-based scoring algorithm
- `websocket_handler.py` - WebSocket connection lifecycle
- `websocket_api.py` - Message routing and handlers
- `spotify_service.py` - Wrapper for HA Spotify service calls
- `storage.py` - HA Registry persistence utilities

**Frontend (JavaScript):**
- `websocket-client.js` - WebSocket connection with auto-reconnect
- `game-state.js` - Client-side state management
- `ui-admin.js` - Admin interface logic (setup, controls)
- `ui-player.js` - Player interface logic (join, guess, results)
- `utils.js` - Shared utilities (formatting, validation)

## Technology Stack Details

### Core Technologies

**Backend:**
- **Python** 3.11+ (Home Assistant 2024.x requirement)
- **aiohttp** (bundled with HA) - Async HTTP/WebSocket server
- **Home Assistant Core APIs**
  - `hass.http` - HTTP component for WebSocket registration
  - `hass.services` - Service call API (Spotify control)
  - `hass.helpers.storage` - Registry API for persistence
- **Standard Library:**
  - `asyncio` - Async primitives (Lock, Queue, Event)
  - `logging` - Logging infrastructure
  - `dataclasses` - Data models
  - `enum` - State enums
  - `typing` - Type hints

**Frontend:**
- **HTML5** - Semantic markup
- **Tailwind CSS** 3.4+ - Utility-first CSS framework
  - Development: CDN (`<script src="https://cdn.tailwindcss.com">`)
  - Production: Compiled CSS (tailwindcss CLI)
- **JavaScript ES2020** - Modern browser features
  - ES6 Modules (`import`/`export`)
  - Async/await
  - WebSocket API
  - Fetch API
- **No framework dependencies** - Vanilla JS only

**Development Tools:**
- **pytest** + **pytest-asyncio** - Python testing
- **ruff** - Python linting
- **GitHub Actions** - CI/CD pipeline

### Integration Points

**1. Home Assistant Spotify Integration**
```python
# Call HA service to control Spotify
await hass.services.async_call(
    domain="media_player",
    service="play_media",
    service_data={
        "entity_id": player_entity_id,
        "media_content_type": "track",
        "media_content_id": f"spotify:track:{track_id}"
    }
)
```

**2. Home Assistant Registry Storage**
```python
# Store game configuration
from homeassistant.helpers import storage

store = storage.Store(hass, version=1, key="beatsy.games")
await store.async_save(game_data)
data = await store.async_load()
```

**3. WebSocket Communication**
```python
# Server registers custom WebSocket endpoint
hass.http.register_view(BeatsyWebSocketView)

# Endpoint: ws://192.168.0.191:8123/api/beatsy/ws
```

**4. Static File Serving**
```
# Files in custom_components/beatsy/www/ automatically served at:
http://192.168.0.191:8123/local/beatsy/admin.html
http://192.168.0.191:8123/local/beatsy/start.html
```

## Novel Architectural Patterns

Beatsy requires custom patterns for its unique "smart home as game console" use case.

### Pattern 1: Unauthenticated WebSocket in HA Ecosystem

**Challenge:** Home Assistant requires authentication by default, but Beatsy needs public WebSocket access for party guests without HA accounts.

**Solution: Public WebSocket View with Game-Based Authorization**

```python
# custom_components/beatsy/websocket_handler.py
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

class BeatsyWebSocketView(HomeAssistantView):
    """WebSocket endpoint for Beatsy game communication."""

    url = "/api/beatsy/ws"
    name = "api:beatsy:websocket"
    requires_auth = False  # Bypass HA authentication

    async def get(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Game-based authorization (not user-based)
        game_id = await self._handshake(ws)
        if game_id:
            await self._handle_connection(ws, game_id)

        return ws
```

**Authorization Flow:**
1. Client connects → Server assigns temporary connection ID
2. Client sends `join_game` with game_id (UUID) + player_name
3. Server validates game exists → Binds connection to game session
4. No HA user accounts needed, just game session membership

**Security:** Game IDs are UUIDs (unguessable), sessions auto-expire after 24h inactivity

---

### Pattern 2: Server-Authoritative Real-Time State Sync

**Challenge:** Synchronize timer, scores, and bets across 10+ clients with varying network latency.

**Solution: Broadcast State Machine with Client-Side Prediction**

**Server (Python) - Authoritative State:**
```python
class GameManager:
    async def start_round(self):
        self.state = GameState.ACTIVE
        self.round_start_time = time.monotonic()

        # Broadcast to all connected players
        await self.broadcast({
            "type": "round_start",
            "timer_start": self.round_start_time,
            "timer_duration": self.config.timer_duration,
            "metadata": {...}
        })

        # Server-side timer
        await asyncio.sleep(self.config.timer_duration)
        await self.end_round()  # Authoritative end
```

**Client (JavaScript) - Predictive Display:**
```javascript
// Receive server start signal
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'round_start') {
        // Calculate time remaining locally (smooth countdown)
        const updateTimer = () => {
            const elapsed = (Date.now() / 1000) - msg.timer_start;
            const remaining = Math.max(0, msg.timer_duration - elapsed);
            displayTimer(remaining);
        };
        setInterval(updateTimer, 100);  // Update every 100ms
    }
};
```

**Sync Protocol:**
- Server sends sync checkpoints at 20s, 10s, 5s (clients adjust if drift > 500ms)
- Server's `time_up` message is authoritative (triggers auto-submit)
- Resilient to brief network hiccups

---

### Pattern 3: Ephemeral Multi-Player Session Management

**Challenge:** Manage temporary game sessions without HA user accounts or persistent player profiles.

**Solution: UUID-Based Sessions with Grace Period**

```python
@dataclass
class GameSession:
    game_id: str  # UUID
    created_at: datetime
    last_activity: datetime
    state: GameState  # SETUP, WAITING, ACTIVE, RESULTS
    players: dict[str, Player]  # connection_id → Player
    config: GameConfig
    current_round: Optional[Round]

    # In-memory WebSocket connections
    _connections: dict[str, WebSocketResponse]
```

**Lifecycle:**
1. **Creation:** Admin opens `/admin.html` → Server creates GameSession with UUID
2. **Join:** Players connect via `/start.html?game_id=<uuid>`
3. **Active:** State lives in memory, WebSocket broadcasts keep clients synced
4. **Persistence:** Save to HA Registry only on game end (final scores/history)
5. **Cleanup:** Auto-delete after 24h inactivity

**Reconnection Handling:**
- Player disconnects → Keep Player object for 5 minutes
- Player reconnects (same name) → Restore session, send current state
- Timeout → Mark "disconnected" in leaderboard

---

### Pattern 4: Minimal Playlist JSON with Runtime Metadata

**Challenge:** Need track year for scoring, but don't want to duplicate Spotify metadata.

**Solution: Minimal JSON + HA Media Player State**

**Playlist JSON (only what HA can't provide):**
```json
{
  "playlist_name": "80s Hits Collection",
  "playlist_id": "beatsy_80s_hits",
  "songs": [
    {
      "spotify_uri": "spotify:track:0J6mQxEZnlRt9ymzFntA6z",
      "year": 1986,
      "fun_fact": "The talk box effect was played by Richie Sambora."
    }
  ]
}
```

**Runtime Metadata Enrichment:**
```python
async def start_round(self, track_data: dict):
    # 1. Play track via HA service
    await self.spotify.play_track(entity_id, track_data["spotify_uri"])

    # 2. Wait for HA state to update
    await asyncio.sleep(2)

    # 3. Get metadata from media player state
    state = self.hass.states.get(entity_id)
    metadata = {
        "title": state.attributes["media_title"],      # From HA
        "artist": state.attributes["media_artist"],    # From HA
        "album": state.attributes["media_album_name"], # From HA
        "cover_url": state.attributes["entity_picture"], # From HA
        "year": track_data["year"],                    # From JSON
        "fun_fact": track_data.get("fun_fact", "")    # From JSON
    }

    # 4. Broadcast to all players
    await self.broadcast_round_start(metadata)
```

**Benefits:**
- Minimal JSON files (just URI + year + fun fact)
- Always accurate metadata from Spotify via HA
- Automatic album art URLs
- Fun facts shown on results screen (party conversation starter)

**File Location:**
```
custom_components/beatsy/playlists/
├── 80s_hits.json
├── 90s_pop.json
└── rock_classics.json
```

---

### Pattern 5: WebSocket Message Protocol

**Challenge:** Consistent message format for all client-server communication.

**Solution: Typed Message Protocol**

**Server → Client Messages:**
```javascript
{
    "type": "game_state" | "round_start" | "round_end" | "player_joined" | "error",
    "data": {...},
    "timestamp": "2025-01-09T12:34:56.789Z"
}
```

**Client → Server Messages:**
```javascript
{
    "action": "join_game" | "submit_guess" | "start_round" | "next_song",
    "player_id": "uuid",  // Assigned on connect
    "data": {...}
}
```

**Message Types:**
- `game_state` - Full state snapshot (on connect/reconnect)
- `round_start` - New round begins, includes metadata and timer
- `round_end` - Results: all guesses, correct year, scores
- `player_joined` - New player added to game
- `player_left` - Player disconnected
- `bet_placed` - Player activated bet multiplier
- `error` - Error message with code and description

**Implementation in both Python and JavaScript for consistency.**

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Conventions

**Python (Backend):**
- **Files:** `snake_case.py` (e.g., `game_manager.py`, `websocket_handler.py`)
- **Classes:** `PascalCase` (e.g., `GameManager`, `BeatsyWebSocketView`)
- **Functions/Methods:** `snake_case` (e.g., `start_round()`, `submit_guess()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DOMAIN = "beatsy"`, `DEFAULT_TIMER = 30`)
- **Private methods:** Prefix with `_` (e.g., `_handle_connection()`)

**JavaScript (Frontend):**
- **Files:** `kebab-case.js` (e.g., `websocket-client.js`, `ui-player.js`)
- **Classes:** `PascalCase` (e.g., `GameState`, `WebSocketClient`)
- **Functions/Variables:** `camelCase` (e.g., `startRound()`, `playerId`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `WS_ENDPOINT`, `DEFAULT_TIMEOUT`)

**HTML/CSS:**
- **Files:** `kebab-case.html`, `kebab-case.css`
- **CSS Classes:** Tailwind utility classes (e.g., `bg-sunset-primary`, `text-lg`)
- **Custom CSS:** `kebab-case` (e.g., `.timer-ring`, `.bet-active`)
- **IDs:** `kebab-case` (e.g., `#player-list`, `#round-timer`)

### Code Organization Patterns

**Python Module Structure:**
```python
# custom_components/beatsy/game_manager.py

"""Game state machine and round management."""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional

_LOGGER = logging.getLogger(__name__)

class GameState(Enum):
    """Game state enumeration."""
    SETUP = "setup"
    WAITING = "waiting"
    ACTIVE = "active"
    RESULTS = "results"

@dataclass
class GameConfig:
    """Game configuration."""
    timer_duration: int = 30
    exact_points: int = 10
    close_points: int = 5
    near_points: int = 2

class GameManager:
    """Manages game state and rounds."""

    def __init__(self, hass, game_id: str):
        """Initialize game manager."""
        self.hass = hass
        self.game_id = game_id
        self.state = GameState.SETUP
        _LOGGER.info("GameManager initialized for game %s", game_id)
```

**JavaScript Module Structure:**
```javascript
// www/js/websocket-client.js

/**
 * WebSocket client with auto-reconnect.
 */

const WS_ENDPOINT = '/api/beatsy/ws';
const RECONNECT_DELAY = 1000;  // ms

export class WebSocketClient {
    constructor(gameId) {
        this.gameId = gameId;
        this.ws = null;
        this.reconnectAttempts = 0;
    }

    async connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}${WS_ENDPOINT}`;

        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = () => this.handleOpen();
        this.ws.onmessage = (event) => this.handleMessage(event);
        this.ws.onerror = (error) => this.handleError(error);
        this.ws.onclose = () => this.handleClose();
    }

    handleOpen() {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.send({ action: 'join_game', game_id: this.gameId });
    }
}
```

### Error Handling Conventions

**Python:**
```python
try:
    await self.hass.services.async_call("media_player", "play_media", {...})
except HomeAssistantError as err:
    _LOGGER.error("Failed to play track: %s", err)
    await self.broadcast_error("spotify_playback_failed", str(err))
    # Don't crash - continue game with error state
except Exception as err:
    _LOGGER.exception("Unexpected error in playback: %s", err)
    raise  # Re-raise unexpected errors
```

**JavaScript:**
```javascript
try {
    ws.send(JSON.stringify(message));
} catch (error) {
    console.error('WebSocket send failed:', error);
    showToast('Connection error, retrying...', 'error');
    this.reconnect();
}
```

### WebSocket Message Formatting

**All agents MUST use these exact formats:**

**Python (Server):**
```python
async def broadcast(self, msg_type: str, data: dict):
    """Broadcast message to all connected players."""
    message = {
        "type": msg_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await self._send_to_all(json.dumps(message))
```

**JavaScript (Client):**
```javascript
send(action, data) {
    const message = {
        action: action,
        player_id: this.playerId,
        data: data
    };
    this.ws.send(JSON.stringify(message));
}
```

### State Management Patterns

**Server State (Python):**
- Single source of truth: `GameManager.state`
- State transitions via methods only (no direct assignment)
- Use `asyncio.Lock()` for state transitions
- Log all state changes

```python
async def transition_to(self, new_state: GameState):
    """Transition to new state."""
    async with self._state_lock:
        old_state = self.state
        self.state = new_state
        _LOGGER.info("Game %s: %s → %s", self.game_id, old_state, new_state)
        await self.broadcast("state_change", {"state": new_state.value})
```

**Client State (JavaScript):**
- React to server state broadcasts (don't predict state changes)
- Local UI state only (timer countdown, form inputs)
- Always defer to server for authoritative state

```javascript
handleStateChange(newState) {
    this.currentState = newState;
    this.updateUI(newState);
    // Don't predict - wait for server confirmation
}
```

### Testing Patterns

**Python Unit Tests:**
```python
# tests/test_game_manager.py
import pytest
from custom_components.beatsy.game_manager import GameManager, GameState

@pytest.mark.asyncio
async def test_start_round(hass, game_manager):
    """Test round start transition."""
    await game_manager.start_round()
    assert game_manager.state == GameState.ACTIVE
    assert game_manager.round_start_time is not None
```

**Test File Locations:**
- Python: `tests/test_*.py`
- Co-located with source files: `tests/test_game_manager.py` for `game_manager.py`

### Logging Patterns

**Python:**
```python
_LOGGER.debug("Player %s submitted guess: %d", player_id, year)
_LOGGER.info("Round started for game %s", game_id)
_LOGGER.warning("Player %s reconnecting after timeout", player_id)
_LOGGER.error("Spotify service call failed: %s", error)
```

**JavaScript:**
```javascript
console.log('WebSocket connected');
console.warn('Reconnecting after disconnect...');
console.error('Failed to send message:', error);
```

## Consistency Rules

(See Implementation Patterns section above for complete naming conventions, code organization, error handling, and logging strategies)

## Data Architecture

### Core Data Models

**Python (Backend):**
```python
@dataclass
class GameConfig:
    """Game configuration settings."""
    timer_duration: int = 30  # seconds
    exact_points: int = 10
    close_points: int = 5    # ±2 years
    near_points: int = 2     # ±5 years
    year_range: tuple[int, int] = (1950, 2024)

@dataclass
class Player:
    """Player data model."""
    player_id: str  # UUID
    name: str
    score: int = 0
    guesses: list[dict] = field(default_factory=list)
    connected: bool = True
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class Round:
    """Single round data."""
    round_number: int
    track_uri: str
    correct_year: int
    metadata: dict  # title, artist, album, cover_url, fun_fact
    guesses: dict[str, tuple[int, bool]] = field(default_factory=dict)  # player_id → (year, bet)
    results: Optional[dict] = None

class GameState(Enum):
    """Game state enumeration."""
    SETUP = "setup"
    WAITING = "waiting"
    ACTIVE = "active"
    RESULTS = "results"
```

### Data Flow

1. **Game Creation:** Admin → Server creates `GameSession` with UUID
2. **Player Join:** Client → Server adds `Player` to session
3. **Round Start:** Server loads track from JSON → Calls Spotify → Fetches metadata → Broadcasts `Round`
4. **Guess Submission:** Client → Server stores guess in `Round.guesses`
5. **Round End:** Server calculates scores → Updates `Player.score` → Broadcasts results
6. **Persistence:** Server saves final state to HA Registry (game history)

### HA Registry Storage Schema

```python
# Stored in HA Registry as: beatsy.game_{game_id}
{
    "game_id": "uuid",
    "created_at": "2025-01-09T...",
    "ended_at": "2025-01-09T...",
    "config": {...},
    "playlist_id": "80s_hits",
    "final_scores": [
        {"player_name": "Markus", "score": 75},
        {"player_name": "Anna", "score": 62}
    ],
    "rounds": [
        {"track": "...", "year": 1986, "guesses": {...}}
    ]
}
```

## API Contracts

### WebSocket Message Specifications

**Client → Server Actions:**

```javascript
// Join game
{
    "action": "join_game",
    "data": {
        "game_id": "uuid",
        "player_name": "Markus"
    }
}

// Submit guess
{
    "action": "submit_guess",
    "player_id": "uuid",
    "data": {
        "year": 1987,
        "bet": true
    }
}

// Admin: Start round
{
    "action": "start_round",
    "player_id": "uuid (admin)",
    "data": {}
}
```

**Server → Client Messages:**

```javascript
// Game state snapshot
{
    "type": "game_state",
    "data": {
        "game_id": "uuid",
        "state": "waiting",
        "players": [...],
        "config": {...}
    },
    "timestamp": "2025-01-09T..."
}

// Round start
{
    "type": "round_start",
    "data": {
        "round_number": 3,
        "timer_start": 1704805200.123,
        "timer_duration": 30,
        "metadata": {
            "title": "Livin' on a Prayer",
            "artist": "Bon Jovi",
            "album": "Slippery When Wet",
            "cover_url": "https://...",
            "fun_fact": "..."
        }
    },
    "timestamp": "..."
}

// Round results
{
    "type": "round_end",
    "data": {
        "correct_year": 1986,
        "results": [
            {
                "player_name": "Markus",
                "guess": 1987,
                "bet": true,
                "points_earned": 10,
                "new_score": 45
            }
        ],
        "leaderboard": [...]
    },
    "timestamp": "..."
}
```

## Security Architecture

### Threat Model

**Low-Risk Environment:**
- Local network only (same WiFi as HA)
- Party game context (guests are physically present)
- No sensitive data (just names and game scores)
- Ephemeral sessions (24h auto-delete)

### Security Measures

**1. Network Isolation:**
- WebSocket only accessible on local network
- No external internet exposure required
- Firewall: Block external access to port 8123

**2. Game-Based Authorization:**
- Game IDs are UUIDs (128-bit, unguessable)
- No user accounts or passwords
- Sessions expire after 24h inactivity

**3. Input Validation:**
```python
# Validate player name
if not (1 <= len(name) <= 20) or not name.isalnum():
    raise ValueError("Invalid player name")

# Validate year guess
if not (1900 <= year <= datetime.now().year):
    raise ValueError("Year out of range")
```

**4. Rate Limiting:**
- Max 1 guess per player per round
- Max 20 players per game
- Max 10 games per HA instance

**5. DoS Protection:**
- WebSocket connection limit: 50 concurrent
- Auto-disconnect idle connections (5min timeout)
- Max message size: 1KB

**Attack Vectors NOT Protected:**
- Malicious guest with physical access (out of scope)
- WiFi network compromise (HA security concern, not Beatsy-specific)

## Performance Considerations

### Target Metrics (from PRD)

- **Setup Time:** <60s from link share to first song
- **Round Latency:** <2s from timer expiration to results displayed
- **Concurrent Players:** 10+ without lag
- **WebSocket Latency:** <100ms message delivery

### Optimization Strategies

**Backend:**
1. **In-Memory State:** Game state in RAM (no disk I/O during gameplay)
2. **Async I/O:** `asyncio` for all network operations
3. **Connection Pooling:** Reuse HA service connections
4. **Minimal Serialization:** JSON only (no heavy formats)

**Frontend:**
5. **Tailwind Compiled:** Production uses minified CSS (~50KB)
6. **ES6 Modules:** Native browser imports (no bundler overhead)
7. **Lazy Image Loading:** Album art loads on-demand
8. **WebSocket Keep-Alive:** Ping/pong every 30s

**Network:**
9. **Local Network Only:** No internet round-trip
10. **Binary WebSocket:** Use if JSON proves slow (future optimization)

### Resource Limits

- Max game sessions: 10 concurrent
- Max players per game: 20
- Max message rate: 10/second per player
- Memory per game: ~1MB (negligible on HA)

## Deployment Architecture

### Installation (HACS)

1. **User adds custom repository:**
   ```
   https://github.com/username/beatsy
   ```

2. **HACS downloads integration:**
   ```
   /config/custom_components/beatsy/
   ```

3. **User restarts Home Assistant**

4. **Integration auto-registers:**
   - Domain: `beatsy`
   - WebSocket endpoint: `/api/beatsy/ws`
   - Static files: `/local/beatsy/*`

### File Deployment

**Deployed Files:**
```
/config/custom_components/beatsy/
├── __init__.py
├── manifest.json
├── hacs.json
├── *.py (backend modules)
└── www/
    ├── *.html
    ├── js/*.js
    ├── css/*.css
    └── playlists/*.json
```

**URLs:**
- Admin: `http://<HA_IP>:8123/local/beatsy/admin.html`
- Player: `http://<HA_IP>:8123/local/beatsy/start.html?game_id=<uuid>`
- WebSocket: `ws://<HA_IP>:8123/api/beatsy/ws`

### Local Development Workflow

1. **Edit code:** VS Code in project folder
2. **Copy to HA:**
   ```bash
   rsync -av custom_components/beatsy/ /config/custom_components/beatsy/
   ```
3. **Restart HA:** Developer Tools → Restart
4. **Test:** Open admin page, create game, join from phone

## Development Environment

### Prerequisites

- **Home Assistant:** 2024.1+ installed and running
- **Python:** 3.11+ (for local testing)
- **Node.js:** 18+ (for Tailwind CLI compilation)
- **Git:** For version control
- **VS Code:** Recommended IDE

### Setup Commands

```bash
# Clone repository
git clone <repo-url> beatsy
cd beatsy

# Install Python dev dependencies
pip install pytest pytest-asyncio ruff

# Install Tailwind CLI (for CSS compilation)
npm install -D tailwindcss

# Compile Tailwind CSS
npx tailwindcss -i ./custom_components/beatsy/www/css/tailwind.css \
                -o ./custom_components/beatsy/www/css/tailwind.min.css \
                --minify

# Copy to HA (adjust path as needed)
cp -r custom_components/beatsy /config/custom_components/

# Restart HA to load integration
# (via HA UI: Developer Tools → Restart)
```

### Development Cycle

1. Edit Python/JavaScript files
2. Copy to HA: `cp -r custom_components/beatsy /config/custom_components/`
3. Restart HA (or reload integration if supported)
4. Test via browser: `http://192.168.0.191:8123/local/beatsy/admin.html`
5. Check logs: HA → Settings → System → Logs (filter: beatsy)

## Architecture Decision Records (ADRs)

### ADR-001: Custom WebSocket vs HA WebSocket API

**Status:** Accepted

**Context:** Need real-time communication without authentication.

**Decision:** Use custom aiohttp WebSocket endpoint with `requires_auth = False`.

**Rationale:**
- HA's WebSocket API requires authentication (conflicts with public access)
- Custom endpoint gives full control over message format
- Direct WebSocket communication (no event indirection)

**Consequences:** Must implement reconnection logic, but gain flexibility.

---

### ADR-002: Hybrid State Storage (Memory + Registry)

**Status:** Accepted

**Context:** Need fast gameplay but also crash recovery.

**Decision:** Active game in memory, snapshots to HA Registry.

**Rationale:**
- In-memory state eliminates I/O latency during gameplay
- Registry persistence enables crash recovery and game history
- Best of both performance and durability

**Consequences:** Must implement save/load logic, but worth the tradeoff.

---

### ADR-003: Minimal JSON + Runtime Metadata

**Status:** Accepted

**Context:** Need track year for scoring, but avoid metadata duplication.

**Decision:** JSON stores only (URI, year, fun_fact), fetch metadata from HA.

**Rationale:**
- HA already fetches Spotify metadata (title, artist, album, cover)
- Avoids outdated metadata if Spotify updates
- Minimal JSON files (easier to create/maintain)

**Consequences:** 2-second delay for HA state to update after playback starts.

---

### ADR-004: ES6 Modules Without Bundler

**Status:** Accepted

**Context:** UX spec requires "no build process" but need code modularity.

**Decision:** Use native ES6 modules in browsers.

**Rationale:**
- Modern browsers (2020+) support ES6 imports natively
- No webpack/vite overhead or complexity
- Clean code organization without build step

**Consequences:** Older browser support dropped (acceptable for party game).

---

### ADR-005: Server-Authoritative Timer

**Status:** Accepted

**Context:** Timer must be synchronized across all players.

**Decision:** Server runs timer, clients display countdown locally with sync.

**Rationale:**
- Prevents cheating (server decides when time's up)
- Client-side prediction provides smooth UX
- Sync checkpoints correct drift

**Consequences:** Network latency affects timer accuracy by <500ms (acceptable).

---

_Generated by BMAD Decision Architecture Workflow v1.0_
_Date: 2025-01-09_
_For: Markus_
_Project: Beatsy (Home Assistant Custom Component)_
