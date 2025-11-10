# HA Dashboard - Project Documentation Index

**Generated:** 2025-11-09
**Project:** Home Assistant Configuration
**Type:** Infrastructure (Smart Home Automation)
**Scan Level:** Deep

---

## Project Overview

- **Type:** Monolith (single cohesive configuration)
- **Primary Language:** YAML + Python
- **Architecture:** Configuration-Driven Event-Based System
- **Components:** 6 automations, 5 scripts, custom integrations
- **Dashboard Size:** 201KB Lovelace UI

---

## Quick Reference

**Tech Stack:**
- Home Assistant (YAML Configuration)
- Python 3.11+ (Custom Scripts)
- Lovelace Dashboard
- Custom Components: lovelace_gen, zha_toolkit, beatsy

**Entry Point:** `home-assistant-config/configuration.yaml`

**Architecture Pattern:** Event-driven automation with declarative configuration

**Key Features:**
- Automated lights, covers, climate, security
- FoxESS solar/battery integration
- Kiosk mode dashboard
- Performance optimized (recorder/WebSocket)

---

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md)
  - Executive summary
  - Tech stack and architecture type
  - Component inventory
  - Key features and statistics

- [Architecture](./architecture.md)
  - System design and patterns
  - Technology stack details
  - Data flow diagrams
  - Integration points
  - Performance optimization strategies

- [Source Tree Analysis](./source-tree-analysis.md)
  - Complete directory structure
  - Critical folders explained
  - Entry points documented
  - Integration points mapped

- [Development Guide](./development-guide.md)
  - Prerequisites and setup
  - Environment configuration
  - Development workflow
  - Adding automations, sensors, scripts
  - Testing and debugging
  - Common tasks and troubleshooting

---

## Existing Documentation

### User Guides

- [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md)
  - WebSocket performance optimization
  - Recorder configuration best practices
  - Database load reduction techniques

- [README_ROOM_CONFIG.md](../home-assistant-config/input_helpers/README_ROOM_CONFIG.md)
  - Room configuration guide
  - Input helper setup

- [scripts/README.md](../home-assistant-config/scripts/README.md)
  - Utility scripts documentation
  - Usage instructions for analysis tools

---

## Getting Started

### Quick Start

1. **Understand the System**
   - Start with [Project Overview](./project-overview.md)
   - Review [Architecture](./architecture.md) for design patterns

2. **Navigate the Code**
   - Use [Source Tree Analysis](./source-tree-analysis.md) to understand structure
   - Entry point: `home-assistant-config/configuration.yaml`

3. **Set Up Development**
   - Follow [Development Guide](./development-guide.md)
   - Configure `.env` and `secrets.yaml`
   - Validate configuration before changes

### For AI-Assisted Development

When using this documentation with AI assistants (BMad PRD workflow, etc.):

**Primary Reference**: This index.md file provides comprehensive navigation

**For PRD Creation**:
- Reference [Architecture](./architecture.md) for technical constraints
- Use [Source Tree Analysis](./source-tree-analysis.md) for code locations
- Check [Development Guide](./development-guide.md) for workflow requirements

**For Implementation**:
- Follow modular structure (automations/, sensors/, etc.)
- Maintain configuration-driven approach
- Use existing patterns from architecture docs

---

## Documentation by Task

### Planning New Features
1. [Project Overview](./project-overview.md) - Understand current capabilities
2. [Architecture](./architecture.md) - Technical constraints and patterns
3. [Source Tree Analysis](./source-tree-analysis.md) - Where to add code

### Development
1. [Development Guide](./development-guide.md) - Setup and workflow
2. [Architecture](./architecture.md) - Design patterns to follow
3. Existing docs - Domain-specific guides

### Troubleshooting
1. [Development Guide](./development-guide.md#troubleshooting) - Common issues
2. [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md) - Performance issues
3. Home Assistant logs - Runtime errors

### Understanding System
1. [Architecture](./architecture.md) - How it works
2. [Source Tree Analysis](./source-tree-analysis.md) - What's where
3. [Project Overview](./project-overview.md) - What it does

---

## Key Configuration Files

### Entry Points
- `home-assistant-config/configuration.yaml` - Main configuration
- `home-assistant-config/ui-lovelace.yaml` - Dashboard UI (201KB)

### Automation
- `home-assistant-config/automations/` - 6 automation files by domain
- `home-assistant-config/scripts/` - 5 reusable scripts

### Data
- `home-assistant-config/sensors/` - Sensor integrations (FoxESS, SQL, etc.)
- `home-assistant-config/templates/` - Template sensors
- `home-assistant-config/binary_sensors/` - On/off sensors

### UI & Control
- `home-assistant-config/dashboard/` - Dashboard components
- `home-assistant-config/input_helpers/` - UI control elements

### Extensions
- `home-assistant-config/custom_components/beatsy/` - Custom integration
- `home-assistant-config/python_scripts/` - Custom Python logic

### Configuration
- `home-assistant-config/integrations/` - Core integration configs
  - `frontend.yaml` - Themes and custom modules
  - `recorder.yaml` - Optimized database settings
  - `logger.yaml` - Logging configuration

---

## System Architecture Highlights

### Architecture Pattern
**Configuration-Driven Event-Based System**

```
Triggers (Motion, Time, State)
    ↓
Event Bus
    ↓
Automations (Conditions + Actions)
    ↓
Service Calls
    ↓
State Changes
    ↓
Frontend Updates + Recorder Storage
```

### Key Architectural Principles
1. **Event-Driven**: Automations react to state/time/event triggers
2. **Declarative**: System behavior defined via YAML
3. **Modular**: Logical separation by function
4. **Optimized**: Recorder excludes high-frequency entities
5. **Extensible**: Custom components and Python scripts

---

## Component Inventory

| Component Type | Count | Location |
|----------------|-------|----------|
| Automations | 6 files | `automations/` |
| Scripts | 5 files | `scripts/` |
| Sensor Types | 4+ | `sensors/`, `templates/`, `binary_sensors/` |
| Input Helpers | 6 types | `input_helpers/` |
| Custom Components | 1 | `custom_components/beatsy/` |
| Python Scripts | 3 | `python_scripts/`, `scripts/*.py` |
| Dashboard | 1 (201KB) | `ui-lovelace.yaml` |

---

## Integration Points

### Internal
- Automations ↔ Entities (triggers and actions)
- Sensors ↔ Recorder (state persistence)
- Dashboard ↔ State Engine (real-time updates)
- Python Scripts ↔ HA Core (extended logic)

### External
- FoxESS Solar/Battery System (energy monitoring)
- Custom Beatsy Component (extended functionality)
- REST API (external script access via .env)

---

## Performance Optimizations

- **Database**: Selective recording excludes high-frequency entities
- **WebSocket**: Optimized to reduce message flooding
- **UI**: Decluttering templates minimize code duplication

See: [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md)

---

## Version Control

- **Git Repository**: All configuration files tracked
- **Secrets Management**: `secrets.yaml` and `.env` gitignored
- **Template**: `secrets.yaml.example` provided

---

## Project Statistics

- **Project Type**: Infrastructure (Home Assistant Configuration)
- **Repository Type**: Monolith
- **Automation Files**: 6
- **Script Files**: 5
- **Sensor Integrations**: 4+ types
- **Input Helpers**: 6 types
- **Custom Components**: 1
- **Dashboard Size**: 201KB
- **Documentation Files**: 7 total (3 existing + 4 generated)

---

## Additional Resources

### Home Assistant Resources
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Lovelace UI Documentation](https://www.home-assistant.io/lovelace/)
- [Automation Documentation](https://www.home-assistant.io/docs/automation/)

### Project-Specific
- Configuration: `/Volumes/My Passport/HA_Dashboard/home-assistant-config`
- Documentation: `/Volumes/My Passport/HA_Dashboard/docs`
- BMM Workflow Status: `docs/bmm-workflow-status.yaml`

---

## Next Steps

### For New Features
1. Review [Architecture](./architecture.md) for technical approach
2. Create PRD using BMM workflow (reference this index)
3. Follow [Development Guide](./development-guide.md) for implementation

### For Modifications
1. Check [Source Tree Analysis](./source-tree-analysis.md) for file locations
2. Follow [Development Guide](./development-guide.md) workflow
3. Validate configuration before restart

### For Learning
1. Read [Project Overview](./project-overview.md) for high-level understanding
2. Study [Architecture](./architecture.md) for deep technical details
3. Explore existing docs for domain-specific knowledge

---

**Last Updated:** 2025-11-09
**Documentation Version:** 1.0
**Scan Type:** Deep Scan
**Project Owner:** Markus
