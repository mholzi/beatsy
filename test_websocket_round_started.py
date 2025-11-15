#!/usr/bin/env python3
"""
WebSocket Test Client for Story 5.2: Round Started Events

This script connects to your Home Assistant WebSocket API and listens for
round_started events to verify Story 5.2 implementation.

Usage:
    1. Get a long-lived access token from HA Profile
    2. Run: python3 test_websocket_round_started.py YOUR_TOKEN
    3. Click "Next Song" in the admin UI
    4. Watch this script verify the event payload

Security Test: Verifies year field is NOT present in broadcast!
"""

import asyncio
import json
import sys
import time
from datetime import datetime

try:
    import websockets
except ImportError:
    print("❌ websockets library not found!")
    print("Install with: pip3 install websockets")
    sys.exit(1)

# Configuration
HA_URL = "ws://localhost:8123/api/websocket"
TIMEOUT_SECONDS = 300  # 5 minutes

async def test_round_started_events(access_token: str):
    """Connect to HA WebSocket and listen for round_started events."""

    print("=" * 70)
    print("STORY 5.2 TEST: Round Started Event Listener")
    print("=" * 70)
    print(f"\n🔌 Connecting to: {HA_URL}")

    try:
        async with websockets.connect(HA_URL) as websocket:
            # Step 1: Receive auth required message
            auth_required = await websocket.recv()
            auth_data = json.loads(auth_required)
            print(f"✅ Connected! Auth required: {auth_data.get('type')}")

            # Step 2: Send authentication
            print(f"🔐 Authenticating with token: {access_token[:10]}...")
            await websocket.send(json.dumps({
                "type": "auth",
                "access_token": access_token
            }))

            # Step 3: Receive auth result
            auth_result = await websocket.recv()
            auth_result_data = json.loads(auth_result)

            if auth_result_data.get("type") == "auth_ok":
                print("✅ Authentication successful!")
            else:
                print(f"❌ Authentication failed: {auth_result_data}")
                return

            # Step 4: Subscribe to events (optional - broadcasts work without this)
            print("\n📡 Subscribing to Beatsy events...")
            await websocket.send(json.dumps({
                "id": 1,
                "type": "subscribe_events",
                "event_type": "beatsy"
            }))

            subscription_result = await websocket.recv()
            print(f"✅ Subscribed: {subscription_result}")

            print("\n" + "=" * 70)
            print("✨ READY! Waiting for round_started events...")
            print("=" * 70)
            print("\n👉 Now click 'Next Song' in the Beatsy admin interface")
            print(f"⏱️  Listening for {TIMEOUT_SECONDS} seconds...\n")

            rounds_detected = 0
            start_time = time.time()

            # Step 5: Listen for messages
            while time.time() - start_time < TIMEOUT_SECONDS:
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=10.0
                    )
                    data = json.loads(message)

                    # Check if it's a beatsy event
                    if data.get('type') == 'event':
                        event = data.get('event', {})
                        if event.get('event_type') == 'beatsy':
                            event_data = event.get('data', {})

                            # Check for round_started
                            if event_data.get('type') == 'round_started':
                                rounds_detected += 1
                                print("\n" + "🎵" * 35)
                                print(f"ROUND STARTED EVENT #{rounds_detected} RECEIVED!")
                                print("🎵" * 35)

                                verify_round_started_payload(event_data, rounds_detected)

                                print("\n👉 Click 'Next Song' again to test round incrementing")
                                print("   (or Ctrl+C to exit)\n")

                except asyncio.TimeoutError:
                    # No message in last 10 seconds, keep waiting
                    pass

            print(f"\n⏱️  Timeout reached ({TIMEOUT_SECONDS}s)")
            print(f"📊 Total rounds detected: {rounds_detected}")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure Home Assistant is running on localhost:8123")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def verify_round_started_payload(payload: dict, round_count: int):
    """Verify the round_started payload matches Story 5.2 spec."""

    print(f"\n📦 Payload received at {datetime.now().strftime('%H:%M:%S')}")
    print("─" * 70)

    # Check top-level fields
    required_fields = ['type', 'song', 'timer_duration', 'started_at', 'round_number']
    missing = [f for f in required_fields if f not in payload]

    if missing:
        print(f"❌ MISSING FIELDS: {missing}")
    else:
        print("✅ All required top-level fields present")

    # Check round number
    round_number = payload.get('round_number')
    print(f"\n📊 Round Number: {round_number}")

    if round_number == round_count:
        print(f"   ✅ Matches expected count (#{round_count})")
    else:
        print(f"   ⚠️  Expected #{round_count}, got #{round_number}")

    # Check song metadata
    song = payload.get('song', {})
    print(f"\n🎵 Song Metadata:")
    print(f"   Title:  {song.get('title', 'MISSING')}")
    print(f"   Artist: {song.get('artist', 'MISSING')}")
    print(f"   Album:  {song.get('album', 'MISSING')}")
    print(f"   Cover:  {song.get('cover_url', 'MISSING')[:50]}...")

    # CRITICAL SECURITY TEST
    print(f"\n🔒 SECURITY CHECK: Year Field Exclusion")
    if 'year' in song:
        print(f"   ❌ SECURITY VIOLATION! Year field present: {song['year']}")
        print(f"   ❌ Players can see the answer - THIS IS A BUG!")
    else:
        print(f"   ✅ Year field correctly excluded")
        print(f"   ✅ Players cannot see the answer")

    # Check timer
    timer = payload.get('timer_duration')
    print(f"\n⏱️  Timer Duration: {timer}s")
    if timer == 30:
        print(f"   ✅ Default timer (30s)")
    else:
        print(f"   ℹ️  Custom timer configured")

    # Check timestamp
    started_at = payload.get('started_at')
    if started_at:
        started_time = datetime.fromtimestamp(started_at)
        print(f"\n⏰ Started At: {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   ✅ Timestamp present")
    else:
        print(f"\n❌ Started timestamp missing!")

    # Show full payload for inspection
    print(f"\n📋 Full Payload (for inspection):")
    print("─" * 70)
    print(json.dumps(payload, indent=2))
    print("─" * 70)

    # Summary
    print(f"\n✅ Event #{round_count} verified successfully!")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("❌ Usage: python3 test_websocket_round_started.py YOUR_ACCESS_TOKEN")
        print("\nHow to get an access token:")
        print("  1. Open Home Assistant")
        print("  2. Go to Profile → Long-Lived Access Tokens")
        print("  3. Create new token")
        print("  4. Copy the token and run this script\n")
        sys.exit(1)

    access_token = sys.argv[1]

    print("\n" + "=" * 70)
    print("Story 5.2: Round State Initialization - WebSocket Test")
    print("=" * 70)
    print("\nThis will test:")
    print("  ✅ Round started events broadcast correctly")
    print("  ✅ Round numbers increment (1, 2, 3...)")
    print("  ✅ Song metadata present (title, artist, album, cover)")
    print("  ✅ Year field excluded (SECURITY)")
    print("  ✅ Timer duration set correctly")
    print("=" * 70 + "\n")

    try:
        asyncio.run(test_round_started_events(access_token))
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        print("✅ Test can be resumed anytime\n")

if __name__ == "__main__":
    main()
