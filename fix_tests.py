#!/usr/bin/env python3
"""Fix test_game_state.py to use new RoundState structure."""

import re

def create_new_round_state(indent, round_number="1", title="Song", artist="Artist", year="2000", status='"active"'):
    """Generate new RoundState instantiation code."""
    return f'''{indent}round_state = RoundState(
{indent}    round_number={round_number},
{indent}    song={{
{indent}        "uri": "spotify:track:123",
{indent}        "title": "{title}",
{indent}        "artist": "{artist}",
{indent}        "album": "Album",
{indent}        "year": {year},
{indent}        "cover_url": "https://example.com/cover.jpg"
{indent}    }},
{indent}    started_at=time.time(),
{indent}    timer_duration=30,
{indent}    status={status},
{indent}    guesses=[]
{indent})'''

# Read the test file
with open('/Volumes/My Passport/HA_Dashboard/tests/test_game_state.py', 'r') as f:
    content = f.read()

# Pattern to match old RoundState instantiations
# This matches:
#   round_state = RoundState(
#       round_number=...,
#       track_uri=...,
#       track_name=...,
#       track_artist=...,
#       correct_year=...,
#       [status=...,]  # optional
#   )

pattern = r'(\s+)round_state = RoundState\(\s+round_number=(\d+),\s+track_uri="[^"]+",\s+track_name="([^"]+)",\s+track_artist="([^"]+)",\s+correct_year=(\d+),(?:\s+status="([^"]+)",)?\s+\)'

def replace_round_state(match):
    indent = match.group(1)
    round_number = match.group(2)
    title = match.group(3)
    artist = match.group(4)
    year = match.group(5)
    status = match.group(6) if match.group(6) else "active"
    return create_new_round_state(indent, round_number, title, artist, year, f'"{status}"')

# Replace all old RoundState instantiations
content = re.sub(pattern, replace_round_state, content)

# Also need to fix guess assertions that use dict access
# Changed from: assert "Alice" in retrieved_round.guesses
# Changed from: assert retrieved_round.guesses["Alice"]["year"] == 1998
# To: Find guess in list

# Write back
with open('/Volumes/My Passport/HA_Dashboard/tests/test_game_state.py', 'w') as f:
    f.write(content)

print("Fixed all RoundState instantiations!")
