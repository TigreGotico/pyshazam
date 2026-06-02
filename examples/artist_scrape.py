"""Example: resolve artist metadata from a Shazam artist ID.

Usage:
    python artist_scrape.py 3996865

Requires:
    pip install shazampy
"""

import asyncio
import sys

from shazampy import ShazamScraper, ShazamTransport


async def main(artist_id: str):
    async with ShazamTransport() as transport:
        scraper = ShazamScraper(transport)
        data = await scraper.get_artist_metadata(artist_id)

    artists = data.get("results", {}).get("artists", {}).get("data", [])
    if not artists:
        print("Artist not found.")
        return

    artist = artists[0]
    attr = artist["attributes"]
    print(f"Name:   {attr['name']}")
    print(f"Genres: {', '.join(attr.get('genreNames', []))}")
    print(f"URL:    {attr.get('url', 'N/A')}")

    albums = artist.get("relationships", {}).get("albums", {}).get("data", [])
    if albums:
        print(f"Albums: {len(albums)} (first ID: {albums[0]['id']})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <artist_id>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
