"""Example: batch-identify every audio file in a directory.

Usage:
    python batch_identify.py /path/to/music/

Requires:
    pip install pyshazam tqdm
"""

import asyncio
import sys
from pathlib import Path

from tqdm import tqdm

from pyshazam import ShazamClient, ShazamTransport

EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}


async def identify_one(client: ShazamClient, path: Path) -> dict:
    with open(path, "rb") as f:
        audio = f.read()
    try:
        return await client.identify_track(audio)
    except Exception as exc:
        return {"error": str(exc)}


async def main(directory: str):
    root = Path(directory)
    files = [p for p in root.iterdir() if p.suffix.lower() in EXTENSIONS]
    if not files:
        print("No audio files found.")
        return

    results = []
    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        for path in tqdm(files, desc="Identifying"):
            result = await identify_one(client, path)
            results.append((path.name, result))

    # Print summary
    for name, result in results:
        track = result.get("track", {})
        if track:
            print(f"{name:30s} -> {track.get('title', '?')} — {track.get('subtitle', '?')}")
        else:
            print(f"{name:30s} -> (no match)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <directory>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
