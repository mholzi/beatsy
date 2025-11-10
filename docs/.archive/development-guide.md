# Development Guide - HA Dashboard

**Project:** Home Assistant Configuration
**Type:** Infrastructure (Smart Home Automation)
**Generated:** 2025-11-09

## Prerequisites

### Required Software
- **Home Assistant Core** (or Home Assistant OS/Supervised)
- **Python 3.11+** (for custom Python scripts)
- **Git** (for version control)
- **Text Editor** (VS Code recommended with Home Assistant extension)

### Home Assistant Setup
- Running Home Assistant instance accessible at configured URL
- API Long-Lived Access Token (configured in `.env`)
- HACS (Home Assistant Community Store) for custom components

## Environment Setup

### 1. Clone Configuration

```bash
git clone <repository-url>
cd HA_Dashboard/home-assistant-config
```

### 2. Configure Secrets

Create `secrets.yaml` from template:

```bash
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your actual credentials
```

### 3. Set Up API Access

Create `.env` file in project root:

```bash
# In /Volumes/My Passport/HA_Dashboard/.env
HA_URL=http://your-ha-instance:8123
HA_TOKEN=your-long-lived-access-token
```

**Note:** This token is for external API access (scripts, tools). Do not commit to version control.

## Configuration Structure

### Main Configuration Files

#### Entry Point
- **configuration.yaml**: Main configuration file
  - Loads all integrations, automations, scripts, sensors
  - Uses `!include` directives for modular structure

#### UI Dashboard
- **ui-lovelace.yaml**: Complete Lovelace dashboard (201KB)
  - Kiosk mode settings
  - Card configurations
  - Custom button cards

### Modular Components

#### Automations (automations/)
Organized by functional area:
- `covers.yaml`: Window/blind automation
- `lights.yaml`: Lighting control
- `media.yaml`: Media player automation
- `motion.yaml`: Motion detection responses
- `notifications.yaml`: Alert system
- `security.yaml`: Security automation

#### Scripts (scripts/)
Reusable automation scripts (5 YAML files)
- Use `!include_dir_merge_named` in main config
- Callable from automations or UI

#### Sensors (sensors/)
- `command_line.yaml`: Command-line sensors
- `foxess.yaml`: FoxESS solar/battery sensors
- `sql.yaml`: Database query sensors
- `time_date.yaml`: Time/date utilities

#### Input Helpers (input_helpers/)
UI control elements:
- `input_boolean.yaml`: Toggle switches
- `input_datetime.yaml`: Date/time pickers
- `input_number.yaml`: Number sliders
- `input_select.yaml`: Dropdown menus
- `input_text.yaml`: Text inputs
- `timer.yaml`: Timer controls

## Development Workflow

### Making Changes

1. **Edit Configuration Files**
   ```bash
   # Edit YAML files in appropriate directory
   vim automations/lights.yaml
   ```

2. **Validate Configuration**
   ```bash
   # In Home Assistant UI: Configuration > Server Controls > Check Configuration
   # Or use CLI:
   hass --script check_config -c /config
   ```

3. **Test Changes**
   - Use Home Assistant Developer Tools
   - Test automations manually
   - Check logs for errors

4. **Reload Configuration**
   ```bash
   # Reload specific components (faster):
   # - Automations: Configuration > Automations > ⋮ > Reload Automations
   # - Scripts: Configuration > Scripts > ⋮ > Reload Scripts
   # - Input Helpers: Developer Tools > YAML > Reload Input Helpers

   # Full restart (if needed):
   # Configuration > Server Controls > Restart
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add: description of changes"
   git push
   ```

### Adding New Automations

1. Create YAML file in `automations/` or add to existing file
2. Follow standard automation format:
   ```yaml
   - id: unique_automation_id
     alias: "Descriptive Name"
     trigger:
       - platform: state
         entity_id: sensor.example
     action:
       - service: light.turn_on
         target:
           entity_id: light.example
   ```
3. Reload automations via UI
4. Test trigger conditions

### Adding New Sensors

1. Add sensor to appropriate file in `sensors/`
2. Common sensor types:
   - Template sensors → `templates/`
   - Command-line → `sensors/command_line.yaml`
   - Integration-specific → create new file
3. Reload configuration
4. Verify sensor in Developer Tools > States

### Custom Components

Located in `custom_components/`:
- **beatsy/**: Custom integration
  - `__init__.py`: Component initialization
  - Install via HACS or manual copy
  - Restart required after installation

### Python Scripts

Located in `python_scripts/`:
- `sync_room_config.py`: Room configuration sync

To add new Python script:
1. Create `.py` file in `python_scripts/`
2. Restart Home Assistant
3. Call from automations:
   ```yaml
   service: python_script.your_script_name
   data:
     param1: value
   ```

## Utility Scripts

Located in `scripts/` directory (Python analysis tools):

- **analyze_entities_vs_dashboard.py**: Compare entities vs dashboard usage
- **check_thermostat_entities.py**: Validate thermostat entities

Run scripts:
```bash
cd /Volumes/My\ Passport/HA_Dashboard/home-assistant-config/scripts
python3 analyze_entities_vs_dashboard.py
```

## Configuration Management

### Include Directives

- `!include file.yaml`: Include single file
- `!include_dir_merge_list dir/`: Merge list files from directory
- `!include_dir_merge_named dir/`: Merge named dictionaries
- `!include_dir_list dir/`: Include as list of files

### Lovelace Dashboard

#### Main Dashboard
Edit `ui-lovelace.yaml` for main dashboard changes

#### Modular Components
- **Buttons**: `dashboard/buttons/`
- **Decluttering Templates**: `dashboard/decluttering/`
- **Lovelace Gen**: `dashboard/lovelace_gen/`

#### Kiosk Mode
Configured in `ui-lovelace.yaml`:
```yaml
kiosk_mode:
  non_admin_settings:
    hide_header: true
  entity_settings:
    - entity:
        input_boolean.kiosk_mode: "on"
```

## Performance Optimization

### Database (Recorder)

Optimized in `integrations/recorder.yaml`:
- Excludes high-frequency sensors (voltage, current, network stats)
- Excludes forecast sensors
- Reduces WebSocket message flooding

See: `WEBSOCKET_OPTIMIZATION_GUIDE.md` for details

### Best Practices
1. Exclude noisy sensors from recorder
2. Use template sensors for calculated values
3. Group related automations
4. Use input helpers for stateful automations

## Logging & Debugging

### View Logs
```bash
# In Home Assistant UI:
# Configuration > Logs

# Or via CLI:
tail -f /config/home-assistant.log
```

### Enable Debug Logging

Edit `integrations/logger.yaml`:
```yaml
logs:
  homeassistant.components.automation: debug
  custom_components.beatsy: debug
```

## Testing

### Manual Testing
1. Use Developer Tools > States to monitor entities
2. Developer Tools > Services to test service calls
3. Test automations via trigger simulation

### Validation
- Check Configuration before restart
- Monitor logs for errors
- Test in development environment first

## Common Tasks

### Add New Device
1. Configure device integration via UI
2. Add automation rules to appropriate file
3. Update dashboard if needed
4. Test automation triggers

### Update Custom Component
1. Update via HACS or manual copy
2. Restart Home Assistant
3. Clear browser cache
4. Test functionality

### Backup Configuration
```bash
# Configuration files are in Git
git push

# Full Home Assistant backup:
# Configuration > System > Backups > Create Backup
```

## Troubleshooting

### Configuration Won't Load
1. Check configuration validation
2. Review logs for YAML syntax errors
3. Check file permissions
4. Verify !include paths are correct

### Automation Not Triggering
1. Check automation is enabled
2. Verify trigger conditions
3. Check entity IDs exist
4. Review automation traces (UI)

### Sensor Not Updating
1. Check integration is loaded
2. Verify sensor configuration
3. Check entity is not disabled
4. Review recorder exclusions

## Additional Resources

- [README_ROOM_CONFIG.md](../home-assistant-config/input_helpers/README_ROOM_CONFIG.md): Room configuration guide
- [scripts/README.md](../home-assistant-config/scripts/README.md): Scripts documentation
- [WEBSOCKET_OPTIMIZATION_GUIDE.md](../home-assistant-config/WEBSOCKET_OPTIMIZATION_GUIDE.md): Performance optimization

## API Access

API credentials configured in `.env`:
- **URL**: Home Assistant instance URL
- **Token**: 10-year long-lived access token
- **Use Case**: External scripts, Epic 1 API access for area/label discovery

Example API call:
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
HA_URL = os.getenv('HA_URL')
HA_TOKEN = os.getenv('HA_TOKEN')

headers = {
    'Authorization': f'Bearer {HA_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(f'{HA_URL}/api/states', headers=headers)
```
