# Story 5.2 Testing Guide

## 🎯 What We're Testing

Story 5.2 implements round state initialization with:
- Round number incrementing (1, 2, 3...)
- Song metadata broadcast (WITHOUT year field)
- Timer initialization
- WebSocket round_started events

---

## ✅ Quick Test (5 minutes)

### Prerequisites
1. Home Assistant running with Beatsy v0.1.22
2. Playlist configured (at least 3 songs)
3. At least 1 player connected

### Test Steps

**1. Open Browser Console (F12)**
```javascript
// Connect WebSocket to listen for events
const ws = new WebSocket('ws://localhost:8123/api/websocket');
ws.onopen = () => {
    // Authenticate
    ws.send(JSON.stringify({type: 'auth', access_token: 'YOUR_TOKEN'}));
};
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    // Look for round_started event
    if (data.type === 'beatsy/event' && data.event_type === 'round_started') {
        console.log('🎵 Round Started Event:', data.data);
        console.log('🔒 Year field present?', 'year' in data.data.song);
        console.log('📊 Round number:', data.data.round_number);
    }
};
```

**2. Click "Next Song" in Admin UI**

**3. Verify Console Output:**
```
✅ Round Started Event received
✅ Year field: false (NOT present)
✅ Round number: 1
✅ Song metadata: {title, artist, album, cover_url}
✅ Timer duration: 30
✅ Started timestamp: present
```

**4. Click "Next Song" Again**
```
✅ Round number: 2 (incremented!)
```

**5. Click "Next Song" Third Time**
```
✅ Round number: 3 (continuous increment!)
```

---

## 🔬 Detailed Testing

### Test 1: Round State Structure

**Check Home Assistant Logs:**
```bash
tail -f home-assistant.log | grep "beatsy"
```

**Expected Log Output:**
```
INFO: Round 1 started: 'Song Title' by Artist Name (3 players connected)
DEBUG: Round state: started_at=1699891250.789, timer_duration=30s
```

### Test 2: Security - Year Field Exclusion

**Critical Security Test!**

Open browser DevTools Network tab:
1. Filter for WebSocket messages
2. Click "Next Song"
3. Find the `round_started` event payload
4. **VERIFY:** `song.year` field is NOT present

**Expected Payload:**
```json
{
  "type": "beatsy/event",
  "event_type": "round_started",
  "data": {
    "type": "round_started",
    "song": {
      "uri": "spotify:track:xyz",
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "cover_url": "https://..."
      // NO "year" field!
    },
    "timer_duration": 30,
    "started_at": 1699891250.789,
    "round_number": 1
  }
}
```

### Test 3: Round Number Incrementing

**Python Test Script:**
```python
# Run this in Home Assistant Python shell or as a script

from custom_components.beatsy import game_state

# Get game state
hass = ... # Your hass instance
state = game_state.get_game_state(hass)

print(f"Played songs: {len(state.played_songs)}")
print(f"Current round: {state.current_round.round_number if state.current_round else 'None'}")

# Click "Next Song" in UI, then check again
# Round number should equal len(played_songs)
```

### Test 4: Empty Playlist Error Handling

**Exhaust the playlist:**
1. Click "Next Song" repeatedly until all songs played
2. Click "Next Song" one more time
3. **Expected:** Error message "All songs have been played"
4. **Verify:** No crash, game state intact

### Test 5: Multiple Client Broadcast

**Open 3 browser windows:**
- Window 1: Admin view
- Window 2: Player 1 interface
- Window 3: Player 2 interface

**Steps:**
1. All windows connect to game
2. Admin clicks "Next Song"
3. **Verify:** ALL windows receive round_started event simultaneously
4. **Verify:** All show same song (but NOT the year)

---

## 📱 Manual UI Testing

### What to Verify:

**Admin View:**
- ✅ "Next Song" button works
- ✅ Round number displayed and increments
- ✅ Song title/artist shown
- ✅ Success message after clicking

**Player View:**
- ✅ Screen transitions to "Active Round" view
- ✅ Song title and artist displayed
- ✅ Album cover image shows
- ✅ Year dropdown available (1960-2024)
- ✅ Timer counts down from 30 seconds
- ✅ **Year is NOT pre-filled or visible**

---

## 🧪 API Testing (curl/Postman)

### WebSocket Test (via Python)

Create `test_websocket_5_2.py`:

```python
import asyncio
import json
import websockets

async def test_round_started():
    uri = "ws://localhost:8123/api/websocket"

    async with websockets.connect(uri) as websocket:
        # Receive auth required
        auth_msg = await websocket.recv()
        print(f"< {auth_msg}")

        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": "YOUR_LONG_LIVED_TOKEN"
        }))

        # Receive auth OK
        auth_result = await websocket.recv()
        print(f"< {auth_result}")

        # Subscribe to events (if needed)
        await websocket.send(json.dumps({
            "id": 1,
            "type": "subscribe_events"
        }))

        print("\n✅ Listening for round_started events...")
        print("👉 Now click 'Next Song' in the admin UI\n")

        # Listen for events
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            # Check for round_started
            if (data.get('type') == 'beatsy/event' and
                data.get('event_type') == 'round_started'):

                print("🎵 ROUND STARTED EVENT RECEIVED!")
                print(json.dumps(data, indent=2))

                # Security check
                payload = data['data']
                if 'year' in payload.get('song', {}):
                    print("\n❌ SECURITY VIOLATION: Year field found!")
                else:
                    print("\n✅ SECURITY PASSED: Year field not present")

                print(f"\n📊 Round #{payload['round_number']}")
                print(f"🎵 Song: {payload['song']['title']} by {payload['song']['artist']}")
                print(f"⏱️  Timer: {payload['timer_duration']}s")

                break

asyncio.run(test_round_started())
```

---

## 🐛 Known Issues to Test

### What Should NOT Happen:

- ❌ Year field visible to players
- ❌ Round number resets to 1 between songs
- ❌ Clients don't receive broadcast
- ❌ Crash on empty playlist
- ❌ Timer not initialized

### What SHOULD Happen:

- ✅ Year field hidden from all clients
- ✅ Round numbers increment continuously
- ✅ All connected clients receive event
- ✅ Graceful error on empty playlist
- ✅ Timer starts at configured duration

---

## 📊 Success Criteria

**All these must pass:**

- [ ] Round 1 starts with round_number=1
- [ ] Round 2 has round_number=2 (not reset!)
- [ ] Round 3 has round_number=3
- [ ] Year field NEVER visible in client payloads
- [ ] Song metadata (title, artist, album, cover) present
- [ ] Timer duration matches config (default 30s)
- [ ] All connected clients receive round_started
- [ ] Empty playlist shows error (no crash)
- [ ] Logs show round details with player count

---

## 🔍 Debugging

### Check Game State:

**Via Home Assistant Developer Tools → Template:**
```jinja2
{{ state_attr('beatsy', 'current_round') }}
{{ state_attr('beatsy', 'played_songs') | count }}
```

### Check Logs:

```bash
# Filter for Story 5.2 logs
grep "Round.*started:" home-assistant.log
grep "initialize_round" home-assistant.log
```

### Inspect WebSocket Traffic:

Browser DevTools → Network → WS → Messages tab

Look for:
- `beatsy/event` with `event_type: "round_started"`
- Verify payload structure

---

## ✅ Test Completion Checklist

- [ ] Unit tests passing (8/8)
- [ ] Manual UI test - Round numbers increment
- [ ] Security test - Year field not visible
- [ ] Multi-client test - All receive broadcast
- [ ] Error test - Empty playlist handled
- [ ] Log verification - INFO/DEBUG messages present
- [ ] Integration test - Works with Story 5.1

**If all checked, Story 5.2 is ready for production! 🚀**
