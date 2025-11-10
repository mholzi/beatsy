# Source Tree Analysis - HA Dashboard

**Project Type:** Home Assistant Configuration
**Repository Type:** Monolith
**Generated:** 2025-11-09

## Overview

This is a comprehensive Home Assistant configuration managing smart home automation, sensors, UI dashboards, and custom integrations.

## Directory Structure

```
home-assistant-config/
├── automations/                    # Automation rules (6 files)
│   ├── covers.yaml                # Window/blind automation
│   ├── lights.yaml                # Lighting automation
│   ├── media.yaml                 # Media control automation
│   ├── motion.yaml                # Motion detection automation
│   ├── notifications.yaml         # Notification automation
│   └── security.yaml              # Security automation
│
├── binary_sensors/                # Binary sensor definitions
│   └── [4 sensor configuration files]
│
├── custom_components/             # Custom Home Assistant components
│   └── beatsy/                    # Custom Beatsy integration
│       └── __init__.py           # Component initialization
│
├── dashboard/                     # Lovelace UI dashboard components
│   ├── buttons/                   # Custom button cards
│   ├── config/                    # Dashboard configuration
│   ├── decluttering/              # Decluttering templates
│   └── lovelace_gen/              # Lovelace generation templates
│
├── input_helpers/                 # Input helpers for UI controls
│   ├── input_boolean.yaml        # Boolean toggles
│   ├── input_datetime.yaml       # Date/time inputs
│   ├── input_number.yaml         # Number inputs
│   ├── input_select.yaml         # Dropdown selects
│   ├── input_text.yaml           # Text inputs
│   ├── timer.yaml                # Timer helpers
│   └── README_ROOM_CONFIG.md     # Room configuration guide
│
├── integrations/                  # Core integration configs
│   ├── frontend.yaml             # Frontend/theme configuration
│   ├── logger.yaml               # Logging configuration
│   └── recorder.yaml             # Database recorder config (optimized)
│
├── python_scripts/                # Custom Python scripts
│   └── sync_room_config.py       # Room configuration sync script
│
├── scripts/                       # Automation scripts (5 files)
│   ├── [5 YAML script files]
│   ├── analyze_entities_vs_dashboard.py  # Entity analysis tool
│   ├── check_thermostat_entities.py      # Thermostat checker
│   └── README.md                  # Scripts documentation
│
├── sensors/                       # Sensor definitions
│   ├── command_line.yaml         # Command-line sensors
│   ├── foxess.yaml               # FoxESS integration sensors
│   ├── sql.yaml                  # SQL-based sensors
│   └── time_date.yaml            # Time/date sensors
│
├── templates/                     # Template sensors
│   └── [Template sensor files]
│
├── configuration.yaml             # Main configuration file (entry point)
├── ui-lovelace.yaml              # Main Lovelace dashboard (201KB)
├── automations.yaml              # Automation loader
├── scenes.yaml                   # Scene definitions
├── shell_commands.yaml           # Shell command definitions
├── secrets.yaml.example          # Secrets template
├── .gitignore                    # Git ignore rules
└── WEBSOCKET_OPTIMIZATION_GUIDE.md  # WebSocket performance guide

```

## Critical Folders Explained

### Configuration Core
- **configuration.yaml**: Entry point - loads all integrations, helpers, sensors
- **integrations/**: Core Home Assistant integration settings
  - Frontend themes and custom modules
  - Recorder with optimized exclusions to reduce database load
  - Logger configuration

### Automation & Logic
- **automations/**: Event-driven automation rules organized by domain
  - Covers (window/blind control)
  - Lights (lighting scenes and triggers)
  - Media (media player automation)
  - Motion (motion sensor responses)
  - Notifications (alert system)
  - Security (alarm and security automation)

- **scripts/**: Reusable automation scripts (5 script files)
- **python_scripts/**: Custom Python logic for advanced automation

### User Interface
- **dashboard/**: Lovelace UI components
  - buttons/: Custom button card definitions
  - decluttering/: Template system for reducing UI code duplication
  - lovelace_gen/: Dynamic dashboard generation
- **ui-lovelace.yaml**: Main dashboard configuration (201KB - comprehensive UI)

### Data & Sensors
- **sensors/**: Sensor integrations
  - Command-line sensors
  - FoxESS solar/battery integration
  - SQL database queries
  - Time/date utilities
- **binary_sensors/**: On/off state sensors
- **templates/**: Template-based calculated sensors

### Input & Control
- **input_helpers/**: UI control elements
  - Booleans, numbers, text, selects, datetimes, timers
  - Used for user input and automation state management

### Extensions
- **custom_components/beatsy/**: Custom integration (likely music/audio related)

## Entry Points

1. **Main Configuration**: `configuration.yaml`
   - Loads all components via `!include` directives
   - Defines core integrations: default_config, lovelace_gen, zha_toolkit

2. **Dashboard**: `ui-lovelace.yaml`
   - Kiosk mode configuration
   - Main UI definition

## Integration Points

- **Frontend ↔ Backend**: Lovelace UI (ui-lovelace.yaml) → Home Assistant Core
- **Automations ↔ Entities**: Automation files trigger actions on sensors/switches/covers
- **Python Scripts ↔ HA**: Python scripts callable from automations
- **Custom Components**: Beatsy integration extends HA functionality

## Key Configuration Files

- `.env`: API credentials (HA_URL, HA_TOKEN)
- `secrets.yaml.example`: Template for sensitive data
- `WEBSOCKET_OPTIMIZATION_GUIDE.md`: Performance optimization documentation
- `recorder.yaml`: Database optimization to reduce WebSocket flooding

## Notes

- Modular structure using `!include` and `!include_dir_merge_list` directives
- Optimized recorder configuration excludes high-frequency sensors
- Kiosk mode support for dedicated display panels
- Custom Beatsy integration for extended functionality
