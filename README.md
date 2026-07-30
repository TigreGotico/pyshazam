# xazam

`xazam` is an async Python client for the Shazam API. It uses `shazamio_core` for audio fingerprinting, and adds track identification and artist metadata scraping on top.

## Features

- **Track identification**: send audio bytes and get track metadata back.
- **Artist metadata scraping**: resolve artist pages and query the Apple Music catalog proxy.
- **Modular transport**: `ShazamTransport` handles headers and sessions. `ShazamClient` and `ShazamScraper` build on top of it.

## Install

```bash
pip install -e .
# or with dev dependencies
pip install -e ".[dev]"
```

## Quick start

### Identify a track (typed API: recommended)

```python
import asyncio
from xazam import ShazamClient, ShazamTransport

async def main():
    with open("song.mp3", "rb") as f:
        audio = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify(audio)

    if result.matched:
        track = result.track
        print(f"{track.title} — {track.subtitle}")
        print(f"Cover art: {track.cover_art}")
        print(f"Apple Music: {track.apple_music_url}")
        print(f"Spotify: {track.spotify_uri}")
        print(f"Lyrics: {track.lyrics[:200]}...")
    else:
        print("No match")

asyncio.run(main())
```

### Fetch extra track metadata

After identification, query the track detail endpoint for lyrics, related
videos, and extended metadata:

```python
    extra = await client.get_track_info(track.key)
    print(extra.metadata_table)   # {'Album': '…', 'Released': '…', 'Label': '…'}
    print(extra.related_videos)    # ['https://youtube.com/watch?v=…', ...]
```

### Identify a track (legacy raw-dict API)

`identify_track()` still returns the raw Shazam JSON, for backward
compatibility:

```python
    result = await client.identify_track(audio)
    print(result["track"]["title"], "—", result["track"]["subtitle"])
```

### Scrape artist metadata

```python
import asyncio
from xazam import ShazamScraper, ShazamTransport

async def main():
    async with ShazamTransport() as transport:
        scraper = ShazamScraper(transport)
        data = await scraper.get_artist_metadata("3996865")

    artist = data["results"]["artists"]["data"][0]
    print(artist["attributes"]["name"])

asyncio.run(main())
```

## CLI

```bash
# Identify a file
python -m xazam_cli identify --file song.mp3

# Scrape artist metadata
python -m xazam_cli scrape --artist-id 3996865
```

See [docs/cli.md](docs/cli.md) for the full command reference.

## Tests

Live integration tests hit the real Shazam API. Set a custom audio file with
an environment variable:

```bash
export SHAZAMPY_TEST_AUDIO="/path/to/track.mp3"
pytest tests/test_integration.py -v
```

## Architecture

| Module | Purpose |
|--------|---------|
| `client.py` | `ShazamClient`: high-level track identification |
| `scraper.py` | `ShazamScraper`: artist name resolution and catalog search |
| `transport.py` | `ShazamTransport`: aiohttp sessions, headers, request helpers |
| `models.py` | `Track`, `Artist` dataclasses |

See [docs/architecture.md](docs/architecture.md) for the full data flow.

## Status

- Artist metadata scraping works (405 errors resolved with a dedicated web-page session).
- Track identification works (matches return correctly through `shazamio_core` fingerprinting).

## Related projects

- [TigreGotico/pyshazam](https://github.com/TigreGotico/pyshazam): the package that `xazam` was renamed from on PyPI.
- [TigreGotico/shazam2mqtt](https://github.com/TigreGotico/shazam2mqtt): a Dockerized bridge that uses `xazam` to identify music from a microphone and publish results to MQTT.

## Documentation

- [docs/usage.md](docs/usage.md): library usage and error handling
- [docs/cli.md](docs/cli.md): command-line reference
- [docs/api.md](docs/api.md): reverse-engineered Shazam API reference
- [docs/architecture.md](docs/architecture.md): internal design and data flow
- [docs/dataset.md](docs/dataset.md): data products and their suitability for publication

## License

MIT
