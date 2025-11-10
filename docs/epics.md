# Beatsy - Epic Breakdown

**Author:** Markus
**Date:** 2025-11-10
**Project Level:** Low-Medium Complexity
**Target Scale:** Home Assistant Custom Component (HACS)

---

## Overview

This document provides the complete epic and story breakdown for Beatsy, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

### Epic Summary

**10 Epics - POC-Driven Development Strategy (Risk-Optimized Sequence)**

1. **Foundation & Multi-Risk POC** - Validate ALL critical architectural assumptions (auth, WebSocket, Spotify, data registry, scale)
2. **HACS Integration & Core Infrastructure** - Production-ready HA component foundation
3. **Admin Interface & Game Configuration** - Web UI for game setup and control (mobile-first design)
4. **Player Registration & Lobby** - Name-based joining and waiting room (mobile-first design)
5. **Game Mechanics - Song Selection & Scoring** - Core game logic, algorithms, and leaderboard API
6. **Real-Time Event Infrastructure** - Generic pub/sub event bus for live updates
7. **Music Playback Integration** - Spotify playlist fetch, metadata extraction, playback control, conflict handling
8. **Active Round - Player UI** - Guess interface with betting and timer (mobile-first, builds on Epics 5-7)
9. **Results & Leaderboards** - Round results and overall standings display (mobile-first, builds on Epics 5-6)
10. **Production Readiness** - Testing (E2E, load, cross-browser), error handling, documentation

**Sequencing Philosophy:** POC first to validate architectural feasibility, then foundation, then admin controls, then player flows, **THEN real-time infrastructure and music integration BEFORE building UIs that depend on them**, then polish.

### Risk Mitigations Embedded in Epic Structure

**Critical Risks Addressed:**

- **POC Failure Risk:** Epic 1 validates unauthenticated access AND WebSocket viability before investing in remaining epics
- **WebSocket Authentication:** Research public WebSocket channels; fallback to SSE/polling if needed
- **Epic Dependencies:** Real-time (Epic 6) and Music (Epic 7) moved before dependent UIs (Epics 8-9)
- **Spotify Conflicts:** Epic 7 includes state saving/restoration and conflict detection
- **Data Registry Performance:** Epic 2 uses in-memory state; registry only for config persistence
- **Timer Desync:** Epic 5 uses client-side calculation from start timestamp (not server ticks)
- **Admin Abandonment:** Epic 3 stores admin secret key for reconnection
- **Missing Metadata:** Epic 5 filters songs without year data during playlist load
- **HACS Compliance:** Research HACS requirements before Epic 2 implementation
- **Betting Confusion:** Epic 8 includes clear tooltips and example calculations

### Epic Dependency Map

**Critical Path to MVP:** Epic 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 (sequential completion required)

**Parallel Work Opportunities:**
- After Epic 2: Epic 3 (Admin) ‖ Epic 4 (Player) can develop in parallel
- After Epic 5: Epic 6 (Real-Time) ‖ Epic 7 (Music) can develop in parallel
- After Epics 6 & 7: Epic 8 (Active Round) ‖ Epic 9 (Results) can develop with shared mocks

**Key Dependencies:**

| Epic | Depends On | Provides To | Critical Outputs |
|------|------------|-------------|------------------|
| Epic 1 | None (POC) | ALL epics | Unauthenticated access pattern, WebSocket strategy |
| Epic 2 | Epic 1 | Epics 3-10 | `hass.data` API, HTTP/WebSocket infrastructure, Spotify detection |
| Epic 3 | Epic 2 | Epics 5, 8 | `game_config` state, admin controls, start/stop game |
| Epic 4 | Epic 2 | Epics 5, 8, 9 | `players` state, player identity system, lobby |
| Epic 5 | Epics 3, 4 | Epics 8, 9 | Scoring algorithm, timer logic, `current_round` state |
| Epic 6 | Epic 2 | Epics 8, 9 | WebSocket event bus, live update infrastructure |
| Epic 7 | Epic 2 | Epics 8, 9 | Song metadata, playback control, Spotify integration |
| Epic 8 | Epics 5, 6, 7 | Epic 9 | Player guess submission, bet placement, active round UI |
| Epic 9 | Epics 4, 5, 6 | Epic 10 | Results display, leaderboard rendering |
| Epic 10 | Epics 3, 4, 8, 9 | Production | Responsive design, error handling, documentation |

**State Ownership:**
- `game_config`: Epic 2 creates, Epic 3 writes, Epics 5-7 read
- `players`: Epic 4 creates/manages, Epic 5 updates scores, Epic 9 displays
- `current_round`: Epic 5 creates, Epic 7 adds song metadata, Epic 8 collects guesses
- `websocket_connections`: Epic 6 manages, Epics 8-9 send/receive events

**Integration Contract Requirements:**
- Epic 6 must provide generic event bus infrastructure (pub/sub pattern); each epic defines own event types
- Epic 5 must define `get_leaderboard()` API (input: players state → output: sorted top 5 + current player)
- Epic 7 must define song metadata structure before Epic 8 begins
- Each UI epic (3, 4, 8, 9) must implement mobile-first responsive design (320px-428px) during development
- Each epic includes unit tests + mocked integration tests
- Epic 10 provides full end-to-end integration testing, load testing (20 players), cross-browser validation

### Critical Perspective Insights

**Epic 1 Expanded Scope (Multi-Risk POC):**
- ✅ Unauthenticated HTTP access validation
- ✅ WebSocket without auth token validation
- ➕ **Spotify API basic test:** Fetch playlist + play one song
- ➕ **Load test:** 10 simulated WebSocket connections
- ➕ **Data registry stress test:** Rapid write/read cycles with game state
- 🚨 **Required Deliverable:** Pass/Fail decision document with pivot plan if POC fails

**POC Failure Pivot Alternatives (if Epic 1 fails):**
1. **Partial Pass (HTTP works, WebSocket needs auth):** Pivot to Server-Sent Events (SSE) or polling → Revise Epic 6
2. **Full Fail (no unauthenticated access):** Implement alternative auth strategy:
   - Alternative A: Simple 4-digit PIN code system (stored in `game_config`)
   - Alternative B: QR code with embedded temporary token (expires after game)
   - Alternative C: Admin manually approves each player join request
   - Alternative D: Use HA's `person` entities (breaks "zero friction" promise)

**Epic Complexity Warnings:**
- **Epic 3 (Admin):** Heavyweight - form validation, Spotify dropdown population, config persistence, admin-as-player flow → May need 2-3 weeks
- **Epic 7 (Music):** Deceptively complex - pagination, metadata extraction, year validation, conflict handling, state restoration → Expect 2-3 weeks
- **Epic 8 (Active Round):** High integration complexity - depends on Epics 5, 6, 7 → Requires robust mocking strategy

**State Ownership Clarification:**
- **Leaderboard Logic:** Epic 5 owns calculation completely; provides `get_leaderboard()` API
- **Real-Time Transport:** Epic 6 provides event bus only (no business logic); each epic defines own event types
- **Display Responsibility:** Epic 9 calls Epic 5's leaderboard API and renders (no calculation logic in Epic 9)

**Mobile-First Mandate:**
- Epic 10 does NOT handle "mobile optimization as afterthought"
- Each UI epic (3, 4, 8, 9) must design mobile-first from day 1
- Test on actual phones during development (iOS Safari + Chrome Android)
- Touch targets minimum 44x44px (Apple HIG standard)
- Validate 320px-428px width range before marking epic complete

---

## Epic 1: Foundation & Multi-Risk POC

**Goal:** Validate ALL critical architectural assumptions before investing in remaining epics.

**Value:** De-risk the entire project by confirming feasibility of zero-friction player access, real-time updates, Spotify integration, and system scalability.

### Story 1.1: Minimal Component Structure & Registration

As a **Home Assistant administrator**,
I want **a minimal Beatsy custom component that loads successfully in HA**,
So that **I can begin testing core architectural assumptions**.

**Acceptance Criteria:**

**Given** a Home Assistant instance running Core 2024.1+
**When** the Beatsy component folder is placed in `custom_components/beatsy/`
**Then** HA recognizes the component at startup without errors

**And** the component appears in HA logs as "Beatsy custom component loaded"

**And** the component includes:
- `__init__.py` (minimal setup function)
- `manifest.json` (valid HACS-style metadata)
- `const.py` (domain constant: "beatsy")

**Prerequisites:** None (first story)

**Technical Notes:**
- Minimal viable component structure only
- No configuration, no entities, no services yet
- Focus: Does HA accept our component structure?
- Validate manifest.json schema compliance
- Test: Restart HA, check logs, confirm no errors

---

### Story 1.2: Serve Static HTML Without Authentication

As a **party guest (player)**,
I want **to access a test HTML page without logging into Home Assistant**,
So that **I can join games with zero friction**.

**Acceptance Criteria:**

**Given** Beatsy component is loaded in HA
**When** I navigate to `http://<HA_IP>:8123/api/beatsy/test.html` from any device on local network
**Then** the page loads successfully without authentication prompt

**And** the page displays "Beatsy POC - Unauthenticated Access Test"

**And** accessing the page does NOT require HA login credentials

**And** the page is accessible from multiple devices simultaneously

**Prerequisites:** Story 1.1 (component structure exists)

**Technical Notes:**
- Research `homeassistant.components.http.HomeAssistantView` for public routes
- Investigate `@require_auth(False)` decorator or `CORS_ALLOWED_ORIGINS`
- Alternative: Use `hass.http.register_static_path()` with public flag
- Create `/www/` folder in component with `test.html`
- CRITICAL TEST: Verify access from phone without HA app/login
- **Deliverable:** Document exact pattern for unauthenticated HTTP access

---

### Story 1.3: WebSocket Connection Without Authentication

As a **party guest (player)**,
I want **to establish a WebSocket connection to Beatsy without HA credentials**,
So that **I can receive real-time updates during gameplay**.

**Acceptance Criteria:**

**Given** unauthenticated HTTP access works (Story 1.2)
**When** I open the test page and JavaScript attempts WebSocket connection
**Then** the WebSocket connects successfully without auth token

**And** the client can send a test message to the server

**And** the server can broadcast a test message to all connected clients

**And** multiple clients (10+) can connect simultaneously

**Prerequisites:** Story 1.2 (HTTP access working)

**Technical Notes:**
- Research `hass.components.websocket_api.async_register_command` for public channels
- Investigate if HA supports unauthenticated WebSocket subscriptions
- Test alternatives if auth required:
  - Server-Sent Events (SSE) for one-way updates
  - Long-polling with AJAX as fallback
- Create test WebSocket handler in component
- Client-side JavaScript to test connection
- **CRITICAL DECISION POINT:** If WebSocket requires auth, document pivot strategy to SSE/polling
- **Deliverable:** Working WebSocket connection OR fallback strategy documented

---

### Story 1.4: Spotify API Basic Integration Test

As a **Beatsy developer**,
I want **to verify I can fetch a playlist and play one song via HA's Spotify integration**,
So that **I validate Spotify API viability before building game mechanics**.

**Acceptance Criteria:**

**Given** Home Assistant has an active Spotify integration configured
**When** Beatsy calls `hass.services.async_call("media_player", "play_media", {...})`
**Then** a Spotify track plays on the configured media player

**And** Beatsy can fetch playlist track list from Spotify URI

**And** Beatsy can extract track metadata (title, artist, release year, album cover URL)

**And** playback starts within 2 seconds of command

**Prerequisites:** Story 1.1 (component loaded)

**Technical Notes:**
- Use HA's existing `spotify` integration (don't create new auth)
- Test API: `spotify.get_playlist(playlist_id)` or equivalent
- Verify metadata structure includes `album.release_date` or `track.release_date`
- Test with real Spotify playlist (use test playlist with ~10 songs)
- Handle case: Track missing release year (document filtering strategy)
- **Deliverable:** Document Spotify metadata structure and API limits

---

### Story 1.5: Data Registry Write/Read Stress Test

As a **Beatsy developer**,
I want **to validate that HA's data registry can handle rapid game state updates**,
So that **I avoid performance issues during live gameplay**.

**Acceptance Criteria:**

**Given** Beatsy component has access to `hass.data["beatsy"]`
**When** the test writes game state 100 times in 30 seconds (simulating 10 players, 3 rounds)
**Then** all writes complete without errors

**And** subsequent reads return accurate data

**And** Home Assistant remains responsive (no UI lag)

**And** HA logs show no performance warnings

**Prerequisites:** Story 1.1 (component loaded)

**Technical Notes:**
- Test pattern: Rapid writes to `hass.data["beatsy"]["game_state"]`
- Simulate realistic game state structure:
  ```python
  {
    "players": [{"name": "Player1", "score": 10}, ...],
    "current_round": {"song_uri": "...", "guesses": [...]},
    "played_songs": ["uri1", "uri2", ...]
  }
  ```
- Do NOT use HA's persistent storage (`hass.helpers.storage`) for this test (too slow)
- Confirm: In-memory `hass.data` is appropriate for active game state
- **Deliverable:** Confirmation that in-memory storage is sufficient; document persistence strategy for config only

---

### Story 1.6: Load Test - 10 Concurrent WebSocket Connections

As a **Beatsy developer**,
I want **to simulate 10 concurrent players connected via WebSocket**,
So that **I validate the system can handle typical party sizes**.

**Acceptance Criteria:**

**Given** WebSocket connectivity works (Story 1.3)
**When** 10 simulated clients connect simultaneously and send messages
**Then** all clients receive broadcasted messages within 500ms

**And** no connections drop during 5-minute test

**And** message delivery is reliable (no lost messages)

**And** HA resource usage remains acceptable (<50% CPU, <500MB RAM increase)

**Prerequisites:** Story 1.3 (WebSocket working)

**Technical Notes:**
- Use Python script or Node.js tool to simulate 10 WebSocket clients
- Test scenario: All clients send "bet_placed" event simultaneously
- Measure: Latency from send to broadcast receive
- Monitor: HA system resources during test
- **Stress test:** Try 20 connections to find breaking point
- **Deliverable:** Document max concurrent connections supported; note performance characteristics

---

### Story 1.7: POC Decision Document & Pivot Plan

As a **Product Manager**,
I want **a clear Pass/Fail assessment of all POC tests**,
So that **I can decide whether to proceed with the current architecture or pivot**.

**Acceptance Criteria:**

**Given** all Stories 1.1-1.6 are complete
**When** I review the POC Decision Document
**Then** the document clearly states PASS or FAIL for each test:
- ✅/❌ Unauthenticated HTTP access
- ✅/❌ Unauthenticated WebSocket
- ✅/❌ Spotify API integration
- ✅/❌ Data registry performance
- ✅/❌ WebSocket scale (10 connections)

**And** the document includes:
- **Overall Verdict:** Proceed / Pivot / Stop
- **Identified Risks:** Any limitations discovered
- **Pivot Plan (if needed):** Alternative architectures with implementation effort estimates
- **Next Steps:** Recommendations for Epic 2

**Prerequisites:** Stories 1.1-1.6 (all tests complete)

**Technical Notes:**
- Document exact HA configuration required for unauthenticated access
- Include code snippets for key patterns (HTTP view, WebSocket handler)
- If WebSocket auth required: Document SSE/polling pivot strategy
- If unauthenticated access fails: Document PIN/QR code alternatives
- **Deliverable:** Markdown document saved as `docs/poc-decision.md`

---

## Epic 2: HACS Integration & Core Infrastructure

**Goal:** Build production-ready Home Assistant integration foundation that other epics will build upon.

**Value:** Provides the component lifecycle, data management, and integration APIs that all subsequent features depend on.

### Story 2.1: HACS-Compliant Manifest & Repository Structure

As a **Home Assistant user**,
I want **Beatsy to be installable via HACS**,
So that **I can install and update it like any other custom component**.

**Acceptance Criteria:**

**Given** HACS submission requirements documented
**When** I add Beatsy repository to HACS custom repositories
**Then** HACS recognizes it as valid custom integration

**And** `hacs.json` includes all required fields (name, domains, country, render_readme)

**And** `manifest.json` includes all required HA fields (domain, name, version, dependencies, codeowners, requirements)

**And** repository includes README.md with installation instructions

**And** repository follows HACS directory structure conventions

**Prerequisites:** Epic 1 complete (POC validated)

**Technical Notes:**
- Research HACS requirements: https://hacs.xyz/docs/publish/start
- Required files:
  - `/custom_components/beatsy/manifest.json`
  - `/hacs.json` (at repo root)
  - `/README.md`
  - `/info.md` (HACS description)
- Dependencies in manifest: `["http", "spotify"]`
- Version: Use semantic versioning (0.1.0 for MVP)
- Test: Add to HACS, verify it appears in integrations list

---

### Story 2.2: Component Lifecycle Management

As a **Beatsy component**,
I want **proper lifecycle hooks (setup, reload, unload)**,
So that **Home Assistant can manage me correctly**.

**Acceptance Criteria:**

**Given** Beatsy is installed via HACS
**When** Home Assistant starts
**Then** `async_setup()` function executes successfully

**And** component registers in HA's integration registry

**And** component logs "Beatsy integration loaded" at INFO level

**When** HA reloads integrations
**Then** `async_reload()` function cleans up and reinitializes

**When** HA shuts down
**Then** `async_unload()` function cleans up resources gracefully

**Prerequisites:** Story 2.1 (HACS structure complete)

**Technical Notes:**
- Implement in `__init__.py`:
  ```python
  async def async_setup(hass, config):
      # Initialize component

  async def async_unload_entry(hass, entry):
      # Cleanup on unload
  ```
- Register cleanup handlers for WebSocket connections, timers
- Ensure no resource leaks (open connections, threads, etc.)
- Test: HA restart, reload service, shutdown

---

### Story 2.3: In-Memory Game State Management

As a **Beatsy game manager**,
I want **a structured in-memory state system using `hass.data`**,
So that **game state is fast and accessible across all modules**.

**Acceptance Criteria:**

**Given** Beatsy component is loaded
**When** game state is initialized
**Then** `hass.data[DOMAIN]` contains structured game state object

**And** state structure includes:
```python
{
  "game_config": {},    # Admin settings
  "players": [],        # Player list with scores
  "current_round": {},  # Active round state
  "played_songs": [],   # Track history
  "websocket_connections": {}  # Active clients
}
```

**And** state access functions provided:
- `get_game_config(hass)` → dict
- `get_players(hass)` → list
- `update_player_score(hass, player_name, points)` → void
- `get_current_round(hass)` → dict

**Prerequisites:** Story 2.2 (lifecycle management)

**Technical Notes:**
- Create `game_state.py` module with state management functions
- Do NOT use `hass.helpers.storage` for active game (too slow)
- In-memory only; state resets on HA restart (acceptable for games)
- Consider: Game config persistence (admin settings survive restart)
- Thread-safe access if needed (HA is async, so likely not needed)

---

### Story 2.4: Spotify Media Player Detection

As an **admin**,
I want **Beatsy to detect all Spotify-capable media players in my HA instance**,
So that **I can select which speaker to use for the game**.

**Acceptance Criteria:**

**Given** Home Assistant has Spotify integration configured
**When** Beatsy calls `get_spotify_media_players(hass)`
**Then** function returns list of all `media_player.*` entities where `source_list` includes "Spotify"

**And** each media player includes:
- `entity_id` (e.g., "media_player.living_room")
- `friendly_name` (e.g., "Living Room Speaker")
- `state` (e.g., "idle", "playing")

**And** function handles case where no Spotify players exist (returns empty list)

**And** function handles case where Spotify integration not configured (returns empty list with warning log)

**Prerequisites:** Story 2.3 (state management)

**Technical Notes:**
- Query: `hass.states.async_all("media_player")`
- Filter: Check entity attributes for Spotify capability
- Alternative check: `entity_id.startswith("media_player.spotify_")`
- Create `spotify_helper.py` module
- Test with: Sonos, Chromecast, native Spotify speakers
- Return format: List of dicts with entity_id and friendly_name

---

### Story 2.5: HTTP Route Registration

As a **Beatsy component**,
I want **to register HTTP routes for serving web interfaces**,
So that **admin and players can access the game UIs**.

**Acceptance Criteria:**

**Given** Beatsy component is setting up
**When** HTTP routes are registered
**Then** the following routes are available:
- `/api/beatsy/admin` → Admin interface (authenticated)
- `/api/beatsy/player` → Player interface (unauthenticated, based on POC results)
- `/api/beatsy/api/*` → REST API endpoints (for future use)

**And** static files are served from `/www/` directory in component

**And** routes handle CORS appropriately for local network access

**And** authenticated routes require HA access token

**And** unauthenticated routes are accessible per Epic 1 POC strategy

**Prerequisites:** Story 2.2 (lifecycle management), Epic 1 (POC pattern documented)

**Technical Notes:**
- Use `hass.http.register_view()` for API endpoints
- Use `hass.http.register_static_path()` for HTML/CSS/JS files
- Create `http_view.py` module with view classes
- Reference Epic 1 POC Decision Document for unauthenticated access pattern
- Test: Access routes from browser, verify auth behavior

---

### Story 2.6: WebSocket Command Registration

As a **Beatsy component**,
I want **to register WebSocket commands for real-time communication**,
So that **clients can send events and receive broadcasts**.

**Acceptance Criteria:**

**Given** Beatsy component is setting up
**When** WebSocket commands are registered
**Then** the following commands are available:
- `beatsy/join_game` → Player registration
- `beatsy/submit_guess` → Year guess submission
- `beatsy/place_bet` → Bet toggle
- `beatsy/next_song` → Admin advance round
- `beatsy/start_game` → Admin start game

**And** commands follow HA WebSocket API schema (id, type, data)

**And** authentication handled per Epic 1 POC results (unauthenticated if possible)

**And** WebSocket broadcasting infrastructure is initialized

**And** helper function `broadcast_event(hass, event_type, data)` is available

**Prerequisites:** Story 2.2 (lifecycle management), Epic 1 (POC pattern documented)

**Technical Notes:**
- Use `hass.components.websocket_api.async_register_command()`
- Create `websocket_api.py` module with command handlers
- Implement broadcast mechanism for all connected clients
- Reference Epic 1 POC Decision Document for auth strategy
- If WebSocket auth required: Implement alternative (SSE/polling) from POC pivot plan
- Test: Connect client, send command, verify response

---

### Story 2.7: Configuration Entry Setup Flow (2025 Best Practice)

**⚠️ UPDATED 2025-11-10:** Reflects modern HA 2025 config flow patterns (Story 1.1 completion)

As a **Home Assistant user**,
I want **a configuration UI in HA to set up Beatsy**,
So that **I can configure basic settings through HA's integrations page following 2025 best practices**.

**Acceptance Criteria:**

**Given** Beatsy is installed via HACS
**When** I navigate to Settings → Integrations → Add Integration → Beatsy
**Then** a configuration dialog appears

**And** configuration dialog asks for:
- Default timer duration (optional, default: 30 seconds)
- Default year range (optional, default: 1950-2024)

**And** component uses `async_setup_entry()` pattern (2025 standard)

**And** config is persisted via ConfigEntry (not just `hass.data`)

**And** config can be updated later via integration options

**Prerequisites:** Story 2.3 (state management)

**Technical Notes (Updated for 2025):**

**Modern Config Flow Pattern:**
- Config entries are now the **PREFERRED** pattern in Home Assistant (2025)
- Legacy `async_setup()` used in Story 1.1 for POC only
- Production integrations should use `async_setup_entry()` + `ConfigFlow`
- Provides better user experience and integration with HA UI

**Implementation Approach:**
1. Create `config_flow.py` with `ConfigFlow` class extending `config_entries.ConfigFlow`
2. Implement `async_step_user()` for initial setup flow
3. Add `async_step_reconfigure()` for updating settings
4. Update `__init__.py` to use `async_setup_entry()` instead of `async_setup()`
5. Register config flow in manifest.json: `"config_flow": true`

**Config Entry vs Legacy YAML:**
- **Config Entry (2025):** UI-based setup, persisted in `.storage/`, no YAML editing
- **Legacy YAML:** Defined in `configuration.yaml`, deprecated for new integrations
- **Decision:** Use Config Entry for better UX and future-proofing

**Storage Pattern:**
- ConfigEntry data stored in `.storage/core.config_entries`
- Runtime state still in `hass.data[DOMAIN]` (ephemeral)
- Use `entry.data` for user config, `entry.options` for changeable settings

**References:**
- [HA Config Entries Docs](https://developers.home-assistant.io/docs/config_entries_index/)
- [Config Flow Best Practices](https://developers.home-assistant.io/docs/config_entries_config_flow_handler/)

**Story Priority:**
- OPTIONAL for MVP (game can be fully configured via web UI in Epic 3)
- RECOMMENDED for production quality and HACS compliance
- Consider implementing post-POC if time permits

---

## Epic 3: Admin Interface & Game Configuration

**Goal:** Enable admins to configure and control games through mobile-first web UI.

**Value:** Admin can set up and start games quickly, configure game rules, and control game flow.

### Story 3.1: Admin HTML Page & Mobile-First Layout

As an **admin**,
I want **a mobile-optimized admin interface accessible via my phone**,
So that **I can set up games without needing a laptop**.

**Acceptance Criteria:**

**Given** Beatsy component is installed
**When** I navigate to `/api/beatsy/admin` (requires HA auth)
**Then** the admin page loads with mobile-first responsive design

**And** page is usable on screens 320px-428px wide

**And** all touch targets are minimum 44x44px

**And** page includes sections: Game Configuration, Game Control, Game Status

**Prerequisites:** Story 2.5 (HTTP routes registered)

**Technical Notes:**
- Create `/www/admin.html`
- Mobile-first CSS (start with small screens, scale up)
- Test on actual iPhone/Android devices
- Use simple, clean design (no heavy frameworks needed for MVP)
- Single-page app or multi-section scroll design

---

### Story 3.2: Spotify Media Player Selector

As an **admin**,
I want **to select which media player will play the music**,
So that **the game uses the right speaker in my house**.

**Acceptance Criteria:**

**Given** admin page is loaded
**When** page fetches available media players via API call
**Then** dropdown populates with all Spotify-capable players

**And** each option shows friendly name (e.g., "Living Room Speaker")

**And** if no Spotify players found, show helpful error message

**And** selected player is saved to game config

**Prerequisites:** Story 2.4 (Spotify player detection), Story 3.1 (admin page)

**Technical Notes:**
- API endpoint: `GET /api/beatsy/api/media_players`
- Returns JSON list from Story 2.4
- Dropdown `<select>` with player entity_ids as values
- Save selection to `hass.data[DOMAIN]["game_config"]["media_player"]`

---

### Story 3.3: Playlist URI Input & Validation

As an **admin**,
I want **to paste a Spotify playlist URL and have it validated**,
So that **I know the playlist will work before starting the game**.

**Acceptance Criteria:**

**Given** admin has selected media player
**When** admin pastes Spotify playlist URI into input field
**Then** system validates URI format (spotify:playlist:* or https://open.spotify.com/playlist/*)

**And** system attempts to fetch playlist metadata

**And** if valid, show playlist name and track count

**And** if invalid, show clear error message

**And** validated playlist URI saved to game config

**Prerequisites:** Story 3.2 (media player selected)

**Technical Notes:**
- API endpoint: `POST /api/beatsy/api/validate_playlist`
- Accept both URI formats, normalize to `spotify:playlist:ID`
- Call Spotify API via HA integration to verify playlist exists
- Return: `{valid: true/false, name: "...", track_count: N, error: "..."}`
- Save to `hass.data[DOMAIN]["game_config"]["playlist_uri"]`

---

###Story 3.4: Game Settings Configuration

As an **admin**,
I want **to configure timer duration, year range, and scoring rules**,
So that **I can customize the game for my group**.

**Acceptance Criteria:**

**Given** admin page is loaded
**When** admin views game settings section
**Then** the following inputs are available:
- Timer duration (number input, 10-120 seconds, default: 30)
- Year range min (number input, 1900-2024, default: 1950)
- Year range max (number input, 1900-2024, default: 2024)
- Exact match points (number input, default: 10)
- ±2 years points (number input, default: 5)
- ±5 years points (number input, default: 2)
- Bet multiplier (number input, default: 2)

**And** all settings have sensible defaults pre-filled

**And** settings are saved to game config

**Prerequisites:** Story 3.1 (admin page)

**Technical Notes:**
- Simple HTML number inputs with min/max validation
- Save to `hass.data[DOMAIN]["game_config"]` on change (or on Start Game click)
- Consider: Local storage to remember last settings
- Validation: year_min < year_max

---

### Story 3.5: Start Game Button & Player Reset

As an **admin**,
I want **a prominent "Start Game" button that clears previous players and initializes a new game**,
So that **I can begin a fresh game session**.

**Acceptance Criteria:**

**Given** all required configuration is complete (player selected, playlist validated)
**When** admin clicks "Start Game" button
**Then** system clears all previous players from state

**And** system resets played songs list

**And** system loads playlist tracks into memory

**And** game status changes to "lobby" (waiting for players)

**And** button changes to "Game Active" (disabled) or "Stop Game"

**And** admin is redirected to player registration to add their own name

**Prerequisites:** Stories 3.2, 3.3, 3.4 (all config complete)

**Technical Notes:**
- API endpoint: `POST /api/beatsy/api/start_game`
- Backend: Clear `players`, `current_round`, `played_songs`
- Backend: Fetch all tracks from Spotify playlist (Story 2.4 helper + Spotify API)
- Store tracks in `hass.data[DOMAIN]["available_songs"]`
- Redirect to `/api/beatsy/player` for admin to register name
- Status tracking: `game_status`: "setup" | "lobby" | "active" | "ended"

---

### Story 3.6: Admin Player Registration & "Next Song" Control

As an **admin**,
I want **to register my name as a player and see a "Next Song" button others don't have**,
So that **I can play the game while controlling the flow**.

**Acceptance Criteria:**

**Given** game has been started (Story 3.5)
**When** admin registers their name as a player
**Then** admin name is added to players list with `is_admin: true` flag

**And** admin sees player interface like everyone else

**And** admin player view includes additional "Next Song" button (hidden for other players)

**And** admin can place guesses and earn points like any player

**Prerequisites:** Story 3.5 (game started), Story 4.1 (player registration exists)

**Technical Notes:**
- Store admin secret key in localStorage on admin device (e.g., UUID generated on Start Game)
- When player registers, check if they have admin secret key
- If yes: Set `player.is_admin = true`
- Player UI checks: If `is_admin === true`, show "Next Song" button
- Button calls: `POST /api/beatsy/api/next_song` (Epic 5)
- Security: Admin key is device-specific, not transferred

---

### Story 3.7: Game Status Display

As an **admin**,
I want **to see current game status (players joined, songs remaining)**,
So that **I know the game state at a glance**.

**Acceptance Criteria:**

**Given** game is active
**When** admin views status section
**Then** display shows:
- Game status ("Lobby", "Round Active", "Waiting for Next Song")
- Number of players joined
- Songs remaining in playlist
- Current round number (if in active game)

**And** status updates in real-time via WebSocket

**Prerequisites:** Story 3.5 (game started), Story 2.6 (WebSocket)

**Technical Notes:**
- Listen to WebSocket events: `game_status_update`
- Update UI dynamically without page reload
- Simple text display, no complex visualization needed for MVP
- Consider: Link to view player list (or show inline)

---

## Epic 4: Player Registration & Lobby

**Goal:** Players can join games with their name and wait in lobby for first song.

**Value:** Zero-friction player onboarding - name entry and done.

### Story 4.1: Player Registration Form

As a **party guest**,
I want **to enter my name and join the game instantly**,
So that **I can start playing without any friction**.

**Acceptance Criteria:**

**Given** I navigate to `/api/beatsy/player` (unauthenticated)
**When** I see the player page
**Then** a registration form appears with:
- Name input field (max 20 characters)
- "Join Game" button

**And** form is mobile-optimized (320px-428px screens)

**And** inputs are touch-friendly (44x44px minimum)

**Prerequisites:** Story 2.5 (HTTP routes), Story 3.5 (game started)

**Technical Notes:**
- Create `/www/player.html` (or `/www/start.html` per PRD)
- Simple HTML form, minimal JavaScript
- API endpoint: `POST /api/beatsy/api/join_game` with `{name: "..."}`
- Client-side validation: Name required, max 20 chars
- On success: Store player session ID in localStorage, transition to lobby

---

### Story 4.2: Duplicate Name Handling

As a **game system**,
I want **to handle duplicate player names automatically**,
So that **multiple "Sarah"s can play without conflict**.

**Acceptance Criteria:**

**Given** a player named "Sarah" already exists
**When** another player tries to register as "Sarah"
**Then** system appends number: "Sarah (2)"

**And** if "Sarah (2)" exists, use "Sarah (3)", etc.

**And** player is notified of their adjusted name

**And** adjusted name is used throughout the game

**Prerequisites:** Story 4.1 (registration form)

**Technical Notes:**
- Backend checks `players` array for existing name
- Append ` (N)` suffix if duplicate found
- Return adjusted name in API response: `{player_name: "Sarah (2)", session_id: "..."}`
- Frontend displays: "You're registered as: Sarah (2)"
- Store session_id in localStorage for reconnection

---

### Story 4.3: Lobby View with Player List

As a **player in lobby**,
I want **to see all players who have joined**,
So that **I know who's playing and that the game is filling up**.

**Acceptance Criteria:**

**Given** I've successfully registered
**When** I'm in the lobby view
**Then** I see:
- "Waiting for game to start..." message
- List of all player names who have joined
- Total player count

**And** player list updates in real-time as others join (via WebSocket)

**And** my name is highlighted in the list

**Prerequisites:** Story 4.1 (registration), Story 2.6 (WebSocket)

**Technical Notes:**
- WebSocket event: `player_joined` → broadcast to all clients
- Event payload: `{player_name: "...", total_players: N}`
- Frontend: Append to player list on receive
- CSS: Highlight current player's name (compare with localStorage session)
- Mobile-first design: Scrollable list if many players

---

### Story 4.4: Player Reconnection After Disconnect

As a **player**,
I want **to rejoin the game if I refresh my browser or lose connection**,
So that **I don't lose my place and score**.

**Acceptance Criteria:**

**Given** I was previously registered with session_id in localStorage
**When** I reload the player page or reconnect
**Then** system recognizes my session_id

**And** I'm returned to my current game state (lobby, active round, or results)

**And** my score and name are preserved

**And** I don't create a duplicate player entry

**Prerequisites:** Story 4.1 (registration with session_id)

**Technical Notes:**
- On page load: Check localStorage for `beatsy_session_id`
- If exists: API call `POST /api/beatsy/api/reconnect` with session_id
- Backend: Look up player by session_id in `players` array
- If found: Return player state and current game state
- If not found (game reset): Show registration form again
- Frontend: Skip registration, go directly to appropriate view

---

### Story 4.5: Lobby to Active Round Transition

As a **player in lobby**,
I want **to automatically transition to the active round when admin starts first song**,
So that **I don't miss the beginning of the game**.

**Acceptance Criteria:**

**Given** I'm waiting in the lobby
**When** admin clicks "Next Song" (first round starts)
**Then** I receive WebSocket event `round_started`

**And** my UI transitions from lobby to active round view

**And** I see the song information, year selector, bet toggle, and timer

**And** transition is smooth and immediate (<500ms)

**Prerequisites:** Story 4.3 (lobby view), Epic 5 (round start logic), Story 2.6 (WebSocket)

**Technical Notes:**
- WebSocket event: `round_started` with payload `{song: {...}, timer_duration: 30, started_at: timestamp}`
- Frontend: Listen for event, switch view from lobby to active round (Epic 8)
- Use `started_at` timestamp to calculate client-side timer
- Pre-load active round HTML/CSS to enable fast transition

---

## Epic 5: Game Mechanics - Song Selection & Scoring

**Goal:** Core game logic for song selection, timer management, scoring calculation, and leaderboard API.

**Value:** The brain of the game - all business logic that makes the game work.

### Story 5.1: Random Song Selection (No Repeats)

As a **game system**,
I want **to select a random song from the playlist without repeating songs**,
So that **each round features a unique track**.

**Acceptance Criteria:**

**Given** playlist tracks are loaded in memory (Story 3.5)
**When** admin triggers "Next Song"
**Then** system selects one random track from `available_songs` list

**And** selected track is removed from `available_songs`

**And** selected track is added to `played_songs` list

**And** if `available_songs` is empty, notify admin "All songs played"

**Prerequisites:** Story 3.5 (playlist loaded)

**Technical Notes:**
- Use random selection: `import random; random.choice(available_songs)`
- Track structure: `{uri, title, artist, album, year, cover_url}`
- Move from `available_songs` → `played_songs`
- Handle edge case: Empty playlist → return error, don't start round
- Store selected song in `current_round.song`

---

### Story 5.2: Round State Initialization

As a **game system**,
I want **to initialize a new round with song, timer, and empty guesses**,
So that **players can submit their guesses**.

**Acceptance Criteria:**

**Given** a song has been selected (Story 5.1)
**When** round is initialized
**Then** `current_round` state includes:
- `song`: {uri, title, artist, year, cover_url}
- `started_at`: UTC timestamp
- `timer_duration`: configured seconds
- `guesses`: [] (empty array)
- `status`: "active"

**And** round number increments

**And** WebSocket event `round_started` is broadcast to all players

**Prerequisites:** Story 5.1 (song selected), Story 2.6 (WebSocket)

**Technical Notes:**
- API endpoint: `POST /api/beatsy/api/next_song` (called by admin)
- Backend: Call Story 5.1 to select song
- Backend: Initialize `current_round` structure
- Backend: Broadcast WebSocket event with song data (without year!)
- Players receive: song metadata minus the year (they're guessing it)
- Timer logic: Use `started_at` timestamp for client-side countdown

---

### Story 5.3: Guess Submission & Storage

As a **player**,
I want **the system to record my year guess and bet choice**,
So that **my score can be calculated when the round ends**.

**Acceptance Criteria:**

**Given** round is active and timer hasn't expired
**When** I submit my guess via WebSocket command `beatsy/submit_guess`
**Then** system stores my guess in `current_round.guesses`

**And** guess includes: `{player_name, year_guess, bet_placed, submitted_at}`

**And** I cannot submit again (locked out)

**And** late submissions (after timer) are rejected

**Prerequisites:** Story 5.2 (round active)

**Technical Notes:**
- WebSocket command handler in `websocket_api.py`
- Validate: Timer hasn't expired (check `started_at + timer_duration` vs current time)
- Validate: Player hasn't already submitted guess for this round
- Store in: `hass.data[DOMAIN]["current_round"]["guesses"]`
- Return confirmation to client: `{success: true}`
- Client: Lock UI inputs after successful submission

---

### Story 5.4: Timer Expiration & Round End

As a **game system**,
I want **to detect when the timer expires and end the round automatically**,
So that **scoring can begin**.

**Acceptance Criteria:**

**Given** a round is active
**When** timer duration elapses (e.g., 30 seconds since `started_at`)
**Then** round status changes to "ended"

**And** no more guesses are accepted

**And** scoring calculation begins (Story 5.5)

**And** WebSocket event `round_ended` is broadcast

**Prerequisites:** Story 5.2 (round started), Story 5.3 (guesses submitted)

**Technical Notes:**
- Use asyncio timer: `asyncio.sleep(timer_duration)` then call `end_round()`
- Alternative: Client-side timers end independently, server doesn't need precise timer
- Server-side: Accept guesses for `timer_duration + 2 seconds` grace period
- When grace period ends: Lock round, calculate scores
- Broadcast `round_ended` event to trigger results display (Epic 9)

---

### Story 5.5: Proximity-Based Scoring Calculation

As a **game system**,
I want **to calculate points based on how close each guess was to the actual year**,
So that **players are rewarded for accuracy**.

**Acceptance Criteria:**

**Given** round has ended with guesses submitted
**When** scoring calculation runs
**Then** for each guess, calculate points:
- Exact year match: 10 points (or configured value)
- Within ±2 years: 5 points
- Within ±5 years: 2 points
- Beyond ±5 years: 0 points

**And** if player placed bet: multiply points by bet_multiplier (default 2)

**And** update each player's `total_points` in `players` array

**And** generate results structure for display

**Prerequisites:** Story 5.4 (round ended), Stories 3.4 (scoring config)

**Technical Notes:**
- Scoring function: `calculate_score(actual_year, guess_year, bet_placed, config)`
- Logic: Use absolute value `abs(actual_year - guess_year)` for proximity
- Bet modifier: `points * bet_multiplier` (can result in negative if base is negative - but base scoring is 0 minimum, so bet just doubles positive)
- Update `players` array: Find player by name, add points to `total_points`
- Return results: List of {player_name, guess, actual_year, points_earned, proximity}

---

### Story 5.6: Leaderboard Calculation API

As a **game system**,
I want **to provide a leaderboard API that returns sorted player standings**,
So that **results view (Epic 9) can display current standings**.

**Acceptance Criteria:**

**Given** players have accumulated points
**When** `get_leaderboard(hass)` function is called
**Then** function returns sorted player list by `total_points` descending

**And** response includes:
- Top 5 players (or all if fewer than 5)
- For a specific player: their position even if not in top 5

**And** ties are handled (players with same score have same rank)

**And** response format: `[{rank, player_name, total_points, is_current_player}, ...]`

**Prerequisites:** Story 5.5 (scoring updates total_points)

**Technical Notes:**
- Function signature: `get_leaderboard(hass, current_player_name=None) -> list`
- Sort: `sorted(players, key=lambda p: p['total_points'], reverse=True)`
- Assign ranks: Handle ties (same score = same rank)
- If `current_player_name` provided: Mark their entry with `is_current_player: true`
- Epic 9 will consume this API for results display
- This is the official leaderboard logic owner (per dependency map)

---

### Story 5.7: Session Management & Game Reset

As an **admin or system**,
I want **to track session state and support game reset**,
So that **I can start a new game without restarting HA**.

**Acceptance Criteria:**

**Given** a game is in progress
**When** admin clicks "Stop Game" or "Start Game" again
**Then** all game state is reset:
- Clear `players` array
- Clear `current_round`
- Clear `played_songs`
- Reset `available_songs` to full playlist
- Set `game_status` to "setup" or "lobby"

**And** all connected clients receive `game_reset` WebSocket event

**And** clients return to registration or lobby state

**Prerequisites:** Story 5.2 (round management)

**Technical Notes:**
- API endpoint: `POST /api/beatsy/api/reset_game`
- Clear all game state in `hass.data[DOMAIN]`
- Keep `game_config` (admin settings persist)
- Broadcast `game_reset` WebSocket event
- Clients: Clear localStorage session (optional) and return to registration
- Consider: Confirmation dialog before resetting active game

---

## Epic 6: Real-Time Event Infrastructure

**Goal:** Build generic pub/sub event bus for live updates across all clients.

**Value:** Enables social magic - everyone sees bets, results, leaderboards instantly.

### Story 6.1: Generic WebSocket Event Bus

As a **Beatsy developer**,
I want **a generic event bus for pub/sub messaging**,
So that **any epic can broadcast events to all connected clients**.

**Acceptance Criteria:**

**Given** WebSocket commands are registered (Story 2.6)
**When** any backend code calls `broadcast_event(hass, event_type, payload)`
**Then** event is sent to all connected WebSocket clients

**And** event format follows: `{type: "beatsy/event", event_type: "...", data: {...}}`

**And** clients can subscribe to specific event types or all events

**And** disconnected clients automatically unsubscribe

**Prerequisites:** Story 2.6 (WebSocket infrastructure)

**Technical Notes:**
- Maintain list of active WebSocket connections in `hass.data[DOMAIN]["websocket_connections"]`
- Function: `broadcast_event(hass, event_type, payload)` → Send to all
- Track connections: Add on connect, remove on disconnect
- Event types defined by each epic (e.g., "bet_placed", "round_started")
- No business logic in this layer - pure transport mechanism

---

### Story 6.2: Connection Management & Client Registry

As a **WebSocket infrastructure**,
I want **to track connected clients and their metadata**,
So that **I can manage broadcasts and detect disconnects**.

**Acceptance Criteria:**

**Given** a client connects via WebSocket
**When** connection is established
**Then** client is added to connections registry with:
- `connection_id`: unique ID
- `player_name`: associated player (if registered)
- `connected_at`: timestamp
- `last_ping`: for heartbeat monitoring

**And** when client disconnects, they're removed from registry

**And** registry is cleaned up on component unload

**Prerequisites:** Story 6.1 (event bus)

**Technical Notes:**
- Store in `hass.data[DOMAIN]["websocket_connections"]`
- Structure: `{connection_id: {player_name, connected_at, ...}, ...}`
- On disconnect: `del websocket_connections[connection_id]`
- Optional: Implement heartbeat/ping every 30s to detect stale connections
- Cleanup handler registered in Story 2.2 (lifecycle)

---

### Story 6.3: Event Type Definitions & Schema

As a **Beatsy developer**,
I want **clear definitions of all event types and their payloads**,
So that **frontend and backend stay in sync**.

**Acceptance Criteria:**

**Given** event bus is implemented (Story 6.1)
**When** developers reference event documentation
**Then** all event types are documented with schemas:
- `player_joined`: `{player_name, total_players}`
- `bet_placed`: `{player_name}`
- `round_started`: `{song: {...}, timer_duration, started_at}`
- `round_ended`: `{correct_year, results: [...]}`
- `leaderboard_updated`: `{leaderboard: [...]}`
- `game_reset`: `{}`

**And** schemas include data types and required fields

**And** documentation is in code comments or separate markdown doc

**Prerequisites:** Story 6.1 (event bus)

**Technical Notes:**
- Create `events.py` module with event type constants and schema documentation
- Example:
  ```python
  EVENT_PLAYER_JOINED = "player_joined"
  # Schema: {player_name: str, total_players: int}
  ```
- Each epic that broadcasts events adds documentation here
- Consider: JSON schema validation (optional for MVP)
- This story is primarily documentation, minimal code

---

### Story 6.4: Broadcast Helpers for Common Events

As a **backend developer**,
I want **convenience functions for broadcasting common events**,
So that **I don't repeat boilerplate code**.

**Acceptance Criteria:**

**Given** event bus exists (Story 6.1)
**When** developers need to broadcast events
**Then** the following helper functions are available:
- `broadcast_player_joined(hass, player_name, total_players)`
- `broadcast_bet_placed(hass, player_name)`
- `broadcast_round_started(hass, song, timer_duration, started_at)`
- `broadcast_round_ended(hass, correct_year, results)`
- `broadcast_leaderboard_updated(hass, leaderboard)`

**And** helpers internally call `broadcast_event()` with correct schema

**Prerequisites:** Story 6.1 (event bus), Story 6.3 (event definitions)

**Technical Notes:**
- Create helper functions in `events.py` or `broadcast_helpers.py`
- Each function constructs proper payload and calls `broadcast_event()`
- Example:
  ```python
  def broadcast_player_joined(hass, player_name, total_players):
      broadcast_event(hass, EVENT_PLAYER_JOINED, {
          "player_name": player_name,
          "total_players": total_players
      })
  ```
- Reduces coupling - if event schema changes, update helper only

---

## Epic 7: Music Playback Integration

**Goal:** Fetch Spotify playlists, extract metadata, control playback, handle conflicts.

**Value:** The music is the core experience - this makes it work.

### Story 7.1: Spotify Playlist Track Fetching with Pagination

As a **game system**,
I want **to fetch all tracks from a Spotify playlist (handling pagination)**,
So that **large playlists work correctly**.

**Acceptance Criteria:**

**Given** admin has provided a valid playlist URI
**When** system fetches playlist tracks
**Then** all tracks are retrieved (handle Spotify's 100-track page limit)

**And** each track includes: `{uri, name, artists, album, track_number}`

**And** tracks are stored in `available_songs` list

**And** fetch completes within reasonable time (< 10 seconds for 500-track playlist)

**Prerequisites:** Story 2.4 (Spotify helper), Story 3.5 (playlist URI from config)

**Technical Notes:**
- Use HA's Spotify integration API
- Spotify API returns 100 tracks per page, use `offset` parameter for pagination
- Loop until all tracks fetched:
  ```python
  while offset < total_tracks:
      fetch_tracks(playlist_id, offset=offset, limit=100)
      offset += 100
  ```
- Store raw track data for metadata extraction (Story 7.2)
- Handle API errors: Rate limits, network failures (retry logic)

---

### Story 7.2: Track Metadata Extraction & Year Validation

As a **game system**,
I want **to extract release year and other metadata from each track**,
So that **I have the correct answer for scoring**.

**Acceptance Criteria:**

**Given** tracks have been fetched (Story 7.1)
**When** system processes each track
**Then** the following metadata is extracted:
- `title`: Track name
- `artist`: Primary artist name
- `year`: Release year (from `album.release_date`)
- `cover_url`: Album cover image URL (medium size, ~300px)
- `uri`: Spotify track URI

**And** tracks without release year are filtered out (logged as warning)

**And** filtered track count reported to admin

**Prerequisites:** Story 7.1 (tracks fetched)

**Technical Notes:**
- Parse `album.release_date` (format: "YYYY-MM-DD" or "YYYY")
- Extract year: `int(release_date.split('-')[0])`
- Handle missing year: Skip track, log warning, decrement available songs count
- Album cover: Use `album.images[1]` (medium size) or largest available
- Store processed tracks in `available_songs` with clean structure
- Report: "Loaded 145 of 150 tracks (5 skipped - missing year)"

---

### Story 7.3: Media Player State Detection & Conflict Handling

As a **game system**,
I want **to detect if the media player is already playing something**,
So that **I don't interrupt the user's music unexpectedly**.

**Acceptance Criteria:**

**Given** admin starts a game
**When** system checks media player state
**Then** if player is currently playing, show warning to admin

**And** admin can choose to proceed (take over) or cancel

**And** if proceeding, save current media player state for restoration later

**And** state includes: `{source, media_title, media_artist, volume, position}`

**Prerequisites:** Story 2.4 (media player detection)

**Technical Notes:**
- Query media player entity: `hass.states.get(media_player_entity_id)`
- Check attribute: `state == "playing"`
- If playing: Store current state in `game_config.saved_player_state`
- Warning in admin UI: "Living Room Speaker is currently playing. Start game anyway?"
- Restoration logic in Story 7.6

---

### Story 7.4: Playback Initiation & Control

As a **game system**,
I want **to play the selected song on the configured media player**,
So that **players hear the music during the guessing round**.

**Acceptance Criteria:**

**Given** a round has started (Story 5.2)
**When** playback is initiated
**Then** selected song plays on configured media player

**And** playback starts within 2 seconds

**And** song plays for the configured timer duration

**And** if playback fails, error is logged and admin is notified

**Prerequisites:** Story 5.2 (round started), Story 2.4 (media player)

**Technical Notes:**
- Call HA service: `hass.services.async_call("media_player", "play_media", {"entity_id": player_entity, "media_content_type": "music", "media_content_id": track_uri})`
- Spotify URI format: `spotify:track:xxxxx`
- Error handling: Network failures, Spotify token expired, media player offline
- Don't block on playback - start async, continue round initialization
- Optional: Stop playback when timer expires (or let song play out)

---

### Story 7.5: Playback Error Handling & Retry

As a **game system**,
I want **to handle Spotify playback errors gracefully**,
So that **one failed song doesn't break the entire game**.

**Acceptance Criteria:**

**Given** playback initiation fails (Story 7.4)
**When** error is detected
**Then** system logs error with details (track URI, error message)

**And** admin receives notification: "Failed to play song. Skip to next?"

**And** if admin skips, select another song and retry

**And** if failure persists (3 retries), suggest checking Spotify connection

**Prerequisites:** Story 7.4 (playback)

**Technical Notes:**
- Catch exceptions from `play_media` service call
- Common errors: Token expired, network timeout, track not available in region
- Retry logic: Max 3 attempts with different songs
- Fallback: Admin manually troubleshoots or ends game
- Display error in admin status section (Story 3.7)

---

### Story 7.6: Media Player State Restoration

As a **game system**,
I want **to restore the media player's previous state after the game ends**,
So that **I don't leave the user's music disrupted**.

**Acceptance Criteria:**

**Given** game had saved media player state (Story 7.3)
**When** game ends or is reset (Story 5.7)
**Then** system restores previous playback state:
- Resume previous source if possible
- Restore volume level
- Resume playback position (if applicable)

**And** if restoration fails, log error but don't block game end

**And** if no state was saved, leave player idle

**Prerequisites:** Story 7.3 (state saved), Story 5.7 (game reset)

**Technical Notes:**
- Call HA services to restore state:
  - `media_player.select_source` for source
  - `media_player.volume_set` for volume
  - `media_player.media_seek` for position (if supported)
- Best-effort restoration - some players/sources may not support full restoration
- Clear saved state after restoration attempt
- Log: "Restored Living Room Speaker to previous state"

---

## Epic 8: Active Round - Player UI

**Goal:** Players see song info, select year, place bets, and submit guesses with timer.

**Value:** The core gameplay interface where the magic happens.

### Story 8.1: Active Round View Layout (Mobile-First)

As a **player**,
I want **a clean mobile interface showing song info and guess controls**,
So that **I can quickly make my guess without confusion**.

**Acceptance Criteria:**

**Given** round has started (receive `round_started` WebSocket event)
**When** active round view loads
**Then** layout includes (top to bottom):
- Album cover image (large, prominent)
- Song title (readable text, ~18-20px)
- Artist name (slightly smaller, ~16px)
- Timer display (large, centered, ~32px)
- Year dropdown selector
- "BET ON IT" toggle/button
- Submit button (prominent, ~48px height)

**And** all elements fit on screen without scrolling (320px-428px width)

**And** touch targets are 44x44px minimum

**Prerequisites:** Story 4.5 (transition from lobby), Story 5.2 (round started event)

**Technical Notes:**
- Create active round section in `/www/player.html`
- Mobile-first CSS, single-column layout
- Album cover: Load from `song.cover_url` in WebSocket event
- Use system fonts for fast load
- No year displayed (that's what they're guessing!)
- Test on actual phones for usability

---

### Story 8.2: Year Dropdown Selector

As a **player**,
I want **to select my year guess from a dropdown**,
So that **input is fast and error-free**.

**Acceptance Criteria:**

**Given** active round is displayed
**When** I interact with year selector
**Then** dropdown shows years from configured range (e.g., 1950-2024)

**And** years are in descending order (2024 → 1950)

**And** dropdown is touch-friendly on mobile

**And** selected year is visually confirmed

**And** I can change selection before submitting

**Prerequisites:** Story 8.1 (active round layout), Story 3.4 (year range config)

**Technical Notes:**
- HTML `<select>` element populated from config `year_range_min` to `year_range_max`
- Generate options dynamically:
  ```javascript
  for (let year = maxYear; year >= minYear; year--) {
      options.push(`<option value="${year}">${year}</option>`)
  }
  ```
- Default selection: None or middle year (optional)
- Styling: Increase font size for readability (16px minimum)

---

### Story 8.3: Bet Toggle & Visual Feedback

As a **player**,
I want **to toggle "BET ON IT" with clear visual feedback**,
So that **I know I've placed a bet before submitting**.

**Acceptance Criteria:**

**Given** active round is displayed
**When** I click "BET ON IT" button/toggle
**Then** button changes state visually (e.g., color, icon, label)

**And** bet state is clearly indicated ("BETTING" or checkmark)

**And** I can toggle bet on/off before submitting

**And** when I place bet, WebSocket event `beatsy/place_bet` is sent

**Prerequisites:** Story 8.1 (active round layout), Story 6.1 (WebSocket event bus)

**Technical Notes:**
- Button states: OFF (gray/outline) vs ON (red/solid, bold)
- Or checkbox with large label: "☐ BET ON IT" vs "☑ BETTING!"
- WebSocket command: `{"type": "beatsy/place_bet", "player_name": "...", "bet": true/false}`
- Backend: Broadcast `bet_placed` event to all clients (Story 8.4)
- Client tracks bet state locally until submission

---

### Story 8.4: Live Bet Indicators (Who's Betting)

As a **player**,
I want **to see which other players have placed bets**,
So that **I feel the social pressure and excitement**.

**Acceptance Criteria:**

**Given** active round is in progress
**When** any player places a bet (receive `bet_placed` WebSocket event)
**Then** their name appears in "Betting Now" list or indicator area

**And** updates appear within 500ms

**And** my own bet status is included

**And** list is cleared when round ends

**Prerequisites:** Story 8.3 (bet toggle), Story 6.4 (broadcast helpers)

**Technical Notes:**
- WebSocket event: `bet_placed` with payload `{player_name: "..."}`
- Display: Simple list below timer: "Betting: Sarah, Alex, Chris"
- Or icons: "🔥 3 players betting"
- Update DOM on each `bet_placed` event received
- Clear list on `round_ended` event

---

### Story 8.5: Timer Countdown Display

As a **player**,
I want **to see a live countdown timer**,
So that **I know how much time I have left to guess**.

**Acceptance Criteria:**

**Given** round is active
**When** timer is counting down
**Then** remaining seconds are displayed prominently

**And** timer updates every second smoothly

**And** timer is calculated client-side from `started_at` timestamp

**And** when timer reaches 0, inputs are locked (Story 8.6)

**And** visual urgency increases as time runs low (e.g., color change at < 10 seconds)

**Prerequisites:** Story 8.1 (active round layout), Story 5.2 (started_at timestamp)

**Technical Notes:**
- Receive `started_at` timestamp from `round_started` event
- Client-side calculation:
  ```javascript
  const elapsed = Date.now() - started_at;
  const remaining = timer_duration - elapsed;
  ```
- Update every 1000ms with `setInterval()`
- CSS: Change color at <10 seconds (e.g., red)
- When remaining <= 0: Call lockInputs() (Story 8.6)
- Don't rely on server timer ticks (avoids desync issues)

---

### Story 8.6: Guess Submission & Input Locking

As a **player**,
I want **to submit my guess and have inputs lock immediately**,
So that **I can't accidentally change my answer**.

**Acceptance Criteria:**

**Given** I've selected a year (and optionally placed bet)
**When** I click "Submit" button
**Then** WebSocket command `beatsy/submit_guess` is sent with my guess

**And** all inputs are disabled immediately (dropdown, bet button, submit button)

**And** UI shows "Guess submitted! Waiting for results..."

**And** timer continues counting down for other players

**And** late submissions (after timer expires) are rejected with error message

**Prerequisites:** Story 8.2 (year selector), Story 8.3 (bet toggle), Story 5.3 (backend guess handling)

**Technical Notes:**
- WebSocket command payload: `{"type": "beatsy/submit_guess", "player_name": "...", "year_guess": N, "bet_placed": true/false}`
- Backend validates submission (Story 5.3) and returns confirmation
- On success: Disable all inputs, show waiting message
- On failure (late/duplicate): Show error, allow re-submission if time remains
- Lock also triggered automatically when timer expires (Story 8.5)

---

### Story 8.7: Auto-Transition to Results View

As a **player**,
I want **to automatically see results when the round ends**,
So that **I don't miss the big reveal**.

**Acceptance Criteria:**

**Given** round is active and I've submitted guess (or timer expired)
**When** I receive `round_ended` WebSocket event
**Then** UI transitions from active round to results view (Epic 9)

**And** transition is immediate (<500ms)

**And** results display shows correct year, my guess, points earned

**Prerequisites:** Story 8.6 (guess submitted), Story 5.4 (round ended event), Epic 9 (results view)

**Technical Notes:**
- Listen for `round_ended` event with payload `{correct_year, results: [...]}`
- Switch view: Hide active round section, show results section (Epic 9)
- Pass data to results view: current player's result, all results, leaderboard
- Smooth transition: CSS fade or slide animation (optional)

---

## Epic 9: Results & Leaderboards

**Goal:** Display round results and overall standings after each round.

**Value:** The celebration moment - see who won, update standings, build anticipation for next round.

### Story 9.1: Results View Layout (Mobile-First)

As a **player**,
I want **to see results in a clear, scannable layout**,
So that **I quickly understand outcomes and standings**.

**Acceptance Criteria:**

**Given** round has ended (receive `round_ended` event)
**When** results view loads
**Then** layout includes (top to bottom):
- Correct year reveal (large, prominent)
- Round results board (all players' guesses)
- Overall leaderboard (top 5 + my position)
- "Waiting for next song..." message

**And** layout is mobile-optimized (320px-428px)

**And** my position is highlighted in both results and leaderboard

**Prerequisites:** Story 8.7 (transition to results), Story 5.5 (scoring data)

**Technical Notes:**
- Create results section in `/www/player.html`
- Data from `round_ended` event payload
- Mobile-first CSS, scrollable if needed
- Clear visual hierarchy: Correct year → Round results → Leaderboard
- Use contrasting colors for current player highlight

---

### Story 9.2: Correct Year Reveal

As a **player**,
I want **to see the correct year displayed prominently**,
So that **I immediately know the answer and can compare to my guess**.

**Acceptance Criteria:**

**Given** results view is displayed
**When** I see the correct year section
**Then** actual release year is shown in large text (~48-64px)

**And** optional: Album release date or additional context

**And** visual design emphasizes this as "the answer"

**Prerequisites:** Story 9.1 (results layout), Story 5.4 (correct year in event)

**Technical Notes:**
- Display `correct_year` from `round_ended` event
- Large, bold font
- Consider: "The answer was: **1985**"
- Optional enhancement: Show full release date if available
- Center alignment, prominent position at top of results

---

### Story 9.3: Round Results Board (All Players' Guesses)

As a **player**,
I want **to see everyone's guesses sorted by proximity to the correct year**,
So that **I can see who got close and who was way off**.

**Acceptance Criteria:**

**Given** results view is displayed
**When** I see the round results board
**Then** all players are listed, sorted by points earned (descending)

**And** each entry shows:
- Player name
- Their year guess
- Points earned this round
- Bet indicator (icon/badge if they bet)

**And** my entry is highlighted

**And** ties are shown (same points)

**Prerequisites:** Story 9.1 (results layout), Story 5.5 (results data)

**Technical Notes:**
- Data from `round_ended` event: `results` array
- Results structure: `[{player_name, year_guess, points_earned, bet_placed, proximity}, ...]`
- Sort by `points_earned` descending
- Display as table or list:
  | Player | Guess | Points | Bet |
  | Sarah  | 1987  | +10    | 🔥  |
- Highlight current player row (CSS background color)
- Bet indicator: Emoji or icon if `bet_placed: true`

---

### Story 9.4: Overall Leaderboard Display

As a **player**,
I want **to see current overall standings with top players**,
So that **I know my position in the competition**.

**Acceptance Criteria:**

**Given** results view is displayed
**When** I see the leaderboard section
**Then** top 5 players are shown by total points

**And** each entry shows: Rank, Player Name, Total Points

**And** if I'm not in top 5, my position is shown separately below

**And** ties are handled (players with same score have same rank)

**And** my entry is highlighted

**Prerequisites:** Story 9.1 (results layout), Story 5.6 (leaderboard API)

**Technical Notes:**
- Call backend API or receive leaderboard in `round_ended` event
- Alternative: Call `get_leaderboard(hass, current_player_name)` and include in event payload
- Display format:
  ```
  1. Sarah - 45 pts
  2. Alex - 40 pts
  3. Chris - 38 pts
  ...
  Your position: 7. You - 25 pts
  ```
- Highlight current player entry (bold or background color)
- Rank ties: If 2 players have 40 pts, both are rank 2, next is rank 4

---

### Story 9.5: Waiting State & Next Round Anticipation

As a **player**,
I want **clear indication that I'm waiting for the next song**,
So that **I know the game isn't stuck and admin will advance soon**.

**Acceptance Criteria:**

**Given** results have been displayed
**When** I'm waiting for next round
**Then** message displays: "Waiting for next song..."

**And** message is prominent and clear

**And** optional: Loading animation or pulsing indicator

**And** when admin clicks "Next Song", I automatically transition back to active round (Story 8.7 reverse)

**Prerequisites:** Story 9.1 (results layout), Story 8.7 (round start transition)

**Technical Notes:**
- Simple text message below leaderboard
- Optional CSS animation: Pulsing dot or spinner
- Listen for `round_started` event to transition back to Story 8.1
- Maintain engagement during wait time (don't let energy drop)
- Consider: Show fun stats while waiting (e.g., "Closest guess this game: Sarah with ±0 years")

---

### Story 9.6: Responsive Scrolling for Long Results

As a **player**,
I want **results to scroll smoothly if there are many players**,
So that **I can see everyone's guesses on my small phone screen**.

**Acceptance Criteria:**

**Given** there are 10+ players in the game
**When** results view is displayed
**Then** round results board scrolls vertically

**And** scrolling is smooth and touch-friendly

**And** leaderboard section remains accessible (not cut off)

**And** important elements (correct year, my position) are prioritized in viewport

**Prerequisites:** Story 9.3 (results board)

**Technical Notes:**
- CSS: `overflow-y: auto` on results board container
- Max height: Set to ensure leaderboard visible without initial scroll
- Touch scrolling: `-webkit-overflow-scrolling: touch` for smooth iOS scroll
- Consider: Sticky header for "Correct Year: 1985" while scrolling
- Test with 20 players to verify usability

---

## Epic 10: Production Readiness

**Goal:** Testing, error handling, documentation, and production polish.

**Value:** Ensure Beatsy is reliable, handles edge cases, and is easy for users to adopt.

### Story 10.1: End-to-End Integration Test Suite

As a **QA engineer**,
I want **automated tests covering the complete game flow**,
So that **we catch regressions before users do**.

**Acceptance Criteria:**

**Given** all epics are complete
**When** E2E test suite runs
**Then** tests cover full game flow:
1. Component loads in HA
2. Admin configures game
3. Admin starts game
4. Multiple players join
5. Admin advances to first round
6. Players submit guesses (some with bets)
7. Timer expires, scores calculated
8. Results displayed correctly
9. Leaderboard updates
10. Admin advances to second round
11. Game reset works

**And** tests run in CI/CD pipeline

**And** tests use mocked Spotify API (no real playlists needed)

**Prerequisites:** All prior epics complete

**Technical Notes:**
- Use pytest for backend tests
- Use Playwright or Selenium for frontend E2E tests
- Mock external dependencies (Spotify API)
- Test both success paths and failure scenarios
- Run tests on HA test instance (containerized)
- Document: `/tests/README.md` with setup instructions

---

### Story 10.2: Load Testing (20 Concurrent Players)

As a **developer**,
I want **to verify the system handles 20 concurrent players smoothly**,
So that **large house parties don't cause issues**.

**Acceptance Criteria:**

**Given** load test environment is set up
**When** 20 simulated players connect and play 5 rounds
**Then** all players receive broadcasts within 500ms

**And** no WebSocket connections drop

**And** scoring calculations remain accurate

**And** HA resource usage stays reasonable (<70% CPU, <1GB RAM)

**And** any performance bottlenecks are documented

**Prerequisites:** Epic 6 (WebSocket), Epic 5 (scoring)

**Technical Notes:**
- Use locust.io or custom Python script to simulate 20 WebSocket clients
- Each client: Connect, join game, submit guesses with timing variations
- Monitor: HA system resources, WebSocket latency, score accuracy
- Document results: "Tested with 20 players, avg latency: 250ms"
- Stress test: Try 30-40 players to find breaking point
- Deliverable: Performance report in `docs/performance-testing.md`

---

### Story 10.3: Cross-Browser & Device Testing

As a **QA engineer**,
I want **to verify Beatsy works on all common mobile browsers and devices**,
So that **players with different phones can all play**.

**Acceptance Criteria:**

**Given** Beatsy is deployed
**When** tested on the following platforms
**Then** all core functionality works:
- iOS Safari (latest + previous version)
- Chrome on Android (latest)
- Firefox on Android
- Desktop browsers (Chrome, Firefox, Safari) - bonus

**And** mobile-first design renders correctly (320px-428px)

**And** touch interactions work smoothly

**And** any browser-specific issues are documented and fixed

**Prerequisites:** Epics 8, 9 (player UI complete)

**Technical Notes:**
- Test real devices if possible (not just emulators)
- Focus on: WebSocket support, CSS rendering, touch targets
- Common issues: iOS Safari WebSocket behavior, Android Chrome scrolling
- Use BrowserStack or similar for cross-browser testing
- Document known issues and workarounds in README
- Fix critical issues, document minor ones as "known limitations"

---

### Story 10.4: Error Handling Hardening

As a **developer**,
I want **comprehensive error handling for all failure scenarios**,
So that **errors don't crash the game or confuse users**.

**Acceptance Criteria:**

**Given** various error scenarios occur
**When** errors are triggered
**Then** user-friendly error messages are displayed:
- Spotify playlist not found → "Playlist not found. Check your URL."
- No Spotify players available → "No Spotify players found. Check your HA integration."
- Network timeout → "Connection lost. Reconnecting..."
- WebSocket disconnect → Auto-reconnect with status indicator

**And** errors are logged for debugging (HA logs)

**And** errors don't crash component or leave game in broken state

**And** users are given clear next steps

**Prerequisites:** All epics (cross-cutting concern)

**Technical Notes:**
- Review all API calls, WebSocket handlers, Spotify integration points
- Add try/except blocks with specific error handling
- User messages: No technical jargon, actionable guidance
- Logging: Include context (player name, round number, error details)
- Graceful degradation: If WebSocket fails, offer page refresh
- Test: Disconnect WiFi, kill Spotify, invalid inputs, etc.

---

### Story 10.5: Input Validation & Sanitization

As a **security-conscious developer**,
I want **all user inputs validated and sanitized**,
So that **malicious inputs don't cause issues**.

**Acceptance Criteria:**

**Given** users provide various inputs
**When** inputs are processed
**Then** validation rules enforced:
- Player names: Max 20 chars, alphanumeric + spaces, no HTML/script tags
- Playlist URIs: Valid Spotify format only
- Year guesses: Within configured range
- Numeric inputs: Min/max bounds, integers only

**And** dangerous inputs are rejected with error messages

**And** inputs are sanitized before storage/display (XSS prevention)

**And** rate limiting prevents spam (Story 10.6)

**Prerequisites:** Epics 3, 4, 8 (all user input points)

**Technical Notes:**
- Backend validation: Never trust client-side only
- Sanitize player names: Strip HTML tags, escape special chars
- Validate Spotify URIs: Regex match `spotify:playlist:[a-zA-Z0-9]+`
- XSS prevention: Use templating engine auto-escaping or manual escaping
- Reject suspicious inputs: SQL keywords, script tags, excessive length
- Log suspicious inputs for security monitoring

---

### Story 10.6: Rate Limiting & Spam Prevention

As a **system administrator**,
I want **rate limiting on player actions**,
So that **one bad actor can't disrupt the game**.

**Acceptance Criteria:**

**Given** rate limits are configured
**When** players attempt actions
**Then** limits are enforced:
- Player registration: Max 1 join per IP per 5 seconds
- Bet toggle: Max 1 change per second (debounced)
- Guess submission: Max 1 per round per player

**And** excessive requests are blocked with error message

**And** legitimate users are not affected

**And** rate limits are configurable

**Prerequisites:** Epics 4, 8 (player actions)

**Technical Notes:**
- Implement in WebSocket command handlers and API endpoints
- Track: Player IP or session ID + action timestamp
- Use in-memory dictionary: `{ip: last_action_timestamp}`
- Clean up old entries periodically (avoid memory leak)
- Rate limit values:
  - Join: 1 per 5 sec per IP
  - Bet toggle: 1 per sec (debounce client-side too)
  - Guess: 1 per round (enforce in Story 5.3)
- Return error: `{error: "Too many requests. Please wait."}`

---

### Story 10.7: README & Installation Guide

As a **new Beatsy user**,
I want **clear installation and setup instructions**,
So that **I can get Beatsy running quickly**.

**Acceptance Criteria:**

**Given** user reads README.md
**When** they follow installation steps
**Then** README includes:
- What is Beatsy (elevator pitch)
- Prerequisites (HA Core 2024.1+, Spotify integration)
- Installation via HACS (step-by-step)
- Configuration (how to set up game)
- Usage (admin vs player, how to start game)
- Troubleshooting (common issues)
- Screenshots of admin and player interfaces

**And** instructions are clear and concise

**And** links to HA documentation where relevant

**Prerequisites:** All epics complete

**Technical Notes:**
- Create `/README.md` at repo root
- Include: Screenshots from actual gameplay
- Format: Markdown with sections, headers, bullet points
- Keep updated as features evolve
- Consider: Video walkthrough (optional, post-MVP)
- Link to PRD and architecture docs for developers

---

### Story 10.8: Troubleshooting Guide & FAQ

As a **Beatsy user**,
I want **answers to common questions and solutions to common problems**,
So that **I can resolve issues without creating GitHub issues**.

**Acceptance Criteria:**

**Given** user encounters an issue
**When** they check troubleshooting guide
**Then** guide includes solutions for:
- "Players can't access the game" → Check unauthenticated access config
- "Spotify won't play" → Check Spotify integration, token refresh
- "WebSocket disconnects" → Check HA WebSocket config, network stability
- "Scores are wrong" → Report as bug with details
- "Game is laggy with 15 players" → Expected limits, optimize or reduce players

**And** FAQ includes:
- Can I use Apple Music? (No, Spotify only for MVP)
- Do players need HA accounts? (No)
- Can I run multiple games simultaneously? (No, one game per HA instance)
- Will this work over the internet? (No, local network only for MVP)

**Prerequisites:** Production usage and feedback (post-MVP)

**Technical Notes:**
- Create `/docs/TROUBLESHOOTING.md`
- Update based on user-reported issues
- Link from README
- Include: Log locations, debug mode instructions
- Community contributions welcome (GitHub issues → FAQ entries)

---

### Story 10.9: Code Quality & Documentation

As a **future contributor**,
I want **clean, well-documented code**,
So that **I can understand and extend Beatsy**.

**Acceptance Criteria:**

**Given** developer reviews codebase
**When** they examine code
**Then** code follows HA development guidelines

**And** Python code includes:
- Type hints for function signatures
- Docstrings for all public functions/classes
- Clear variable and function names
- Comments for complex logic only

**And** JavaScript code includes:
- Clear function names
- Comments for non-obvious behavior
- Consistent formatting

**And** project includes:
- `CONTRIBUTING.md` with contribution guidelines
- Code style guide reference (Black for Python, Prettier for JS - optional)

**Prerequisites:** All epics complete

**Technical Notes:**
- Run linters: `pylint`, `black` for Python; `eslint` for JavaScript
- Add pre-commit hooks (optional but recommended)
- Document: Module structure, key design decisions
- Inline docs: Docstrings use Google or NumPy style
- Reference: HA developer docs for component patterns

---

### Story 10.10: Final Testing & Production Checklist

As a **Product Manager**,
I want **a pre-release checklist to ensure nothing is missed**,
So that **MVP launch is smooth**.

**Acceptance Criteria:**

**Given** all stories are complete
**When** PM reviews launch checklist
**Then** checklist confirms:
- ✅ POC passed (Epic 1 results documented)
- ✅ All functional requirements from PRD implemented
- ✅ Mobile-first design validated on real devices
- ✅ E2E tests passing
- ✅ Load test results documented (20 players)
- ✅ Cross-browser testing complete
- ✅ Error handling tested
- ✅ README and docs complete
- ✅ HACS submission requirements met
- ✅ Security review complete (input validation, rate limiting)
- ✅ Performance acceptable (load times, real-time latency)
- ✅ User acceptance testing with real party (optional but recommended!)

**And** any blockers are addressed before launch

**Prerequisites:** All other Epic 10 stories

**Technical Notes:**
- Create `/docs/LAUNCH_CHECKLIST.md`
- Review in team meeting before HACS submission
- Document any known issues or limitations
- Plan: Soft launch to small user group before public HACS listing
- Celebrate! 🎉

---

---

## Epic Breakdown Summary

**Total: 10 Epics, ~70 Stories**

| Epic | Stories | Estimated Effort |
|------|---------|------------------|
| Epic 1: Foundation & POC | 7 | 1-2 weeks (CRITICAL) |
| Epic 2: HACS Integration & Core | 6-7 | 1-2 weeks |
| Epic 3: Admin Interface | 7 | 1-2 weeks |
| Epic 4: Player Registration & Lobby | 5 | 1 week |
| Epic 5: Game Mechanics | 7 | 1-2 weeks |
| Epic 6: Real-Time Infrastructure | 4 | 1 week |
| Epic 7: Music Playback | 6 | 2-3 weeks (complex) |
| Epic 8: Active Round UI | 7 | 1-2 weeks |
| Epic 9: Results & Leaderboards | 6 | 1 week |
| Epic 10: Production Readiness | 10 | 2 weeks |

**Total Estimated Effort: 12-18 weeks (3-4.5 months) for single developer**

**Parallel Work Opportunities (Can reduce timeline to ~10-14 weeks with team):**
- After Epic 2: Epic 3 ‖ Epic 4
- After Epic 5: Epic 6 ‖ Epic 7
- After Epic 6 & 7: Epic 8 ‖ Epic 9

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._
