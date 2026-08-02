# xazam Documentation

This directory holds the full documentation for the `xazam` library.

## Contents

- [`usage.md`](usage.md): how to use the Python library: identify tracks, scrape artist metadata, and handle errors.
- [`api.md`](api.md): reverse-engineered Shazam API reference: endpoints, payloads, headers, and response schemas.
- [`architecture.md`](architecture.md): internal design, module responsibilities, and data flow.
- [`dataset.md`](dataset.md): data products this client can produce, their suitability for publication, and the ML tasks they serve.

## Quick start

Install the library and run a live identification:

```bash
pip install -e .
```

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
        print(result.track.title, "—", result.track.subtitle)

asyncio.run(main())
```

See [`usage.md`](usage.md) for programmatic examples.
