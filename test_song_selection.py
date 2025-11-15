#!/usr/bin/env python3
"""
Test script for Story 5.1: Random Song Selection
Run this from Home Assistant Python environment or standalone.

Usage:
  python3 test_song_selection.py
"""

import asyncio
import json
import time
from typing import Dict, Any


async def test_song_selection_websocket():
    """Test song selection via WebSocket commands."""
    try:
        import websockets
    except ImportError:
        print("❌ websockets module not installed")
        print("Install: pip install websockets")
        return

    # Connect to Home Assistant WebSocket
    uri = "ws://homeassistant.local:8123/api/websocket"

    print("🔌 Connecting to Home Assistant WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            # 1. Receive auth_required message
            auth_msg = json.loads(await websocket.recv())
            print(f"✅ Connected: {auth_msg}")

            # 2. Send auth message (you'll need to provide a long-lived access token)
            # Create one at: http://homeassistant.local:8123/profile
            access_token = input("Enter your Home Assistant access token: ").strip()

            await websocket.send(json.dumps({
                "type": "auth",
                "access_token": access_token
            }))

            auth_result = json.loads(await websocket.recv())
            if auth_result.get("type") != "auth_ok":
                print(f"❌ Authentication failed: {auth_result}")
                return

            print("✅ Authenticated successfully")

            # 3. Send next_song command
            print("\n📨 Sending next_song command...")

            command_id = int(time.time() * 1000)
            await websocket.send(json.dumps({
                "id": command_id,
                "type": "beatsy/next_song"
            }))

            # 4. Receive response
            response = json.loads(await websocket.recv())
            print(f"\n📥 Response received:")
            print(json.dumps(response, indent=2))

            if response.get("success"):
                result = response.get("result", {})
                print(f"\n✅ Song selected successfully!")
                print(f"   Round: {result.get('round_number')}")
                print(f"   Title: {result.get('title')}")
                print(f"   Artist: {result.get('artist')}")
            else:
                error = response.get("error", {})
                print(f"\n❌ Error: {error.get('code')}")
                print(f"   Message: {error.get('message')}")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_song_selection_direct():
    """Test song selection directly (requires running in HA context)."""
    print("🧪 Testing song selection directly...")

    try:
        # This would only work if running inside Home Assistant
        from homeassistant.core import HomeAssistant
        from custom_components.beatsy.game_state import (
            select_random_song,
            get_game_state,
            PlaylistExhaustedError
        )

        print("❌ This test requires Home Assistant context")
        print("   Use test_song_selection_websocket() instead")

    except ImportError:
        print("❌ Not running in Home Assistant environment")
        print("   Use Option A (Browser Console) or Option B (pytest) instead")


async def test_multiple_selections():
    """Test multiple song selections to verify no duplicates."""
    print("🎲 Testing multiple selections for duplicates...")
    print("   (This uses WebSocket - requires setup)")

    # Implementation would be similar to test_song_selection_websocket
    # but in a loop to select 10 songs and track URIs

    print("⚠️  Use Option D (pytest tests) for comprehensive duplicate testing")


if __name__ == "__main__":
    print("=" * 60)
    print("Story 5.1: Random Song Selection - Test Script")
    print("=" * 60)
    print()
    print("Select test mode:")
    print("1. WebSocket test (requires HA running + access token)")
    print("2. Direct test (requires HA Python environment)")
    print("3. Multiple selections test (WebSocket)")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(test_song_selection_websocket())
    elif choice == "2":
        test_song_selection_direct()
    elif choice == "3":
        asyncio.run(test_multiple_selections())
    else:
        print("Invalid choice")
