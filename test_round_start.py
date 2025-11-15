"""
Test script to trigger round_started event for Story 4.5 testing.
Run this from Home Assistant Python environment.

Usage:
  python3 test_round_start.py
"""

import asyncio
import time
from homeassistant.core import HomeAssistant

async def test_round_started(hass: HomeAssistant):
    """Broadcast a test round_started event to all connected clients."""

    # Import the broadcast function
    from custom_components.beatsy.websocket_api import broadcast_event

    # Create test round data
    test_data = {
        "song": {
            "title": "Livin' on a Prayer",
            "artist": "Bon Jovi",
            "album": "Slippery When Wet",
            "cover_url": "https://i.scdn.co/image/ab67616d0000b273d9194aa18fa4c9362b47464f"
        },
        "timer_duration": 30,
        "started_at": time.time(),
        "round_number": 1
    }

    print("Broadcasting round_started event to all clients...")
    print(f"Song: {test_data['song']['title']} by {test_data['song']['artist']}")
    print(f"Timer: {test_data['timer_duration']} seconds")

    # Broadcast to all connected WebSocket clients
    await broadcast_event(hass, "round_started", test_data)

    print("✅ Event broadcasted successfully!")
    print("Check browser - players should transition to active round view")


if __name__ == "__main__":
    # Note: This requires running in Home Assistant context
    # You may need to adapt this to your HA setup
    print("⚠️  This script needs to run in Home Assistant Python environment")
    print("Recommended: Use browser console test (Option A) for quick testing")
