# shazampy Examples

## basic_identify.py

Identify a single audio file.

```bash
python basic_identify.py song.mp3
```

Output:
```
Matched: Nothing Else Matters — Metallica
Confidence: 4 match(es)
```

## artist_scrape.py

Resolve artist metadata from a Shazam ID.

```bash
python artist_scrape.py 3996865
```

Output:
```
Name:   Metallica
Genres: Metal
URL:    https://music.apple.com/gb/artist/metallica/3996865
Albums: 25 (first ID: 1571968136)
```

## batch_identify.py

Batch-process every audio file in a directory.

```bash
pip install tqdm
python batch_identify.py ~/Music/
```

Output:
```
Identifying: 100%|████████████████| 12/12 [00:24<00:00,  2.0s/it]
song01.mp3                     -> Nothing Else Matters — Metallica
song02.mp3                     -> (no match)
```

## custom_transport.py

Use a different language / catalog country.

```bash
python custom_transport.py song.mp3
```

This sends `Accept-Language: pt-PT` and queries the Brazil (`BR`) catalog.
