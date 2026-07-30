# xazam Documentation

This directory holds the full documentation for the `xazam` library and CLI.

## Contents

- [`usage.md`](usage.md): how to use the Python library: identify tracks, scrape artist metadata, and handle errors.
- [`cli.md`](cli.md): command-line interface reference and examples.
- [`api.md`](api.md): reverse-engineered Shazam API reference: endpoints, payloads, headers, and response schemas.
- [`architecture.md`](architecture.md): internal design, module responsibilities, and data flow.
- [`dataset.md`](dataset.md): data products this client can produce, their suitability for publication, and the ML tasks they serve.

## Quick start

Install the library and run a live identification:

```bash
pip install -e .
python -m xazam_cli identify --file song.mp3
```

See [`usage.md`](usage.md) for programmatic examples.
