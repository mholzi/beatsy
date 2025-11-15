#!/usr/bin/env python3
"""Comprehensive fix for test_game_state.py Story 5.2 structure."""

import re

# Read the file
with open('/Volumes/My Passport/HA_Dashboard/tests/test_game_state.py', 'r') as f:
    content = f.read()

# Fix all the extra blank lines that were added
content = re.sub(r'\n{3,}', '\n\n', content)

# Fix guess assertions that use dict access -> list access
# Pattern: assert retrieved_round.guesses["Alice"]["bet"] is True
content = re.sub(
    r'assert retrieved_round\.guesses\["([^"]+)"\]\["bet"\] is True',
    r'''alice_guess = next((g for g in retrieved_round.guesses if g.get("player_name") == "\1"), None)
    assert alice_guess is not None
    assert alice_guess["bet"] is True''',
    content
)

# Fix test_update_bet patterns
content = re.sub(
    r'assert retrieved_round\.guesses\["([^"]+)"\]\["bet"\] is False',
    r'''guess = next((g for g in retrieved_round.guesses if g.get("player_name") == "\1"), None)
    assert guess is not None
    assert guess["bet"] is False''',
    content
)

# Fix test_round_operations_performance - uses track_uri etc
# Pattern 1: Performance test RoundState creation
perf_pattern = r'''for i in range\(100\):
        round_state = RoundState\(
            round_number=i,
            track_uri=f"spotify:track:\{i\}",
            track_name=f"Song \{i\}",
            track_artist=f"Artist \{i\}",
            correct_year=2000 \+ i,
        \)'''

perf_replacement = '''for i in range(100):
        round_state = RoundState(
            round_number=i,
            song={
                "uri": f"spotify:track:{i}",
                "title": f"Song {i}",
                "artist": f"Artist {i}",
                "album": f"Album {i}",
                "year": 2000 + i,
                "cover_url": "https://example.com/cover.jpg"
            },
            started_at=time.time(),
            timer_duration=30,
            guesses=[]
        )'''

content = content.replace(perf_pattern.replace('\\', ''), perf_replacement)

# Fix test_round_state_dataclass_types
types_pattern = r'''round_state = RoundState\(
        round_number=1,
        track_uri="spotify:track:123",
        track_name="Song",
        track_artist="Artist",
        correct_year=2000,
    \)

    assert isinstance\(round_state\.round_number, int\)
    assert isinstance\(round_state\.track_uri, str\)
    assert isinstance\(round_state\.track_name, str\)
    assert isinstance\(round_state\.track_artist, str\)
    assert isinstance\(round_state\.correct_year, int\)'''

types_replacement = '''round_state = RoundState(
        round_number=1,
        song={
            "uri": "spotify:track:123",
            "title": "Song",
            "artist": "Artist",
            "album": "Album",
            "year": 2000,
            "cover_url": "https://example.com/cover.jpg"
        },
        started_at=time.time(),
        timer_duration=30,
        guesses=[]
    )

    assert isinstance(round_state.round_number, int)
    assert isinstance(round_state.song, dict)
    assert isinstance(round_state.started_at, float)
    assert isinstance(round_state.timer_duration, int)'''

content = content.replace(types_pattern.replace('\\', ''), types_replacement)

# Write back
with open('/Volumes/My Passport/HA_Dashboard/tests/test_game_state.py', 'w') as f:
    f.write(content)

print("Comprehensive fix applied!")
