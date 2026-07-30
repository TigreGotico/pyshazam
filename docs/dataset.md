# Data Products

Every API client in this organization also works as a dataset construction pipeline. This document describes what `xazam` can produce, what is safe and useful to publish, and the downstream ML tasks the data serves.

## 1. Datasets the Client Can Produce

### 1.1 Chart Rankings Time Series

**Source:** `GET /services/charts/csv/{chart_path}`  
**Content:** Rank, title, subtitle (artist), track ID for top-200 / top-50 charts.  
**Update frequency:** Weekly (Shazam charts refresh on a weekly cadence).  
**Scope:** Global, per-country, per-city, per-genre.

**Schema (CSV)**

```csv
rank,title,subtitle,track_id
1,Blinding Lights,The Weeknd,123456789
```

**Suitability for publication:** **High.** Chart data is factual public information, similar to Billboard or Spotify charts. No personal data, no copyrighted audio.

### 1.2 Artist Catalog Snapshots

**Source:** `GET /services/amapi/v1/catalog/{country}/search?types=artists`  
**Content:** Artist name, genres, artwork URLs, Apple Music URLs, album relationships.  
**Update frequency:** On-demand or batch-crawled periodically.

**Schema (JSONL)**

```json
{"artist_id": "3996865", "name": "Metallica", "genres": ["Metal"], "url": "https://music.apple.com/gb/artist/metallica/3996865", "albums": ["1571968136", "1440845417"]}
```

**Suitability for publication:** **Medium-High.** Metadata is factual and publicly listed on Apple Music / Shazam. Artwork URLs are hotlinks to Apple CDN; redistributing the actual image files would violate Apple terms, but the JSON metadata itself is low risk.

### 1.3 Track Metadata Corpus

**Source:** `GET /discovery/v5/.../web/-/track/{track_id}` + recognition responses  
**Content:** Track title, artist, Apple Music / Spotify links, lyrics sections, related videos, genre tags.  
**Update frequency:** On-demand ( triggered by recognition hits or batch list).

**Schema (JSONL)**

```json
{"track_id": "549952578", "title": "Nothing Else Matters", "artist": "Metallica", "apple_music_url": "...", "spotify_url": "...", "sections": [...]}
```

**Suitability for publication:** **Medium.** Similar to artist metadata; factual and public, but richer and closer to content-owner data. Prefer linking rather than full mirroring.

### 1.4 Audio Fingerprint → Metadata Mappings (Internal Only)

**Source:** `POST /discovery/v5/...` recognition pipeline  
**Content:** Raw Shazam signatures (`data:audio/vnd.shazam.sig;base64,...`) paired with resolved track IDs and metadata.  
**Update frequency:** Real-time during identification.

**Suitability for publication:** **None.** Signatures are proprietary Shazam intellectual property. This dataset is strictly for internal research, debugging, and model validation. Do **not** publish signatures on Hugging Face or any public repository.

## 2. Worth Publishing on Hugging Face?

| Dataset | Publish? | Notes |
|---------|----------|-------|
| Chart Rankings Time Series | **Yes** | Public factual data; useful for trend analysis. |
| Artist Catalog Snapshots | **Yes** | Metadata only; filter out Apple CDN artwork if paranoid. |
| Track Metadata Corpus | **Yes, curated** | Factual metadata; avoid mirroring full lyrics or long prose. |
| Signature Mappings | **No** | Proprietary; internal use only. |

## 3. ML Tasks Served

| Task | Dataset | Approach |
|------|---------|----------|
| **Music recommendation** | Chart time series + track metadata | Collaborative filtering on chart co-occurrence; content-based on genre/artist graphs. |
| **Genre classification** | Track metadata (genre tags) | Multi-label classifier on title/artist embeddings or audio features (external). |
| **Artist similarity** | Artist catalog (genres, albums, related tracks) | Graph embedding on artist-album-track graph; vector similarity on genre vectors. |
| **Temporal trend prediction** | Chart time series | Time-series forecasting (ARIMA, Prophet, or deep sequence models) on rank trajectories. |
| **Named Entity Recognition (NER)** | Track metadata | Train a model to extract artist, album, and track names from raw web text or user queries. |
| **Retrieval / RAG** | Track + artist metadata | Build a vector index of music metadata for natural-language track lookup ("that song that goes ..."). |

## 4. Implementation Plan

A `dataset.py` module (mirroring `clients/archives/*` patterns) should dump the datasets above:

- **Resumable:** store the last-seen chart path, date, and offset in a state file.
- **Polite:** add `asyncio.sleep(0.5)` between requests, and cap concurrent connections.
- **Incremental:** fetch only charts that changed since the last run.
- **Output format:** Markdown tables for human review, plus JSONL for machine consumption.
- **Run location:** run heavy bulk crawls on `/mnt/homelab` (sshfs bulk tier) to save local SSD space.

## 5. Legal and ToS considerations

- Shazam and Apple Music data are governed by their respective Terms of Service.
- Do not scrape at high velocity. Stay well below any perceptible rate limit.
- Do not redistribute audio, artwork files, or fingerprint signatures.
- Redistribute factual chart rankings and structured metadata; these are not copyrightable in most jurisdictions.

---
[← Architecture](architecture.md) · [Home](README.md)
