# Usage Guide

## Installation

```bash
# From source
pip install -e .

# With test dependencies
pip install -e ".[dev]"
```

Dependencies: `aiohttp`, `shazamio_core`.

## Identify a Track

### Typed API (recommended)

`ShazamClient.identify()` returns a typed `RecognitionResult` with rich
models — no more raw dict drilling.

```python
import asyncio
from shazampy import ShazamClient, ShazamTransport

async def main():
    with open("song.mp3", "rb") as f:
        audio = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify(audio)

    if not result.matched:
        print("No match found.")
        return

    track = result.track
    print(f"Title:   {track.title}")
    print(f"Artist:  {track.subtitle}")
    print(f"Key:     {track.key}")
    print(f"Matches: {track.confidence}")
    print(f"Cover:   {track.cover_art}")          # highest-quality image
    print(f"Apple:   {track.apple_music_url}")
    print(f"Spotify: {track.spotify_uri}")
    print(f"Deezer:  {track.deezer_uri}")
    print(f"Shazam:  {track.url}")
    print(f"Share:   {track.share.text}")
    print(f"Lyrics:  {track.lyrics[:200]}...")

    # Flat metadata from the SONG section
    for key, value in track.metadata_table.items():
        print(f"  {key}: {value}")

asyncio.run(main())
```

### Legacy raw-dict API

`identify_track()` is still available for backwards compatibility:

```python
    result = await client.identify_track(audio)
    matches = result.get("matches", [])
    if matches:
        track = result["track"]
        print(f"Matched: {track['title']} — {track['subtitle']}")
```

## Fetch Extra Track Info

The discovery endpoint returns basic metadata, but lyrics and related videos
live in a separate track-info endpoint. Use `get_track_info()` after
identification:

```python
    rec = await client.identify(audio)
    if rec.track:
        extra = await client.get_track_info(rec.track.key)
        print("Sections:", [s.type for s in extra.sections])
        print("Related videos:", extra.related_videos)
```

## Scrape Artist Metadata

Resolve an artist name from their Shazam ID and fetch Apple Music catalog data.

```python
import asyncio
from shazampy import ShazamScraper, ShazamTransport

async def main():
    async with ShazamTransport() as transport:
        scraper = ShazamScraper(transport)
        data = await scraper.get_artist_metadata("3996865")

    artists = data.get("results", {}).get("artists", {}).get("data", [])
    if artists:
        attr = artists[0]["attributes"]
        print(f"Name:  {attr['name']}")
        print(f"Genre: {', '.join(attr.get('genreNames', []))}")
        print(f"URL:   {attr['url']}")

asyncio.run(main())
```

## Configuration

`ShazamTransport` accepts two optional settings:

```python
transport = ShazamTransport(
    language="en-US",        # Accept-Language header
    endpoint_country="GB"    # Country segment in catalog URLs
)
```

These control the catalog edition and language tags returned by Shazam.

## Error Handling

All network errors raise `aiohttp.ClientResponseError`. Wrap calls appropriately:

```python
from aiohttp import ClientResponseError

try:
    result = await client.identify(audio)
except ClientResponseError as exc:
    if exc.status == 405:
        print("Blocked by Shazam (wrong headers)")
    elif exc.status == 429:
        print("Rate limited")
    else:
        raise
```

## Context Manager Usage

`ShazamTransport` is an async context manager and will close its `aiohttp.ClientSession` on exit. If you use it without `async with`, remember to call `await transport.session.close()` manually.

## Live Integration Tests

The repository includes live tests that hit the real API:

```bash
export PYSHAZAM_TEST_AUDIO="/path/to/track.mp3"
pytest tests/test_integration.py -v
```

If `PYSHAZAM_TEST_AUDIO` is not set, a default path is used; the test is skipped if the file does not exist.

## Model Reference

| Class | What it holds |
|-------|---------------|
| `RecognitionResult` | Top-level response: `track`, `matched`, `timezone`, `timestamp` |
| `Track` | Rich track record: `title`, `subtitle`, `images`, `hub`, `share`, `sections`, `matches`, `confidence` |
| `TrackImage` | `coverart`, `coverarthq`, `background` |
| `TrackHub` | `displayname`, `apple_music_uri`, `providers` list |
| `HubProvider` | `type` (SPOTIFY, DEEZER…), `caption`, `uri` |
| `TrackShare` | `subject`, `text`, `href`, `image`, `twitter`, `html` |
| `TrackSection` | `type` (SONG, LYRICS, VIDEO, RELATED), `text`, `metadata`, `metapages`, `youtubeurl` |
| `TrackMatch` | `id`, `offset`, `channel`, `timeskew`, `frequencyskew` |

All models expose `.from_dict(raw)` for manual parsing and are plain
`@dataclass` objects with sensible defaults.
