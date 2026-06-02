# Architecture

## Module Overview

```
shazampy/
├── __init__.py      # Public exports: ShazamClient, ShazamScraper, ShazamTransport, Track, Artist
├── client.py        # ShazamClient — high-level track identification
├── scraper.py       # ShazamScraper — artist name resolution + catalog search
├── transport.py     # ShazamTransport — aiohttp sessions, header generation, request helpers
└── models.py        # Track, Artist dataclasses
```

## Data Flow: Track Identification

```
Audio file (bytes)
    |
    v
shazamio_core.Recognizer.recognize_bytes()
    |
    +---> Decodes audio (mp3, wav, flac, etc.)
    +---> Generates Shazam fingerprint signature (Rust)
    |
    v
Signature { uri: "data:audio/vnd.shazam.sig;base64,...", samples: 10000, timestamp: 1234567890 }
    |
    v
ShazamClient.identify_track()
    |
    +---> Builds JSON payload: { timezone, signature, timestamp, context: {}, geolocation: {} }
    +---> Builds discovery URL: amp.shazam.com/discovery/v5/.../tag/{uuid}/{uuid}
    |
    v
ShazamTransport.request("POST", url, headers=common_headers(), json=payload)
    |
    v
Shazam API
    |
    v
JSON response -> { matches: [...], track: {...} }
```

Key design decisions:

- `shazamio_core` (Rust) is treated as a black-box fingerprint engine. The Python side never manipulates raw audio samples or signature math.
- The `timestamp` returned by `shazamio_core` is forwarded verbatim; it is **not** regenerated from `time.time()`.
- Query-string parameters (`sync`, `webv3`, `sampling`, etc.) are hard-coded to match the current mobile-app contract.

## Data Flow: Artist Metadata Scraping

```
Artist ID (e.g. "3996865")
    |
    v
ShazamScraper._resolve_artist_name()
    |
    +---> GET https://www.shazam.com/artist/_/{artist_id}
    +---> Dedicated aiohttp.ClientSession with browser-like headers
    +---> Extracts name from <title>Name - Shazam</title>
    |
    v
Artist name (e.g. "Metallica")
    |
    v
ShazamScraper.get_artist_metadata()
    |
    +---> GET https://www.shazam.com/services/amapi/v1/catalog/{country}/search?term=Metallica&limit=1&types=artists
    +---> Uses ShazamTransport (mobile-app headers)
    |
    v
Apple Music catalog JSON -> { results: { artists: { data: [...] } } }
```

Key design decisions:

- The artist page (`shazam.com/artist/_/...`) and the catalog API (`services/amapi/...`) require **different** header personas. The scraper uses a dedicated session for the HTML page and the shared transport for the API.
- The catalog search endpoint is strict about `User-Agent`. Modern desktop UAs trigger `405`; the transport only rotates legacy mobile-app UAs.

## Header Strategy

| Endpoint | Required Persona | Rationale |
|----------|------------------|-----------|
| `amp.shazam.com/discovery/v5/...` | Mobile app (`X-Shazam-Platform`, legacy UA) | Fingerprinting endpoint expects a native client. |
| `www.shazam.com/services/amapi/...` | Mobile app (legacy UA) | Rejects modern desktop UAs with `405`. |
| `www.shazam.com/artist/_/...` | Browser (`Accept: text/html`, generic UA) | HTML page serving; needs to look like a normal browser. |

`ShazamTransport.common_headers()` returns the mobile-app persona. The scraper overrides this for the HTML step only.

## Transport Lifecycle

`ShazamTransport` is an async context manager:

```python
async with ShazamTransport() as transport:
    ...
```

On enter it creates an `aiohttp.ClientSession`. On exit it closes it. If used outside a context manager, the session is created lazily on the first request but **must** be closed manually to avoid connection leaks.

The transport exposes two helpers:

- `request(method, url, headers, **kwargs)` — JSON API wrapper; raises on non-200.
- `get_text(url, headers, **kwargs)` — Plain-text wrapper for HTML scraping.

## Models

```python
@dataclass
class Artist:
    id: str
    name: str

@dataclass
class Track:
    id: str
    title: str
    artist: Optional[Artist] = None
```

These are lightweight value objects. The library currently returns raw dicts from the API; the dataclasses are reserved for future typed wrappers.

## Testing Strategy

- **Live integration tests** (`tests/test_integration.py`) exercise the real API with a known audio file and artist ID. They are gated by `pytest.mark.skipif` when the test audio is absent.
- **No mocked unit tests yet.** Because the API is reverse-engineered and may change, live tests are the primary source of truth. Mock-based unit tests can be added for offline CI if needed.
