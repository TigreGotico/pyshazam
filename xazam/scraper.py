import logging
import re
import aiohttp # Import aiohttp for the dedicated session
from .transport import ShazamTransport

logger = logging.getLogger(__name__)

class ShazamScraper:
    def __init__(self, transport: ShazamTransport):
        self.transport = transport

    async def _resolve_artist_name(self, artist_id: str) -> str:
        url = f"https://www.shazam.com/artist/_/{artist_id}"
        # Create a dedicated session with specific headers for shazam.com web page
        async with aiohttp.ClientSession(headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", # From ShazamIO
            "Accept": "text/html",
        }) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Could not resolve artist name for ID {artist_id}: HTTP {response.status}")
                    response.raise_for_status()
                html = await response.text()

        # Updated regex to match "Artist Name - Shazam"
        match = re.search(r"<title>(.*?)\s*-\s*Shazam</title>", html)
        if match:
            name = match.group(1).strip()
            if name:
                return name
        return ""

    async def get_artist_metadata(self, artist_id: str):
        artist_name = await self._resolve_artist_name(artist_id)
        if not artist_name:
            return {"error": "Could not resolve artist name"}

        # Use the new search endpoint (this still uses the general ShazamTransport)
        url = (
            f"https://www.shazam.com/services/amapi/v1/catalog/{self.transport.endpoint_country}"
            f"/search?term={artist_name}&limit=1&offset=0&types=artists"
        )
        return await self.transport.request("GET", url, headers=self.transport.common_headers())

