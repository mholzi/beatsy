# Epic 2 Manual Testing Guide
## HACS Integration & Core Infrastructure

**Epic ID:** epic-2
**Test Date:** ___________
**Tester:** ___________
**HA Version:** ___________
**Status:** [ ] Pass [ ] Fail

---

## Prerequisites

Before starting manual testing, ensure you have:

- [ ] Home Assistant 2024.1.0+ running and accessible
- [ ] HACS (Home Assistant Community Store) installed
- [ ] Spotify integration configured in Home Assistant
- [ ] At least one Spotify-capable media player entity
- [ ] Browser with Developer Tools (Chrome/Firefox recommended)
- [ ] Network access to HA instance (e.g., http://192.168.0.191:8123)
- [ ] HA access token (for authenticated endpoints)

---

## Testing Overview

Epic 2 establishes the production-ready foundation for Beatsy. This manual test covers:
1. HACS installation and compliance
2. Component lifecycle (load/reload/unload)
3. In-memory game state management
4. Spotify media player detection
5. HTTP route registration
6. WebSocket command infrastructure
7. Configuration entry setup (optional)

Expected Duration: 60-90 minutes

---

## Story 2.1: HACS Compliance

### Test 2.1.1: Repository Structure Validation

**Objective:** Verify repository has all required HACS files

**Steps:**
1. Navigate to repository root directory
2. Verify the following files exist:
   - [ ] `hacs.json`
   - [ ] `custom_components/beatsy/manifest.json`
   - [ ] `README.md`
   - [ ] `info.md`
   - [ ] `LICENSE`

3. Open `hacs.json` and verify required fields:
   ```json
   {
     "name": "Beatsy - Music Year Guessing Game",
     "domains": ["beatsy"],
     "country": ["DE"],
     "render_readme": true
   }
   ```
   - [ ] All fields present
   - [ ] Domain matches "beatsy"

4. Open `custom_components/beatsy/manifest.json` and verify:
   ```json
   {
     "domain": "beatsy",
     "name": "Beatsy",
     "version": "x.x.x",
     "documentation": "...",
     "dependencies": ["http"],
     "codeowners": ["@..."],
     "requirements": []
   }
   ```
   - [ ] All required HA fields present
   - [ ] Version follows semantic versioning
   - [ ] Dependencies include "http"

**Expected Result:** All files present with valid structure

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.1.2: HACS Installation

**Objective:** Install Beatsy via HACS custom repository

**Steps:**
1. Open Home Assistant web interface
2. Navigate to HACS → Integrations
3. Click three-dot menu (⋮) → Custom repositories
4. Add repository URL: `https://github.com/YOUR_USERNAME/beatsy`
5. Select category: Integration
6. Click "Add"
7. Search for "Beatsy" in HACS
8. Click "Download"
9. Restart Home Assistant

**Expected Result:**
- [ ] Beatsy appears in HACS integrations list
- [ ] Download completes without errors
- [ ] Component loads after HA restart
- [ ] No errors in HA logs during startup

**Check HA logs:**
```bash
# SSH into HA or use Terminal add-on
tail -f /config/home-assistant.log | grep -i beatsy
```

Look for:
- [ ] "Beatsy integration loaded" (INFO level)
- [ ] No ERROR or WARNING messages

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.2: Component Lifecycle Management

### Test 2.2.1: Component Startup

**Objective:** Verify component loads successfully on HA startup

**Steps:**
1. Restart Home Assistant (Settings → System → Restart)
2. Wait for HA to fully restart (~30-60 seconds)
3. Check HA logs:
   ```bash
   tail -n 100 /config/home-assistant.log | grep -i beatsy
   ```

**Expected Result:**
- [ ] Log message: "Beatsy integration loaded" (INFO level)
- [ ] No exceptions or errors during setup
- [ ] `async_setup()` completed successfully
- [ ] Component appears in `hass.data["beatsy"]`

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.2.2: Component Reload

**Objective:** Verify component can reload without errors

**Steps:**
1. Open Developer Tools → YAML
2. Click "All YAML configuration" → Reload
3. OR use service call:
   ```yaml
   service: homeassistant.reload_config_entry
   target:
     entity_id: beatsy
   ```
4. Check HA logs for reload messages

**Expected Result:**
- [ ] Component reloads without errors
- [ ] Resources cleaned up (WebSocket connections closed)
- [ ] State reinitialized successfully
- [ ] No resource leaks or warnings

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.2.3: Component Unload

**Objective:** Verify graceful component shutdown

**Steps:**
1. Remove Beatsy from configuration OR
2. Use Developer Tools to unload integration
3. Check HA logs

**Expected Result:**
- [ ] `async_unload()` executes successfully
- [ ] All WebSocket connections closed
- [ ] `hass.data["beatsy"]` cleared
- [ ] No hanging resources or memory leaks
- [ ] No errors during unload

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.3: In-Memory Game State Management

### Test 2.3.1: State Initialization

**Objective:** Verify game state structure is created correctly

**Steps:**
1. Access HA Developer Tools → Template
2. Paste and execute:
   ```jinja2
   {{ states.sensor.beatsy_debug | default('not found') }}
   ```
   OR use Python script via HA:
   ```python
   hass.data.get("beatsy", {})
   ```

3. Verify state structure exists with keys:
   - [ ] `game_config`
   - [ ] `players`
   - [ ] `current_round`
   - [ ] `played_songs`
   - [ ] `available_songs`
   - [ ] `websocket_connections`

**Expected Result:**
State structure initialized with defaults:
```python
{
  "game_config": {
    "media_player": None,
    "timer_duration": 30,
    "year_range_min": 1950,
    "year_range_max": 2024,
    "exact_points": 10,
    "close_points": 5,
    "near_points": 2,
    "bet_multiplier": 2
  },
  "players": [],
  "current_round": None,
  "played_songs": [],
  "available_songs": [],
  "websocket_connections": {}
}
```

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.3.2: Accessor Functions

**Objective:** Verify game state accessor functions work correctly

**Prerequisites:** Component loaded successfully

**Steps:**

**A. Test `get_game_config()`**
1. Create test script in `/config/python_scripts/test_beatsy_state.py`:
   ```python
   from custom_components.beatsy.game_state import get_game_config
   config = get_game_config(hass)
   logger.info(f"Game config: {config}")
   ```
2. Execute script
3. Verify config returned with all fields

**B. Test `get_players()`**
1. Call `get_players(hass)`
2. Verify returns empty list initially: `[]`

**C. Test `update_player_score()`**
1. Add test player to state manually (via WebSocket in Test 2.6)
2. Call `update_player_score(hass, "TestPlayer", 10)`
3. Verify player's `total_points` increased by 10

**D. Test `get_current_round()`**
1. Call `get_current_round(hass)` when no round active
2. Verify returns `None`
3. Start a round (via WebSocket command)
4. Call again, verify returns round dict

**Expected Result:**
- [ ] All accessor functions return expected data types
- [ ] No exceptions raised
- [ ] State modifications persist in memory
- [ ] Functions complete in <10ms (performance requirement)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.4: Spotify Media Player Detection

### Test 2.4.1: Detect Spotify Media Players

**Objective:** Verify Spotify-capable media players are detected

**Prerequisites:**
- [ ] Spotify integration configured in HA
- [ ] At least one Spotify media player entity exists

**Steps:**
1. Open Developer Tools → States
2. Filter for `media_player.` entities
3. Note Spotify entities (e.g., `media_player.spotify_living_room`)

4. Test detection function:
   - Option A: Via HTTP endpoint (if implemented):
     ```bash
     curl -X GET http://192.168.0.191:8123/api/beatsy/api/media_players \
       -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN"
     ```

   - Option B: Via Python script:
     ```python
     from custom_components.beatsy.spotify_helper import get_spotify_media_players
     players = await get_spotify_media_players(hass)
     logger.info(f"Found {len(players)} Spotify players")
     for player in players:
         logger.info(f"  - {player.entity_id}: {player.friendly_name}")
     ```

**Expected Result:**
```json
[
  {
    "entity_id": "media_player.spotify_living_room",
    "friendly_name": "Living Room Speaker",
    "state": "idle",
    "source_list": ["Spotify", "Bluetooth", ...]
  }
]
```

- [ ] Function returns list of Spotify media players
- [ ] Each player has `entity_id`, `friendly_name`, `state`
- [ ] Only Spotify-capable entities included
- [ ] Function completes without errors

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.4.2: Handle No Spotify Players

**Objective:** Verify graceful handling when no Spotify players exist

**Steps:**
1. Temporarily disable Spotify integration (Settings → Integrations → Spotify → Disable)
2. Call `get_spotify_media_players(hass)`
3. Check HA logs

**Expected Result:**
- [ ] Function returns empty list: `[]`
- [ ] WARNING log: "No Spotify media players found"
- [ ] No exceptions raised
- [ ] Function degrades gracefully

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.5: HTTP Route Registration

### Test 2.5.1: Admin Route - Authenticated Access

**Objective:** Verify admin route requires HA authentication

**Steps:**
1. Open browser Developer Tools (F12) → Network tab

2. **Test WITHOUT authentication:**
   ```bash
   curl -X GET http://192.168.0.191:8123/api/beatsy/admin
   ```
   **Expected:** HTTP 401 Unauthorized

3. **Test WITH authentication:**
   - Get long-lived access token from HA:
     - Profile → Security → Long-Lived Access Tokens → Create Token
   ```bash
   curl -X GET http://192.168.0.191:8123/api/beatsy/admin \
     -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN"
   ```
   **Expected:** HTTP 200 OK with placeholder content

4. **Test via Browser (authenticated session):**
   - Ensure logged into HA web interface
   - Navigate to: `http://192.168.0.191:8123/api/beatsy/admin`
   - **Expected:** Page loads (placeholder HTML or redirect)

**Expected Result:**
- [ ] Unauthenticated request returns 401
- [ ] Authenticated request returns 200
- [ ] Route registered at `/api/beatsy/admin`
- [ ] `requires_auth = True` enforced

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.5.2: Player Route - Unauthenticated Access

**Objective:** Verify player route accessible without authentication

**Steps:**
1. **Test WITHOUT authentication (incognito/private window):**
   - Open incognito browser window (not logged into HA)
   - Navigate to: `http://192.168.0.191:8123/api/beatsy/player`
   - **Expected:** HTTP 200 OK (page loads)

2. **Test via curl:**
   ```bash
   curl -X GET http://192.168.0.191:8123/api/beatsy/player
   ```
   **Expected:** HTTP 200 OK with placeholder content

3. **Test from mobile device on same network:**
   - Use phone browser (not logged into HA)
   - Navigate to: `http://192.168.0.191:8123/api/beatsy/player`
   - **Expected:** Page loads without login prompt

**Expected Result:**
- [ ] Unauthenticated request returns 200
- [ ] No login redirect or auth required
- [ ] Route accessible from any device on local network
- [ ] `requires_auth = False` working correctly
- [ ] CORS headers set appropriately for local network

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.5.3: Route Response Content

**Objective:** Verify routes return valid responses

**Steps:**
1. Access both routes (authenticated for admin, unauthenticated for player)
2. Inspect response content:
   ```bash
   curl -i http://192.168.0.191:8123/api/beatsy/player
   ```

**Expected Result:**
- [ ] Content-Type header present (e.g., `text/html` or `application/json`)
- [ ] Response body not empty
- [ ] Placeholder content OR redirect to static files
- [ ] No 404 or 500 errors

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.6: WebSocket Command Registration

### Test 2.6.1: WebSocket Connection

**Objective:** Verify WebSocket endpoint accepts connections

**Steps:**
1. Open browser Developer Tools (F12) → Console tab

2. Paste and execute JavaScript:
   ```javascript
   // Connect to Beatsy WebSocket endpoint
   const ws = new WebSocket('ws://192.168.0.191:8123/api/beatsy/ws');

   ws.onopen = () => {
     console.log('✅ WebSocket connected');
   };

   ws.onerror = (error) => {
     console.error('❌ WebSocket error:', error);
   };

   ws.onmessage = (event) => {
     console.log('📨 Received:', event.data);
   };

   ws.onclose = () => {
     console.log('🔌 WebSocket disconnected');
   };
   ```

3. Check console output

**Expected Result:**
- [ ] Connection established: "✅ WebSocket connected"
- [ ] No authentication required
- [ ] Connection tracked in `hass.data["beatsy"]["websocket_connections"]`
- [ ] HA logs show: "WebSocket connection established from [IP]"

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.6.2: Join Game Command

**Objective:** Verify `beatsy/join_game` WebSocket command works

**Prerequisites:** WebSocket connection established (Test 2.6.1)

**Steps:**
1. In browser console (with WebSocket connected):
   ```javascript
   ws.send(JSON.stringify({
     type: 'beatsy/join_game',
     data: {
       player_name: 'TestPlayer1',
       game_id: 'default'
     }
   }));
   ```

2. Wait for response
3. Check HA logs

**Expected Result:**
- [ ] Server processes command without errors
- [ ] Response received (success or error message)
- [ ] Player added to `hass.data["beatsy"]["players"]`
- [ ] Broadcast event sent to all connected clients: `player_joined`
- [ ] HA log: "Player TestPlayer1 joined game"

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.6.3: Submit Guess Command

**Objective:** Verify `beatsy/submit_guess` WebSocket command works

**Prerequisites:**
- WebSocket connected
- Player joined (Test 2.6.2)
- Round active (may need to start round via admin)

**Steps:**
1. Send submit guess command:
   ```javascript
   ws.send(JSON.stringify({
     type: 'beatsy/submit_guess',
     data: {
       player_name: 'TestPlayer1',
       year_guess: 1985,
       bet_placed: true
     }
   }));
   ```

2. Wait for response

**Expected Result:**
- [ ] Command processed
- [ ] Guess stored in `current_round.guesses`
- [ ] Input validation applied (year in valid range)
- [ ] Broadcast event: `guess_submitted`
- [ ] Response confirms submission

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.6.4: Broadcast Event Function

**Objective:** Verify `broadcast_event()` sends to all connected clients

**Steps:**
1. Open 3 browser windows/tabs
2. Connect WebSocket from each:
   ```javascript
   const ws = new WebSocket('ws://192.168.0.191:8123/api/beatsy/ws');
   ws.onmessage = (event) => {
     console.log('📨 Received broadcast:', JSON.parse(event.data));
   };
   ```

3. From one client, join game:
   ```javascript
   ws.send(JSON.stringify({
     type: 'beatsy/join_game',
     data: { player_name: 'Player1' }
   }));
   ```

4. Check ALL browser consoles

**Expected Result:**
- [ ] All 3 clients receive `player_joined` broadcast
- [ ] Message format:
  ```json
  {
    "type": "beatsy/event",
    "event_type": "player_joined",
    "data": {
      "player_name": "Player1",
      "timestamp": 1234567890
    }
  }
  ```
- [ ] Broadcast delivered within 500ms (performance requirement)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.6.5: Connection Cleanup

**Objective:** Verify WebSocket connections are cleaned up on disconnect

**Steps:**
1. Connect WebSocket from browser console
2. Note connection count in HA logs
3. Close browser tab or manually disconnect:
   ```javascript
   ws.close();
   ```
4. Check HA logs

**Expected Result:**
- [ ] HA log: "WebSocket connection closed for [connection_id]"
- [ ] Connection removed from `websocket_connections`
- [ ] No memory leaks or hanging references
- [ ] Other connected clients unaffected

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.6.6: Multiple Commands Registered

**Objective:** Verify all WebSocket command types are registered

**Steps:**
Test each command type (send placeholder data):

**A. Place Bet:**
```javascript
ws.send(JSON.stringify({
  type: 'beatsy/place_bet',
  data: { player_name: 'Player1', bet: true }
}));
```

**B. Start Game (admin only):**
```javascript
ws.send(JSON.stringify({
  type: 'beatsy/start_game',
  data: { config: { timer_duration: 30 } }
}));
```

**C. Next Song (admin only):**
```javascript
ws.send(JSON.stringify({
  type: 'beatsy/next_song',
  data: {}
}));
```

**Expected Result:**
- [ ] All command types recognized by server
- [ ] Commands return response (success or error)
- [ ] Unknown command types return error: "Unknown command type"
- [ ] Admin commands validate admin permission

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Story 2.7: Configuration Entry Setup (Optional)

### Test 2.7.1: Add Integration via UI

**Objective:** Verify Beatsy appears in HA integrations list

**Steps:**
1. Navigate to: Settings → Devices & Services → Integrations
2. Click "+ Add Integration"
3. Search for "Beatsy"

**Expected Result:**
- [ ] Beatsy appears in search results
- [ ] Icon/logo displayed correctly
- [ ] Clicking opens ConfigFlow

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail [ ] N/A (if Story 2.7 not implemented)

---

### Test 2.7.2: Configuration Flow

**Objective:** Verify ConfigFlow presents form and validates inputs

**Prerequisites:** Story 2.7 implemented

**Steps:**
1. Click "Beatsy" from Add Integration search
2. ConfigFlow displays form with fields:
   - Timer Duration (seconds)
   - Year Range Min
   - Year Range Max

3. **Test validation - Invalid input:**
   - Timer Duration: `5` (below minimum 10)
   - Submit form
   - **Expected:** Error message displayed

4. **Test validation - Valid input:**
   - Timer Duration: `30`
   - Year Range Min: `1950`
   - Year Range Max: `2024`
   - Submit form
   - **Expected:** Configuration created successfully

**Expected Result:**
- [ ] Form displays with correct fields
- [ ] Validation rejects invalid inputs:
  - Timer < 10 or > 120
  - Year range min >= max
- [ ] Valid inputs create ConfigEntry
- [ ] Entry stored in `.storage/core.config_entries`
- [ ] Component loads via `async_setup_entry()`

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail [ ] N/A

---

### Test 2.7.3: Reconfigure Integration

**Objective:** Verify integration options can be updated

**Steps:**
1. Navigate to: Settings → Devices & Services → Integrations
2. Find Beatsy integration
3. Click "Configure" or gear icon (⚙️)
4. Update Timer Duration to `45`
5. Save changes

**Expected Result:**
- [ ] Reconfigure flow opens
- [ ] Current values pre-populated in form
- [ ] Changes saved to ConfigEntry
- [ ] Component reloads with new configuration
- [ ] Game config defaults updated

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail [ ] N/A

---

## Edge Cases and Error Handling

### Test EC-1: Malformed WebSocket Messages

**Objective:** Verify server handles invalid JSON gracefully

**Steps:**
1. Connect WebSocket
2. Send malformed JSON:
   ```javascript
   ws.send('{"type": "beatsy/join_game", invalid json}');
   ```

**Expected Result:**
- [ ] Server doesn't crash
- [ ] Error response sent to client
- [ ] HA log: "Invalid JSON received from WebSocket client"
- [ ] Other connections unaffected

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test EC-2: Missing Required Fields

**Objective:** Verify input validation catches missing fields

**Steps:**
1. Send command with missing `player_name`:
   ```javascript
   ws.send(JSON.stringify({
     type: 'beatsy/join_game',
     data: { game_id: 'default' }  // player_name missing
   }));
   ```

**Expected Result:**
- [ ] Error response: "Missing required field: player_name"
- [ ] Command rejected
- [ ] State unchanged

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test EC-3: Special Characters in Player Name

**Objective:** Verify player name validation

**Steps:**
Test various player names:

1. **Valid:** `"Alice Smith"`
2. **Invalid (HTML):** `"<script>alert('xss')</script>"`
3. **Invalid (too long):** `"A" * 30` (exceeds 20 char limit)
4. **Invalid (special chars):** `"Player@#$%"`

**Expected Result:**
- [ ] Valid names accepted
- [ ] HTML tags rejected/sanitized
- [ ] Names >20 chars rejected
- [ ] Special characters rejected (only alphanumeric + spaces allowed)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test EC-4: Component Reload During Active WebSocket

**Objective:** Verify connections handled during component reload

**Steps:**
1. Connect 3 WebSocket clients
2. Join game from each
3. Reload Beatsy component (via Developer Tools)
4. Check client connections

**Expected Result:**
- [ ] All WebSocket connections closed gracefully
- [ ] Clients receive disconnect event
- [ ] No hanging connections or memory leaks
- [ ] Clients can reconnect after reload completes
- [ ] State reinitialized (players cleared)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test EC-5: Rapid Connection/Disconnection

**Objective:** Stress test connection pool

**Steps:**
1. Write script to rapidly connect/disconnect:
   ```javascript
   for (let i = 0; i < 20; i++) {
     const ws = new WebSocket('ws://192.168.0.191:8123/api/beatsy/ws');
     ws.onopen = () => ws.close();
   }
   ```
2. Execute script
3. Check HA logs and memory usage

**Expected Result:**
- [ ] All connections handled without errors
- [ ] Cleanup executed for each disconnect
- [ ] No resource exhaustion
- [ ] Memory usage stable after test
- [ ] No ERROR logs

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test EC-6: No Spotify Integration Configured

**Objective:** Verify graceful degradation when Spotify integration missing

**Steps:**
1. Disable or remove Spotify integration
2. Restart HA
3. Check Beatsy component loads
4. Call `get_spotify_media_players()`

**Expected Result:**
- [ ] Beatsy component loads successfully
- [ ] WARNING log: "Spotify integration not found"
- [ ] `get_spotify_media_players()` returns empty list
- [ ] Admin UI shows message: "No Spotify players available"
- [ ] Component remains functional for other features

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Performance Validation

### Test P-1: State Accessor Latency

**Objective:** Verify state access completes within 10ms (NFR-P1)

**Steps:**
1. Create performance test script:
   ```python
   import time
   from custom_components.beatsy.game_state import get_game_config

   times = []
   for i in range(100):
       start = time.perf_counter()
       config = get_game_config(hass)
       end = time.perf_counter()
       times.append((end - start) * 1000)  # Convert to ms

   avg_time = sum(times) / len(times)
   max_time = max(times)
   logger.info(f"Avg latency: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
   ```

2. Execute script
3. Check results

**Expected Result:**
- [ ] Average latency < 10ms
- [ ] Max latency < 20ms
- [ ] Consistent performance across 100 calls

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test P-2: WebSocket Broadcast Latency

**Objective:** Verify broadcast delivers to all clients within 500ms (NFR-P2)

**Steps:**
1. Connect 10 WebSocket clients
2. Timestamp when message sent from server
3. Record timestamp when each client receives message
4. Calculate latency distribution

**Expected Result:**
- [ ] All clients receive broadcast
- [ ] 95th percentile latency < 500ms
- [ ] No message loss
- [ ] Latency scales linearly with client count (not exponentially)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test P-3: Component Initialization Time

**Objective:** Verify `async_setup()` completes within 2 seconds (NFR-P3)

**Steps:**
1. Restart Home Assistant
2. Check HA logs for timestamps:
   ```
   [timestamp1] Loading Beatsy integration
   [timestamp2] Beatsy integration loaded
   ```
3. Calculate duration: timestamp2 - timestamp1

**Expected Result:**
- [ ] Initialization completes in < 2 seconds
- [ ] No blocking I/O during setup
- [ ] HA startup not delayed significantly

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test P-4: Memory Footprint

**Objective:** Verify memory usage < 50MB for active game (NFR-P4)

**Steps:**
1. Start fresh HA instance
2. Note baseline memory usage
3. Load Beatsy component
4. Simulate active game:
   - 10 players joined
   - 50 songs loaded in `available_songs`
   - 10 WebSocket connections
5. Check HA process memory:
   ```bash
   ps aux | grep "home-assistant"
   # Or use HA's System Monitor integration
   ```

**Expected Result:**
- [ ] Beatsy memory usage < 50MB
- [ ] No memory leaks over time
- [ ] Memory released after component unload

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Security Validation

### Test S-1: Unauthenticated Access Scope

**Objective:** Verify only player routes are unauthenticated (NFR-S1)

**Steps:**
Test access to all routes WITHOUT authentication:

1. `/api/beatsy/admin` → **Expected: 401**
2. `/api/beatsy/player` → **Expected: 200**
3. `/api/beatsy/ws` → **Expected: Connection allowed**
4. `/api/beatsy/api/media_players` (if exists) → **Expected: 401**

**Expected Result:**
- [ ] Only player route and WebSocket accessible without auth
- [ ] Admin routes require HA token
- [ ] API endpoints require authentication
- [ ] Authenticated scope correctly enforced

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test S-2: Input Validation

**Objective:** Verify all WebSocket data validated (NFR-S2)

**Steps:**
Test validation rules:

**A. Player Name:**
- Max 20 chars: `"A" * 21` → **Rejected**
- HTML tags: `"<b>Player</b>"` → **Sanitized or rejected**
- Only alphanumeric + spaces: `"Player123"` → **Accepted**

**B. Year Guess:**
- Within range: `1985` (range 1950-2024) → **Accepted**
- Below min: `1900` → **Rejected**
- Above max: `2030` → **Rejected**
- Not integer: `"abc"` → **Rejected**

**C. Bet Placed:**
- Boolean true: `true` → **Accepted**
- Boolean false: `false` → **Accepted**
- String: `"true"` → **Rejected**

**Expected Result:**
- [ ] All validation rules enforced
- [ ] Invalid inputs rejected with clear error messages
- [ ] No SQL injection or XSS vulnerabilities
- [ ] Type coercion prevented

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Cross-Browser Testing

### Test CB-1: WebSocket Compatibility

**Objective:** Verify WebSocket works across modern browsers

**Steps:**
Test WebSocket connection from:

1. **Chrome/Chromium** (latest)
2. **Firefox** (latest)
3. **Safari** (iOS/macOS)
4. **Edge** (Chromium-based)

**Expected Result:**
- [ ] WebSocket connects successfully in all browsers
- [ ] Commands processed correctly
- [ ] Broadcasts received
- [ ] No browser-specific errors

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

### Test CB-2: Mobile Device Testing

**Objective:** Verify player route accessible from mobile devices

**Steps:**
1. Connect mobile device to same WiFi as HA
2. Open browser on mobile
3. Navigate to: `http://192.168.0.191:8123/api/beatsy/player`
4. Test WebSocket connection

**Expected Result:**
- [ ] Player route loads on mobile
- [ ] WebSocket connects
- [ ] Touch interactions work (if UI implemented)
- [ ] Responsive layout (if UI implemented)

**Actual Result:** ___________

**Status:** [ ] Pass [ ] Fail

---

## Final Checklist

### Epic 2 Success Criteria

Verify all acceptance criteria met:

- [ ] **AC-1:** Beatsy installs via HACS successfully
- [ ] **AC-2:** Component loads/reloads/unloads without errors
- [ ] **AC-3:** All game state accessor functions tested (>80% coverage)
- [ ] **AC-4:** Spotify media players detected correctly
- [ ] **AC-5:** HTTP routes return 200 OK, auth correctly enforced
- [ ] **AC-6:** WebSocket infrastructure functional, broadcast working
- [ ] **AC-7:** Configuration entry created (if Story 2.7 implemented)

### Non-Functional Requirements

- [ ] **NFR-P1:** State access latency < 10ms
- [ ] **NFR-P2:** WebSocket broadcast latency < 500ms
- [ ] **NFR-P3:** Component initialization < 2 seconds
- [ ] **NFR-P4:** Memory usage < 50MB
- [ ] **NFR-S1:** Unauthenticated access scope correct
- [ ] **NFR-S2:** Input validation enforced
- [ ] **NFR-O1:** Logging standards met (INFO, DEBUG, WARNING, ERROR levels)

### HA Logs Review

Check for any issues:
```bash
tail -n 500 /config/home-assistant.log | grep -i beatsy
```

- [ ] No ERROR messages during normal operation
- [ ] WARNING messages appropriate (e.g., no Spotify players)
- [ ] INFO messages for key events (component loaded, players joined)
- [ ] DEBUG messages provide sufficient detail for troubleshooting

---

## Test Summary

**Total Tests:** 42
**Passed:** ___________
**Failed:** ___________
**Skipped/N/A:** ___________

**Epic 2 Status:** [ ] PASS [ ] FAIL

**Critical Issues Found:**
1. ___________
2. ___________

**Recommendations:**
1. ___________
2. ___________

**Tester Signature:** ___________
**Date:** ___________

---

## Appendix: Useful Commands

### Check HA Logs
```bash
# Real-time logs
tail -f /config/home-assistant.log | grep -i beatsy

# Last 100 lines
tail -n 100 /config/home-assistant.log | grep -i beatsy

# Search for errors
grep -i "error" /config/home-assistant.log | grep -i beatsy
```

### WebSocket Test Script (Browser Console)
```javascript
// Complete WebSocket test
const testBeatsy = () => {
  const ws = new WebSocket('ws://192.168.0.191:8123/api/beatsy/ws');

  ws.onopen = () => {
    console.log('✅ Connected');

    // Join game
    ws.send(JSON.stringify({
      type: 'beatsy/join_game',
      data: { player_name: 'TestPlayer', game_id: 'default' }
    }));
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log('📨 Received:', msg);
  };

  ws.onerror = (error) => {
    console.error('❌ Error:', error);
  };

  ws.onclose = () => {
    console.log('🔌 Disconnected');
  };

  return ws;
};

// Run test
const ws = testBeatsy();
```

### cURL Authentication Test
```bash
# Get token from HA: Profile → Security → Long-Lived Access Tokens

# Test admin route (needs auth)
curl -X GET http://192.168.0.191:8123/api/beatsy/admin \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -i

# Test player route (no auth)
curl -X GET http://192.168.0.191:8123/api/beatsy/player -i
```

---

**End of Epic 2 Manual Testing Guide**
