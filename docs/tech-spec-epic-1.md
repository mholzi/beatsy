# Epic Technical Specification: Foundation & Multi-Risk POC

Date: 2025-11-10
Author: Markus
Epic ID: epic-1
Status: Draft

---

## Overview

Epic 1 establishes the technical foundation for Beatsy by validating all critical architectural assumptions before committing to full development. This POC-driven epic tests five core risks: unauthenticated HTTP/WebSocket access, Spotify API integration viability, data registry performance, and system scalability with concurrent connections.

The epic delivers a minimal but functional Home Assistant custom component that proves the "zero friction party game" concept is technically feasible. Success means we can confidently proceed to production implementation knowing that guests can join without HA credentials, real-time updates work smoothly, and the system handles typical party sizes (10+ players).

This is the most critical epic in the project - if POC tests fail, we pivot to alternative architectures before investing weeks in full development.

## Objectives and Scope

**Primary Objectives:**
1. Validate unauthenticated HTTP access pattern for player web interface
2. Prove WebSocket connectivity works without HA authentication tokens
3. Confirm Spotify API integration can fetch playlists and extract track metadata
4. Verify HA data registry (`hass.data`) handles rapid game state updates
5. Demonstrate system scales to 10+ concurrent WebSocket connections

**In Scope:**
- Minimal component structure (`__init__.py`, `manifest.json`, `const.py`)
- Static test HTML page served without authentication
- Basic WebSocket connection handling (no business logic)
- Spotify playlist fetch and single song playback test
- In-memory state stress test (100 writes in 30 seconds)
- Load test with 10 simulated WebSocket clients
- POC decision document with pass/fail verdicts and pivot recommendations

**Out of Scope:**
- Production-ready code (quality, error handling, documentation)
- Full game logic or UI design
- HACS compliance (handled in Epic 2)
- User-facing features (admin config, player registration)
- Mobile-first design implementation
- Comprehensive testing or security hardening

**Success Criteria:**
Epic succeeds if all 5 POC tests pass OR clear pivot strategy is documented for any failures. Deliverable is the POC Decision Document (`docs/poc-decision.md`) that gates Epic 2 initiation.

## System Architecture Alignment

This epic implements the foundational components from the architecture document:

**Component Structure (Architecture Section: Project Structure)**
- Creates `custom_components/beatsy/` with minimal integration blueprint structure
- Establishes Python 3.11+ component using Home Assistant 2024.x patterns
- Validates component registration and lifecycle

**Unauthenticated Access Pattern (Architecture ADR-001)**
- Tests custom aiohttp WebSocket endpoint with `requires_auth = False`
- Validates static file serving via `/local/beatsy/` or custom HTTP view
- Proves feasibility of game-based authorization (not user-based) per Novel Pattern #1

**WebSocket Infrastructure (Architecture Section: Real-Time Communication)**
- Implements basic WebSocket view from `homeassistant.components.http.HomeAssistantView`
- Tests broadcast capability (one-to-many messaging)
- Validates connection tracking for multiple concurrent clients

**Spotify Integration Strategy (Architecture Section: Integration Points)**
- Leverages existing HA Spotify integration (no duplicate auth)
- Tests `hass.services.async_call("media_player", "play_media", ...)` pattern
- Validates metadata extraction including `album.release_date` for year

**State Management Approach (Architecture ADR-002)**
- Confirms in-memory `hass.data[DOMAIN]` is suitable for active gameplay
- Tests rapid read/write performance (target: 100 ops in 30 seconds)
- Defers persistent storage strategy to Epic 2 (POC focuses on memory performance)

**Constraints Validated:**
- Local network access requirement (no external internet dependencies for gameplay)
- No authentication for player access (breaks standard HA security model intentionally)
- Real-time latency targets (<500ms for WebSocket events per NFR-P2)

## Detailed Design

### Services and Modules

**Python Modules (custom_components/beatsy/):**

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| `__init__.py` | Component registration and setup | HA config | Setup success/failure | Story 1.1 |
| `manifest.json` | HA metadata (domain, version, dependencies) | N/A (static file) | Metadata for HA | Story 1.1 |
| `const.py` | Constants (DOMAIN = "beatsy") | N/A | Constants for all modules | Story 1.1 |
| `http_view.py` | HTTP view for static test page | HTTP requests | HTML response | Story 1.2 |
| `websocket_handler.py` | WebSocket connection manager | WebSocket connections | Broadcast messages | Story 1.3 |
| `spotify_test.py` | Spotify API test helper | Playlist URI, media player entity | Playback result, metadata | Story 1.4 |
| `state_test.py` | Data registry stress test | Test iterations | Performance metrics | Story 1.5 |
| `load_test.py` | WebSocket load test (separate script) | Number of clients | Latency metrics | Story 1.6 |

**Static Files (custom_components/beatsy/www/):**
- `test.html` - Unauthenticated access test page with WebSocket client

**Test Scripts (external to component):**
- `tests/poc_load_test.py` - Python script to simulate 10 concurrent WebSocket clients

### Data Models and Contracts

**POC Data Structures (simplified, not production-ready):**

```python
# In-memory state structure for testing (Story 1.5)
POC_GAME_STATE = {
    "players": [
        {"name": "Player1", "score": 10},
        {"name": "Player2", "score": 15}
    ],
    "current_round": {
        "song_uri": "spotify:track:xxxxx",
        "guesses": [{"player": "Player1", "year": 1985, "bet": True}]
    },
    "played_songs": ["spotify:track:xxxxx", "spotify:track:yyyyy"]
}

# Stored in hass.data[DOMAIN]["game_state"] for stress testing
```

**WebSocket Message Format (Story 1.3):**

```javascript
// Client → Server (test message)
{
    "type": "test_message",
    "data": {"client_id": "test-1", "timestamp": 1704805200}
}

// Server → Client (broadcast test)
{
    "type": "broadcast",
    "data": {"message": "Hello from server", "timestamp": 1704805201}
}
```

**Spotify Metadata Structure (Story 1.4):**

```python
# Example track metadata extracted from Spotify API
{
    "uri": "spotify:track:0J6mQxEZnlRt9ymzFntA6z",
    "name": "Livin' on a Prayer",
    "artists": [{"name": "Bon Jovi"}],
    "album": {
        "name": "Slippery When Wet",
        "release_date": "1986-08-18",  # Critical: Extract year from this
        "images": [{"url": "https://...", "height": 640, "width": 640}]
    }
}
```

**Performance Test Metrics (Story 1.5, 1.6):**

```python
@dataclass
class PerformanceMetrics:
    test_type: str  # "state_writes" or "websocket_load"
    total_operations: int
    duration_seconds: float
    success_count: int
    failure_count: int
    avg_latency_ms: float
    max_latency_ms: float
    errors: List[str]
```

### APIs and Interfaces

**HTTP Endpoints (Story 1.2):**

```python
# Test endpoint for unauthenticated access validation
GET /api/beatsy/test.html
Response: 200 OK (HTML page)
Authentication: None required (requires_auth = False)
Purpose: Validate unauthenticated HTTP access pattern
```

**WebSocket Endpoint (Story 1.3):**

```python
# WebSocket connection for real-time testing
WS ws://<HA_IP>:8123/api/beatsy/ws
Authentication: None required (game-based auth in future)
Messages: JSON format with "type" and "data" fields
Purpose: Validate WebSocket connectivity without HA auth

# Example handshake
Client → Server: {"type": "connect", "data": {"client_id": "test-1"}}
Server → Client: {"type": "connected", "data": {"session_id": "uuid"}}

# Example broadcast
Server → All Clients: {"type": "broadcast", "data": {"message": "Test"}}
```

**Home Assistant Service Calls (Story 1.4):**

```python
# Spotify playback test
await hass.services.async_call(
    domain="media_player",
    service="play_media",
    service_data={
        "entity_id": "media_player.spotify_living_room",
        "media_content_type": "music",
        "media_content_id": "spotify:track:0J6mQxEZnlRt9ymzFntA6z"
    }
)

# Expected result: Song plays on media player within 2 seconds
```

**HA Data Registry Access (Story 1.5):**

```python
# Write operation (test pattern)
hass.data[DOMAIN] = {"game_state": POC_GAME_STATE}
hass.data[DOMAIN]["game_state"]["players"].append(new_player)

# Read operation
game_state = hass.data[DOMAIN]["game_state"]
players = game_state["players"]

# Performance target: 100 write+read cycles in < 30 seconds
```

**Test Script Interface (Story 1.6):**

```python
# Load test script CLI
python tests/poc_load_test.py --clients 10 --duration 300

# Output: JSON metrics
{
    "total_clients": 10,
    "total_messages": 500,
    "avg_latency_ms": 245,
    "max_latency_ms": 480,
    "dropped_connections": 0
}
```

### Workflows and Sequencing

**Story 1.1: Component Registration Flow**
```
Developer → Deploy component files to /config/custom_components/beatsy/
HA Start → Discover component via manifest.json
HA → Call async_setup() in __init__.py
Component → Register domain in hass.data
Component → Log "Beatsy custom component loaded"
HA → Component appears in integrations registry
```

**Story 1.2: Unauthenticated HTTP Access Test**
```
Developer → Create test.html in www/ folder
Component Setup → Register HTTP view with requires_auth=False
Test User → Navigate to http://<HA_IP>:8123/api/beatsy/test.html
HTTP View → Serve HTML without checking HA authentication
Browser → Display "Beatsy POC - Unauthenticated Access Test"
✅ Success: No login prompt, page loads on any device
```

**Story 1.3: WebSocket Connection Test**
```
test.html loads → JavaScript creates WebSocket connection
Client → ws://<HA_IP>:8123/api/beatsy/ws
WebSocket Handler → Accept connection (no auth check)
Client → Send {"type": "test_message", "data": {...}}
Server → Receive and log message
Server → Broadcast {"type": "broadcast", "data": {...}} to all connected clients
Client → Receive broadcast and display in console
✅ Success: Bidirectional messaging without authentication
```

**Story 1.4: Spotify Integration Test**
```
Developer → Configure test playlist URI
Component → Fetch playlist via HA Spotify integration
Spotify API → Return track list (paginated)
Component → Extract track metadata (uri, name, artists, album.release_date)
Component → Parse year from release_date field
Component → Call media_player.play_media service
Media Player → Play track on Spotify speaker
Component → Wait 2 seconds for HA state update
Component → Read media player state attributes (title, artist, cover URL)
✅ Success: Metadata extracted, playback initiated
```

**Story 1.5: Data Registry Stress Test**
```
Test Script → Initialize hass.data[DOMAIN] with POC_GAME_STATE
Loop (100 iterations):
    Write → Update player score in hass.data[DOMAIN]["game_state"]
    Read → Retrieve and validate updated score
    Measure → Record latency for write+read cycle
End Loop
Test Script → Calculate avg/max latency, success/failure count
✅ Success: All writes complete in < 30 seconds, no data corruption
```

**Story 1.6: WebSocket Load Test**
```
Load Test Script → Launch 10 simulated WebSocket clients
For each client:
    Connect → ws://<HA_IP>:8123/api/beatsy/ws
    Handshake → Send connect message
    Subscribe → Listen for broadcasts
Each client (async):
    Send test message every 5 seconds
    Measure latency from send to broadcast receive
Monitor (5 minutes):
    Track: Connection stability, message latency, resource usage
Test Script → Aggregate metrics (avg latency, dropped connections)
✅ Success: All connections stable, latency < 500ms, HA responsive
```

**Story 1.7: POC Decision Document Creation**
```
Developer → Compile results from Stories 1.1-1.6
For each test:
    Record PASS/FAIL verdict
    Document exact configuration used
    Capture code snippets of working patterns
    Note limitations or edge cases discovered
Analyze Failures (if any):
    Identify root cause
    Research alternative approaches
    Document pivot strategy with effort estimate
Create docs/poc-decision.md:
    Summary table (✅/❌ for each test)
    Overall verdict: PROCEED / PIVOT / STOP
    Recommendations for Epic 2
    Pivot plan (if needed): Alternative architectures
✅ Deliverable: POC Decision Document gates Epic 2 initiation
```

## Non-Functional Requirements

### Performance

**Target Metrics (from PRD NFR-P1, NFR-P2, NFR-P4):**

| Metric | Target | Test Story | Rationale |
|--------|--------|------------|-----------|
| Component load time | < 5 seconds (HA startup) | Story 1.1 | POC allows slower startup than production |
| HTTP page load | < 2 seconds | Story 1.2 | Validates basic responsiveness |
| WebSocket connection time | < 1 second | Story 1.3 | Must be instant for user perception |
| WebSocket broadcast latency | < 500ms | Story 1.6 | Critical for real-time social features (NFR-P2) |
| Spotify playback initiation | < 2 seconds | Story 1.4 | Target from NFR-P3 |
| Data registry write latency | < 300ms per operation | Story 1.5 | Must support rapid updates during gameplay |
| Concurrent WebSocket clients | 10 minimum | Story 1.6 | NFR-P4: Support 10+ players |

**Performance Validation Approach:**
- Story 1.5: Measure 100 sequential write+read cycles, calculate avg/max latency
- Story 1.6: Monitor WebSocket message round-trip time for 10 concurrent clients over 5 minutes
- Acceptable degradation: Up to 20% slower than targets acceptable for POC (tighten in Epic 10)

### Security

**POC Security Posture (from PRD NFR-S1, NFR-S2):**

**Intentional Security Relaxations (for POC only):**
- Unauthenticated HTTP/WebSocket access (validates feasibility, NOT recommended for production)
- No input validation or sanitization (Story 1.2, 1.3 test with trusted inputs only)
- No rate limiting or DoS protection
- No session management or CSRF protection

**Security Constraints Validated:**
- Local network access only (NFR-S1): Test from devices on same WiFi as HA instance
- No external internet exposure required (confirm Spotify works via HA's existing integration)

**Epic 2 Security Hardening Requirements (to be implemented post-POC):**
- Input validation for all user-submitted data (Epic 10, Story 10.5)
- Rate limiting on player joins and WebSocket messages (Epic 10, Story 10.6)
- Game-based authorization strategy (UUID session tokens, not HA user accounts)
- XSS prevention via input sanitization

**Known POC Vulnerabilities (ACCEPTABLE FOR POC ONLY):**
- ⚠️ Any user on local network can access test page (Story 1.2)
- ⚠️ No protection against malicious WebSocket messages (Story 1.3)
- ⚠️ Spotify API credentials exposed via HA integration (existing HA risk, not Beatsy-specific)

### Reliability/Availability

**POC Reliability Goals (from PRD NFR-R1, NFR-R3):**

| Requirement | POC Target | Validation | Production Requirement |
|-------------|-----------|------------|----------------------|
| Component stability | Must not crash HA during testing | Story 1.1: Monitor HA logs for crashes | NFR-R1: Graceful failure modes |
| WebSocket connection stability | No dropped connections during 5-min test | Story 1.6: Track connection drops | NFR-R3: Auto-reconnect |
| Data integrity | 100% accuracy in state read/write | Story 1.5: Validate all 100 operations | NFR-R2: No score corruption |
| Spotify API reliability | Handle API failures gracefully (log, don't crash) | Story 1.4: Test with invalid playlist | Epic 7: Comprehensive error handling |

**Graceful Degradation Approach (POC):**
- If HTTP view fails: Log error, document issue, do NOT crash HA
- If WebSocket connection fails: Log error, client shows "Connection lost"
- If Spotify API fails: Log error with details (token expired, network timeout, etc.)
- If data registry write fails: Log error, continue test, mark as FAIL in metrics

**Deferred to Later Epics:**
- Auto-reconnect logic (Epic 6: Real-Time Infrastructure)
- Session persistence across HA restarts (Epic 2: Core Infrastructure)
- Comprehensive error recovery (Epic 10: Production Readiness)

### Observability

**POC Logging Strategy (from PRD NFR-M3):**

**Required Log Events:**

| Event | Level | Format | Purpose |
|-------|-------|--------|---------|
| Component loaded | INFO | "Beatsy custom component loaded (POC)" | Confirm component registration |
| HTTP view registered | INFO | "Test HTTP view registered at /api/beatsy/test.html" | Validate unauthenticated access setup |
| WebSocket connection | DEBUG | "WebSocket client connected: {client_id}" | Track active connections |
| WebSocket disconnection | DEBUG | "WebSocket client disconnected: {client_id}" | Detect connection issues |
| Spotify API call | INFO | "Fetching playlist: {playlist_uri}" | Trace Spotify integration |
| Spotify playback initiated | INFO | "Playing track {track_uri} on {media_player_entity}" | Confirm playback |
| Data registry write | DEBUG | "State write: {operation} completed in {latency_ms}ms" | Performance monitoring |
| Test metrics | INFO | "POC Test Results: {test_name} - {result}" | Final POC verdicts |
| Errors | ERROR | "{component}.{function}: {error_message}" | Troubleshooting failures |

**Logging Configuration:**
- Use Python `logging` module with logger name: `custom_components.beatsy`
- Debug logs enabled for POC (disable in production for performance)
- All logs written to HA's standard log file: `/config/home-assistant.log`
- Log format: `YYYY-MM-DD HH:MM:SS LEVEL [beatsy] message`

**Performance Metrics Collection (Story 1.5, 1.6):**
- Write performance data to JSON file: `tests/poc_metrics.json`
- Include: Test name, timestamp, success/failure count, latency stats, errors
- Use for POC Decision Document (Story 1.7)

**Observability Deferred to Epic 10:**
- Structured logging with trace IDs
- Prometheus metrics export (if applicable)
- HA DevTools integration for debugging

## Dependencies and Integrations

**Home Assistant Core Dependencies:**

| Dependency | Version | Purpose | Used In |
|------------|---------|---------|---------|
| Home Assistant Core | 2024.1+ | Integration platform | All stories |
| Python | 3.11+ | Programming language | All Python code |
| aiohttp | (bundled with HA) | HTTP/WebSocket server | Stories 1.2, 1.3 |
| asyncio | (Python stdlib) | Async runtime | Stories 1.3, 1.4, 1.5 |
| logging | (Python stdlib) | Logging infrastructure | All stories |

**External Integrations (via Home Assistant):**

| Integration | Required For | Configuration | Story |
|-------------|--------------|---------------|-------|
| Spotify | Music playback and metadata | Existing HA Spotify integration | Story 1.4 |
| Media Player domain | Playback control | At least one Spotify-capable player | Story 1.4 |
| HTTP component | Serving static files/views | Built-in HA component | Story 1.2 |
| WebSocket API | Real-time messaging | Built-in HA component | Story 1.3 |

**Development Dependencies (local testing only):**

```python
# tests/requirements.txt (not deployed to HA)
pytest==8.0.0           # Unit testing framework
pytest-asyncio==0.23.0  # Async test support
aiohttp==3.9.0          # WebSocket client for load testing
```

**Manifest Dependencies (Story 1.1):**

```json
{
  "domain": "beatsy",
  "name": "Beatsy",
  "version": "0.1.0-poc",
  "dependencies": ["http", "spotify"],
  "requirements": [],
  "codeowners": ["@markusholzhaeuser"],
  "iot_class": "local_push"
}
```

**Integration Points:**
- `hass.http` → Register HTTP views and static file paths (Story 1.2)
- `hass.components.websocket_api` → Register WebSocket commands (Story 1.3)
- `hass.services` → Call Spotify media_player services (Story 1.4)
- `hass.states` → Read media player state attributes (Story 1.4)
- `hass.data` → In-memory state storage (Story 1.5)

**No External Services Required:**
- All functionality works offline within local network
- Spotify API accessed via existing HA integration (no separate auth)
- No cloud dependencies or third-party APIs

## Acceptance Criteria (Authoritative)

**Epic-Level Acceptance Criteria:**

✅ **AC-1: Component Registration**
- Beatsy component loads in HA without errors
- Component appears in HA integrations registry
- No HA crashes or performance degradation during/after loading
- Verified via: HA logs, HA UI integrations page

✅ **AC-2: Unauthenticated HTTP Access**
- Test HTML page accessible at `/api/beatsy/test.html` without HA login
- Page loads successfully from multiple devices on local network
- No authentication prompt or 401/403 errors
- Verified via: Browser tests from phone, tablet, laptop (not logged into HA)

✅ **AC-3: WebSocket Connectivity Without Authentication**
- WebSocket connection established to `ws://<HA_IP>:8123/api/beatsy/ws` without auth token
- Client can send messages to server
- Server can broadcast messages to all connected clients
- 10+ simultaneous WebSocket connections supported
- Verified via: JavaScript WebSocket client in test.html, load test script

✅ **AC-4: Spotify API Integration**
- Beatsy fetches playlist tracks via HA's Spotify integration
- Track metadata extracted: uri, title, artist, album, release year
- Playback initiated on configured media player
- Song plays within 2 seconds of command
- Verified via: Spotify API test with real playlist, audio output confirmation

✅ **AC-5: Data Registry Performance**
- 100 write+read cycles complete in < 30 seconds
- All operations succeed without data corruption
- No HA performance impact (UI remains responsive)
- Verified via: Stress test script with metrics collection

✅ **AC-6: Concurrent WebSocket Scalability**
- 10 concurrent WebSocket clients connect and communicate
- No connections dropped during 5-minute test
- Average message latency < 500ms
- HA resource usage acceptable (< 50% CPU, < 500MB RAM increase)
- Verified via: Load test script with 10 simulated clients

✅ **AC-7: POC Decision Document**
- All 6 POC tests documented with PASS/FAIL verdicts
- Exact configuration patterns captured (code snippets)
- If any test fails: Pivot strategy documented with effort estimate
- Overall verdict: PROCEED / PIVOT / STOP
- Recommendations for Epic 2 provided
- Document saved as `docs/poc-decision.md`

**Epic Success Criteria:**
Epic 1 succeeds if AC-1 through AC-7 are all met. If any AC fails, epic still succeeds if AC-7 documents a viable pivot strategy.

## Traceability Mapping

**PRD Requirements → Epic 1 Stories:**

| PRD Requirement | Epic 1 Story | Acceptance Criteria | Test Approach |
|-----------------|--------------|---------------------|---------------|
| FR-1.1: HACS Installation | Story 1.1 | AC-1 | Component loads without errors |
| FR-1.2: Spotify Integration | Story 1.4 | AC-4 | Fetch playlist, play track, extract metadata |
| FR-1.3: Data Persistence | Story 1.5 | AC-5 | Rapid state write/read performance |
| FR-1.4: WebSocket Communication | Stories 1.3, 1.6 | AC-3, AC-6 | Unauthenticated WebSocket, 10 concurrent clients |
| NFR-P2: Real-Time Updates (< 500ms) | Story 1.6 | AC-6 | Measure WebSocket broadcast latency |
| NFR-P3: Music Playback (< 2s) | Story 1.4 | AC-4 | Measure playback initiation time |
| NFR-P4: Concurrent Players (10+) | Story 1.6 | AC-6 | Load test with 10 WebSocket clients |
| NFR-S1: Local Network Only | Stories 1.2, 1.3 | AC-2, AC-3 | Test from devices on same WiFi |
| NFR-R1: Component Stability | Story 1.1 | AC-1 | Monitor HA logs for crashes |

**Architecture Decisions → Epic 1 Validation:**

| Architecture Decision | Epic 1 Validation | Story | Outcome |
|----------------------|-------------------|-------|---------|
| ADR-001: Custom WebSocket vs HA WebSocket API | Test unauthenticated WebSocket | Story 1.3 | Proves feasibility of `requires_auth=False` pattern |
| ADR-002: Hybrid State Storage (Memory + Registry) | Stress test in-memory state | Story 1.5 | Confirms `hass.data` performance sufficient |
| ADR-003: Minimal JSON + Runtime Metadata | Extract Spotify metadata | Story 1.4 | Validates metadata available from HA media player state |
| Pattern #1: Unauthenticated WebSocket in HA | Test public WebSocket view | Story 1.3 | Documents exact implementation pattern |

**Epic 1 Stories → Epic 2+ Dependencies:**

| Epic 1 Deliverable | Consumed By | Purpose |
|--------------------|-------------|---------|
| Component structure pattern | Epic 2 (Story 2.1) | HACS-compliant manifest |
| Unauthenticated HTTP pattern | Epic 3 (Story 3.1), Epic 4 (Story 4.1) | Admin and player interfaces |
| WebSocket broadcast pattern | Epic 6 (All stories) | Real-time event infrastructure |
| Spotify integration pattern | Epic 7 (All stories) | Music playback integration |
| In-memory state performance data | Epic 2 (Story 2.3) | Game state management design |
| POC Decision Document | Epic 2 (Gate) | Proceed/Pivot decision |

**Test Coverage Matrix:**

| Component | Unit Test | Integration Test | Load Test | Story |
|-----------|-----------|------------------|-----------|-------|
| Component registration | ✅ Story 1.1 | ✅ Story 1.1 (HA startup) | N/A | 1.1 |
| HTTP view (unauthenticated) | ✅ Story 1.2 | ✅ Story 1.2 (multi-device) | N/A | 1.2 |
| WebSocket connection | ✅ Story 1.3 | ✅ Story 1.3 (broadcast) | ✅ Story 1.6 (10 clients) | 1.3, 1.6 |
| Spotify API | ✅ Story 1.4 | ✅ Story 1.4 (real playlist) | N/A | 1.4 |
| Data registry | ✅ Story 1.5 | ✅ Story 1.5 (100 ops) | N/A | 1.5 |

## Risks, Assumptions, Open Questions

**High-Priority Risks:**

| Risk ID | Description | Probability | Impact | Mitigation | Owner |
|---------|-------------|-------------|--------|------------|-------|
| R-1 | Unauthenticated WebSocket may not be supported by HA | Medium | **CRITICAL** | Story 1.3 tests feasibility; Pivot to SSE/polling if fails | Story 1.3, 1.7 |
| R-2 | Spotify API may not expose release year metadata | Low | High | Story 1.4 validates metadata structure; Filter songs without year | Story 1.4 |
| R-3 | Data registry performance insufficient for gameplay | Low | High | Story 1.5 stress tests 100 ops; Pivot to optimized structures if needed | Story 1.5 |
| R-4 | WebSocket may not scale to 10+ concurrent connections | Low | Medium | Story 1.6 load test; Document max capacity, may need connection pooling | Story 1.6 |
| R-5 | HA may crash or degrade with custom component | Low | **CRITICAL** | Story 1.1 monitors logs; Implement error handling, avoid blocking operations | Story 1.1 |

**Medium-Priority Risks:**

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R-6 | Spotify token may expire during testing | Medium | Low | Document refresh pattern for Epic 7; Handle gracefully in Story 1.4 |
| R-7 | Network latency on WiFi may exceed 500ms target | Medium | Medium | Accept for POC; Optimize in Epic 6 with client-side prediction |
| R-8 | HACS manifest format may have changed | Low | Low | Reference latest HACS docs; Story 1.1 validates structure |

**Assumptions:**

| ID | Assumption | Validation | Risk if Wrong |
|----|------------|------------|---------------|
| A-1 | Home Assistant 2024.1+ installed on test system | Story 1.1 (check HA version) | Component won't load on older versions |
| A-2 | Spotify integration already configured in HA | Story 1.4 (verify integration exists) | Cannot test Spotify without manual setup |
| A-3 | At least one Spotify-capable media player available | Story 1.4 (check media players) | Cannot test playback without hardware |
| A-4 | Local network WiFi supports 10+ concurrent devices | Story 1.6 (load test validates) | Load test may fail due to network limits |
| A-5 | Test environment has stable internet for Spotify API | Story 1.4 (monitor network) | Intermittent failures may skew results |
| A-6 | Developer has HA API access and can deploy components | Story 1.1 (deploy attempt) | Cannot proceed if deployment restricted |

**Open Questions:**

| ID | Question | Resolution Target | Blocker For |
|----|----------|-------------------|-------------|
| Q-1 | Does HA support `requires_auth=False` for WebSocket views? | Story 1.3 | Epic 6 (WebSocket infrastructure) |
| Q-2 | What is the exact metadata structure returned by Spotify via HA? | Story 1.4 | Epic 7 (Music integration) |
| Q-3 | Can we use `hass.http.register_static_path()` or need custom view? | Story 1.2 | Epic 3, 4 (Admin/Player UIs) |
| Q-4 | What is the practical limit for concurrent WebSocket connections? | Story 1.6 | Epic 6, 10 (Scalability planning) |
| Q-5 | Do we need HACS repository setup for POC or just local testing? | Story 1.1 | Epic 2 (HACS compliance) |

**Pivot Strategies (if POC fails):**

**Scenario 1: WebSocket Auth Required (R-1)**
- **Alternative A:** Server-Sent Events (SSE) for server→client, AJAX for client→server
- **Alternative B:** Polling with long-timeout requests
- **Alternative C:** Simple 4-digit PIN code per game session
- **Effort:** 1-2 weeks to implement alternative

**Scenario 2: Spotify Metadata Insufficient (R-2)**
- **Alternative A:** Manual JSON playlist files with track URIs + years
- **Alternative B:** Use Spotify Web API directly (separate auth, more complex)
- **Effort:** 1 week for JSON approach, 2-3 weeks for direct API

**Scenario 3: Performance Issues (R-3, R-4)**
- **Alternative:** Reduce player count limit to tested maximum
- **Alternative:** Implement connection pooling or optimize state structures
- **Effort:** 1 week optimization

## Test Strategy Summary

**Testing Approach: POC Validation (Not Production QA)**

Epic 1 focuses on feasibility validation, not comprehensive testing. Each story includes specific tests to prove/disprove architectural assumptions.

**Story-Level Testing:**

| Story | Test Type | Test Method | Success Criteria | Duration |
|-------|-----------|-------------|------------------|----------|
| 1.1 | Manual Integration | Deploy to HA, check logs/UI | Component loads, no errors | 30 min |
| 1.2 | Manual Functional | Access from multiple devices | Page loads without auth | 30 min |
| 1.3 | Manual + Automated | JS client + Python test script | Bidirectional messaging | 1 hour |
| 1.4 | Manual Integration | Real Spotify playlist + playback | Metadata extracted, song plays | 1 hour |
| 1.5 | Automated Performance | Python stress test script | 100 ops < 30s, no corruption | 30 min |
| 1.6 | Automated Load | Python WebSocket load test | 10 clients, <500ms latency | 15 min |
| 1.7 | Documentation | Compile test results | All tests documented | 2 hours |

**Test Environment:**

```yaml
Hardware:
  - Home Assistant: Running on local server/Raspberry Pi
  - HA Version: 2024.1 or later
  - Network: Local WiFi, stable connection
  - Test Devices: 1 laptop (developer), 2 phones (player simulation)

Software:
  - Python: 3.11+ for test scripts
  - Browsers: Safari (iOS), Chrome (Android), Firefox (Desktop)
  - Spotify: Active premium account with playlists
  - Media Player: At least 1 Spotify-capable speaker/player

Test Data:
  - Test Playlist: 10-20 tracks with release years (1950-2024 range)
  - Test Players: Simulated player data (names, scores)
```

**Test Execution Sequence:**

1. **Story 1.1** (Day 1): Deploy component, verify registration
2. **Story 1.2** (Day 1): Test unauthenticated HTTP access
3. **Story 1.3** (Day 2): Test unauthenticated WebSocket
4. **Story 1.5** (Day 2): Data registry stress test (can run parallel to 1.3)
5. **Story 1.4** (Day 3): Spotify integration test (requires real playlist setup)
6. **Story 1.6** (Day 3): WebSocket load test
7. **Story 1.7** (Day 4): Compile results, write POC decision doc

**Total Estimated Time: 3-4 days**

**Test Metrics Collected:**

```python
# Example metrics structure (saved to tests/poc_metrics.json)
{
  "test_date": "2025-11-15",
  "ha_version": "2024.1.2",
  "tests": {
    "component_registration": {
      "status": "PASS",
      "load_time_ms": 1250,
      "errors": []
    },
    "http_unauthenticated": {
      "status": "PASS",
      "devices_tested": ["iPhone 14", "MacBook Pro", "Android Phone"],
      "errors": []
    },
    "websocket_connectivity": {
      "status": "PASS",
      "connection_time_ms": 450,
      "broadcast_latency_ms": 180,
      "errors": []
    },
    "spotify_integration": {
      "status": "PASS",
      "playlist_tracks": 15,
      "playback_time_ms": 1850,
      "metadata_complete": true,
      "errors": []
    },
    "data_registry_performance": {
      "status": "PASS",
      "total_operations": 100,
      "duration_seconds": 22.4,
      "avg_latency_ms": 224,
      "max_latency_ms": 310,
      "errors": []
    },
    "websocket_load": {
      "status": "PASS",
      "concurrent_clients": 10,
      "test_duration_seconds": 300,
      "avg_latency_ms": 245,
      "max_latency_ms": 480,
      "dropped_connections": 0,
      "errors": []
    }
  },
  "overall_verdict": "PROCEED"
}
```

**Pass/Fail Criteria:**

Each test must meet its specific acceptance criteria (AC-1 through AC-7). If ANY test fails:
- Document failure details in `poc_metrics.json`
- Investigate root cause
- Propose pivot strategy in Story 1.7
- Overall verdict becomes "PIVOT" instead of "PROCEED"

**Epic 1 gates Epic 2:** No work begins on Epic 2 until POC Decision Document (Story 1.7) is approved.

**Deferred Testing (Handled in Later Epics):**
- Unit tests for production code quality (Epic 10)
- End-to-end integration tests (Epic 10)
- Cross-browser compatibility testing (Epic 10)
- Security penetration testing (Epic 10)
- User acceptance testing (Epic 10)

**POC Philosophy:** Prove it works, document how it works, decide if we continue.
