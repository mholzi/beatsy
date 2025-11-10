# Story 1.2: Serve Static HTML Without Authentication

Status: ready-for-dev

## Story

As a **party guest (player)**,
I want **to access a test HTML page without logging into Home Assistant**,
So that **I can join games with zero friction**.

## Acceptance Criteria

**AC-1: Unauthenticated Access**
- **Given** Beatsy component is loaded in HA
- **When** I navigate to `http://<HA_IP>:8123/api/beatsy/test.html` from any device on local network
- **Then** the page loads successfully without authentication prompt
- **And** accessing the page does NOT require HA login credentials

**AC-2: Page Content**
- **Given** the test page loads
- **When** I view the page content
- **Then** the page displays "Beatsy POC - Unauthenticated Access Test"
- **And** the page renders valid HTML with proper structure

**AC-3: Multi-Device Access**
- **Given** the test page is accessible
- **When** multiple devices access the page simultaneously
- **Then** all devices can load and view the page concurrently
- **And** no authentication prompt appears on any device

**AC-4: HTTP View Registration**
- **Given** Beatsy component initializes
- **When** the HTTP view is registered
- **Then** HA logs confirm view registration: "Test HTTP view registered at /api/beatsy/test.html"
- **And** no errors occur during registration

**AC-5: No HA Impact**
- **Given** the test page is being accessed
- **When** multiple requests are made
- **Then** Home Assistant remains responsive
- **And** no performance degradation detected
- **And** HA UI remains accessible to authenticated users

## Tasks / Subtasks

- [x] Task 1: Research Unauthenticated HTTP Patterns in HA (AC: #1)
  - [x] Research `homeassistant.components.http.HomeAssistantView` class
  - [x] Investigate `requires_auth` parameter or decorator patterns
  - [x] Review HA documentation on public routes (2025 standards)
  - [x] Document exact pattern for bypassing authentication

- [x] Task 2: Create Static HTML Test Page (AC: #2)
  - [x] Create `custom_components/beatsy/www/` directory
  - [x] Create `test.html` with basic HTML structure
  - [x] Add heading: "Beatsy POC - Unauthenticated Access Test"
  - [x] Add visual confirmation elements (timestamp, device info)
  - [x] Add metadata and DOCTYPE declaration
  - [x] Validate HTML structure

- [x] Task 3: Implement HTTP View Handler (AC: #1, #4)
  - [x] Create `custom_components/beatsy/http_view.py` module
  - [x] Import necessary HA HTTP modules (`HomeAssistantView` or alternatives)
  - [x] Implement view class with `requires_auth=False` or equivalent
  - [x] Define route: `/api/beatsy/test.html`
  - [x] Implement GET handler to serve `test.html` content
  - [x] Add proper HTTP headers (Content-Type: text/html)
  - [x] Add INFO log: "Test HTTP view registered at /api/beatsy/test.html"

- [x] Task 4: Register HTTP View in Component Initialization (AC: #4)
  - [x] Update `__init__.py` to import `http_view` module
  - [x] Add HTTP view registration in `async_setup()` function
  - [x] Use `hass.http` API to register the view
  - [x] Ensure registration happens after component data initialization
  - [x] Add error handling for registration failures

- [ ] Task 5: Deploy and Test Unauthenticated Access (AC: #1, #3, #5) **[MANUAL TESTING REQUIRED]**
  - [ ] Deploy updated component files to HA
  - [ ] Restart Home Assistant
  - [ ] Test from laptop browser (logged out of HA)
  - [ ] Test from mobile phone browser (no HA app login)
  - [ ] Test from tablet or second device
  - [ ] Verify no authentication prompt appears
  - [ ] Verify page loads successfully on all devices
  - [ ] Test concurrent access from multiple devices

- [ ] Task 6: Validation and Documentation (AC: #4, #5) **[MANUAL TESTING REQUIRED]**
  - [ ] Verify HA logs show view registration message
  - [ ] Confirm no errors or warnings in HA logs
  - [ ] Monitor HA UI responsiveness during testing
  - [x] Document exact URL pattern used
  - [x] Document HTTP view implementation pattern
  - [ ] Capture successful test results (screenshots optional)
  - [ ] Note any limitations or edge cases discovered

## Dev Notes

### Architecture Patterns and Constraints

**HTTP View Pattern (2025 - CONFIRMED CURRENT):**
- Home Assistant provides `homeassistant.components.http.HomeAssistantView` base class
- Standard pattern requires authentication by default (`requires_auth = True`)
- Use `requires_auth = False` class attribute to bypass authentication
- **2025 Web Research Confirmation:** Pattern actively used in core integrations (Telegram webhook) - NOT deprecated
- **Alternative Available:** Home Assistant webhook component (`/api/webhook/{webhook_id}`) provides unauthenticated endpoints by design
- **Why HTTP View over webhook:** Validates custom endpoint pattern needed for Story 1.3 WebSocket registration
- Novel Pattern #1: Unauthenticated access in HA (validated in this story)

**Static File Serving (2025 Clarification):**
- **Standard HA Pattern:** Files in `/config/www/` served at `/local/` (unauthenticated by default)
- **Custom Component Pattern:** Use `HomeAssistantView` for programmatic serving
- Option A: Custom `HomeAssistantView` subclass (full control, validates pattern for WebSocket)
- Option B: Place files in `/config/www/beatsy/` → access at `/local/beatsy/` (simpler but doesn't validate HTTP view pattern)
- **Recommend:** Option A for POC (explicit control, better logging, validates foundation for Story 1.3)
- This story serves HTML programmatically via HTTP view at `/api/beatsy/test.html`
- Production static files (Epic 3+) may use `/config/www/` for actual game HTML

**Security Considerations (POC):**
- ⚠️ **Intentional security relaxation for POC** - not production-ready
- Unauthenticated access acceptable for local network testing
- No input validation required for static HTML page
- Production implementation (Epic 3+) should use game-based authorization
- Local network only (NFR-S1): Verify test devices on same WiFi as HA

**From Tech Spec (Epic 1):**
- Test endpoint: `GET /api/beatsy/test.html`
- Response: 200 OK (HTML page)
- Authentication: None required (`requires_auth = False`)
- Purpose: Validate unauthenticated HTTP access pattern for player interfaces

**From Architecture Document:**
- Static File Serving decision: Use HA www/ folder mechanism
- Files served at `/local/beatsy/` in production (this POC uses `/api/beatsy/`)
- Component Structure: Add `http_view.py` module to component
- ADR-001: Custom WebSocket vs HA WebSocket API (HTTP view validates first step)

### Learnings from Previous Story

**From Story 1-1-minimal-component-structure-registration (Status: done)**

- **New Files Created**:
  - `custom_components/beatsy/__init__.py` - Component registration with async_setup
  - `custom_components/beatsy/manifest.json` - 2025-compliant HA metadata
  - `custom_components/beatsy/const.py` - Domain constant definition

- **Component Foundation Established**:
  - Component successfully loads in Home Assistant without errors
  - Uses `hass.data[DOMAIN]` pattern for data storage (architecture.md ADR-002)
  - Simple `async_setup()` pattern validated (config flow deferred to Epic 2)

- **2025 Standards Applied**:
  - Manifest includes `version` field (required for custom components)
  - Manifest includes `iot_class: "local_push"` (modern HA standard)
  - Dependencies: `["http", "spotify"]` declared in manifest
  - Modern type hints used (`dict[str, Any]` vs `Dict[str, Any]`)

- **Architectural Pattern**:
  - `hass.data[DOMAIN]` initialized as empty dict for component state
  - Proper logging setup: `_LOGGER = logging.getLogger(__name__)`
  - Async/await pattern established

- **Action Items for This Story**:
  - Leverage existing `hass.http` dependency (already in manifest)
  - Add HTTP view registration after `hass.data[DOMAIN]` initialization
  - Follow established logging pattern for HTTP view registration
  - Maintain async/await consistency

- **Technical Patterns to Reuse**:
  - Import structure: Use `from homeassistant.core import HomeAssistant`
  - Type hints: Use modern Python 3.11+ syntax
  - Logging: Use module-level `_LOGGER` variable
  - Error handling: Return `True`/`False` from setup functions

- **No Blocking Issues**:
  - Component loads successfully and appears in HA integrations registry
  - Foundation is stable for adding HTTP functionality
  - Story 2.7 flagged for future config flow update (not blocking this story)

[Source: stories/1-1-minimal-component-structure-registration.md#Dev-Agent-Record]

### Project Structure Notes

**Expected File Paths:**
```
/config/custom_components/beatsy/
├── __init__.py          # Component registration (EXISTING - from Story 1.1)
├── manifest.json        # HA metadata (EXISTING - includes "http" dependency)
├── const.py            # Domain constant (EXISTING)
├── http_view.py        # NEW - HTTP view handler for test page
└── www/                # NEW - Static files directory
    └── test.html       # NEW - Unauthenticated test page
```

**File Alignment with Architecture:**
- http_view.py → Maps to "Static File Serving" decision in architecture.md
- www/ directory → Standard HA custom component pattern for static assets
- Route `/api/beatsy/test.html` → POC test endpoint (production uses `/local/beatsy/`)

**No Conflicts:**
- Story 1.1 established foundation, no existing HTTP views to conflict with
- Adding new module (`http_view.py`) does not affect existing modules
- www/ directory is new, no existing static files

### Testing Standards Summary

**Test Approach:**
- Manual integration test: Access from multiple devices without HA login
- Verification points:
  1. Page accessible from laptop browser (logged out of HA)
  2. Page accessible from mobile phone (no HA app)
  3. Page accessible from tablet or second device
  4. No authentication prompt appears
  5. Page content displays correctly ("Beatsy POC - Unauthenticated Access Test")
  6. HA logs show view registration message
  7. No errors or performance degradation in HA

**Success Criteria:**
- Zero authentication prompts on any device
- Page loads in < 2 seconds (NFR-P1 target)
- HTTP view registered successfully in HA logs
- All devices can access concurrently without issues

**Edge Cases to Test:**
- Access from device not on local network (should still work for POC)
- Concurrent access from 3+ devices
- HA restart while page is being accessed

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-1.md#Story-1.2]
- [Source: docs/epics.md#Story-1.2-Serve-Static-HTML-Without-Authentication]
- [Source: docs/architecture.md#Static-File-Serving]
- [Source: docs/architecture.md#ADR-001]

**Key Technical Decisions:**
- Using `HomeAssistantView` with `requires_auth=False` for explicit control
- Custom route `/api/beatsy/test.html` for POC testing
- Static HTML page (no JavaScript yet, deferred to Story 1.3)
- Production pattern will use `/local/beatsy/` for static files (Epic 3+)

**Dependencies:**
- Story 1.1: Component structure and registration (COMPLETE)
- Home Assistant Core 2024.1+ (validated in Story 1.1)
- Python 3.11+ (validated in Story 1.1)
- `http` dependency in manifest.json (already declared in Story 1.1)

**Home Assistant API References:**
- `homeassistant.components.http.HomeAssistantView` - Base class for HTTP views
- `hass.http.register_view()` - View registration method
- Alternative: `hass.http.register_static_path()` - Static file serving

**Novel Pattern Validation:**
- Pattern #1: Unauthenticated WebSocket access (this story validates HTTP first step)
- Goal: Prove zero-friction player access is technically feasible
- Risk Mitigation: If authentication bypass fails, pivot to PIN/QR code alternatives (documented in Story 1.7)

## Change Log

**Story Created:** 2025-11-10
**Author:** Bob (Scrum Master)
**Epic:** Epic 1 - Foundation & Multi-Risk POC
**Story ID:** 1.2
**Status:** drafted (was backlog)

### Changes Made

**2025-11-10 - Implementation Complete (Dev Agent):**
- Implemented HTTP view handler with `requires_auth=False` for unauthenticated access
- Created static HTML test page with visual confirmation (timestamp, device info)
- Integrated view registration into component initialization
- All acceptance criteria implementations complete (AC-1 through AC-5)
- Tasks 1-4 complete; Tasks 5-6 pending manual testing on HA instance
- Story halted pending deployment and manual testing (POC testing approach)

**Initial Draft:**
- Created story from Epic 1, Story 1.2 requirements
- Extracted acceptance criteria from tech spec and epics document
- Aligned with architecture patterns (Static File Serving, HTTP View)
- Incorporated learnings from Story 1.1 (component foundation, 2025 standards)

**Requirements Source:**
- Tech Spec: Test endpoint validation for unauthenticated HTTP access
- Epics: Player access without HA login, zero-friction join experience
- Architecture: Static file serving decision, `requires_auth=False` pattern

**Technical Approach:**
- Custom `HomeAssistantView` subclass for explicit control and logging
- www/ directory for static HTML test page
- Route: `/api/beatsy/test.html` (POC pattern)
- Leverages existing `http` dependency from manifest.json (Story 1.1)

**Dependencies:**
- Story 1.1 complete: Component loads, `hass.data[DOMAIN]` initialized
- No blocking issues from previous story
- Foundation stable for adding HTTP functionality

**Learnings Applied from Story 1.1:**
- Use established `hass.data[DOMAIN]` pattern
- Follow module-level `_LOGGER` logging pattern
- Maintain async/await consistency
- Use modern Python 3.11+ type hints
- Leverage existing manifest dependencies (`http`)

**Future Story Dependencies:**
- Story 1.3: Will add WebSocket client to test.html for connectivity test
- Epic 3: Will migrate to production `/local/beatsy/` serving pattern
- Story 2.7: Config flow update (not blocking this story)

**2025-11-10 Update: Web Research Validation:**
- Validated `requires_auth = False` pattern is current and NOT deprecated in HA 2025
- Pattern actively used in core integrations (Telegram webhook confirms best practice)
- Alternative documented: HA webhook component provides unauthenticated endpoints
- Clarified static file serving: Standard HA uses `/config/www/` → `/local/` (not custom component www/)
- Confirmed HTTP view approach is correct choice for validating Story 1.3 WebSocket pattern
- Updated Dev Notes and Context file with 2025 findings and alternative approaches

## Dev Agent Record

### Context Reference

- docs/stories/1-2-serve-static-html-without-authentication.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929 (Sonnet 4.5)

### Debug Log References

**Task 1 Research - HTTP View Pattern (2025-11-10):**

Based on context file and story notes, the `HomeAssistantView` pattern is confirmed as current and not deprecated:
- Pattern: Create view class inheriting from `homeassistant.components.http.HomeAssistantView`
- Set `requires_auth = False` class attribute to bypass authentication
- Define `url` class attribute for the route path
- Define `name` class attribute for view identification
- Implement `async def get(self, request)` for GET requests
- Register using `hass.http.register_view(view_instance)`
- Confirmed in use by core integrations (Telegram webhook)

Alternative approaches considered but not chosen:
- Home Assistant webhook component (`/api/webhook/{webhook_id}`) - simpler but less control
- Standard `/config/www/` → `/local/` pattern - doesn't validate custom HTTP view pattern needed for Story 1.3

Implementation approach:
- Create `http_view.py` module with `BeatsyTestView` class
- Route: `/api/beatsy/test.html`
- Serve static HTML from `custom_components/beatsy/www/test.html`
- Add logging for view registration confirmation

**Implementation Complete (2025-11-10):**

**Deployment Issue Found & Fixed:**
- Initial deployment failed: Component detected but not initialized
- Root cause: Manifest declared `spotify` dependency, but Spotify not configured in HA
- Fix: Removed `spotify` from manifest dependencies (will be re-added in Story 1.4)
- Spotify not needed for Story 1.2 HTTP view testing
- Commit: 418c90bc - "Remove Spotify dependency from manifest (Story 1.2 fix)"

Files created:
- `home-assistant-config/custom_components/beatsy/www/test.html` - Static HTML test page with timestamp and device detection
- `home-assistant-config/custom_components/beatsy/http_view.py` - BeatsyTestView class with `requires_auth=False`

Files modified:
- `home-assistant-config/custom_components/beatsy/__init__.py` - Added HTTP view registration with error handling

Key implementation details:
- View class inherits from `HomeAssistantView` with `requires_auth = False`
- Route: `/api/beatsy/test.html`
- GET handler reads HTML from `www/test.html` and serves with proper Content-Type
- Error handling for file not found (404) and server errors (500)
- Logging: INFO message on successful registration, DEBUG on each request, ERROR on failures
- Registration happens in `async_setup()` after `hass.data[DOMAIN]` initialization

Ready for manual deployment and testing on Home Assistant instance.

### Completion Notes List

**2025-11-10 - Implementation Complete:**
- Created HTTP view handler following HomeAssistantView pattern with `requires_auth=False`
- Static HTML test page created with visual confirmation elements (timestamp, user agent)
- View registration integrated into component initialization with error handling
- All code follows 2025 HA standards: async/await, modern type hints, proper logging
- Pattern validated against context file and architecture decisions
- Ready for manual testing on Home Assistant instance

**Development Status:**
- Implementation: ✅ COMPLETE (Tasks 1-4)
- Manual Testing: ⏸️ PENDING (Tasks 5-6)
- All acceptance criteria dependencies are satisfied by implementation
- Story HALTED per workflow: Manual testing required before marking complete

**Testing Instructions for Markus:**
1. Deploy files to your Home Assistant instance (files are already in home-assistant-config directory)
2. Restart Home Assistant to load the updated component
3. Check HA logs for: "Test HTTP view registered at /api/beatsy/test.html"
4. Test from laptop browser (logged out): `http://<HA_IP>:8123/api/beatsy/test.html`
5. Test from mobile phone browser (no HA app login)
6. Test from tablet or second device
7. Verify no authentication prompt appears on any device
8. Verify page displays "Beatsy POC - Unauthenticated Access Test" with timestamp
9. Test concurrent access from multiple devices
10. Mark Task 5 and Task 6 as complete after successful testing
11. Update story Status to "review" when all tests pass
12. Run `/bmad:bmm:agents:dev *story-done 1.2` after code review to mark story complete

### File List

**New Files:**
- `home-assistant-config/custom_components/beatsy/www/test.html` - Static HTML test page
- `home-assistant-config/custom_components/beatsy/http_view.py` - HTTP view handler

**Modified Files:**
- `home-assistant-config/custom_components/beatsy/__init__.py` - Added HTTP view registration
