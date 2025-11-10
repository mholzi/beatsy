# Project Overview - HA Dashboard

**Generated:** 2025-11-09
**Project Type:** Home Assistant Configuration (Infrastructure)
**Repository Type:** Monolith

## Executive Summary

HA Dashboard is a comprehensive Home Assistant configuration project that manages a complete smart home automation system. The project implements event-driven automation, custom integrations, and a sophisticated Lovelace dashboard UI for controlling lights, climate, security, media, and monitoring systems.

## Project Purpose

This Home Assistant configuration provides:
- **Smart Home Automation**: Automated control of lights, covers, climate, and media
- **Security Monitoring**: Motion detection, security automations, and alerts
- **Energy Management**: FoxESS solar/battery system integration
- **Custom Dashboard**: Optimized Lovelace UI with kiosk mode support
- **Extensibility**: Custom components and Python scripts for advanced functionality

## Tech Stack Summary

| Category | Technologies |
|----------|-------------|
| **Platform** | Home Assistant (YAML Configuration) |
| **Scripting** | Python 3.11+ |
| **UI** | Lovelace Dashboard Framework |
| **Custom Integrations** | lovelace_gen, zha_toolkit, beatsy |
| **Database** | Recorder (Optimized SQLite/PostgreSQL) |
| **Version Control** | Git |

## Architecture Type Classification

**Pattern**: Configuration-Driven Event-Based System

The system uses:
- Declarative YAML configuration
- Event-driven automation triggers
- Modular component organization
- State-based logic with input helpers
- Custom Python extensions

## Repository Structure

**Type**: Monolith (Single cohesive configuration)

**Primary Structure**:
```
HA_Dashboard/
├── home-assistant-config/    # Main Home Assistant configuration
│   ├── configuration.yaml   # Entry point
│   ├── ui-lovelace.yaml    # Dashboard (201KB)
│   ├── automations/        # 6 automation files (by domain)
│   ├── scripts/            # 5 reusable scripts
│   ├── sensors/            # 4 sensor integration files
│   ├── dashboard/          # UI components and templates
│   ├── input_helpers/      # 6 input helper types
│   ├── custom_components/  # beatsy custom integration
│   └── python_scripts/     # Custom Python logic
└── docs/                   # Project documentation (this folder)
```

## Key Features

### 1. Modular Automation System
- **6 automation categories**: covers, lights, media, motion, notifications, security
- Event-driven triggers (state changes, time, events)
- Conditional logic
- Organized by functional domain

### 2. Comprehensive Dashboard
- **201KB Lovelace configuration**
- Kiosk mode for wall-mounted displays
- Custom button cards
- Decluttering templates for code reuse
- Dynamic generation with lovelace_gen

### 3. Sensor Integration
- **FoxESS**: Solar and battery monitoring
- **SQL Sensors**: Database-driven data
- **Command-Line Sensors**: System metrics
- **Template Sensors**: Calculated values

### 4. Performance Optimized
- Database recorder excludes high-frequency entities
- WebSocket optimization reduces message flooding
- See: `WEBSOCKET_OPTIMIZATION_GUIDE.md`

### 5. Custom Extensions
- **beatsy**: Custom Home Assistant component
- **Python Scripts**: sync_room_config.py and analysis tools
- **API Access**: External script integration

## Component Inventory

### Automations (6 files)
- Covers (window/blind control)
- Lights (scene activation, motion-based)
- Media (player automation)
- Motion (detection responses)
- Notifications (alert system)
- Security (alarm and monitoring)

### Scripts (5 YAML files)
- Reusable automation sequences
- Callable from automations or UI

### Sensors
- 4 sensor integration files
- Binary sensors for on/off states
- Template sensors for calculations

### Input Helpers (6 types)
- Booleans, Numbers, Text, Selects, DateTimes, Timers
- Enable UI-based configuration and stateful automations

### Dashboard Components
- Custom buttons
- Decluttering templates
- Lovelace generation templates
- Main dashboard: ui-lovelace.yaml (201KB)

## Entry Points

### Main Configuration
**File**: `home-assistant-config/configuration.yaml`
- Loads all integrations and components
- Uses `!include` directives for modularity
- Configures core services (recorder, logger, frontend)

### Dashboard
**File**: `home-assistant-config/ui-lovelace.yaml`
- Primary user interface
- Kiosk mode configuration
- Card and view definitions

## Integration Points

### Internal
- **Automations ↔ Entities**: Triggers and actions
- **Sensors ↔ Recorder**: State persistence
- **Dashboard ↔ State Engine**: Real-time updates
- **Python Scripts ↔ HA Core**: Extended logic

### External
- **FoxESS Solar/Battery System**: Energy monitoring
- **Custom Beatsy Component**: Extended functionality
- **REST API**: External script access (via .env credentials)

## Getting Started

### For Development
See: [Development Guide](./development-guide.md)

Key steps:
1. Clone repository
2. Configure `secrets.yaml` and `.env`
3. Validate configuration
4. Reload/restart Home Assistant
5. Test changes

### For Understanding the System
See: [Architecture Documentation](./architecture.md)

### For Source Code Navigation
See: [Source Tree Analysis](./source-tree-analysis.md)

## Project Statistics

- **Automation Files**: 6
- **Script Files**: 5
- **Sensor Files**: 4 + templates + binary sensors
- **Input Helper Types**: 6
- **Custom Components**: 1 (beatsy)
- **Python Scripts**: 1 (sync) + 2 (analysis tools)
- **Dashboard Size**: 201KB (ui-lovelace.yaml)
- **Documentation Files**: 3 existing + AI-generated docs

## Performance Characteristics

### Optimizations
- **Database**: Selective recording via exclusions
- **WebSocket**: Reduced message flooding
- **UI**: Decluttering templates minimize duplication

### Resource Usage
- Optimized for single-board computers (Raspberry Pi compatible)
- Database grows slowly due to exclusions
- Efficient automation execution

## Maintenance

### Version Control
- Git repository for all configuration files
- `.gitignore` for secrets and sensitive data
- `secrets.yaml.example` as template

### Documentation
- Inline YAML comments
- README files in key directories
- WebSocket optimization guide
- Room configuration guide

### Backup Strategy
- Git commits for configuration changes
- Home Assistant built-in backup system
- Pre-change validation

## Related Documentation

### Generated Documentation
- [Architecture](./architecture.md): System design and patterns
- [Development Guide](./development-guide.md): Setup and workflow
- [Source Tree Analysis](./source-tree-analysis.md): Directory structure

### Existing Documentation
- [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md): Performance tuning
- [README_ROOM_CONFIG.md](../home-assistant-config/input_helpers/README_ROOM_CONFIG.md): Room configuration
- [scripts/README.md](../home-assistant-config/scripts/README.md): Utility scripts

### Master Index
- [index.md](./index.md): Complete documentation navigation

## Contact & Support

- **Project Owner**: Markus
- **Configuration Location**: `/Volumes/My Passport/HA_Dashboard/home-assistant-config`
- **Documentation Location**: `/Volumes/My Passport/HA_Dashboard/docs`

## Next Steps

1. **For New Features**: Plan changes using PRD workflow
2. **For Modifications**: Follow development guide
3. **For Troubleshooting**: Check logs and automation traces
4. **For Learning**: Review architecture documentation
