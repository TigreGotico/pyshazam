# CLI Reference

The CLI is located in `apps/xazam-cli/main.py` and wraps the `xazam` library for quick shell usage.

## Commands

### `identify`

Recognise a track from an audio file.

```bash
python -m xazam_cli identify --file <path>
```

**Options**

| Option | Required | Description |
|--------|----------|-------------|
| `--file` | Yes | Path to the audio file (mp3, wav, flac, etc.) |

**Example**

```bash
python -m xazam_cli identify --file "song.mp3"
```

**Output**

```
Matched: Nothing Else Matters — Metallica
Confidence: 4 match(es)
```

If no match is found:

```
No matches found.
```

### `scrape`

Resolve an artist name from a Shazam artist ID and print catalog metadata.

```bash
python -m xazam_cli scrape --artist-id <id>
```

**Options**

| Option | Required | Description |
|--------|----------|-------------|
| `--artist-id` | Yes | Shazam artist ID (e.g. `3996865` for Metallica) |

**Example**

```bash
python -m xazam_cli scrape --artist-id 3996865
```

**Output**

```
Name: Metallica
Genre: Metal
URL: https://music.apple.com/gb/artist/metallica/3996865
```

## Error Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Missing required argument or scraper/API error |
| `2` | Unhandled exception (Python default) |

## Extending the CLI

The CLI is intentionally minimal. To add a `--json` flag or `--verbose` mode, modify `apps/xazam-cli/main.py` and pass the flag into the `identify()` / `scrape()` coroutines.
