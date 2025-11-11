# Story 1.4: Spotify API Basic Integration Test

Status: review

## Story

As a **Beatsy developer**,
I want **to verify I can fetch a playlist and play one song via HA's Spotify integration**,
So that **I validate Spotify API viability before building game mechanics**.

## Acceptance Criteria

**AC-1: Playlist Track List Fetching**
- **Given** Home Assistant has an active Spotify integration configured
- **When** Beatsy attempts to fetch playlist track list from Spotify URI
- **Then** playlist track list is successfully retrieved
- **And** track data includes: uri, title, artist, album
- **And** playlist fetch completes within 5 seconds
- **And** HA logs confirm: "Beatsy: Fetched {count} tracks from playlist {playlist_id}"

**AC-2: Track Metadata Extraction**
- **Given** playlist tracks have been fetched
- **When** Beatsy extracts metadata for each track
- **Then** each track includes required fields:
  - `uri`: Spotify track URI (spotify:track:xxxxx)
  - `title`: Track name
  - `artist`: Primary artist name
  - `album`: Album name
  - `release_year`: Extracted from album.release_date field
  - `cover_url`: Album cover image URL
- **And** tracks without release year data are identified and logged
- **And** metadata structure is documented for Epic 7

**AC-3: Media Player Playback**
- **Given** track metadata has been extracted
- **When** Beatsy calls `hass.services.async_call("media_player", "play_media", {...})`
- **Then** specified Spotify track plays on the configured media player
- **And** playback starts within 2 seconds of command
- **And** HA logs confirm: "Beatsy: Playing track {track_uri} on {media_player_entity}"
- **And** no playback errors occur

**AC-4: Media Player State Reading**
- **Given** track is playing via media player
- **When** Beatsy reads media player state after 2-second delay
- **Then** media player attributes include:
  - `media_title`: Track name (from Spotify)
  - `media_artist`: Artist name (from Spotify)
  - `media_album_name`: Album name (from Spotify)
  - `entity_picture`: Album cover URL (from Spotify)
- **And** retrieved metadata matches expected track data
- **And** metadata is available for game display

**AC-5: Spotify Integration Documentation**
- **Given** all Spotify tests complete
- **When** developer reviews Spotify integration patterns
- **Then** documentation includes:
  - Exact method for fetching playlist via HA integration
  - Metadata structure and field mappings
  - Playback initiation service call pattern
  - Media player state reading approach
  - Known limitations (tracks without year data, API rate limits)
- **And** documentation saved for Epic 7 implementation

## Tasks / Subtasks

- [x] Task 1: Research HA Spotify Integration Patterns (AC: #1, #2)
  - [x] Review Home Assistant Spotify integration documentation
  - [x] Research `spotify.get_playlist()` or equivalent service/API
  - [x] Investigate how to access playlist tracks via HA
  - [x] Document Spotify URI format requirements
  - [x] Identify API pagination requirements (if applicable)

- [x] Task 2: Create Spotify Helper Module (AC: #1, #2)
  - [x] Create `custom_components/beatsy/spotify_helper.py`
  - [x] Import: `homeassistant.core`, `logging`, `aiohttp` if needed
  - [x] Implement `async def fetch_playlist_tracks(hass, playlist_uri) -> list[dict]`
  - [x] Handle Spotify API via HA integration (not direct API calls)
  - [x] Parse playlist URI (support both spotify:playlist:xxx and https://open.spotify.com/playlist/xxx formats)
  - [x] Extract track metadata: uri, name, artists, album, release_date

- [x] Task 3: Extract and Validate Metadata Structure (AC: #2)
  - [x] Implement `extract_track_metadata(track_data) -> dict` function
  - [x] Parse `album.release_date` field (format: "YYYY-MM-DD" or "YYYY")
  - [x] Extract year: `int(release_date.split('-')[0])`
  - [x] Handle missing release year gracefully (log warning, return None)
  - [x] Select album cover URL from `album.images` array (prefer medium size ~300px)
  - [x] Return clean structure: {uri, title, artist, year, album, cover_url}

- [x] Task 4: Implement Playback Service Call (AC: #3)
  - [x] Implement `async def play_track(hass, entity_id, track_uri) -> bool` function
  - [x] Call HA service: `hass.services.async_call("media_player", "play_media", ...)`
  - [x] Service data structure:
    ```python
    {
        "entity_id": entity_id,
        "media_content_type": "music",
        "media_content_id": track_uri  # spotify:track:xxxxx
    }
    ```
  - [x] Add error handling: HomeAssistantError, network timeout, invalid entity
  - [x] Log playback initiation with track URI and entity ID
  - [x] Return success/failure status

- [x] Task 5: Read Media Player State (AC: #4)
  - [x] Implement `async def get_media_player_metadata(hass, entity_id) -> dict` function
  - [x] Wait 2 seconds after playback initiation (allow HA state to update)
  - [x] Call: `state = hass.states.get(entity_id)`
  - [x] Extract attributes: media_title, media_artist, media_album_name, entity_picture
  - [x] Validate all required fields are present
  - [x] Return metadata dictionary
  - [x] Handle case where state update hasn't completed (retry once after additional 2s)

- [x] Task 6: Create Test Script for POC Validation (AC: #1-4)
  - [x] Create `tests/poc_spotify_test.py` test script
  - [x] Accept CLI arguments: --playlist_uri, --media_player_entity
  - [x] Test sequence:
    1. Fetch playlist tracks (print count)
    2. Extract metadata for first 3 tracks (print details)
    3. Play first track on specified media player
    4. Wait 2 seconds
    5. Read media player state (verify metadata)
    6. Print results: PASS/FAIL with details
  - [x] Output metrics to JSON: {test_date, ha_version, playlist_uri, tracks_fetched, metadata_complete, playback_success, errors}

- [x] Task 7: Update Component Init to Load Spotify Helper (AC: All)
  - [x] Update `custom_components/beatsy/__init__.py`
  - [x] Import: `from .spotify_helper import fetch_playlist_tracks, play_track`
  - [x] Store Spotify helper functions reference in hass.data[DOMAIN]
  - [x] Log: "Beatsy: Spotify helper loaded"
  - [x] Handle case where Spotify integration not configured (log warning)

- [ ] Task 8: Test with Real Spotify Playlist (AC: #1-4) **[MANUAL TESTING REQUIRED]**
  - [x] Test script created and ready for execution
  - [ ] **[USER ACTION]** Deploy updated component to Home Assistant
  - [ ] **[USER ACTION]** Ensure Spotify integration configured in HA
  - [ ] **[USER ACTION]** Identify available Spotify-capable media player
  - [ ] **[USER ACTION]** Create or select test playlist (10-20 tracks, mix of decades)
  - [ ] **[USER ACTION]** Run test script: `python tests/poc_spotify_test.py --playlist_uri=<uri> --media_player_entity=<entity_id>`
  - [ ] **[USER ACTION]** Verify playlist tracks fetched successfully
  - [ ] **[USER ACTION]** Verify metadata includes release years
  - [ ] **[USER ACTION]** Verify playback initiates and song plays audibly
  - [ ] **[USER ACTION]** Verify media player state updates with correct metadata

- [ ] Task 9: Document Missing Year Data Handling (AC: #2, #5) **[DEPENDS ON TASK 8]**
  - [x] Code handles missing year data gracefully (logs warnings)
  - [ ] **[USER ACTION]** Test with tracks that have incomplete metadata
  - [ ] **[USER ACTION]** Document percentage of tracks with missing year data
  - [x] Filtering strategy proposed: Skip tracks without year (implemented in helper)
  - [x] Log warning implemented: "Track {title} missing release year - will be filtered in production"
  - [ ] **[USER ACTION]** Update documentation with actual test findings

- [ ] Task 10: Document Spotify Integration Patterns (AC: #5) **[DEPENDS ON TASK 8]**
  - [x] Code implementation documents all patterns used
  - [ ] **[USER ACTION]** Create documentation section in POC Decision Document (Story 1.7)
  - [x] Exact API methods documented in spotify_helper.py
  - [x] Metadata structure defined in extract_track_metadata() return type
  - [x] Playback patterns implemented and logged
  - [ ] **[USER ACTION]** Note actual limitations discovered during testing
  - [x] Code snippets available in spotify_helper.py for Epic 7 reference

## Dev Notes

### Architecture Patterns and Constraints

**Spotify Integration via Home Assistant (2025 Pattern):**
- Beatsy DOES NOT create separate Spotify auth or direct API calls
- Leverages existing HA Spotify integration (respects user's existing setup)
- Uses HA service calls for all Spotify operations
- Avoids auth conflicts and credential management complexity

**From Tech Spec (Epic 1 - Story 1.4):**
- **Purpose:** Validate Spotify API viability before building game mechanics
- **Critical Validation:** Confirm release year metadata is accessible
- **Service Call:** `hass.services.async_call("media_player", "play_media", {...})`
- **Metadata Source:** HA media player state attributes after playback starts
- **Timing:** 2-second delay for HA state update after playback initiation

**From Architecture Document (ADR-003):**
- **Minimal JSON + Runtime Metadata** pattern validated in this story
- JSON playlists will store only (URI, year, fun_fact) in production
- Title, artist, album, cover URL fetched from HA media player state at runtime
- This story proves metadata is available and timing is acceptable

**Spotify URI Formats:**
```
URI Format: spotify:playlist:{playlist_id}
URL Format: https://open.spotify.com/playlist/{playlist_id}
Track URI: spotify:track:{track_id}
```

**Metadata Structure (from HA Media Player State):**
```python
state = hass.states.get("media_player.spotify_living_room")
attributes = {
    "media_title": "Livin' on a Prayer",       # From Spotify
    "media_artist": "Bon Jovi",                 # From Spotify
    "media_album_name": "Slippery When Wet",   # From Spotify
    "entity_picture": "https://...",            # Album cover URL
    "media_duration": 249,                      # Track length in seconds
    "media_position": 15,                       # Current playback position
    "source": "Spotify",                        # Source name
    "volume_level": 0.5                         # Volume (0.0-1.0)
}
```

**From PRD Requirements:**
- **NFR-P3:** Music playback within 2 seconds of command - VALIDATED in this story
- **FR-1.2:** Leverage existing HA Spotify integration - CORE PRINCIPLE
- **Epic 7 Dependency:** This story provides patterns for full Spotify integration

**Service Call Pattern:**
```python
await hass.services.async_call(
    domain="media_player",
    service="play_media",
    service_data={
        "entity_id": "media_player.spotify_living_room",
        "media_content_type": "music",  # or "track"
        "media_content_id": "spotify:track:0J6mQxEZnlRt9ymzFntA6z"
    }
)
```

**Error Handling Considerations:**
- **Spotify Token Expired:** HA handles refresh automatically, but may fail if user revoked
- **Network Timeout:** Spotify API may be slow, use reasonable timeout (10 seconds)
- **Invalid Playlist URI:** Validate format before API call
- **Media Player Offline:** Check entity state before playback attempt
- **Track Unavailable:** Some tracks may not be available in user's region

**Testing Approach:**
- Manual test with real Spotify playlist (no mocking for POC)
- Use developer's actual Spotify account and media players
- Document exact configuration used for reproducibility

### Learnings from Previous Story

**From Story 1.3 (Status: ready-for-dev)**

**CRITICAL FINDING: Spotify Dependency Resolved**
- **Issue:** Manifest originally declared `spotify` dependency, but Spotify not configured → Component failed to load
- **Fix Applied:** Removed `spotify` from `manifest.json` dependencies (commit 418c90bc)
- **Resolution:** Component now loads successfully even without Spotify configured
- **Action for Story 1.4:** Add Spotify back to manifest IF required, or document as optional runtime dependency
- **Future:** Spotify integration is required for gameplay but not for component registration

**Component Foundation Confirmed Stable:**
- Component loads in HA without errors (Story 1.1 validated)
- `hass.data[DOMAIN]` initialized and accessible
- HTTP dependency available (if needed for Spotify API calls)
- Async/await patterns established and working

**2025 Standards Applied & Validated:**
- Modern Python 3.11+ type hints used throughout (`dict[str, Any]`)
- Async service call pattern: `await hass.services.async_call(...)`
- Module-level `_LOGGER = logging.getLogger(__name__)` logging
- Error handling with comprehensive try/except blocks

**Pattern to Reuse from Story 1.2/1.3:**
- Service call wrapper pattern (similar to WebSocket view registration)
- Logging approach: INFO for operations, DEBUG for details, ERROR for failures
- Error handling: Graceful degradation with user-friendly error messages
- Type hints for all function signatures

**Files Created/Modified in Previous Stories:**
- `__init__.py` - Component initialization (modify for Spotify helper)
- `const.py` - Constants defined (DOMAIN = "beatsy")
- `websocket_handler.py` - WebSocket endpoint (not needed for this story)
- `test.html` - HTTP test page (not needed for this story)

**No Blocking Technical Debt:**
- All foundational components stable from Story 1.1-1.3
- WebSocket implementation complete (pending deployment testing)
- Component lifecycle working correctly
- No errors or warnings in HA logs

**Key Architectural Validation Complete:**
- HTTP unauthenticated access ✅ VALIDATED (Story 1.2)
- WebSocket unauthenticated access ✅ IMPLEMENTED (Story 1.3, testing pending)
- Spotify integration viability ⏳ TO BE VALIDATED (THIS STORY)
- Pattern consistency maintained across all stories

[Source: stories/1-3-websocket-connection-without-authentication.md#Dev-Agent-Record]

### Project Structure Notes

**Expected File Paths:**
```
/config/custom_components/beatsy/
├── __init__.py              # MODIFY: Import and register Spotify helper
├── manifest.json            # VALIDATE: Check if spotify dependency needed
├── const.py                # EXISTS
├── spotify_helper.py       # NEW FILE: Spotify integration wrapper
├── websocket_handler.py    # EXISTS (from Story 1.3)
└── www/                    # EXISTS
    └── test.html           # EXISTS (from Story 1.2)

/tests/
└── poc_spotify_test.py     # NEW FILE: Test script for POC validation
```

**New File: spotify_helper.py**
- Purpose: Wrapper for HA Spotify integration service calls
- Responsibilities:
  - Fetch playlist tracks via HA Spotify integration
  - Extract and normalize track metadata
  - Initiate playback via media_player service
  - Read media player state for runtime metadata
  - Error handling for all Spotify operations
- Pattern: Pure async functions, no state storage (stateless utility)

**Modified File: __init__.py**
- Add import: `from .spotify_helper import fetch_playlist_tracks, play_track`
- Store function references in `hass.data[DOMAIN]` for other modules
- Optional: Check if Spotify integration exists, log warning if not configured
- No impact on component registration (Spotify not blocking dependency)

**Test File: tests/poc_spotify_test.py**
- Standalone Python script (not pytest test)
- CLI arguments for playlist URI and media player entity
- Manual execution for POC validation
- Outputs metrics JSON for Story 1.7 POC Decision Document

**File Alignment with Architecture:**
- `spotify_helper.py` → Maps to "Spotify Integration Strategy" in architecture.md
- Service call pattern → Follows "Integration Points" section (HA service calls)
- Metadata extraction → Validates ADR-003 (Minimal JSON + Runtime Metadata)

**No Conflicts:**
- Spotify helper is new module, no existing Spotify code to conflict with
- Service calls use standard HA media_player domain
- No WebSocket or HTTP view dependencies (isolated testing)

### Testing Standards Summary

**Test Approach (POC Validation - Manual):**
- Real Spotify integration test (no mocking)
- Test with actual HA instance and Spotify account
- Manual playlist creation or selection
- Verification via:
  1. HA logs (playlist fetch, playback initiation)
  2. Audible playback on media player
  3. Media player state inspection (HA UI or script)

**Success Criteria:**
- Playlist tracks fetched successfully (10+ tracks)
- Metadata includes all required fields (especially release year)
- Playback initiates within 2 seconds (NFR-P3 target)
- Media player state updates with correct track info
- No HA crashes or errors in logs

**Edge Cases to Document:**
- Tracks without release year data (percentage and handling strategy)
- Playlist with 100+ tracks (pagination requirements)
- Media player already playing (state preservation for later)
- Spotify token expired (error handling and user guidance)
- Invalid playlist URI (validation and error messages)

**Manual Test Steps:**
1. Ensure Spotify integration configured in HA (Settings → Integrations → Spotify)
2. Identify available media player entity ID (Developer Tools → States → media_player.*)
3. Create test playlist in Spotify with 10-20 tracks (varied decades)
4. Deploy updated Beatsy component to HA
5. Restart Home Assistant
6. Run test script: `python tests/poc_spotify_test.py --playlist_uri=<uri> --media_player_entity=<id>`
7. Observe:
   - Console output (track count, metadata samples)
   - HA logs (fetch and playback confirmation)
   - Audio output (verify song plays)
   - Test script output (PASS/FAIL with metrics)
8. Document results in `tests/poc_metrics.json`

**Performance Validation:**
- Playlist fetch: < 5 seconds (AC-1)
- Playback initiation: < 2 seconds (AC-3, NFR-P3)
- Metadata extraction: Immediate (in-memory processing)
- Total test duration: ~30 seconds for full validation

**Metrics to Collect:**
```json
{
  "test": "spotify_integration",
  "status": "PASS",
  "playlist_uri": "spotify:playlist:xxxxx",
  "tracks_fetched": 15,
  "tracks_with_year": 14,
  "tracks_without_year": 1,
  "playback_time_ms": 1850,
  "metadata_fields_present": ["title", "artist", "album", "year", "cover_url"],
  "errors": []
}
```

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-1.md#Story-1.4-Spotify-API-Basic-Integration-Test]
- [Source: docs/epics.md#Story-1.4-Spotify-API-Basic-Integration-Test]
- [Source: docs/architecture.md#Integration-Points - HA Spotify Integration]
- [Source: docs/architecture.md#ADR-003 - Minimal JSON + Runtime Metadata]

**Key Technical Decisions:**
- Use HA's existing Spotify integration (no separate auth)
- Service call pattern for all Spotify operations
- 2-second delay for media player state update
- Filter tracks without year data (document percentage)
- Metadata from runtime state, not stored JSON

**Dependencies:**
- Story 1.1: Component structure and registration (COMPLETE)
- Home Assistant Spotify integration (user must configure)
- Spotify-capable media player entity (user must have hardware)
- Active Spotify account (user prerequisite)

**Home Assistant API References:**
- `hass.services.async_call()` - Service invocation
- `hass.states.get()` - Entity state reading
- `media_player.play_media` - Playback service
- Spotify integration - Existing HA integration (external)

**Spotify API Concepts (accessed via HA):**
- Playlist URI: Unique identifier for playlists
- Track URI: Unique identifier for individual tracks
- Album metadata: Includes release_date field (YYYY-MM-DD format)
- Album images: Array of cover art URLs at different resolutions

**Novel Pattern Validation:**
- **Pattern #3 (Minimal JSON + Runtime Metadata):** This story is THE validation
- Goal: Prove metadata is accessible and complete without storing in JSON
- Risk Mitigation: If metadata insufficient, pivot to full JSON playlists (1 week effort)
- CRITICAL DECISION POINT: This story determines Epic 7 data architecture

**Metadata Extraction Logic:**
```python
# Parse release year from album.release_date
release_date = track["album"]["release_date"]  # "1986-08-18" or "1986"
year = int(release_date.split('-')[0]) if release_date else None

# Select album cover (prefer medium size)
images = track["album"]["images"]
cover_url = images[1]["url"] if len(images) > 1 else images[0]["url"]
```

**Pivot Plan (if Spotify metadata insufficient):**
- Alternative A: Manual JSON playlist files with full metadata
- Alternative B: Direct Spotify Web API (separate auth, more complex)
- Effort: 1 week for JSON approach, 2-3 weeks for direct API
- Decision documented in Story 1.7 (POC Decision Document)

## Change Log

**Story Created:** 2025-11-10
**Author:** Bob (Scrum Master)
**Epic:** Epic 1 - Foundation & Multi-Risk POC
**Story ID:** 1.4
**Status:** review (was ready-for-dev)

**Implementation Completed:** 2025-11-10
**Developer:** Amelia (Dev Agent) / Claude Sonnet 4.5
**Tasks Completed:** 1-7 (Implementation complete, manual testing pending)

**Implementation Summary:**
- Created Spotify helper module with HA coordinator access pattern
- Implemented playlist fetching, metadata extraction, playback, and state reading
- Created POC test script for manual validation
- Updated component init to load and register Spotify helper functions
- All acceptance criteria code complete - manual testing required for validation

### Changes Made

**2025-11-10 - Implementation Complete (Tasks 1-7):**
- ✅ Created `spotify_helper.py` module (295 lines)
  - `fetch_playlist_tracks()`: Fetch playlist via HA Spotify coordinator
  - `extract_track_metadata()`: Parse track data including release year
  - `play_track()`: Initiate playback via media_player.play_media service
  - `get_media_player_metadata()`: Read runtime metadata from player state
  - Helper functions: URI normalization, coordinator access, playlist ID extraction
- ✅ Created `tests/poc_spotify_test.py` test script (335 lines)
  - CLI args: --playlist_uri, --media_player_entity, --output
  - Test sequence: fetch tracks → extract metadata → play → read state
  - JSON metrics output for Story 1.7 documentation
- ✅ Updated `__init__.py` to import and register Spotify helper
  - Functions stored in `hass.data[DOMAIN]["spotify"]`
  - Spotify integration detection with warning if not configured
  - Logging: "Beatsy: Spotify helper loaded"
- ✅ Research completed: Discovered HA Spotify coordinator access pattern
  - Uses `entry.runtime_data.coordinator` from Spotify config entry
  - Client method: `coordinator.client.get_playlist(uri)`
  - No need for separate Spotify auth - leverages existing HA integration

**Tasks 8-10 Status: Manual Testing Required**
- Task 8: Requires deployment to HA with Spotify integration configured
- Task 9: Requires analysis of actual Spotify track metadata (missing years)
- Task 10: Documentation consolidation depends on test results

**Story Status:** Marked as "review" - Implementation complete, ready for manual POC validation testing

**Initial Draft:**
- Created story from Epic 1, Story 1.4 requirements
- Extracted acceptance criteria from tech spec and epics document
- Aligned with architecture patterns (Spotify Integration via HA, ADR-003)
- Incorporated learnings from Story 1.3 (Spotify dependency fix)
- Incorporated learnings from Stories 1.1-1.2 (component foundation, logging)

**Requirements Source:**
- Tech Spec: Validate Spotify API integration can fetch playlists and extract metadata
- Epics: Confirm release year is accessible, playback within 2 seconds
- Architecture: ADR-003 Minimal JSON + Runtime Metadata pattern validation

**Technical Approach:**
- Leverage HA's existing Spotify integration (no separate auth)
- Service call pattern: `hass.services.async_call("media_player", "play_media", ...)`
- Metadata from HA media player state after playback starts (2-second delay)
- Track year extracted from `album.release_date` field
- Filter strategy for tracks without year data (documented for Epic 7)

**Dependencies:**
- Story 1.1 complete: Component loads, `hass.data[DOMAIN]` initialized
- User must have Spotify integration configured in HA (prerequisite)
- User must have Spotify-capable media player entity (hardware requirement)
- No blocking issues from previous stories

**Learnings Applied from Story 1.3:**
- **CRITICAL:** Removed `spotify` from manifest dependencies (resolves load failure)
- Use async service call pattern (same as media player operations)
- Module-level `_LOGGER` logging pattern
- Comprehensive error handling with graceful degradation
- Modern Python 3.11+ type hints throughout

**Learnings Applied from Stories 1.1-1.2:**
- Component initialization pattern (`async_setup`)
- Utility module creation (stateless helper functions)
- HA service call wrapper approach
- Logging: INFO for operations, DEBUG for details, ERROR for failures

**Critical POC Validation:**
- This story validates Novel Pattern #3 (Minimal JSON + Runtime Metadata)
- Success = Epic 7 proceeds with minimal JSON playlist architecture
- Failure = Pivot to full JSON playlists or direct Spotify API (1-3 weeks)
- Decision documented in Story 1.7 (POC Decision Document)

**Future Story Dependencies:**
- Story 1.5: Data registry test (can run in parallel with this story)
- Story 1.6: WebSocket load test (independent of Spotify)
- Epic 7: Music Playback Integration (depends on patterns validated here)

**Novel Patterns Introduced:**
- HA Spotify integration wrapper (no duplicate auth)
- Runtime metadata enrichment from media player state
- 2-second delay pattern for HA state synchronization
- Track filtering strategy for missing year data

## Dev Agent Record

### Context Reference

- docs/stories/1-4-spotify-api-basic-integration-test.context.xml

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

**Task 1 Research Findings:**
- HA's core Spotify integration uses `spotifyaio` library (async Spotify client)
- Coordinator accessible via `entry.runtime_data.coordinator`
- Spotify domain: `"spotify"`
- Playlist fetching: `coordinator.client.get_playlist(uri)` method exists
- No direct service for fetching playlist track lists - must access coordinator
- Implemented helper pattern to access Spotify coordinator from config entries

**Implementation Approach:**
- Created `spotify_helper.py` with functions to access HA's Spotify coordinator
- Wrapper functions avoid duplicate auth - leverage existing HA Spotify integration
- URI normalization supports both `spotify:playlist:xxx` and URL formats
- Error handling includes HomeAssistantError for missing integration/invalid data
- Modern Python 3.11+ type hints throughout (dict[str, Any] pattern)

**Architecture Alignment:**
- ADR-003 validation: Metadata extraction proves runtime metadata pattern viable
- Service call pattern: `hass.services.async_call()` for playback
- 2-second delay pattern documented for media player state sync
- Module-level `_LOGGER` logging (INFO/DEBUG/ERROR levels)

### Completion Notes List

**Tasks 1-7: Implementation Complete ✅**

1. ✅ Research complete - Discovered HA Spotify coordinator access pattern
2. ✅ Created `spotify_helper.py` (295 lines) with all required functions
3. ✅ Metadata extraction with year parsing and album cover URL selection
4. ✅ Playback service call wrapper with error handling
5. ✅ Media player state reader with field validation
6. ✅ Test script created (`tests/poc_spotify_test.py`) - ready for manual execution
7. ✅ Component init updated - Spotify helper loaded and stored in hass.data[DOMAIN]

**Tasks 8-10: Manual Testing Required 🔧**

Tasks 8-10 require manual execution with real Spotify integration:
- Task 8: Manual testing with actual HA instance, Spotify account, and media players
- Task 9: Document missing year data percentage after manual testing
- Task 10: Consolidate findings for Story 1.7 POC Decision Document

**Testing Status:**
- POC test script created and documented
- Manual testing steps documented in story Dev Notes
- Requires deployment to HA and execution with real Spotify playlist
- Test script will output metrics to `tests/poc_metrics.json`

**Implementation Ready for Deployment:**
All code complete and ready for manual POC validation testing. Story marked as review status pending manual test execution by user.

### File List

**New Files Created:**
- `home-assistant-config/custom_components/beatsy/spotify_helper.py` (295 lines)
- `tests/poc_spotify_test.py` (test script, 335 lines)

**Modified Files:**
- `home-assistant-config/custom_components/beatsy/__init__.py`
  - Added Spotify helper imports
  - Stored functions in hass.data[DOMAIN]["spotify"]
  - Added Spotify integration detection with warning if not configured
  - Logged "Beatsy: Spotify helper loaded"
