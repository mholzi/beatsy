# Story 1.3: WebSocket Connection Without Authentication

Status: ready-for-dev

## Story

As a **party guest (player)**,
I want **to establish a WebSocket connection to Beatsy without HA credentials**,
So that **I can receive real-time updates during gameplay**.

## Acceptance Criteria

**AC-1: WebSocket Endpoint Registration**
- **Given** Beatsy component is loaded in HA
- **When** the component initializes
- **Then** WebSocket endpoint is registered at `/api/beatsy/ws`
- **And** endpoint does NOT require HA authentication (`requires_auth = False`)
- **And** HA logs confirm: "Beatsy WebSocket endpoint registered at /api/beatsy/ws"

**AC-2: Client Connection Establishment**
- **Given** unauthenticated HTTP access works (Story 1.2)
- **When** test.html page loads and JavaScript attempts WebSocket connection
- **Then** connection establishes successfully without auth token
- **And** client receives connection confirmation message
- **And** no authentication errors occur

**AC-3: Client-to-Server Messaging**
- **Given** WebSocket connection is established
- **When** client sends a test message to server
- **Then** server receives and logs the message
- **And** server acknowledges receipt
- **And** message format follows protocol: `{"action": "test_ping", "data": {...}}`

**AC-4: Server-to-Client Broadcasting**
- **Given** multiple clients (2+) are connected
- **When** server broadcasts a test message
- **Then** all connected clients receive the message within 500ms
- **And** message includes server timestamp
- **And** message format follows protocol: `{"type": "test_broadcast", "data": {...}, "timestamp": "..."}`

**AC-5: Multiple Concurrent Connections**
- **Given** WebSocket endpoint is active
- **When** 10+ clients connect simultaneously
- **Then** all clients connect successfully
- **And** no connections are dropped
- **And** broadcast messages reach all clients
- **And** HA remains responsive

**AC-6: Connection Lifecycle Management**
- **Given** clients connect and disconnect
- **When** a client disconnects (close browser tab)
- **Then** server detects disconnection
- **And** server removes client from connections registry
- **And** server logs: "Client disconnected: {connection_id}"
- **And** no resource leaks occur

## Tasks / Subtasks

- [x] Task 1: Research HA WebSocket Patterns (AC: #1)
  - [x] Research `homeassistant.components.http.HomeAssistantView` for WebSocket views
  - [x] Investigate `aiohttp.web.WebSocketResponse` for WebSocket handling
  - [x] Research `requires_auth` attribute for public WebSocket access
  - [x] Review HA source code for WebSocket endpoint examples
  - [x] Document pattern for unauthenticated WebSocket in HA 2024.x

- [x] Task 2: Create WebSocket Handler Module (AC: #1, #6)
  - [x] Create `custom_components/beatsy/websocket_handler.py`
  - [x] Import: `aiohttp`, `HomeAssistantView`, `asyncio`, `logging`
  - [x] Implement `BeatsyWebSocketView` class extending `HomeAssistantView`
  - [x] Set `url = "/api/beatsy/ws"` and `requires_auth = False`
  - [x] Implement `async def get(self, request)` method for WebSocket upgrade
  - [x] Initialize `WebSocketResponse` and call `await ws.prepare(request)`
  - [x] Track active connections in instance variable or hass.data
  - [x] Implement connection cleanup on close

- [x] Task 3: Implement Message Receiving Logic (AC: #3)
  - [x] Create message receive loop: `async for msg in ws:`
  - [x] Parse JSON messages from clients: `data = json.loads(msg.data)`
  - [x] Log received messages: `_LOGGER.debug("Received: %s", data)`
  - [x] Validate message format (has "action" and "data" fields)
  - [x] Send acknowledgment back to client
  - [x] Handle parsing errors gracefully

- [x] Task 4: Implement Broadcasting Mechanism (AC: #4)
  - [x] Store all active WebSocket connections in `hass.data[DOMAIN]["ws_connections"]`
  - [x] Create `broadcast_message(hass, msg_type, data)` function
  - [x] Iterate through all connections and send message
  - [x] Add server timestamp to all broadcast messages
  - [x] Handle send errors (disconnected clients)
  - [x] Remove failed connections from registry

- [x] Task 5: Register WebSocket Endpoint in Component Init (AC: #1)
  - [x] Update `custom_components/beatsy/__init__.py`
  - [x] Import: `from .websocket_handler import BeatsyWebSocketView`
  - [x] Register view in `async_setup()`: `hass.http.register_view(BeatsyWebSocketView())`
  - [x] Initialize `hass.data[DOMAIN]["ws_connections"] = {}`
  - [x] Add INFO log: "Beatsy WebSocket endpoint registered at /api/beatsy/ws"
  - [x] Implement cleanup handler in `async_unload_entry()` to close all connections

- [x] Task 6: Update test.html with WebSocket Client (AC: #2, #3, #4)
  - [x] Update `custom_components/beatsy/www/test.html`
  - [x] Add JavaScript WebSocket client code
  - [x] Connect to `ws://<HA_IP>:8123/api/beatsy/ws`
  - [x] Send test ping message on connection: `{"action": "test_ping", "data": {"client_id": "test-1"}}`
  - [x] Listen for broadcast messages
  - [x] Display received messages in page UI (simple list or console log)
  - [x] Add "Send Test Message" button for manual testing
  - [x] Display connection status (Connected/Disconnected)

- [ ] Task 7: Test Basic Connectivity (AC: #2, #3, #4)
  - [ ] Deploy updated component files to HA
  - [ ] Restart Home Assistant
  - [ ] Open test.html in browser (laptop)
  - [ ] Verify WebSocket connection establishes
  - [ ] Send test message from client
  - [ ] Verify server receives message (check HA logs)
  - [ ] Test broadcast: Open test.html in two browser tabs
  - [ ] Trigger broadcast from one client, verify both receive message

- [ ] Task 8: Test Concurrent Connections (AC: #5)
  - [ ] Create simple Python script to simulate 10 WebSocket clients
  - [ ] Script connects 10 clients simultaneously
  - [ ] Each client sends connect message
  - [ ] Verify all clients connect successfully (check HA logs)
  - [ ] Broadcast test message from server
  - [ ] Verify all 10 clients receive message
  - [ ] Monitor HA resource usage (CPU, memory)
  - [ ] Document maximum concurrent connections supported

- [ ] Task 9: Test Disconnection Handling (AC: #6)
  - [ ] Connect client via test.html
  - [ ] Close browser tab
  - [ ] Verify server detects disconnection (HA logs)
  - [ ] Verify connection removed from registry
  - [ ] Reconnect same client
  - [ ] Verify new connection is tracked
  - [ ] Test multiple rapid connect/disconnect cycles
  - [ ] Verify no memory leaks or orphaned connections

- [ ] Task 10: Document WebSocket Protocol & Patterns (AC: All)
  - [ ] Document message formats (client→server, server→client)
  - [ ] Document connection lifecycle (connect, message, disconnect)
  - [ ] Document broadcasting mechanism
  - [ ] Capture code snippets of working patterns
  - [ ] Note any limitations discovered (max connections, latency)
  - [ ] Update POC decision notes with WebSocket findings

## Dev Notes

### Architecture Patterns and Constraints

**WebSocket Pattern (2025 HA Standard):**
- Home Assistant provides `HomeAssistantView` base class for custom HTTP endpoints
- WebSocket upgrade handled via `aiohttp.web.WebSocketResponse`
- Standard pattern: `requires_auth = True` (default)
- **Novel Pattern #1 (POC Validation):** `requires_auth = False` for public WebSocket access
- This is the CRITICAL architectural validation for Epic 1
- If this pattern fails, Epic 1 pivot plan activates (SSE, polling, or PIN-based auth)

**WebSocket Implementation Approach:**
```python
from homeassistant.components.http import HomeAssistantView
from aiohttp import web
import json

class BeatsyWebSocketView(HomeAssistantView):
    url = "/api/beatsy/ws"
    name = "api:beatsy:websocket"
    requires_auth = False  # ⚠️ KEY POC TEST

    async def get(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Track connection
        conn_id = str(uuid.uuid4())
        self.hass.data[DOMAIN]["ws_connections"][conn_id] = ws

        # Message loop
        async for msg in ws:
            data = json.loads(msg.data)
            _LOGGER.debug("Received from %s: %s", conn_id, data)

            # Echo or broadcast logic here
            await self.broadcast(data)

        # Cleanup
        del self.hass.data[DOMAIN]["ws_connections"][conn_id]
        return ws
```

**Broadcasting Mechanism:**
```python
async def broadcast(self, msg_type: str, data: dict):
    """Broadcast message to all connected clients."""
    message = {
        "type": msg_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    msg_json = json.dumps(message)

    # Send to all connections
    connections = self.hass.data[DOMAIN]["ws_connections"]
    for conn_id, ws in list(connections.items()):
        try:
            await ws.send_str(msg_json)
        except Exception as err:
            _LOGGER.warning("Failed to send to %s: %s", conn_id, err)
            del connections[conn_id]  # Remove dead connection
```

**Client-Side JavaScript Pattern:**
```javascript
// In test.html
const ws = new WebSocket('ws://192.168.0.191:8123/api/beatsy/ws');

ws.onopen = () => {
    console.log('Connected to Beatsy WebSocket');
    ws.send(JSON.stringify({
        action: 'test_ping',
        data: { client_id: 'test-1' }
    }));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log('Received:', msg);
    // Display in UI
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};
```

**From Tech Spec (Epic 1):**
- Test endpoint: `ws://<HA_IP>:8123/api/beatsy/ws`
- Authentication: None required (`requires_auth = False`)
- Purpose: Validate unauthenticated WebSocket pattern for real-time player updates
- Success criteria: Bidirectional messaging without HA authentication

**From Architecture Document:**
- ADR-001: Custom WebSocket vs HA WebSocket API → Decision: Custom aiohttp endpoint
- Real-Time Communication pattern: WebSocket broadcast mechanism
- Server-Authoritative State Sync: Server broadcasts state changes, clients react
- Message Protocol: JSON format with "type", "data", "timestamp" fields

**Connection Management:**
- Track connections in `hass.data[DOMAIN]["ws_connections"]` (dict of conn_id → WebSocketResponse)
- Auto-cleanup on disconnect
- No persistent state (ephemeral connections)
- Connection lifecycle: open → message loop → close → cleanup

**Performance Considerations:**
- Target: 10+ concurrent connections (NFR-P4)
- Broadcast latency target: <500ms (NFR-P2)
- No blocking operations in message loop
- Use asyncio for all I/O
- Memory per connection: ~10KB (negligible)

**Security Considerations (POC):**
- ⚠️ **Intentional security relaxation for POC** - not production-ready
- Unauthenticated access acceptable for local network testing
- No input validation in POC (will be added in Epic 10)
- Production implementation (Epic 6) should implement:
  - Message rate limiting
  - Input sanitization
  - Max connection limits per IP
  - Game-based authorization (UUID session tokens)

### Learnings from Previous Story

**From Story 1.2 (Status: review)**

- **Unauthenticated HTTP Access Pattern VALIDATED**:
  - `homeassistant.components.http.HomeAssistantView` with `requires_auth = False` confirmed working in HA 2025
  - Pattern actively used in core integrations (Telegram webhook) - NOT deprecated
  - HTTP view successfully serves content without authentication prompts
  - Same base class and pattern should extend to WebSocket upgrade
  - `hass.http.register_view()` registration method works as expected

- **Files Created - Ready to Extend**:
  - `custom_components/beatsy/www/test.html` - Static HTML with timestamp, device info (READY FOR WEBSOCKET CLIENT)
  - `custom_components/beatsy/http_view.py` - BeatsyTestView class with `requires_auth=False`
  - `custom_components/beatsy/__init__.py` - HTTP view registration with error handling

- **Deployment Issue Resolved**:
  - **Issue Found**: Manifest declared `spotify` dependency but Spotify not configured
  - **Fix Applied**: Removed spotify from manifest dependencies (commit 418c90bc)
  - **Resolution**: Component loads successfully after configuration reload
  - **Action for Story 1.3**: No Spotify dependency blocking WebSocket implementation
  - **Future**: Spotify will be re-added in Story 1.4 when actually needed

- **2025 Standards Applied & Validated**:
  - Manifest includes `version`, `iot_class: "local_push"` fields (2025 requirement)
  - Modern type hints used (`dict[str, Any]` vs `Dict[str, Any]`)
  - Async/await pattern established and working
  - Module-level `_LOGGER = logging.getLogger(__name__)` logging pattern

- **Component Foundation Confirmed Stable**:
  - Component loads in HA without errors (validated in Story 1.1)
  - `hass.data[DOMAIN]` initialized as empty dict, ready for ws_connections tracking
  - HTTP dependency already in manifest (available for WebSocket)
  - Error handling patterns established (try/except with graceful degradation)

- **Key Patterns to Reuse in This Story**:
  - **Base Class**: `from homeassistant.components.http import HomeAssistantView`
  - **Auth Bypass**: Set `requires_auth = False` class attribute
  - **Registration**: `hass.http.register_view(ViewClass(hass))` in `async_setup()`
  - **Logging**: Use established `_LOGGER` variable, INFO for registration, DEBUG for operations
  - **Error Handling**: Comprehensive try/except blocks with user-friendly error messages
  - **Type Hints**: Modern Python 3.11+ syntax throughout

- **Files to Modify/Create in This Story**:
  - MODIFY: `__init__.py` - Add WebSocket view registration after HTTP view
  - MODIFY: `test.html` - Add JavaScript WebSocket client code
  - CREATE: `websocket_handler.py` - New module for WebSocket endpoint logic

- **Architectural Validation**:
  - HTTP unauthenticated access ✅ CONFIRMED (Story 1.2 complete)
  - WebSocket unauthenticated access ⏳ TO BE VALIDATED (THIS STORY)
  - Pattern consistency: Same `requires_auth = False` approach for both HTTP and WebSocket
  - Risk: If WebSocket requires different auth handling, pivot plan documented in Story 1.7

- **Testing Approach Established**:
  - Manual testing on actual devices (iPhone, laptop, tablet)
  - Zero authentication prompts = success criterion
  - HA logs used for validation (component loaded, view registered, no errors)
  - Multi-device concurrent testing pattern validated

- **No Blocking Technical Debt**:
  - All Story 1.1 and 1.2 foundations are stable
  - No unresolved errors or warnings in HA logs
  - Story 2.7 (config flow) intentionally deferred for post-POC (not blocking)
  - Spotify dependency issue resolved (removed from manifest)

[Source: stories/1-2-serve-static-html-without-authentication.md#Dev-Agent-Record]

### Project Structure Notes

**Expected File Paths:**
```
/config/custom_components/beatsy/
├── __init__.py          # MODIFY: Add WebSocket view registration
├── manifest.json        # EXISTS (includes "http" dependency)
├── const.py            # EXISTS
├── websocket_handler.py # NEW FILE: WebSocket endpoint logic
└── www/                # EXISTS
    └── test.html       # MODIFY: Add WebSocket client JavaScript
```

**New File: websocket_handler.py**
- Purpose: WebSocket endpoint implementation
- Pattern: `HomeAssistantView` subclass with `requires_auth = False`
- Responsibilities:
  - WebSocket upgrade handling
  - Message receive loop
  - Connection tracking
  - Broadcasting mechanism
  - Cleanup on disconnect

**Modified File: __init__.py**
- Add import: `from .websocket_handler import BeatsyWebSocketView`
- Register view in `async_setup()`: `hass.http.register_view(BeatsyWebSocketView(hass))`
- Initialize: `hass.data[DOMAIN]["ws_connections"] = {}`
- Cleanup: Close all connections in `async_unload_entry()`

**Modified File: test.html**
- Add JavaScript section for WebSocket client
- Display connection status
- Show received messages (console or UI list)
- Add "Send Test" button for manual testing

**File Alignment with Architecture:**
- websocket_handler.py → Maps to "Real-Time Communication" in architecture.md
- Message protocol → Follows architecture.md Pattern #5 (WebSocket Message Protocol)
- Broadcasting → Server-Authoritative State Sync pattern (architecture.md Pattern #2)

**No Conflicts:**
- WebSocket endpoint is new, no existing endpoints to conflict with
- HTTP view pattern already validated in Story 1.2
- test.html will be extended (not replaced)

### Testing Standards Summary

**Test Approach:**
- Manual integration test: Connect from browser, send/receive messages
- Load test: Python script to simulate 10 concurrent connections
- Verification points:
  1. WebSocket connection establishes without auth
  2. Client can send message to server
  3. Server can broadcast message to all clients
  4. Multiple clients (10+) can connect simultaneously
  5. Disconnection handled gracefully (no leaks)
  6. HA logs show WebSocket activity
  7. No HA crashes or performance degradation

**Success Criteria:**
- Zero authentication prompts or errors
- WebSocket connection establishes < 1 second
- Broadcast latency < 500ms (NFR-P2 target)
- 10 concurrent connections stable for 5 minutes
- Clean disconnection with resource cleanup

**Edge Cases to Test:**
- Rapid connect/disconnect cycles (connection churn)
- Client disconnect without clean close (network failure simulation)
- Send message before connection fully established
- Very large message (test message size limits)
- HA restart while clients connected

**Manual Test Steps:**
1. Deploy updated component to HA
2. Restart HA
3. Open test.html in browser (check console)
4. Verify "Connected" status displayed
5. Click "Send Test" button
6. Check HA logs for received message
7. Open test.html in second browser tab
8. Send message from one tab, verify received in other
9. Close one tab, verify server logs disconnection
10. Run Python load test script (10 clients)
11. Verify all clients receive broadcast

**Load Test Script (Pseudocode):**
```python
# tests/poc_websocket_load_test.py
import asyncio
import aiohttp

async def test_client(client_id):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://192.168.0.191:8123/api/beatsy/ws') as ws:
            await ws.send_json({"action": "connect", "data": {"id": client_id}})
            async for msg in ws:
                print(f"Client {client_id} received: {msg.data}")

async def main():
    tasks = [test_client(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-1.md#Story-1.3]
- [Source: docs/epics.md#Story-1.3-WebSocket-Connection-Without-Authentication]
- [Source: docs/architecture.md#Pattern-1-Unauthenticated-WebSocket]
- [Source: docs/architecture.md#Real-Time-Communication]

**Key Technical Decisions:**
- Using `HomeAssistantView` with `requires_auth = False` for public access
- Custom WebSocket endpoint (not HA's WebSocket API) for full control
- JSON message protocol with "action" (client→server) and "type" (server→client)
- In-memory connection tracking in `hass.data[DOMAIN]`
- No persistent state (connections are ephemeral)

**Dependencies:**
- Story 1.1: Component structure and registration (COMPLETE)
- Story 1.2: HTTP unauthenticated access pattern (COMPLETE)
- Home Assistant Core 2024.1+ (validated in Story 1.1)
- Python 3.11+ (validated in Story 1.1)
- aiohttp library (bundled with HA)

**Home Assistant API References:**
- `homeassistant.components.http.HomeAssistantView` - Base class for custom HTTP views
- `aiohttp.web.WebSocketResponse` - WebSocket response handler
- `hass.http.register_view()` - View registration method
- `hass.data[DOMAIN]` - In-memory data storage

**Novel Pattern Validation:**
- Pattern #1: Unauthenticated WebSocket access (this story is THE validation)
- Goal: Prove zero-friction real-time communication is technically feasible
- Risk Mitigation: If WebSocket auth required, pivot to SSE/polling (documented in Story 1.7)
- CRITICAL DECISION POINT: This story determines Epic 6 architecture

**WebSocket Message Protocol:**
```javascript
// Client → Server (action-based)
{
    "action": "test_ping" | "connect" | "disconnect",
    "data": {...}
}

// Server → Client (type-based)
{
    "type": "test_broadcast" | "connected" | "error",
    "data": {...},
    "timestamp": "2025-11-10T12:34:56.789Z"
}
```

**Pivot Plan (if WebSocket auth required):**
- Alternative A: Server-Sent Events (SSE) for server→client, AJAX for client→server
- Alternative B: Long-polling with timeout
- Alternative C: Simple 4-digit PIN per game session
- Effort: 1-2 weeks to implement alternative
- Decision documented in Story 1.7 (POC Decision Document)

## Change Log

**Story Created:** 2025-11-10
**Author:** Bob (Scrum Master)
**Epic:** Epic 1 - Foundation & Multi-Risk POC
**Story ID:** 1.3
**Status:** drafted (was backlog)

### Changes Made

**Initial Draft:**
- Created story from Epic 1, Story 1.3 requirements
- Extracted acceptance criteria from tech spec and epics document
- Aligned with architecture patterns (Custom WebSocket, Public Access)
- Incorporated learnings from Story 1.2 (HTTP view pattern, www/ directory)
- Incorporated learnings from Story 1.1 (component foundation, logging patterns)

**Requirements Source:**
- Tech Spec: Validate unauthenticated WebSocket connectivity for real-time updates
- Epics: Real-time communication without HA credentials, 10+ concurrent connections
- Architecture: ADR-001 Custom WebSocket endpoint, Pattern #1 Unauthenticated access

**Technical Approach:**
- `HomeAssistantView` subclass with `requires_auth = False`
- `aiohttp.web.WebSocketResponse` for WebSocket upgrade
- In-memory connection tracking in `hass.data[DOMAIN]["ws_connections"]`
- Broadcasting mechanism: Iterate all connections, send JSON message
- JSON message protocol: "action" for client→server, "type" for server→client

**Dependencies:**
- Story 1.1 complete: Component loads, `hass.data[DOMAIN]` initialized
- Story 1.2 complete: HTTP unauthenticated pattern validated
- No blocking issues from previous stories
- Foundation stable for adding WebSocket functionality

**Learnings Applied from Story 1.2:**
- Use established `homeassistant.components.http.HomeAssistantView` pattern
- Follow `requires_auth = False` pattern (validated in Story 1.2)
- Extend existing test.html file (don't replace)
- Use module-level `_LOGGER` logging pattern
- Maintain async/await consistency

**Learnings Applied from Story 1.1:**
- Use `hass.data[DOMAIN]` for connection tracking
- Register view in `async_setup()` function
- Implement cleanup in `async_unload_entry()`
- Follow modern Python 3.11+ type hints
- Use HA's bundled aiohttp library

**Critical POC Validation:**
- This story is THE validation for Novel Pattern #1 (Unauthenticated WebSocket)
- Success = Epic 6 proceeds with WebSocket architecture
- Failure = Epic 1 pivot plan activates (SSE, polling, or PIN auth)
- Decision documented in Story 1.7 (POC Decision Document)

**Future Story Dependencies:**
- Story 1.4: Spotify API test (can run in parallel with this story)
- Story 1.6: WebSocket load test (depends on this story completing)
- Epic 6: Real-time event infrastructure (architecture depends on this story's outcome)

**Novel Patterns Introduced:**
- Public WebSocket endpoint in Home Assistant ecosystem
- Game-based authorization (not user-based)
- In-memory connection registry with auto-cleanup
- Server-authoritative broadcasting pattern

## Dev Agent Record

### Context Reference

- docs/stories/1-3-websocket-connection-without-authentication.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Researched HA WebSocket patterns - confirmed `HomeAssistantView` with `requires_auth = False` extends to WebSocket
2. Created `websocket_handler.py` with `BeatsyWebSocketView` class implementing WebSocket upgrade
3. Implemented message receiving loop with JSON parsing and validation
4. Implemented `broadcast_message()` function with timestamp and error handling
5. Registered WebSocket endpoint in `__init__.py` with connection tracking in `hass.data[DOMAIN]["ws_connections"]`
6. Updated `test.html` with full WebSocket client UI (auto-connect, ping, broadcast, message log)
7. Created `tests/poc_websocket_load_test.py` for AC-5 concurrent connection testing
8. Ready for deployment and testing

**Implementation Approach:**
- Followed Story 1.2 patterns: `HomeAssistantView`, `requires_auth = False`, module-level `_LOGGER`
- WebSocket upgrade via `aiohttp.web.WebSocketResponse`
- Connection lifecycle: connect → send confirmation → message loop → cleanup on close
- Broadcasting: iterate all connections, send JSON, remove failed connections
- Error handling: comprehensive try/except blocks, graceful degradation
- Message protocol: "action" (client→server), "type" (server→client), timestamps on all server messages

**READY FOR TESTING - Requires HA restart to load new component**

### Completion Notes List

**Implementation Complete (Tasks 1-6):**
- ✅ WebSocket handler module created with full lifecycle management
- ✅ Message receiving and validation implemented
- ✅ Broadcasting mechanism with automatic cleanup
- ✅ WebSocket endpoint registered in component init
- ✅ test.html enhanced with WebSocket client UI
- ✅ Load test script created for concurrent connections
- ⏸️ **Awaiting deployment**: Need HA restart to test AC-1 through AC-6

**Testing Strategy:**
1. Restart HA and verify WebSocket endpoint registration in logs
2. Open test.html in browser, verify auto-connection
3. Test ping/pong messaging
4. Open second tab, test broadcast functionality
5. Run load test script: `python tests/poc_websocket_load_test.py <HA_IP>:8123 10 60`
6. Test disconnection handling (close tab, check logs)

### File List

- home-assistant-config/custom_components/beatsy/__init__.py (modified)
- home-assistant-config/custom_components/beatsy/websocket_handler.py (new)
- home-assistant-config/custom_components/beatsy/www/test.html (modified)
- tests/poc_websocket_load_test.py (new)
