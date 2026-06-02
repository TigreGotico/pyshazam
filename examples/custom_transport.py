"""Example: custom transport settings (language, country, headers).

Usage:
    python custom_transport.py song.mp3
"""

import asyncio
import sys

from xazam import ShazamClient, ShazamTransport


async def main(path: str):
    # Use Portuguese language and Brazil catalog edition
    transport = ShazamTransport(
        language="pt-PT",
        endpoint_country="BR",
    )

    with open(path, "rb") as f:
        audio = f.read()

    async with transport:
        client = ShazamClient(transport)
        result = await client.identify_track(audio)

    track = result.get("track", {})
    if track:
        print(f"Matched: {track['title']} — {track['subtitle']}")
    else:
        print("No match.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <audio_file>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
