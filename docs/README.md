# shazampy Documentation

This directory contains the full documentation for the `shazampy` library and CLI.

## Contents

- [`api.md`](api.md) — Reverse-engineered Shazam API reference. Endpoints, payloads, headers, and response schemas.
- [`usage.md`](usage.md) — How to use the Python library: identify tracks, scrape artist metadata, and handle errors.
- [`cli.md`](cli.md) — Command-line interface reference and examples.
- [`architecture.md`](architecture.md) — Internal design, module responsibilities, and data flow.
- [`dataset.md`](dataset.md) — Data products this client can produce, their suitability for publication, and the ML tasks they serve.

## Quick Start

Install the library and run a live identification:

```bash
pip install -e .
python -m shazampy_cli identify --file song.mp3
```

See [`usage.md`](usage.md) for programmatic examples.
