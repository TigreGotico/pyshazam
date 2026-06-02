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

### From raw bytes

```python
import asyncio
from pyshazam import ShazamClient, ShazamTransport

async def main():
    with open("song.mp3", "rb") as f:
        audio = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify_track(audio)

    matches = result.get("matches", [])
    if matches:
        track = result["track"]
        print(f"Matched: {track['title']} — {track['subtitle']}")
    else:
        print("No match found.")

asyncio.run(main())
```

### From a file path (using `shazamio_core` directly)

If you only need the fingerprint and prefer to manage the HTTP layer yourself:

```python
from shazamio_core import Recognizer
import asyncio

async def main():
    r = Recognizer()
    sig = await r.recognize_path("song.mp3")
    print("URI:", sig.signature.uri)
    print("Samples (ms):", sig.signature.samples)
    print("Timestamp:", sig.timestamp)

asyncio.run(main())
```

## Scrape Artist Metadata

Resolve an artist name from their Shazam ID and fetch Apple Music catalog data.

```python
import asyncio
from pyshazam import ShazamScraper, ShazamTransport

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
    result = await client.identify_track(audio)
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
