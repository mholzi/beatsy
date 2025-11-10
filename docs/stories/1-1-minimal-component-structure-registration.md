# Story 1.1: Minimal Component Structure & Registration

Status: ready-for-dev

## Story

As a **Home Assistant administrator**,
I want **a minimal Beatsy custom component that loads successfully in HA**,
So that **I can begin testing core architectural assumptions**.

## Acceptance Criteria

**AC-1: Component Registration**
- **Given** Home Assistant Core 2024.1+ is running
- **When** Beatsy component files are placed in `custom_components/beatsy/`
- **Then** HA recognizes the component at startup without errors
- **And** component appears in HA logs as "Beatsy custom component loaded (POC)"

**AC-2: Manifest Compliance (2025 Standards)**
- **Given** `manifest.json` exists in component directory
- **When** HA validates the manifest
- **Then** manifest includes all required 2025 fields:
  - `domain`: "beatsy"
  - `name`: "Beatsy"
  - `version`: "0.1.0-poc"
  - `documentation`: (URL or placeholder)
  - `dependencies`: ["http", "spotify"]
  - `codeowners`: ["@markusholzhaeuser"]
  - `iot_class`: "local_push"
  - `requirements`: []

**AC-3: Component Structure**
- **Given** component directory exists
- **When** HA loads the component
- **Then** the following files are present and valid:
  - `__init__.py` with `async_setup(hass, config)` function
  - `manifest.json` with valid JSON schema
  - `const.py` with `DOMAIN = "beatsy"` constant

**AC-4: Integration Registry**
- **Given** component loaded successfully
- **When** checking HA integrations registry
- **Then** Beatsy appears as registered integration
- **And** no errors or warnings in HA logs

**AC-5: No Performance Impact**
- **Given** component is loaded
- **When** HA is running normally
- **Then** no HA crashes occur
- **And** no performance degradation detected
- **And** HA UI remains responsive

## Tasks / Subtasks

- [ ] Task 1: Create Component Directory Structure (AC: #3)
  - [ ] Create `custom_components/beatsy/` directory in HA config
  - [ ] Verify directory permissions and ownership

- [ ] Task 2: Create manifest.json (AC: #2)
  - [ ] Create `manifest.json` with 2025-compliant fields
  - [ ] Include domain: "beatsy"
  - [ ] Include version: "0.1.0-poc" (required for custom components)
  - [ ] Include dependencies: ["http", "spotify"]
  - [ ] Include iot_class: "local_push"
  - [ ] Include codeowners: ["@markusholzhaeuser"]
  - [ ] Validate JSON syntax

- [ ] Task 3: Create const.py (AC: #3)
  - [ ] Create `const.py` file
  - [ ] Define DOMAIN constant: `DOMAIN = "beatsy"`
  - [ ] Add module docstring

- [ ] Task 4: Create __init__.py with async_setup (AC: #1, #3)
  - [ ] Create `__init__.py` file
  - [ ] Import necessary HA modules (homeassistant.core, logging)
  - [ ] Import DOMAIN from const.py
  - [ ] Implement `async_setup(hass, config)` function
  - [ ] Initialize `hass.data[DOMAIN]` with empty dict
  - [ ] Add INFO log: "Beatsy custom component loaded (POC)"
  - [ ] Return True from async_setup
  - [ ] Add module docstring and type hints

- [ ] Task 5: Deploy and Test Component Loading (AC: #1, #4, #5)
  - [ ] Copy component files to HA config directory
  - [ ] Restart Home Assistant
  - [ ] Check HA logs for "Beatsy custom component loaded (POC)" message
  - [ ] Verify no errors or warnings in logs
  - [ ] Check HA integrations registry for Beatsy entry
  - [ ] Verify HA UI remains responsive after loading
  - [ ] Monitor system resources (no performance degradation)

- [ ] Task 6: Validation and Documentation (AC: #4, #5)
  - [ ] Verify component appears in HA integrations list
  - [ ] Document exact HA version tested
  - [ ] Document component load time from logs
  - [ ] Capture log output showing successful load
  - [ ] Note any warnings or observations for Epic 2

- [ ] Task 7: Update Story 2.7 for 2025 Config Flow Patterns
  - [ ] After Story 1.1 completion, update epics.md Story 2.7
  - [ ] Incorporate modern `async_setup_entry()` pattern
  - [ ] Document config entry vs legacy YAML approach
  - [ ] Note that config flow is now preferred in 2025

## Dev Notes

### Architecture Patterns and Constraints

**Component Registration Pattern (2025):**
- Use `async_setup(hass, config)` for this POC story (simpler validation)
- Modern pattern uses `async_setup_entry()` with config flow (defer to Epic 2)
- All operations must be async/await compatible
- Data storage: `hass.data.setdefault(DOMAIN, {})` pattern

**Manifest.json 2025 Requirements:**
- Custom components **MUST** include `version` field (core integrations don't)
- IoT class designation required: Use `"local_push"` for local network integration
- Dependencies array: Include `["http", "spotify"]` as planned
- Requirements array: Empty for now (no external Python packages yet)

**Component Structure:**
- Location: `/config/custom_components/beatsy/`
- Minimal files for POC: `__init__.py`, `manifest.json`, `const.py`
- No configuration UI, entities, or services in Story 1.1
- Focus: Validate HA accepts our component structure

**From Architecture Document:**
- This establishes the foundation for Novel Pattern #1: Unauthenticated WebSocket access
- Component must not crash or degrade HA performance (NFR-R1: Component Stability)
- Python 3.11+ required, Home Assistant 2024.1+ required

### Testing Standards Summary

**Test Approach:**
- Manual integration test: Deploy to HA, restart, check logs
- Verification points:
  1. Component loads without errors
  2. Log message: "Beatsy custom component loaded (POC)"
  3. Integration appears in HA registry
  4. No crashes or performance issues
  5. HA UI remains responsive

**Success Criteria:**
- Zero errors in HA logs related to Beatsy
- Component visible in Settings → Devices & Services → Integrations
- HA startup completes normally (< 5 seconds component load time per NFR)

### Project Structure Notes

**Expected File Paths:**
```
/config/custom_components/beatsy/
├── __init__.py          # Component registration
├── manifest.json        # HA metadata (2025 compliant)
└── const.py            # Domain constant
```

**Future Structure (Epic 2+):**
- `config_flow.py` - Modern config entry setup (Story 2.7 - needs 2025 update)
- `http_view.py` - HTTP routes (Story 2.5)
- `websocket_api.py` - WebSocket commands (Story 2.6)
- `game_state.py` - State management (Story 2.3)
- `www/` - Static files for web UI (Epic 3+)

**No Conflicts:**
- First story, no existing structure to conflict with
- Creates foundation for all subsequent stories

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-1.md#Story-1.1]
- [Source: docs/epics.md#Story-1.1-Minimal-Component-Structure-Registration]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Web Search - HA Developer Docs 2025]

**Key Technical Decisions:**
- Using legacy `async_setup()` for POC (simpler than config entries)
- Config flow deferred to Epic 2 (Story 2.7 - **ACTION REQUIRED: Update with 2025 patterns**)
- Manifest includes modern 2025 required fields (version, iot_class)
- No YAML configuration needed (all setup via web UI in later epics)

**Dependencies:**
- Home Assistant Core 2024.1+
- Python 3.11+
- Access to HA config directory for deployment

**Action Items for Story 2.7:**
⚠️ **Update Required:** Story 2.7 "Configuration Entry (Optional Setup Flow)" needs updating to reflect 2025 best practices:
- Config entries are now the **preferred** pattern (not optional)
- Document `async_setup_entry()` pattern vs legacy `async_setup()`
- Include modern config flow structure with `ConfigFlow` class
- Reference: [HA Config Entries Docs](https://developers.home-assistant.io/docs/config_entries_index/)

## Change Log

**Story Created:** 2025-11-10
**Author:** Bob (Scrum Master)
**Epic:** Epic 1 - Foundation & Multi-Risk POC
**Story ID:** 1.1
**Status:** drafted (was backlog)

### Changes Made

**Initial Draft:**
- Created story from Epic 1, Story 1.1 requirements
- Extracted acceptance criteria from tech spec and epics document
- Aligned with architecture patterns (Component Structure, Project Structure sections)
- Incorporated 2025 Home Assistant best practices from web research

**2025 Updates Applied:**
- Added `version` field requirement to manifest.json (required for custom components in 2025)
- Added `iot_class` field requirement (modern HA standard)
- Noted modern `async_setup_entry()` pattern for future reference
- Flagged Story 2.7 for update to reflect 2025 config flow patterns

**Technical Decisions:**
- Using simple `async_setup()` for POC validation (not config flow)
- Manifest follows 2025 compliance requirements
- Minimal structure only - no configuration, entities, or services

**Dependencies:**
- None (first story in epic)

**Future Story Updates Required:**
- Story 2.7: Update to reflect config entries as preferred pattern (2025)
- Document modern `async_setup_entry()` and `ConfigFlow` patterns

## Dev Agent Record

### Context Reference

- docs/stories/1-1-minimal-component-structure-registration.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
