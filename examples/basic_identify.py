"""Example: identify a single track from an audio file.

Usage:
    python basic_identify.py song.mp3

Requires:
    pip install xazam
"""

import asyncio
import sys
from pathlib import Path

from xazam import ShazamClient, ShazamTransport


async def main(path: str):
    audio_path = Path(path)
    if not audio_path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify_track(audio_data)

    matches = result.get("matches", [])
    if matches:
        track = result["track"]
        print(f"Matched: {track['title']} — {track['subtitle']}")
        print(f"Confidence: {len(matches)} match(es)")
    else:
        print("No match found.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <audio_file>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
