# Beatsy Playlists

This directory contains playlist JSON files for the Beatsy music guessing game.

## Playlist JSON Format

Each playlist file must follow this structure:

```json
{
  "playlist_name": "Your Playlist Name",
  "playlist_id": "unique_playlist_id",
  "songs": [
    {
      "spotify_uri": "spotify:track:TRACK_ID",
      "year": 1985,
      "fun_fact": "Optional fun fact about the song"
    }
  ]
}
```

### Required Fields

**Playlist Level:**
- `playlist_name` (string): Display name shown in admin dropdown
- `playlist_id` (string): Unique identifier (lowercase, underscores only)
- `songs` (array): List of song objects

**Song Level:**
- `spotify_uri` (string): Spotify track URI in format `spotify:track:TRACK_ID`
- `year` (integer): Release year of the song

**Optional Fields:**
- `fun_fact` (string): Interesting trivia about the song

## Finding Spotify Track URIs

1. Open Spotify desktop or web player
2. Find the song you want to add
3. Right-click on the song
4. Click "Share" → "Copy Song Link"
5. The link will look like: `https://open.spotify.com/track/TRACK_ID`
6. Convert to URI format: `spotify:track:TRACK_ID`

Example:
- Link: `https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp`
- URI: `spotify:track:3n3Ppam7vgaVa1iaRUc9Lp`

## Validation

The system automatically validates playlist files when loading:
- Missing required fields will cause the playlist to be excluded
- Invalid JSON format will be logged as an error
- Check Home Assistant logs for validation details

## Adding Custom Playlists

1. Create a new `.json` file in this directory
2. Follow the format above
3. Use a unique `playlist_id` (not already used)
4. Add 15-20 songs for best gameplay experience
5. Reload Beatsy component or restart Home Assistant
6. New playlist will appear in admin dropdown automatically

## Sample Playlists Included

- **80s_hits.json**: Popular hits from the 1980s (18 songs)
- **90s_classics.json**: Classic songs from the 1990s (18 songs)
- **classic_rock.json**: Rock classics from 1967-1979 (19 songs)
- **2000s_hits.json**: Popular hits from the 2000s (18 songs)

## Tips for Creating Playlists

- **Variety**: Include a mix of years within your chosen decade
- **Popularity**: Use well-known songs that most people can recognize
- **Difficulty**: Mix easy and challenging years for interesting gameplay
- **Quality**: Ensure Spotify URIs are valid and songs are available
- **Fun Facts**: Add trivia to enhance player experience (optional)

## Troubleshooting

**Playlist not appearing in dropdown:**
- Check JSON file is valid (use a JSON validator)
- Verify all required fields are present
- Check Home Assistant logs for validation errors
- Ensure file has `.json` extension

**Playlist appears but songs won't play:**
- Verify Spotify URIs are correct
- Check songs are available in your region
- Ensure Spotify integration is properly configured
