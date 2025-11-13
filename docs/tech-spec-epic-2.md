# Epic Technical Specification: HACS Integration & Core Infrastructure

Date: 2025-11-11
Author: Markus
Epic ID: epic-2
Status: Draft

---

## Overview

Epic 2 establishes the production-ready foundation that all subsequent epics will build upon. Building on the successful POC validation from Epic 1, this epic transforms the prototype into a HACS-compliant Home Assistant custom integration with proper component lifecycle management, structured game state handling, and the core infrastructure patterns that enable admin configuration, player connections, and real-time gameplay.

This epic delivers the "backbone" of Beatsy - the component registration, HTTP routing, WebSocket infrastructure, in-memory state management, Spotify player detection, and optionally a configuration entry UI. All stories in this epic focus on infrastructure rather than user-facing features, providing the stable platform required for Epic 3 (Admin Interface) and Epic 4 (Player Registration) to build upon.

## Objectives and Scope

**Primary Objectives:**
1. Make Beatsy installable and updateable via HACS (Home Assistant Community Store)
2. Implement proper HA component lifecycle (setup, reload, unload with cleanup)
3. Establish in-memory game state management using `hass.data[DOMAIN]` with accessor functions
4. Detect all Spotify-capable media players in the HA instance
5. Register HTTP routes for admin and player web interfaces
6. Register WebSocket commands and broadcast infrastructure for real-time gameplay
7. (Optional) Implement modern HA 2025 config entry pattern for UI-based setup

**In Scope:**
- HACS-compliant repository structure (`hacs.json`, proper `manifest.json`, `README.md`, `info.md`)
- Component lifecycle hooks (`async_setup`, `async_unload`, cleanup handlers)
- Game state data structure with accessor functions (`get_game_config()`, `get_players()`, `update_player_score()`)
- Spotify media player detection function (`get_spotify_media_players()`)
- HTTP view registration for `/api/beatsy/admin` and `/api/beatsy/player` routes
- WebSocket command registration (`beatsy/join_game`, `beatsy/submit_guess`, etc.) and `broadcast_event()` helper
- Optional: `config_flow.py` with `ConfigFlow` class for HA UI-based configuration
- Unit tests for all core functions

**Out of Scope:**
- Actual admin or player UI implementation (HTML/CSS/JS) - Epic 3 & 4
- Game logic (scoring, timer, song selection) - Epic 5
- Real-time event bus layer - Epic 6 (this epic provides raw WebSocket, Epic 6 adds pub/sub pattern)
- Music playback control - Epic 7
- End-to-end integration tests - Epic 10

**Success Criteria:**
- Beatsy appears in HACS custom repositories and installs successfully
- Component loads/reloads/unloads without errors in HA logs
- All core accessor functions have unit tests with >80% coverage
- HTTP routes return 200 OK (placeholder content is fine)
- WebSocket connections establish successfully and can send/receive test messages
- Spotify media players are detected and returned in expected format

## System Architecture Alignment

Epic 2 directly implements the foundational layers from the architecture document:

**Component Structure (Architecture: Project Structure)**
- Implements the complete `custom_components/beatsy/` directory structure
- Creates all core Python modules: `__init__.py`, `const.py`, `game_state.py`, `http_view.py`, `websocket_api.py`, `spotify_helper.py`, `storage.py`
- Establishes module responsibilities as defined in architecture's "Component Responsibilities" section

**HACS Distribution (Architecture: Integration Points)**
- Implements `hacs.json` and `manifest.json` per HACS requirements
- Follows integration_blueprint structure from `ludeeus/integration_blueprint`
- Enables community distribution and automatic updates

**HTTP Routing (Architecture: Pattern 1 - Unauthenticated Access)**
- Registers custom HTTP views for `/api/beatsy/admin` and `/api/beatsy/player`
- Implements `requires_auth = False` pattern validated in Epic 1 POC
- Establishes static file serving pattern for future HTML/CSS/JS (Epic 3+)

**WebSocket Infrastructure (Architecture: Pattern 2 - Server-Authoritative Sync)**
- Implements `BeatsyWebSocketView` with connection lifecycle management
- Provides `broadcast_event()` foundation for real-time state synchronization
- Registers game-specific WebSocket commands (join_game, submit_guess, etc.)

**State Management (Architecture: ADR-002)**
- Implements hybrid storage: in-memory `hass.data[DOMAIN]` for active gameplay
- Provides accessor pattern: `get_game_config()`, `get_players()`, `update_player_score()`
- Defers persistent storage (HA Registry) to Story 2.7 config entry

**Spotify Integration (Architecture: Integration Points #1)**
- Wraps HA service calls to `media_player.play_media`
- Detects Spotify-capable entities via state attributes
- Respects existing HA Spotify integration (no duplicate authentication)

**Constraints Addressed:**
- Python 3.11+ compatibility (HA 2024.x requirement)
- aiohttp for async HTTP/WebSocket (bundled with HA)
- No external dependencies beyond HA core
- Local network operation (no cloud services)

## Detailed Design

### Services and Modules

**Python Modules (custom_components/beatsy/):**

| Module | Responsibility | Key Functions/Classes | Dependencies | Owner Story |
|--------|----------------|----------------------|--------------|-------------|
| `__init__.py` | Integration setup, component registration | `async_setup()`, `async_unload()` | HA core | 2.2 |
| `manifest.json` | HA metadata (domain, version, deps) | N/A (static JSON) | None | 2.1 |
| `hacs.json` | HACS distribution metadata | N/A (static JSON) | None | 2.1 |
| `const.py` | Constants and defaults | `DOMAIN`, `DEFAULT_TIMER`, `DEFAULT_POINTS` | None | 2.1 |
| `game_state.py` | Game state data structure and accessors | `init_game_state()`, `get_game_config()`, `get_players()`, `update_player_score()`, `get_current_round()` | None | 2.3 |
| `http_view.py` | HTTP route registration for web UIs | `BeatsyAdminView`, `BeatsyPlayerView` | aiohttp, HA http | 2.5 |
| `websocket_api.py` | WebSocket command handlers | `handle_join_game()`, `handle_submit_guess()`, `handle_start_game()`, `handle_next_song()`, `handle_place_bet()` | HA websocket_api | 2.6 |
| `websocket_handler.py` | WebSocket connection management | `BeatsyWebSocketView`, `broadcast_event()`, `track_connection()`, `cleanup_connection()` | aiohttp, HA http | 2.6 |
| `spotify_helper.py` | Spotify media player detection | `get_spotify_media_players()` | HA core (states) | 2.4 |
| `storage.py` | HA Registry utilities (future persistence) | `save_game_config()`, `load_game_config()` | HA helpers.storage | 2.7 (optional) |
| `config_flow.py` | HA UI config flow (optional) | `ConfigFlow`, `async_step_user()`, `async_step_reconfigure()` | HA config_entries | 2.7 (optional) |

**Repository Files:**
- `README.md` - Installation and usage documentation
- `info.md` - HACS description and changelog
- `LICENSE` - MIT or Apache 2.0 license file

### Data Models and Contracts

**Game State Structure (Story 2.3):**

```python
# Stored in hass.data[DOMAIN]
GAME_STATE = {
    "game_config": {
        "media_player": str,           # Entity ID (e.g., "media_player.spotify_living_room")
        "playlist_uri": str,           # Spotify playlist URI
        "timer_duration": int,         # Seconds (default: 30)
        "year_range_min": int,         # Default: 1950
        "year_range_max": int,         # Default: 2024
        "exact_points": int,           # Default: 10
        "close_points": int,           # Default: 5 (±2 years)
        "near_points": int,            # Default: 2 (±5 years)
        "bet_multiplier": int,         # Default: 2
    },
    "players": [
        {
            "name": str,               # Player name (unique in session)
            "session_id": str,         # UUID for reconnection
            "total_points": int,       # Accumulated score
            "is_admin": bool,          # Admin flag
            "connected": bool,         # Connection status
        }
    ],
    "current_round": {
        "song_uri": str,               # Spotify track URI
        "started_at": float,           # Unix timestamp
        "status": str,                 # "active" | "ended"
        "guesses": [
            {
                "player_name": str,
                "year_guess": int,
                "bet_placed": bool,
                "submitted_at": float, # Unix timestamp
            }
        ]
    },
    "played_songs": [str],             # List of played Spotify URIs
    "available_songs": [               # Remaining unplayed songs
        {
            "uri": str,
            "title": str,
            "artist": str,
            "year": int,
            "album": str,
            "cover_url": str,
        }
    ],
    "websocket_connections": {         # Active WebSocket connections
        "connection_id": {
            "player_name": str,
            "connected_at": float,
            "last_ping": float,
        }
    }
}
```

**Spotify Media Player Model (Story 2.4):**

```python
@dataclass
class SpotifyMediaPlayer:
    entity_id: str                     # "media_player.spotify_living_room"
    friendly_name: str                 # "Living Room Speaker"
    state: str                         # "idle" | "playing" | "paused"
    source_list: List[str]             # Available sources (must include "Spotify")
```

**WebSocket Message Schema (Story 2.6):**

```python
# Client → Server
{
    "type": str,                       # "beatsy/join_game" | "beatsy/submit_guess" | etc.
    "data": dict,                      # Command-specific payload
}

# Server → Client
{
    "type": str,                       # "beatsy/event"
    "event_type": str,                 # "player_joined" | "round_started" | etc.
    "data": dict,                      # Event payload
}
```

**Configuration Entry Data (Story 2.7 - Optional):**

```python
# Stored in HA's .storage/core.config_entries
{
    "entry_id": str,                   # UUID
    "domain": "beatsy",
    "data": {
        "timer_duration": int,         # User-configured default
        "year_range_min": int,
        "year_range_max": int,
    },
    "options": {}                      # Changeable settings
}
```

### APIs and Interfaces

**Game State Accessor Functions (Story 2.3):**

```python
def init_game_state(hass: HomeAssistant) -> None:
    """Initialize game state structure in hass.data[DOMAIN]."""

def get_game_config(hass: HomeAssistant) -> dict:
    """Retrieve game configuration."""

def get_players(hass: HomeAssistant) -> List[dict]:
    """Retrieve all players."""

def update_player_score(hass: HomeAssistant, player_name: str, points: int) -> None:
    """Add points to player's total score."""

def get_current_round(hass: HomeAssistant) -> Optional[dict]:
    """Retrieve current round state, or None if no active round."""
```

**Spotify Helper Functions (Story 2.4):**

```python
async def get_spotify_media_players(hass: HomeAssistant) -> List[SpotifyMediaPlayer]:
    """
    Detect all Spotify-capable media players in HA.

    Returns:
        List of SpotifyMediaPlayer objects with entity_id and friendly_name.
        Empty list if no Spotify players found or Spotify integration not configured.
    """
```

**HTTP Endpoints (Story 2.5):**

```python
# Admin interface route
GET /api/beatsy/admin
Response: 200 OK (placeholder HTML or redirect to /local/beatsy/admin.html in Epic 3)
Authentication: Required (standard HA auth)

# Player interface route
GET /api/beatsy/player
Response: 200 OK (placeholder HTML or redirect to /local/beatsy/start.html in Epic 3)
Authentication: None (requires_auth = False, per Epic 1 POC pattern)

# API endpoints for future use
GET /api/beatsy/api/media_players
Response: JSON list of Spotify media players
POST /api/beatsy/api/validate_playlist
POST /api/beatsy/api/start_game
POST /api/beatsy/api/next_song
POST /api/beatsy/api/reset_game
```

**WebSocket Commands (Story 2.6):**

```python
# Command: Join game
{
    "type": "beatsy/join_game",
    "data": {
        "player_name": str,
        "game_id": str  # Optional, for future multi-game support
    }
}

# Command: Submit guess
{
    "type": "beatsy/submit_guess",
    "data": {
        "player_name": str,
        "year_guess": int,
        "bet_placed": bool
    }
}

# Command: Place bet
{
    "type": "beatsy/place_bet",
    "data": {
        "player_name": str,
        "bet": bool  # true = betting, false = not betting
    }
}

# Command: Start game (admin only)
{
    "type": "beatsy/start_game",
    "data": {
        "config": dict  # Game configuration
    }
}

# Command: Next song (admin only)
{
    "type": "beatsy/next_song",
    "data": {}
}
```

**WebSocket Broadcast Function (Story 2.6):**

```python
async def broadcast_event(
    hass: HomeAssistant,
    event_type: str,
    data: dict
) -> None:
    """
    Broadcast event to all connected WebSocket clients.

    Args:
        event_type: Event identifier (e.g., "player_joined", "round_started")
        data: Event payload
    """
```

**Configuration Flow API (Story 2.7 - Optional):**

```python
class BeatsyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Beatsy."""

    async def async_step_user(self, user_input: Optional[dict] = None):
        """Handle user-initiated setup."""

    async def async_step_reconfigure(self, user_input: Optional[dict] = None):
        """Handle reconfiguration."""
```

### Workflows and Sequencing

**Story 2.1: HACS Installation Flow**
```
User → HACS → Add Custom Repository → Enter Beatsy GitHub URL
HACS → Fetch repository → Validate hacs.json and manifest.json
HACS → Display Beatsy in integrations list
User → Click Install → HACS downloads to custom_components/beatsy/
User → Restart Home Assistant
HA → Discover Beatsy via manifest.json → Load component
```

**Story 2.2: Component Lifecycle**
```
HA Startup → Call async_setup(hass, config)
Component → Initialize hass.data[DOMAIN]
Component → Register cleanup handlers
Component → Log "Beatsy integration loaded"
HA → Component active

HA Reload → Call async_reload(hass, entry)
Component → Cleanup resources (WebSockets, timers)
Component → Reinitialize state
HA → Component reloaded

HA Shutdown → Call async_unload(hass, entry)
Component → Close all WebSocket connections
Component → Clear hass.data[DOMAIN]
Component → Unregister HTTP/WebSocket handlers
HA → Component unloaded
```

**Story 2.3: Game State Initialization**
```
Component Setup → Call init_game_state(hass)
Function → Create hass.data[DOMAIN] structure
Function → Initialize game_config with defaults
Function → Initialize empty players, current_round, played_songs lists
Function → Initialize websocket_connections dict
Other Modules → Use get_game_config(), get_players(), etc. to access state
```

**Story 2.4: Spotify Media Player Detection**
```
Admin UI (Epic 3) → Call get_spotify_media_players(hass)
Function → Query hass.states.async_all("media_player")
Function → Filter entities with "Spotify" in source_list or entity_id
Function → Build list of SpotifyMediaPlayer objects
Function → Return list (or empty list with warning if none found)
Admin UI → Populate dropdown with friendly names
```

**Story 2.5: HTTP Route Registration**
```
Component Setup → Register HTTP views
Component → hass.http.register_view(BeatsyAdminView)
Component → hass.http.register_view(BeatsyPlayerView)
BeatsyAdminView → requires_auth = True
BeatsyPlayerView → requires_auth = False
Routes Available:
  - /api/beatsy/admin (authenticated)
  - /api/beatsy/player (unauthenticated)
```

**Story 2.6: WebSocket Connection Lifecycle**
```
Client → Connect to ws://HA_IP:8123/api/beatsy/ws
BeatsyWebSocketView → Accept connection (no auth required)
Server → Assign connection_id
Server → Store in hass.data[DOMAIN]["websocket_connections"]
Client → Send beatsy/join_game command
Server → Handle command, update players list
Server → Call broadcast_event("player_joined", data)
All Connected Clients → Receive player_joined event
Client Disconnects → Cleanup handler removes from websocket_connections
```

**Story 2.7: Configuration Entry Setup (Optional)**
```
User → Settings → Integrations → Add Integration → Beatsy
HA → Launch ConfigFlow.async_step_user()
ConfigFlow → Show form with timer_duration, year_range fields
User → Submit form
ConfigFlow → Validate inputs
ConfigFlow → Create ConfigEntry with data
Component → Load via async_setup_entry(hass, entry)
Component → Store entry.data in game_config defaults
```

## Non-Functional Requirements

### Performance

**NFR-P1: State Access Latency**
- Target: `get_*()` accessor functions complete in <10ms
- Rationale: In-memory `hass.data` access is near-instant
- Validation: Epic 1 stress test confirmed 100 operations in <30 seconds

**NFR-P2: WebSocket Broadcast Latency**
- Target: `broadcast_event()` delivers to all clients within 500ms
- Rationale: Local network latency + Python async overhead
- Validation: Story 2.6 includes latency measurement in tests

**NFR-P3: Component Initialization Time**
- Target: `async_setup()` completes in <2 seconds
- Rationale: No external API calls during setup, only registration
- Validation: HA logs timestamp on setup complete

**NFR-P4: Memory Footprint**
- Target: <50MB RAM for active game (10 players, 50 songs loaded)
- Rationale: In-memory state should be lightweight
- Validation: Monitor HA process memory during development

### Security

**NFR-S1: Unauthenticated Access Scope**
- Requirement: Only `/api/beatsy/player` and `/api/beatsy/ws` are unauthenticated
- Rationale: Admin interface requires HA authentication, player interface does not
- Implementation: `requires_auth = False` only on BeatsyPlayerView and BeatsyWebSocketView
- Validation: Attempt to access admin routes without HA token returns 401

**NFR-S2: Input Validation**
- Requirement: All WebSocket command data validated before processing
- Validation Rules:
  - `player_name`: Max 20 chars, alphanumeric + spaces, no HTML tags
  - `year_guess`: Integer within configured year range
  - `bet_placed`: Boolean only
- Implementation: Validation functions in `websocket_api.py`

**NFR-S3: Connection Security**
- Requirement: WebSocket connections track origin and can be rate-limited
- Implementation: Store connection metadata (IP, connected_at) in websocket_connections
- Future: Epic 10 adds rate limiting (max 1 join per IP per 5 seconds)

**NFR-S4: State Isolation**
- Requirement: Game state in `hass.data[DOMAIN]` does not leak across games
- Implementation: State reset on game start, cleared on component unload
- Validation: Unit tests verify state isolation

### Reliability/Availability

**NFR-R1: Graceful Component Reload**
- Requirement: Component can reload without losing active game state
- Implementation: State persists in `hass.data` across reload, connections tracked
- Degradation: WebSocket clients must reconnect after reload (acceptable)

**NFR-R2: WebSocket Connection Resilience**
- Requirement: Dropped connections don't crash server or affect other players
- Implementation: Connection cleanup in try/except blocks, auto-remove on disconnect
- Validation: Story 2.6 tests forced disconnects during active game

**NFR-R3: Error Recovery**
- Requirement: Exceptions in WebSocket handlers don't crash component
- Implementation: All async handlers wrapped in try/except with logging
- Behavior: Log error, send error message to client, continue serving other clients

**NFR-R4: State Corruption Prevention**
- Requirement: Invalid state transitions rejected gracefully
- Implementation: State validation before mutations, atomic updates
- Example: Can't submit guess if round not active, can't add player with duplicate name

### Observability

**NFR-O1: Logging Standards**
- Levels:
  - `INFO`: Component lifecycle (setup, reload, unload), player joins, round starts
  - `DEBUG`: WebSocket message details, state mutations, Spotify API calls
  - `WARNING`: Spotify players not found, connection errors
  - `ERROR`: Exceptions, failed operations
- Format: Include component name, event type, relevant IDs
- Example: `_LOGGER.info("Player %s joined game", player_name)`

**NFR-O2: Key Metrics to Log**
- Component startup/shutdown timestamps
- WebSocket connection count (current, peak)
- Player join/leave events with timestamps
- WebSocket command execution time (for performance monitoring)
- Error rates by command type

**NFR-O3: Debugging Support**
- Requirement: HA debug logs provide sufficient detail to troubleshoot issues
- Implementation: All WebSocket handlers log incoming messages at DEBUG level
- Validation: Enable debug logging and verify all events captured

**NFR-O4: Health Check**
- Requirement: Component reports healthy status to HA
- Implementation: `async_setup()` returns True on success, False on failure
- Future: Add `/api/beatsy/health` endpoint (Epic 10) for monitoring

## Dependencies and Integrations

**Python Dependencies (manifest.json):**

```json
{
  "dependencies": [
    "http",        // HA HTTP component for HTTP views
    "spotify"      // HA Spotify integration (optional, for media player detection)
  ],
  "requirements": []  // No external pip packages needed
}
```

**Home Assistant Version:**
- Minimum: 2024.1.0 (Python 3.11+ requirement)
- Tested: 2024.11.x (current LTS)

**Integration Points:**

**1. Home Assistant HTTP Component**
- Purpose: Register HTTP views and WebSocket endpoints
- API: `hass.http.register_view(view_class)`
- Module: `homeassistant.components.http`

**2. Home Assistant WebSocket API**
- Purpose: Register WebSocket commands
- API: `hass.components.websocket_api.async_register_command()`
- Module: `homeassistant.components.websocket_api`
- Note: Epic 2 uses custom WebSocket view instead, WebSocket API may be used in Epic 6

**3. Home Assistant States**
- Purpose: Query media player entities
- API: `hass.states.async_all("media_player")`, `hass.states.get(entity_id)`
- Module: `homeassistant.core`

**4. Home Assistant Storage (Optional - Story 2.7)**
- Purpose: Persistent config storage
- API: `storage.Store(hass, version, key)`
- Module: `homeassistant.helpers.storage`

**5. Home Assistant Config Entries (Optional - Story 2.7)**
- Purpose: UI-based configuration
- API: `config_entries.ConfigFlow`
- Module: `homeassistant.config_entries`

**External Services:**
- None (Beatsy only integrates with HA's existing Spotify integration)

**Repository Dependencies:**
- Build: None (Python package)
- Test: pytest, pytest-asyncio, pytest-homeassistant-custom-component
- Lint: ruff (Python linter/formatter)

## Acceptance Criteria (Authoritative)

**AC-1: HACS Compliance (Story 2.1)**
1. Repository includes `hacs.json` with required fields (name, domains, country, render_readme)
2. `manifest.json` includes all required HA fields (domain, name, version, dependencies, codeowners, requirements)
3. Repository includes `README.md` with installation instructions
4. HACS recognizes repository when added to custom repositories
5. Beatsy installs successfully via HACS and appears in HA integrations list

**AC-2: Component Lifecycle (Story 2.2)**
1. `async_setup()` executes successfully on HA startup
2. Component logs "Beatsy integration loaded" at INFO level
3. `async_reload()` cleans up and reinitializes without errors
4. `async_unload()` gracefully closes all resources
5. No resource leaks (connections, timers, memory) after unload

**AC-3: Game State Management (Story 2.3)**
1. `init_game_state()` creates complete hass.data[DOMAIN] structure
2. `get_game_config()` returns dict with all config fields
3. `get_players()` returns list of players
4. `update_player_score()` correctly adds points to player total
5. `get_current_round()` returns None when no active round, dict otherwise
6. All accessor functions have unit tests with >80% coverage

**AC-4: Spotify Detection (Story 2.4)**
1. `get_spotify_media_players()` returns list of Spotify-capable players
2. Each player includes entity_id, friendly_name, state
3. Function handles case where no Spotify players exist (returns empty list)
4. Function handles case where Spotify integration not configured (returns empty list with warning log)
5. Function filters correctly (only entities with Spotify capability)

**AC-5: HTTP Routes (Story 2.5)**
1. `/api/beatsy/admin` endpoint registered and returns 200 OK
2. `/api/beatsy/player` endpoint registered and returns 200 OK
3. Admin route requires HA authentication (401 without token)
4. Player route accessible without authentication
5. Routes handle CORS appropriately for local network access

**AC-6: WebSocket Infrastructure (Story 2.6)**
1. WebSocket endpoint `/api/beatsy/ws` accepts connections without authentication
2. All command types registered (join_game, submit_guess, place_bet, start_game, next_song)
3. `broadcast_event()` sends message to all connected clients
4. Connection tracking works (connections added on connect, removed on disconnect)
5. WebSocket handler gracefully handles client disconnects
6. Test client can connect, send command, and receive broadcast

**AC-7: Configuration Entry (Story 2.7 - Optional)**
1. Beatsy appears in HA's Add Integration dialog
2. ConfigFlow presents form with timer duration and year range inputs
3. Configuration validates inputs (timer 10-120, year range valid)
4. ConfigEntry created and stored in HA's config storage
5. Integration options can be updated via HA UI
6. Component loads successfully via `async_setup_entry()`

## Traceability Mapping

| Acceptance Criteria | Tech Spec Section | Components/APIs | Test Idea |
|---------------------|-------------------|-----------------|-----------|
| AC-1: HACS Compliance | Detailed Design: Services and Modules | `hacs.json`, `manifest.json`, `README.md` | Validate with HACS validator, test install via HACS |
| AC-2: Component Lifecycle | Workflows: Story 2.2 | `__init__.py`: `async_setup()`, `async_unload()` | Unit test lifecycle hooks, verify log messages |
| AC-3: Game State Management | Data Models: Game State Structure | `game_state.py`: accessor functions | Unit tests for each accessor, verify state structure |
| AC-4: Spotify Detection | APIs: Spotify Helper Functions | `spotify_helper.py`: `get_spotify_media_players()` | Mock media player states, test filtering logic |
| AC-5: HTTP Routes | APIs: HTTP Endpoints | `http_view.py`: `BeatsyAdminView`, `BeatsyPlayerView` | Integration test: HTTP requests to routes, verify auth |
| AC-6: WebSocket Infrastructure | APIs: WebSocket Commands | `websocket_handler.py`, `websocket_api.py` | Integration test: Connect client, send command, receive broadcast |
| AC-7: Configuration Entry | APIs: Configuration Flow API | `config_flow.py`: `ConfigFlow` | Integration test with HA config entry system |

**Requirements Traceability to PRD:**

| PRD Requirement | Epic 2 Implementation | Status |
|-----------------|----------------------|--------|
| FR-1.1: HACS Installation | Story 2.1 (HACS-compliant manifest) | ✅ Complete |
| FR-1.2: Spotify Integration | Story 2.4 (Media player detection) | ✅ Foundation |
| FR-1.3: Data Persistence | Story 2.3 (In-memory state), Story 2.7 (Config entry) | ✅ In-memory complete, Registry optional |
| FR-1.4: WebSocket Communication | Story 2.6 (WebSocket infrastructure) | ✅ Foundation (events in Epic 6) |
| FR-2.x: Admin Interface | Story 2.5 (HTTP route registration) | 🔄 Routes only, UI in Epic 3 |
| FR-3.x: Player Interface | Story 2.5 (HTTP route registration) | 🔄 Routes only, UI in Epic 4 |
| NFR-P1: Response Time | NFR Performance section | ✅ Targets defined |
| NFR-S1: Security | NFR Security section | ✅ Auth pattern established |

## Risks, Assumptions, Open Questions

**Risks:**

**R1: HACS Approval Delays**
- Risk: HACS submission may require revisions or face approval delays
- Impact: Users cannot install via HACS, must use manual installation
- Mitigation: Research HACS requirements thoroughly (Story 2.1), follow integration_blueprint structure exactly
- Fallback: Provide manual installation instructions in README

**R2: HA API Breaking Changes**
- Risk: Home Assistant updates may break component APIs (http, websocket)
- Impact: Beatsy stops working after HA updates
- Mitigation: Pin minimum HA version in manifest (2024.1+), monitor HA release notes
- Likelihood: Low (HA maintains backwards compatibility for 1+ years)

**R3: WebSocket Connection Limits**
- Risk: HA may impose limits on concurrent WebSocket connections
- Impact: Cannot support 10+ players simultaneously
- Mitigation: Epic 1 POC validated 10 connections; monitor connection count in production
- Fallback: Document max player limit if discovered

**R4: In-Memory State Loss on HA Restart**
- Risk: Active games lost if HA restarts during gameplay
- Impact: Players disconnected, game state reset
- Mitigation: Story 2.7 optional persistence via config entry; Epic 5 includes session management
- Acceptance: MVP accepts state loss on restart (typical party games are ephemeral)

**Assumptions:**

**A1: Spotify Integration Pre-Configured**
- Assumption: Users have HA Spotify integration already set up
- Validation: Story 2.4 handles "no Spotify integration" gracefully (empty list + warning)
- Documentation: README requires Spotify integration as prerequisite

**A2: Local Network Access**
- Assumption: All players on same WiFi as HA instance
- Validation: Epic 1 POC confirmed local network access pattern works
- Scope: MVP does not support remote/internet access (future feature)

**A3: Modern Browser Support**
- Assumption: Players use browsers with WebSocket API support (all modern browsers post-2015)
- Validation: Frontend uses ES2020 features (Epic 3), no legacy browser support
- Documentation: README lists browser requirements

**A4: Single Game Instance**
- Assumption: Only one active game per HA instance (not multi-tenant)
- Validation: State structure supports single game only in MVP
- Future: Epic 2 provides foundation for future multi-game support (game_id in WebSocket)

**Open Questions:**

**Q1: Config Entry vs YAML Configuration?**
- Question: Should Story 2.7 implement config entry (UI) or skip for MVP?
- Decision Needed: By Story 2.7 start
- Recommendation: Skip for MVP (Story 2.7 marked optional), add post-MVP for better UX
- Rationale: Game config happens in-game via admin UI (Epic 3), HA config entry not critical path

**Q2: WebSocket Command vs REST API for Admin Actions?**
- Question: Should admin actions (start_game, next_song) use WebSocket or REST endpoints?
- Current Design: WebSocket commands registered in Story 2.6
- Consideration: REST may be more RESTful for admin mutations
- Decision: Use WebSocket for consistency (real-time game needs WebSocket anyway)

**Q3: Persistent Game History?**
- Question: Should completed game results be saved to HA storage?
- Scope: Out of scope for Epic 2 (infrastructure only)
- Future: Epic 10 or post-MVP feature (game history, leaderboards)

## Test Strategy Summary

**Unit Tests (pytest + pytest-asyncio):**

**Coverage Target: >80% for all Python modules**

**Story 2.1: HACS Compliance**
- Validate `hacs.json` schema (required fields present)
- Validate `manifest.json` schema (HA required fields)
- Test: README.md exists and contains installation section

**Story 2.2: Component Lifecycle**
- Test: `async_setup()` initializes hass.data[DOMAIN]
- Test: `async_setup()` returns True on success
- Test: `async_unload()` clears hass.data[DOMAIN]
- Test: `async_unload()` closes resources without exceptions

**Story 2.3: Game State Management**
- Test: `init_game_state()` creates complete structure
- Test: `get_game_config()` returns expected defaults
- Test: `get_players()` returns empty list initially
- Test: `update_player_score()` adds points correctly
- Test: `update_player_score()` handles non-existent player gracefully
- Test: `get_current_round()` returns None when no round active

**Story 2.4: Spotify Detection**
- Test: `get_spotify_media_players()` with mocked Spotify entities
- Test: `get_spotify_media_players()` filters non-Spotify entities
- Test: `get_spotify_media_players()` returns empty list when no Spotify players
- Test: `get_spotify_media_players()` handles no Spotify integration

**Story 2.5: HTTP Routes**
- Test: Admin route returns 200 with placeholder content
- Test: Player route returns 200 with placeholder content
- Test: Admin route requires authentication (mock auth check)
- Test: Player route bypasses authentication

**Story 2.6: WebSocket Infrastructure**
- Test: WebSocket view accepts connection
- Test: `broadcast_event()` sends to all connected clients
- Test: Connection tracking adds/removes connections correctly
- Test: Dropped connection handled gracefully (no exception)
- Test: WebSocket command handlers registered correctly

**Story 2.7: Configuration Entry (Optional)**
- Test: ConfigFlow validates timer_duration range
- Test: ConfigFlow validates year range (min < max)
- Test: ConfigEntry created with correct data structure
- Test: `async_setup_entry()` loads config successfully

**Integration Tests (pytest-homeassistant-custom-component):**

**Test: Full Component Load**
- Start HA test instance
- Load Beatsy component
- Verify component in hass.data
- Verify no errors in logs

**Test: HTTP Routes Accessible**
- Load component
- Make HTTP request to /api/beatsy/admin
- Make HTTP request to /api/beatsy/player
- Verify responses

**Test: WebSocket Connection**
- Load component
- Connect WebSocket client to /api/beatsy/ws
- Send test message
- Verify broadcast received
- Disconnect client
- Verify cleanup

**Manual Testing Checklist:**

**Story 2.1:**
- [ ] Add Beatsy repository to HACS custom repositories
- [ ] Install via HACS (no errors)
- [ ] Verify Beatsy appears in HA integrations list
- [ ] Restart HA (component loads successfully)

**Story 2.4:**
- [ ] Configure Spotify integration in HA
- [ ] Call `get_spotify_media_players()` via script
- [ ] Verify correct entities returned with friendly names

**Story 2.6:**
- [ ] Use browser console or Postman to connect WebSocket
- [ ] Send test command
- [ ] Verify broadcast received
- [ ] Check HA logs for connection messages

**Edge Cases to Test:**

- Empty Spotify entity list (no media players configured)
- Malformed WebSocket messages (invalid JSON, missing fields)
- Rapid connection/disconnection cycles (connection pool stress)
- Component reload during active WebSocket connections
- Multiple simultaneous WebSocket connections (10+)
- Player name with special characters (validation)

**Performance Tests:**

- Story 2.3: Measure `get_*()` function latency (target <10ms)
- Story 2.6: Measure `broadcast_event()` latency with 10 clients (target <500ms)
- Story 2.6: Monitor memory usage with 10 concurrent connections (target <50MB)

**Test Environment:**

- Development: Local HA instance (http://192.168.0.191:8123)
- CI/CD: GitHub Actions with HA test container
- Pytest fixtures: Mock hass, mock config_entry, mock WebSocket connections

**Frameworks:**
- pytest (Python testing)
- pytest-asyncio (async test support)
- pytest-homeassistant-custom-component (HA integration test helpers)
- aiohttp.test_utils (WebSocket testing)
