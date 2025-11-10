# DashView Migration Plan: Lovelace-gen to React Dashboard

**Project**: HA_Dashboard Migration
**Target**: Modern React-based dashboard with centralized card management and admin panel
**Strategy**: Incremental, parallel migration - existing dashboard remains operational
**Start Date**: 2025-11-10
**Status**: Planning Phase

---

## Executive Summary

This document outlines the migration strategy from the existing Lovelace-gen YAML-based dashboard to a modern React + TypeScript dashboard while maintaining 100% uptime of the existing system. The migration follows a POC-first approach with incremental element-by-element transitions.

### Key Principles

1. **Zero Disruption**: Existing dashboard continues to operate unchanged
2. **Incremental Migration**: Move one component at a time, validate, then proceed
3. **Parallel Development**: New dashboard runs alongside existing one during transition
4. **Validation Gates**: Each phase requires approval before proceeding
5. **Rollback Ready**: Ability to revert at any point without data loss

---

## Current State Analysis

### Existing Architecture

**Location**: `/home-assistant-config/`

```
home-assistant-config/
├── ui-lovelace.yaml (42,671 tokens - main dashboard config)
├── dashboard/
│   ├── config/
│   │   └── room_floor_config.yaml (centralized room-floor mappings)
│   └── lovelace_gen/
│       ├── floor_swipe.yaml (swipeable floor cards)
│       ├── popup_room_combined.yaml (room detail popups)
│       ├── room_control_card.yaml (room control templates)
│       ├── climate_control.yaml (thermostat cards)
│       ├── light_section.yaml (light controls)
│       ├── motion_activity_section.yaml (motion sensors)
│       └── room_header_icons.yaml (room header badges)
```

### Current Components Inventory

| Component Type | Template File | Usage | Complexity |
|---------------|---------------|-------|------------|
| Floor Swipe Cards | floor_swipe.yaml | 3 floors (Erdgeschoss, Keller, Obergeschoss) | Medium |
| Room Cards | room_control_card.yaml | 27 rooms total | High |
| Thermostat Controls | climate_control.yaml | Per-room climate control | Medium |
| Light Sections | light_section.yaml | Room lighting | Medium |
| Motion Sensors | motion_activity_section.yaml | Activity tracking | Low |
| Room Popups | popup_room_combined.yaml | Detail views | High |
| Header Icons | room_header_icons.yaml | Status badges | Low |

### Custom Cards Used

- **button-card**: Room navigation buttons with state
- **css-swipe-card**: Swipeable card containers
- **bubble-card**: Pop-up modal cards
- **decluttering-card**: Template-based card generation

### Room Configuration

**Current Floors**:
- Erdgeschoss (7 rooms): wohnzimmer, kueche, buero, eingangsflur, gaesteklo, esszimmer, toilette
- Keller (7 rooms): waschkeller, partykeller, sauna, kellerflur, serverraum, buero_keller, heizungskeller
- Obergeschoss (9 rooms): elternschlafzimmer, elternbad, kinderzimmer, zimmer_felicia, zimmer_frederik, kinderbad, kinderflur, gaestezimmer, aupair

---

## Target Architecture

### Technology Stack

```
Frontend:   React 19 + TypeScript + Vite
HA Client:  @hakit/core + @hakit/components
Styling:    Tailwind CSS + shadcn/ui
State:      Zustand + TanStack Query
Backend:    Node.js + Express + TypeScript
Database:   PostgreSQL (room/floor config)
DevOps:     Docker + Docker Compose
```

### New Structure

```
dashview/
├── docs/
│   ├── MIGRATION_PLAN.md (this document)
│   ├── ARCHITECTURE.md
│   └── API_SPEC.md
├── frontend/                         # React Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── cards/               # Reusable card components
│   │   │   │   ├── RoomCard/
│   │   │   │   ├── ThermostatCard/
│   │   │   │   ├── LightCard/
│   │   │   │   └── SensorCard/
│   │   │   ├── floors/              # Floor layouts
│   │   │   │   ├── FloorSwipeView/
│   │   │   │   └── FloorGrid/
│   │   │   ├── admin/               # Admin panel
│   │   │   │   ├── RoomEditor/
│   │   │   │   ├── FloorManager/
│   │   │   │   └── EntityMapper/
│   │   │   └── shared/              # Shared components
│   │   ├── hooks/
│   │   │   ├── useHomeAssistant.ts
│   │   │   ├── useRoomConfig.ts
│   │   │   └── useEntity.ts
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Admin.tsx
│   │   │   └── RoomDetail.tsx
│   │   ├── services/
│   │   │   ├── ha-connection.ts
│   │   │   └── api-client.ts
│   │   ├── store/
│   │   │   └── dashboard-store.ts
│   │   └── types/
│   │       ├── room.types.ts
│   │       └── entity.types.ts
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                          # API Server
│   ├── src/
│   │   ├── routes/
│   │   │   ├── rooms.routes.ts
│   │   │   ├── floors.routes.ts
│   │   │   └── entities.routes.ts
│   │   ├── controllers/
│   │   │   ├── room.controller.ts
│   │   │   └── floor.controller.ts
│   │   ├── models/
│   │   │   ├── Room.ts
│   │   │   ├── Floor.ts
│   │   │   └── EntityMapping.ts
│   │   ├── services/
│   │   │   ├── ha-proxy.service.ts
│   │   │   └── config-sync.service.ts
│   │   ├── middleware/
│   │   │   └── auth.middleware.ts
│   │   └── database/
│   │       ├── connection.ts
│   │       └── migrations/
│   ├── package.json
│   └── tsconfig.json
│
├── database/
│   ├── schema.sql
│   └── seeds/
│       └── initial-rooms.sql
│
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
└── scripts/
    ├── migrate-config.ts           # Import from YAML
    └── sync-to-lovelace.ts         # Export to YAML
```

---

## Migration Phases Overview

| Phase | Duration | Scope | Status |
|-------|----------|-------|--------|
| **Phase 0: POC** | 1 week | Single room card + basic admin | 🟡 Current |
| **Phase 1: Foundation** | 2 weeks | Core infrastructure | ⚪ Planned |
| **Phase 2: Floor View** | 2 weeks | Floor swipe cards | ⚪ Planned |
| **Phase 3: Room Details** | 3 weeks | Room popups + controls | ⚪ Planned |
| **Phase 4: Admin Panel** | 2 weeks | Full CRUD for rooms/floors | ⚪ Planned |
| **Phase 5: Migration** | 3 weeks | Element-by-element migration | ⚪ Planned |
| **Phase 6: Cutover** | 1 week | Final testing + transition | ⚪ Planned |

**Total Estimated Duration**: 14 weeks

---

## Detailed Task List

### PHASE 0: PROOF OF CONCEPT (POC)
**Goal**: Validate technology choices with minimal investment
**Duration**: 1 week
**Success Criteria**: Single room card displaying live HA data with basic CRUD

#### Project Setup

- [ ] **[M0.1]** Create dashview directory structure
- [ ] **[M0.2]** ~~Initialize Git repository for dashview~~ (SKIP - using existing HA_Dashboard repo)
- [ ] **[M0.3]** Update root .gitignore to exclude dashview build artifacts (node_modules, dist, .env)
- [ ] **[M0.4]** Initialize frontend (Vite + React + TypeScript)
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [ ] **[M0.5]** Initialize backend (Express + TypeScript)
- [ ] **[M0.6]** Set up ESLint + Prettier for code quality
- [ ] **[M0.7]** Create development environment documentation

#### Home Assistant Integration

- [ ] **[M0.8]** Install @hakit/core and @hakit/components
  ```bash
  npm install @hakit/core @hakit/components
  ```
- [ ] **[M0.9]** Create HA connection service (ha-connection.ts)
- [ ] **[M0.10]** Implement authentication flow
- [ ] **[M0.11]** Test WebSocket connection to Home Assistant
- [ ] **[M0.12]** Create useHomeAssistant hook for entity access
- [ ] **[M0.13]** Test reading entity states (select 1 test room)

#### POC Component: Single Room Card

- [ ] **[M0.14]** Select POC room (recommend: "Wohnzimmer" - has temp/humidity)
- [ ] **[M0.15]** Create RoomCard component structure
- [ ] **[M0.16]** Implement room name display
- [ ] **[M0.17]** Implement room icon (dynamic based on state)
- [ ] **[M0.18]** Display temperature sensor data
- [ ] **[M0.19]** Display humidity sensor data
- [ ] **[M0.20]** Add motion sensor badge/indicator
- [ ] **[M0.21]** Style card to match existing dashboard aesthetic
- [ ] **[M0.22]** Implement active/inactive state styling
- [ ] **[M0.23]** Test real-time updates (change sensor in HA, verify update)

#### Basic Admin Panel (POC)

- [ ] **[M0.24]** Create simple admin page route
- [ ] **[M0.25]** Display hardcoded "Wohnzimmer" config in form
- [ ] **[M0.26]** Implement form to edit room name
- [ ] **[M0.27]** Implement form to change entity mappings (temp/humidity/motion)
- [ ] **[M0.28]** Add "Save" button (localStorage for POC)
- [ ] **[M0.29]** Update RoomCard when config changes
- [ ] **[M0.30]** Validate configuration changes work end-to-end

#### POC Review & Decision

- [ ] **[M0.31]** Document POC findings and issues
- [ ] **[M0.32]** Conduct stakeholder review
- [ ] **[M0.33]** **DECISION GATE**: Proceed with full migration or adjust approach?

---

### PHASE 1: FOUNDATION
**Goal**: Production-ready infrastructure
**Duration**: 2 weeks
**Prerequisite**: POC approved

#### Backend API Setup

- [ ] **[M1.1]** Set up PostgreSQL database (Docker)
- [ ] **[M1.2]** Design database schema (rooms, floors, entity_mappings)
- [ ] **[M1.3]** Create migration scripts
- [ ] **[M1.4]** Implement Room model with TypeORM/Prisma
- [ ] **[M1.5]** Implement Floor model
- [ ] **[M1.6]** Implement EntityMapping model
- [ ] **[M1.7]** Create REST API: GET /api/rooms
- [ ] **[M1.8]** Create REST API: POST /api/rooms
- [ ] **[M1.9]** Create REST API: PUT /api/rooms/:id
- [ ] **[M1.10]** Create REST API: DELETE /api/rooms/:id
- [ ] **[M1.11]** Create REST API: GET /api/floors
- [ ] **[M1.12]** Create REST API: POST /api/floors
- [ ] **[M1.13]** Create REST API: PUT /api/floors/:id
- [ ] **[M1.14]** Write API integration tests
- [ ] **[M1.15]** Add API request validation middleware
- [ ] **[M1.16]** Add error handling middleware

#### Configuration Import

- [ ] **[M1.17]** Create migrate-config.ts script
- [ ] **[M1.18]** Parse room_floor_config.yaml
- [ ] **[M1.19]** Import all 27 rooms to database
- [ ] **[M1.20]** Import 3 floors (Erdgeschoss, Keller, Obergeschoss)
- [ ] **[M1.21]** Import entity mappings (temp, humidity, motion sensors)
- [ ] **[M1.22]** Verify data integrity after import
- [ ] **[M1.23]** Create backup of imported data

#### Frontend Data Layer

- [ ] **[M1.24]** Install TanStack Query for API data fetching
- [ ] **[M1.25]** Create API client service (Axios)
- [ ] **[M1.26]** Create useRooms hook (fetch + cache)
- [ ] **[M1.27]** Create useFloors hook (fetch + cache)
- [ ] **[M1.28]** Create useRoomMutation hook (CRUD operations)
- [ ] **[M1.29]** Set up Zustand store for UI state
- [ ] **[M1.30]** Test data flow: DB → API → Frontend

#### Styling System

- [ ] **[M1.31]** Install Tailwind CSS
- [ ] **[M1.32]** Install shadcn/ui components
- [ ] **[M1.33]** Extract existing dashboard colors to CSS variables
  ```css
  --gray000, --gray200, --gray400, --gray800
  --active-big, --highlight, --green, --black, --white
  --popupBG
  ```
- [ ] **[M1.34]** Create theme configuration file
- [ ] **[M1.35]** Create shared component library structure
- [ ] **[M1.36]** Document design system tokens

#### Docker & DevOps

- [ ] **[M1.37]** Create Dockerfile for frontend
- [ ] **[M1.38]** Create Dockerfile for backend
- [ ] **[M1.39]** Create docker-compose.yml (frontend + backend + postgres)
- [ ] **[M1.40]** Test full stack startup with Docker
- [ ] **[M1.41]** Create development setup documentation
- [ ] **[M1.42]** Create environment variable template (.env.example)

---

### PHASE 2: FLOOR VIEW MIGRATION
**Goal**: Replicate floor swipe card functionality
**Duration**: 2 weeks
**Prerequisite**: Phase 1 complete

#### Floor Swipe Component

- [ ] **[M2.1]** Install Swiper.js or Embla Carousel for React
- [ ] **[M2.2]** Create FloorSwipeView component
- [ ] **[M2.3]** Fetch floor data from API
- [ ] **[M2.4]** Fetch rooms for each floor
- [ ] **[M2.5]** Render swipe container with pagination dots
- [ ] **[M2.6]** Implement swipe gesture navigation
- [ ] **[M2.7]** Style pagination bullets to match existing (gray200/gray400)
- [ ] **[M2.8]** Set card height to 147px (matching current)

#### Enhanced Room Card

- [ ] **[M2.9]** Refactor RoomCard to accept room config as props
- [ ] **[M2.10]** Implement grid layout (name, icon, temp/humidity)
- [ ] **[M2.11]** Style card with 12px border-radius, gray000 background
- [ ] **[M2.12]** Implement 50px circular icon background
- [ ] **[M2.13]** Apply active state color (active-big gradient)
- [ ] **[M2.14]** Apply inactive state color (highlight rgba)
- [ ] **[M2.15]** Format temperature display (XX° with 2.5em font)
- [ ] **[M2.16]** Format humidity display (XX% with 0.3em, 0.7 opacity)
- [ ] **[M2.17]** Implement tap/click navigation to room detail
- [ ] **[M2.18]** Test with all 3 floors

#### Floor-Specific Logic

- [ ] **[M2.19]** Implement Erdgeschoss floor view
- [ ] **[M2.20]** Implement Keller floor view
- [ ] **[M2.21]** Implement Obergeschoss floor view
- [ ] **[M2.22]** Handle rooms with missing sensors gracefully
- [ ] **[M2.23]** Test state updates (motion triggers, temp changes)

#### Responsive Layout

- [ ] **[M2.24]** Test on mobile viewport (match margin_top_mobile: 50px)
- [ ] **[M2.25]** Test on desktop viewport (match margin_top_desktop: 50px)
- [ ] **[M2.26]** Ensure swipe works on touch devices
- [ ] **[M2.27]** Ensure keyboard navigation works

#### Integration Test

- [ ] **[M2.28]** Run both dashboards side-by-side
- [ ] **[M2.29]** Visual comparison: old vs new (screenshot matching)
- [ ] **[M2.30]** Performance test: measure render time
- [ ] **[M2.31]** Test real-time data sync across both dashboards
- [ ] **[M2.32]** **DECISION GATE**: Approve floor view before proceeding

---

### PHASE 3: ROOM DETAIL VIEWS
**Goal**: Replicate popup_room_combined functionality
**Duration**: 3 weeks
**Prerequisite**: Phase 2 complete

#### Modal/Popup System

- [ ] **[M3.1]** Install modal library (Radix UI Dialog or similar)
- [ ] **[M3.2]** Create RoomDetailModal component
- [ ] **[M3.3]** Implement hash-based routing (#wohnzimmer)
- [ ] **[M3.4]** Style modal: background blur (20), shadow opacity (20), bg opacity (88)
- [ ] **[M3.5]** Implement close button
- [ ] **[M3.6]** Add room icon and name to header
- [ ] **[M3.7]** Style header with popupBG variable

#### Room Header Icons

- [ ] **[M3.8]** Create RoomHeaderIcons component
- [ ] **[M3.9]** Display motion sensor badge
- [ ] **[M3.10]** Display temperature badge
- [ ] **[M3.11]** Display humidity badge
- [ ] **[M3.12]** Apply padding-bottom: 16px standardization
- [ ] **[M3.13]** Handle rooms without motion sensors (Eingang, Sauna, Kinderflur)

#### Thermostat Control Cards

- [ ] **[M3.14]** Install or create thermostat control component
- [ ] **[M3.15]** Map to @hakit ClimateCard if available
- [ ] **[M3.16]** Create ThermostatCard component wrapper
- [ ] **[M3.17]** Display current temperature
- [ ] **[M3.18]** Display target temperature
- [ ] **[M3.19]** Implement temperature adjustment controls (+/-)
- [ ] **[M3.20]** Implement mode selector (heat/cool/off)
- [ ] **[M3.21]** Style to match existing thermostat_card.yaml
- [ ] **[M3.22]** Test with Küche climate entity
- [ ] **[M3.23]** Test with Wohnzimmer climate entity
- [ ] **[M3.24]** Test with Büro climate entity

#### Light Control Section

- [ ] **[M3.25]** Create LightSection component
- [ ] **[M3.26]** Implement collapsible/expandable section (title-card-clickable)
- [ ] **[M3.27]** Display light entity state (on/off)
- [ ] **[M3.28]** Implement toggle switch
- [ ] **[M3.29]** Implement brightness slider (if supported)
- [ ] **[M3.30]** Implement color picker (if supported)
- [ ] **[M3.31]** Style to match light_section.yaml
- [ ] **[M3.32]** Test with multiple light entities

#### Motion/Activity Section

- [ ] **[M3.33]** Create MotionActivitySection component
- [ ] **[M3.34]** Display motion sensor history
- [ ] **[M3.35]** Show last motion timestamp
- [ ] **[M3.36]** Style to match motion_activity_section.yaml
- [ ] **[M3.37]** Test real-time motion updates

#### Room-Specific Layouts

- [ ] **[M3.38]** Create room layout system (grid-template-areas)
- [ ] **[M3.39]** Implement Gästeklo layout (licht1, motion, temp)
- [ ] **[M3.40]** Implement Küche layout
- [ ] **[M3.41]** Implement Wohnzimmer layout
- [ ] **[M3.42]** Implement Büro layout
- [ ] **[M3.43]** Create generic fallback layout
- [ ] **[M3.44]** Test all 27 room detail views
- [ ] **[M3.45]** **DECISION GATE**: Approve room details before proceeding

---

### PHASE 4: ADMIN PANEL
**Goal**: Full CRUD interface for room/floor management
**Duration**: 2 weeks
**Prerequisite**: Phase 3 complete

#### Room Management

- [ ] **[M4.1]** Create Admin page layout
- [ ] **[M4.2]** Install React Admin or Refine framework
- [ ] **[M4.3]** Create RoomList component (table view)
- [ ] **[M4.4]** Add search/filter functionality
- [ ] **[M4.5]** Create RoomEditor form component
- [ ] **[M4.6]** Form field: Room name (text input)
- [ ] **[M4.7]** Form field: Room icon (icon picker)
- [ ] **[M4.8]** Form field: Floor assignment (dropdown)
- [ ] **[M4.9]** Form field: Combined sensor entity (entity selector)
- [ ] **[M4.10]** Form field: Temperature sensor (entity selector)
- [ ] **[M4.11]** Form field: Humidity sensor (entity selector)
- [ ] **[M4.12]** Form field: Motion sensor (entity selector)
- [ ] **[M4.13]** Form validation (required fields)
- [ ] **[M4.14]** Implement Create Room functionality
- [ ] **[M4.15]** Implement Edit Room functionality
- [ ] **[M4.16]** Implement Delete Room functionality (with confirmation)
- [ ] **[M4.17]** Test CRUD operations with real room

#### Floor Management

- [ ] **[M4.18]** Create FloorList component
- [ ] **[M4.19]** Create FloorEditor form
- [ ] **[M4.20]** Form field: Floor name
- [ ] **[M4.21]** Form field: Floor order/sequence
- [ ] **[M4.22]** Display room count per floor
- [ ] **[M4.23]** Drag-and-drop room reordering within floor
- [ ] **[M4.24]** Implement Create Floor functionality
- [ ] **[M4.25]** Implement Edit Floor functionality
- [ ] **[M4.26]** Implement Delete Floor functionality (with safeguards)

#### Entity Mapper

- [ ] **[M4.27]** Create EntityMapper component
- [ ] **[M4.28]** Fetch available HA entities via API
- [ ] **[M4.29]** Filter entities by domain (sensor, binary_sensor, climate, light)
- [ ] **[M4.30]** Implement entity search
- [ ] **[M4.31]** Display entity friendly names
- [ ] **[M4.32]** Show entity state preview
- [ ] **[M4.33]** Implement entity assignment to rooms

#### Configuration Export

- [ ] **[M4.34]** Create sync-to-lovelace.ts script
- [ ] **[M4.35]** Export rooms to room_floor_config.yaml format
- [ ] **[M4.36]** Export floors to room_floor_config.yaml format
- [ ] **[M4.37]** Export entity mappings
- [ ] **[M4.38]** Add "Export to YAML" button in admin UI
- [ ] **[M4.39]** Test: export → import to Lovelace → verify
- [ ] **[M4.40]** **DECISION GATE**: Admin panel ready for production use

---

### PHASE 5: ELEMENT-BY-ELEMENT MIGRATION
**Goal**: Migrate all rooms, cards, and features
**Duration**: 3 weeks
**Prerequisite**: Phase 4 complete

#### Pre-Migration Validation

- [ ] **[M5.1]** Backup entire home-assistant-config directory
- [ ] **[M5.2]** Create migration rollback plan
- [ ] **[M5.3]** Document current dashboard performance baseline
- [ ] **[M5.4]** Set up monitoring for both dashboards
- [ ] **[M5.5]** Create user acceptance test checklist

#### Erdgeschoss Migration (7 rooms)

- [ ] **[M5.6]** Migrate Wohnzimmer (already in POC, verify)
- [ ] **[M5.7]** Migrate Küche
- [ ] **[M5.8]** Migrate Büro
- [ ] **[M5.9]** Migrate Eingangsflur
- [ ] **[M5.10]** Migrate Gästeklo
- [ ] **[M5.11]** Migrate Esszimmer
- [ ] **[M5.12]** Migrate Toilette
- [ ] **[M5.13]** Test Erdgeschoss floor swipe end-to-end
- [ ] **[M5.14]** Visual regression test vs. old dashboard

#### Keller Migration (7 rooms)

- [ ] **[M5.15]** Migrate Waschkeller
- [ ] **[M5.16]** Migrate Partykeller
- [ ] **[M5.17]** Migrate Sauna
- [ ] **[M5.18]** Migrate Kellerflur
- [ ] **[M5.19]** Migrate Serverraum
- [ ] **[M5.20]** Migrate Büro Keller
- [ ] **[M5.21]** Migrate Heizungskeller
- [ ] **[M5.22]** Test Keller floor swipe end-to-end
- [ ] **[M5.23]** Visual regression test vs. old dashboard

#### Obergeschoss Migration (9 rooms)

- [ ] **[M5.24]** Migrate Elternschlafzimmer
- [ ] **[M5.25]** Migrate Elternbad
- [ ] **[M5.26]** Migrate Kinderzimmer
- [ ] **[M5.27]** Migrate Zimmer Felicia
- [ ] **[M5.28]** Migrate Zimmer Frederik
- [ ] **[M5.29]** Migrate Kinderbad
- [ ] **[M5.30]** Migrate Kinderflur
- [ ] **[M5.31]** Migrate Gästezimmer
- [ ] **[M5.32]** Migrate Aupair
- [ ] **[M5.33]** Test Obergeschoss floor swipe end-to-end
- [ ] **[M5.34]** Visual regression test vs. old dashboard

#### Special Views

- [ ] **[M5.35]** Analyze Müll (garbage collection) view requirements
- [ ] **[M5.36]** Create GarbageCard component
- [ ] **[M5.37]** Migrate 4 garbage collection cards (abfuhr_index 0-3)
- [ ] **[M5.38]** Test garbage collection view

#### Advanced Features

- [ ] **[M5.39]** Implement washing machine status card (if present)
- [ ] **[M5.40]** Implement dryer status card (if present)
- [ ] **[M5.41]** Migrate any custom sensor cards
- [ ] **[M5.42]** Migrate any media player cards
- [ ] **[M5.43]** Test all interactive features (toggles, sliders, pickers)

#### Performance Optimization

- [ ] **[M5.44]** Implement lazy loading for room detail views
- [ ] **[M5.45]** Optimize bundle size (code splitting)
- [ ] **[M5.46]** Implement service worker for offline support
- [ ] **[M5.47]** Add loading skeletons for better UX
- [ ] **[M5.48]** Measure and optimize First Contentful Paint (FCP)
- [ ] **[M5.49]** Measure and optimize Time to Interactive (TTI)
- [ ] **[M5.50]** **DECISION GATE**: All elements migrated and tested

---

### PHASE 6: CUTOVER & PRODUCTION
**Goal**: Transition to new dashboard as primary
**Duration**: 1 week
**Prerequisite**: Phase 5 complete

#### Final Testing

- [ ] **[M6.1]** Conduct full user acceptance testing (UAT)
- [ ] **[M6.2]** Test on all target devices (mobile, tablet, desktop)
- [ ] **[M6.3]** Test on all target browsers (Chrome, Safari, Firefox)
- [ ] **[M6.4]** Load testing with multiple concurrent users
- [ ] **[M6.5]** Test HA connection resilience (disconnect/reconnect)
- [ ] **[M6.6]** Security audit (authentication, authorization)
- [ ] **[M6.7]** Accessibility audit (WCAG compliance)

#### Documentation

- [ ] **[M6.8]** Write user guide for dashboard navigation
- [ ] **[M6.9]** Write admin guide for room/floor management
- [ ] **[M6.10]** Document API endpoints
- [ ] **[M6.11]** Create developer onboarding guide
- [ ] **[M6.12]** Document deployment process
- [ ] **[M6.13]** Create troubleshooting guide
- [ ] **[M6.14]** Document backup/restore procedures

#### Deployment

- [ ] **[M6.15]** Set up production environment (server/hosting)
- [ ] **[M6.16]** Configure production environment variables
- [ ] **[M6.17]** Set up SSL certificates
- [ ] **[M6.18]** Configure reverse proxy (Nginx/Traefik)
- [ ] **[M6.19]** Deploy backend to production
- [ ] **[M6.20]** Deploy frontend to production
- [ ] **[M6.21]** Deploy database (or use managed service)
- [ ] **[M6.22]** Run production health checks
- [ ] **[M6.23]** Configure monitoring and alerting

#### Cutover

- [ ] **[M6.24]** Announce planned cutover to users
- [ ] **[M6.25]** Create maintenance window
- [ ] **[M6.26]** Final data sync from YAML config
- [ ] **[M6.27]** Point main dashboard link to DashView
- [ ] **[M6.28]** Keep old dashboard accessible (read-only backup)
- [ ] **[M6.29]** Monitor for issues during first 24 hours
- [ ] **[M6.30]** Collect user feedback

#### Post-Cutover

- [ ] **[M6.31]** Address immediate feedback/issues
- [ ] **[M6.32]** Performance tuning based on real usage
- [ ] **[M6.33]** Create post-migration retrospective document
- [ ] **[M6.34]** Archive old dashboard code (do not delete)
- [ ] **[M6.35]** Update HA_Dashboard README with new architecture
- [ ] **[M6.36]** **PROJECT COMPLETE**: Celebrate! 🎉

---

## Coexistence Strategy

### During Migration

**Dual Dashboard Access**:
- **Old Dashboard**: `http://homeassistant.local:8123` (unchanged)
- **New Dashboard**: `http://dashview.local:3000` (development)

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Home Assistant                        │
│                    (Source of Truth)                     │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
              │ WebSocket API             │ WebSocket API
              ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  OLD: Lovelace-gen      │   │  NEW: DashView React    │
│  (YAML-based)           │   │  (Database-backed)      │
└─────────────────────────┘   └───────────┬─────────────┘
                                          │
                              ┌───────────▼─────────────┐
                              │  PostgreSQL              │
                              │  (Room/Floor Config)     │
                              └─────────────────────────┘
```

### Configuration Synchronization

**Phase 4-5 Strategy**:
1. **Primary Source**: DashView database becomes source of truth for room/floor config
2. **Export**: Use `sync-to-lovelace.ts` to export changes back to YAML
3. **Import**: Old dashboard reads exported YAML (maintains compatibility)
4. **Frequency**: Export after each admin change

**Sync Script** (`sync-to-lovelace.ts`):
```bash
# Run after admin changes
npm run sync-to-lovelace

# This updates:
# - home-assistant-config/dashboard/config/room_floor_config.yaml
```

### Rollback Plan

If critical issues arise:

1. **Immediate**: Point users back to old dashboard URL
2. **Data**: No data loss (old YAML files untouched)
3. **Investigation**: Debug new dashboard in isolation
4. **Fix**: Address issues without time pressure
5. **Retry**: Re-attempt cutover when ready

---

## Success Metrics

### Technical Metrics

- **Performance**: New dashboard loads ≤ 2 seconds (3G network)
- **Reliability**: 99.9% uptime
- **Real-time**: Entity updates appear ≤ 500ms after HA state change
- **Bundle Size**: ≤ 500KB initial load (gzipped)
- **Accessibility**: WCAG 2.1 AA compliance

### User Experience Metrics

- **Visual Parity**: 95%+ visual match with old dashboard
- **Feature Parity**: 100% feature coverage
- **User Satisfaction**: Positive feedback from 80%+ of users
- **Admin Efficiency**: Add new room in ≤ 2 minutes (vs manual YAML editing)

### Migration Metrics

- **Zero Data Loss**: All 27 rooms migrated successfully
- **Zero Downtime**: Old dashboard available throughout migration
- **Timeline Adherence**: Complete within 14 weeks ± 2 weeks

---

## Risk Management

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| HA API breaking changes | Low | High | Pin @hakit version, test updates in staging |
| Database corruption | Low | High | Automated daily backups, transaction safety |
| Performance issues on low-end devices | Medium | Medium | Performance budgets, progressive enhancement |
| Card visual discrepancies | High | Low | Pixel-perfect comparison tools, iterative refinement |
| User resistance to change | Medium | Medium | Training, gradual rollout, feedback loop |
| Timeline slippage | Medium | Low | Buffer time, prioritization, scope management |

### Contingency Plans

- **Technical failure**: Rollback to old dashboard (1-hour SLA)
- **Performance issues**: Progressive rollout (power users first)
- **Missing features**: Phased feature deployment
- **User adoption**: Parallel operation extended period

---

## Communication Plan

### Stakeholders

1. **End Users**: Dashboard users (family members, residents)
2. **Administrators**: Room/floor configuration managers
3. **Developers**: Future maintainers of the system
4. **Project Sponsor**: Decision maker for go/no-go

### Communication Schedule

| Phase | Audience | Method | Content |
|-------|----------|--------|---------|
| POC Complete | Sponsor | Email/Demo | Technology validation, proceed decision |
| Phase 1 Complete | All | Announcement | "New dashboard in development" |
| Phase 3 Complete | End Users | Preview Access | "Try the beta dashboard" |
| Pre-Cutover | All | Email | "Cutover date, what to expect" |
| Post-Cutover | All | Announcement | "New dashboard live, feedback requested" |
| 1 Month Post | All | Survey | Satisfaction, issues, feature requests |

---

## Maintenance & Support

### Post-Migration Support Plan

**First Week**:
- Daily monitoring
- Rapid response to issues (< 4 hour SLA)
- Hot-fix deployment capability

**First Month**:
- Weekly check-ins
- Issue tracking and prioritization
- Performance monitoring

**Ongoing**:
- Monthly maintenance window
- Quarterly feature reviews
- Annual technology stack review

### Knowledge Transfer

- [ ] Document codebase architecture
- [ ] Record video tutorials for admin tasks
- [ ] Create developer setup guide
- [ ] Establish code review process
- [ ] Set up CI/CD pipeline for future updates

---

## Appendix

### A. Technology Stack Details

**Frontend Dependencies** (estimated):
```json
{
  "react": "^19.0.0",
  "@hakit/core": "^latest",
  "@hakit/components": "^latest",
  "vite": "^6.0.0",
  "tailwindcss": "^3.4.0",
  "@tanstack/react-query": "^5.0.0",
  "zustand": "^5.0.0",
  "swiper": "^11.0.0",
  "@radix-ui/react-dialog": "^1.0.0"
}
```

**Backend Dependencies**:
```json
{
  "express": "^4.18.0",
  "typescript": "^5.3.0",
  "prisma": "^5.7.0",
  "pg": "^8.11.0",
  "zod": "^3.22.0",
  "dotenv": "^16.3.0"
}
```

### B. Database Schema

```sql
-- See database/schema.sql for full schema
CREATE TABLE floors (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  key VARCHAR(50) UNIQUE NOT NULL,
  display_order INT NOT NULL
);

CREATE TABLE rooms (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  key VARCHAR(50) UNIQUE NOT NULL,
  floor_id INT REFERENCES floors(id),
  icon VARCHAR(50),
  display_order INT
);

CREATE TABLE entity_mappings (
  id SERIAL PRIMARY KEY,
  room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
  entity_type VARCHAR(50) NOT NULL, -- 'combined_sensor', 'temp', 'hum', 'motion'
  entity_id VARCHAR(255) NOT NULL    -- 'sensor.humidity_wohnzimmer_temperature'
);
```

### C. Reference URLs

- **@hakit Documentation**: https://github.com/shannonhochkins/ha-component-kit
- **Home Assistant API**: https://www.home-assistant.io/integrations/api/
- **React 19 Docs**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **shadcn/ui**: https://ui.shadcn.com/

### D. Version Control & Repository

**Git Repository Strategy**:
- **Repository**: Existing `home-assistant-config` GitHub repository (continued use)
- **Branch Strategy**:
  - `main`: Stable, production-ready code (existing Lovelace-gen dashboard)
  - `dashview-poc`: POC development (Phase 0)
  - `dashview-dev`: Main development branch (Phases 1-5)
  - `dashview-staging`: Pre-production testing (Phase 6)
- **Directory Structure**:
  ```
  HA_Dashboard/
  ├── home-assistant-config/    # Existing HA config (unchanged)
  │   ├── ui-lovelace.yaml
  │   └── dashboard/
  └── dashview/                  # New React dashboard (parallel)
      ├── frontend/
      ├── backend/
      └── docs/
  ```

**Commit Strategy**:
- All dashview development commits prefixed with `[DashView]`
- Example: `[DashView] M0.8: Add @hakit/core integration`
- Keep existing HA config commits separate (no prefix changes)

**Issue Tracking**:
- Use GitHub Issues in existing repository
- Label: `dashview` for migration-related issues
- Milestone: `DashView Migration` for tracking progress

### E. Contact & Support

- **Repository**: `home-assistant-config` GitHub repo (same as current)
- **Local Path**: `/Volumes/My Passport/HA_Dashboard/`

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-10 | Claude Code | Initial migration plan created |
| 1.1 | 2025-11-10 | Claude Code | Updated to use existing home-assistant-config GitHub repo |

---

**Next Steps**: Begin Phase 0 (POC) by executing tasks M0.1 through M0.33.

To start, run:
```bash
cd dashview
# Begin with M0.1: Project setup
```
