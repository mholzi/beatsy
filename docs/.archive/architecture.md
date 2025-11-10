# Architecture Documentation - HA Dashboard

**Project:** Home Assistant Configuration
**Type:** Infrastructure (Smart Home Automation Platform)
**Architecture Pattern:** Configuration-Driven Event-Based System
**Generated:** 2025-11-09

## Executive Summary

This Home Assistant configuration implements a comprehensive smart home automation system using a modular, configuration-driven architecture. The system manages lighting, climate control, security, media, and monitoring through event-driven automations, declarative UI dashboards, and custom integrations.

**Key Characteristics:**
- Configuration-as-Code approach with YAML
- Event-driven automation system
- Modular component organization
- Custom integrations via Python
- Optimized for performance (database and WebSocket optimization)

## Technology Stack

| Category | Technology | Version/Details | Purpose |
|----------|-----------|-----------------|----------|
| **Platform** | Home Assistant | Latest | Smart home automation platform |
| **Configuration** | YAML | - | Declarative configuration language |
| **Scripting** | Python | 3.11+ | Custom components and scripts |
| **UI Framework** | Lovelace | - | Dashboard UI system |
| **Custom Components** | lovelace_gen, zha_toolkit, beatsy | Custom | Extended functionality |
| **Frontend Modules** | custom-sidebar | Custom | UI customization |
| **Database** | Recorder (SQLite/PostgreSQL) | Optimized | State history storage |
| **Version Control** | Git | - | Configuration management |

## Architecture Pattern

### Configuration-Driven Event-Based Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant Core                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Event Bus  │←→│ State Engine │←→│ Service Registry │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         ↑                  ↑                    ↑
         │                  │                    │
    ┌────┴────┐      ┌──────┴──────┐      ┌─────┴─────┐
    │         │      │             │      │           │
┌───▼────┐ ┌─▼────┐ │ ┌─────────┐ │  ┌───▼────┐ ┌────▼────┐
│Triggers│ │States│ │ │Sensors  │ │  │Actions │ │Services │
│        │ │      │ │ │         │ │  │        │ │         │
│Motion  │ │Light │ │ │FoxESS   │ │  │Lights  │ │Notific. │
│Time    │ │Cover │ │ │SQL      │ │  │Covers  │ │Scripts  │
│State   │ │Media │ │ │Template │ │  │Climate │ │Python   │
└────────┘ └──────┘ │ └─────────┘ │  └────────┘ └─────────┘
                    │             │
              ┌─────▼─────────────▼─────┐
              │  Recorder (Database)    │
              │  - Optimized exclusions │
              │  - WebSocket optimized  │
              └─────────────────────────┘
                         │
                    ┌────▼────┐
                    │Frontend │
                    │Lovelace │
                    │Dashboard│
                    └─────────┘
```

### Key Architectural Principles

1. **Event-Driven**: Automations react to state changes, time triggers, and events
2. **Declarative Configuration**: System behavior defined via YAML files
3. **Modular Organization**: Logical separation by function (automations, sensors, scripts)
4. **Performance Optimized**: Recorder excludes high-frequency entities
5. **Extensible**: Custom components and Python scripts for advanced logic

## System Components

### 1. Configuration Core

**Entry Point**: `configuration.yaml`

Loads and orchestrates all components:
- Core integrations (default_config, lovelace_gen, zha_toolkit)
- Frontend configuration
- Python scripts
- Recorder (database)
- Logger

Uses `!include` directives for modular loading:
- `!include file.yaml`: Single file inclusion
- `!include_dir_merge_list`: Merge multiple YAML lists
- `!include_dir_merge_named`: Merge named dictionaries

### 2. Automation Layer

**Location**: `automations/`

Event-driven automation rules organized by domain:

| File | Domain | Purpose |
|------|--------|---------|
| `covers.yaml` | Window/Blind Control | Automated cover positioning based on time/sun |
| `lights.yaml` | Lighting | Scene activation, motion-based lighting |
| `media.yaml` | Media Players | Automated media control |
| `motion.yaml` | Motion Detection | Motion sensor response automations |
| `notifications.yaml` | Alerts | Notification triggers and delivery |
| `security.yaml` | Security | Alarm and security automations |

**Automation Structure**:
```yaml
- id: unique_id
  alias: "Human Readable Name"
  trigger:
    - platform: state|time|event
      # trigger conditions
  condition:
    - condition: state|time|numeric_state
      # optional conditions
  action:
    - service: domain.service
      target:
        entity_id: entity.id
      data:
        # service data
```

### 3. Data Layer

#### Sensors (`sensors/`)

| Type | File | Purpose |
|------|------|---------|
| Command-Line | `command_line.yaml` | Execute shell commands for sensor data |
| FoxESS Integration | `foxess.yaml` | Solar/battery system monitoring |
| SQL Queries | `sql.yaml` | Database-driven sensors |
| Time/Date | `time_date.yaml` | Temporal utilities |

#### Binary Sensors (`binary_sensors/`)

On/off state sensors for:
- Motion detection
- Door/window states
- Occupancy detection

#### Template Sensors (`templates/`)

Calculated sensors using Jinja2 templates:
- Aggregate states
- Derived values
- Complex logic

### 4. User Interface Layer

#### Lovelace Dashboard

**Main File**: `ui-lovelace.yaml` (201KB)

Features:
- Kiosk mode support
- Custom button cards
- Decluttering templates for code reuse
- Dynamic generation via lovelace_gen

**Dashboard Structure**:
```
dashboard/
├── buttons/          # Custom button card definitions
├── config/          # Dashboard configuration
├── decluttering/    # Template system (DRY)
└── lovelace_gen/    # Dynamic generation
```

**Kiosk Mode**:
- Configurable header hiding
- Entity-based toggle (input_boolean.kiosk_mode)
- Suitable for wall-mounted tablets

#### Frontend Configuration

**File**: `integrations/frontend.yaml`

- Theme loading (`themes/` directory)
- Custom sidebar module
- Extra JavaScript modules

### 5. Control Layer

#### Input Helpers (`input_helpers/`)

UI control elements providing state management:

| Type | File | Use Case |
|------|------|----------|
| Boolean | `input_boolean.yaml` | Toggle switches (kiosk mode, etc.) |
| DateTime | `input_datetime.yaml` | Time/date pickers |
| Number | `input_number.yaml` | Numeric sliders |
| Select | `input_select.yaml` | Dropdown menus |
| Text | `input_text.yaml` | Text input fields |
| Timer | `timer.yaml` | Countdown timers |

Input helpers enable:
- User configuration via UI
- Stateful automation logic
- Dashboard interactivity

#### Scripts (`scripts/`)

Reusable automation scripts (5 files):
- Callable from automations
- Parameterizable actions
- Sequence-based logic

### 6. Extension Layer

#### Custom Components

**Location**: `custom_components/`

- **beatsy/**: Custom integration (likely music/audio)
  - Python-based Home Assistant integration
  - Extends core functionality

#### Python Scripts

**Location**: `python_scripts/`

- **sync_room_config.py**: Room configuration synchronization
- Callable from automations via `python_script.script_name`

### 7. Data Persistence Layer

#### Recorder Configuration

**File**: `integrations/recorder.yaml`

Optimized database configuration:

**Exclusions** (prevents database bloat):
- Forecast sensors (change frequently)
- Voltage/current/power factor (high-frequency updates)
- Network sensors (constant changes)
- Uptime sensors (continuous incrementing)

**Benefits**:
- Reduced database size
- Lower WebSocket message flooding
- Improved frontend performance

See: `WEBSOCKET_OPTIMIZATION_GUIDE.md` for details

## Data Flow

### 1. Sensor Data Flow

```
Physical Device → Integration → State Engine → Recorder
                                       ↓
                                  Event Bus
                                       ↓
                            Automation Triggers
                                       ↓
                              Action Execution
```

### 2. User Interaction Flow

```
Frontend (Lovelace) → Service Call → Service Registry
                                           ↓
                                    State Change
                                           ↓
                                      Event Bus
                                           ↓
                                  Automation Triggers
```

### 3. Automation Execution Flow

```
Trigger Event → Condition Check → Action Sequence
     ↓                                  ↓
Event Bus                         Service Calls
                                       ↓
                                  State Changes
                                       ↓
                                  Event Bus (loop)
```

## Integration Points

### Internal Integrations

1. **Automations ↔ Entities**
   - Automations read entity states
   - Automations trigger entity actions

2. **Sensors ↔ Recorder**
   - Sensors publish state changes
   - Recorder stores history (selective)

3. **Dashboard ↔ State Engine**
   - Dashboard displays current states
   - Dashboard triggers service calls

4. **Python Scripts ↔ Home Assistant**
   - Bidirectional integration
   - Access to full HA API

### External Integrations

1. **FoxESS Solar/Battery System**
   - Custom sensors in `sensors/foxess.yaml`
   - Monitoring integration

2. **Custom Beatsy Component**
   - Extended functionality
   - Custom entity types

3. **API Access**
   - External scripts via REST API
   - Token authentication (.env)

## Security Architecture

### Authentication & Authorization

- **API Access**: Long-lived access tokens
- **Frontend**: Home Assistant authentication
- **Secrets Management**: `secrets.yaml` (gitignored)

### Configuration Security

- **secrets.yaml**: Excluded from version control
- **secrets.yaml.example**: Template for deployment
- **.env**: API credentials (gitignored)

### Best Practices

1. Never commit secrets to Git
2. Use `!secret` directive for sensitive data
3. Regularly rotate API tokens
4. Restrict API access to trusted networks

## Performance Optimization

### Database Optimization

**Strategy**: Selective recording

**Implementation**: `integrations/recorder.yaml`
- Exclude high-frequency sensors
- Reduce write operations
- Minimize database size

**Impact**:
- Faster queries
- Lower disk I/O
- Reduced frontend latency

### WebSocket Optimization

**Problem**: High-frequency sensor updates flood WebSocket connection

**Solution**: Recorder exclusions prevent update propagation

**See**: `WEBSOCKET_OPTIMIZATION_GUIDE.md`

### Frontend Optimization

**Techniques**:
- Decluttering templates (code reuse)
- Efficient card rendering
- Lazy loading strategies

## Development Workflow

### Configuration Changes

1. Edit YAML files in appropriate directory
2. Validate configuration (UI or CLI)
3. Reload affected component (no full restart)
4. Test functionality
5. Commit to Git

### Adding Automations

1. Add to `automations/[domain].yaml`
2. Reload automations (UI)
3. Test triggers manually
4. Monitor automation traces

### Dashboard Changes

1. Edit `ui-lovelace.yaml` or modular components
2. Clear browser cache
3. Refresh dashboard
4. Validate rendering

## Deployment Architecture

### Hosting

- **Platform**: Home Assistant OS/Core/Supervised
- **Hardware**: Dedicated server/Raspberry Pi
- **Network**: Local network access
- **Remote Access**: Nabu Casa or VPN

### Configuration Deployment

1. Git repository stores configuration
2. Pull latest changes to HA config directory
3. Restart or reload components
4. Monitor logs for errors

### Backup Strategy

- **Git**: Version-controlled configuration files
- **Home Assistant Backups**: Full system snapshots
- **Frequency**: Pre-change backups recommended

## Testing Strategy

### Configuration Validation

- **Built-in Checker**: Home Assistant configuration validation
- **Pre-restart**: Always validate before restart
- **CI/CD**: Could integrate with GitHub Actions

### Manual Testing

- **Developer Tools**: States, services, events
- **Automation Traces**: Debug automation execution
- **Logs**: Monitor for errors and warnings

### Integration Testing

- **Physical Devices**: Test with actual hardware
- **Simulation**: Use input helpers for state simulation
- **Gradual Rollout**: Test new automations in isolation

## Monitoring & Observability

### Logging

**Configuration**: `integrations/logger.yaml`

- Configurable log levels per component
- Debug mode for troubleshooting
- Log rotation

### State Monitoring

- **Developer Tools > States**: Real-time entity states
- **History**: Time-series state history
- **Logbook**: Event timeline

### Performance Monitoring

- **System Health**: CPU, memory, disk usage
- **Database Size**: Monitor growth
- **Integration Status**: Check integration health

## Future Considerations

### Scalability

- Modular structure supports growth
- Database optimization maintains performance
- Add new automations without refactoring

### Extensibility

- Custom component architecture
- Python script integration
- REST API for external systems

### Maintenance

- Version control enables rollback
- Modular structure simplifies updates
- Documentation supports onboarding

## Related Documentation

- [Source Tree Analysis](./source-tree-analysis.md): Detailed directory structure
- [Development Guide](./development-guide.md): Setup and workflow instructions
- [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md): Performance tuning
- [README_ROOM_CONFIG.md](../home-assistant-config/input_helpers/README_ROOM_CONFIG.md): Room configuration
- [scripts/README.md](../home-assistant-config/scripts/README.md): Utility scripts

## Glossary

- **Entity**: Representation of a device, sensor, or service in HA
- **Automation**: Event-driven rule with trigger, condition, action
- **Script**: Reusable action sequence
- **Service**: Callable function to control entities
- **Integration**: Connection to external system or protocol
- **Lovelace**: Dashboard UI framework
- **Recorder**: Database persistence layer
- **Event Bus**: Central event distribution system
