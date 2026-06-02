import asyncio
import json
import os
import pytest

from pyshazam import ShazamClient, ShazamTransport, ShazamScraper

# Path to a known audio file for live integration tests.
# Override with the PYSHAZAM_TEST_AUDIO env var.
TEST_AUDIO = os.getenv(
    "PYSHAZAM_TEST_AUDIO",
    "/mnt/hdd16/Library/music/Metallica/Nothing Else Matters (1992)/Metallica - Nothing Else Matters - 01 - Nothing Else Matters.mp3",
)

# Known good Shazam artist ID for Metallica.
TEST_ARTIST_ID = os.getenv("PYSHAZAM_TEST_ARTIST_ID", "3996865")


@pytest.fixture
async def transport():
    async with ShazamTransport() as t:
        yield t


@pytest.mark.asyncio
@pytest.mark.skipif(not os.path.exists(TEST_AUDIO), reason="Test audio not found")
async def test_identify_track():
    """Live integration test: identify a well-known track."""
    with open(TEST_AUDIO, "rb") as f:
        audio_data = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify_track(audio_data)

    assert "matches" in result, f"Response missing 'matches' key: {result.keys()}"
    assert len(result["matches"]) > 0, "Expected at least one match, got none"

    track = result.get("track", {})
    assert track, "Expected track metadata in response"
    assert track.get("title"), "Expected track title"
    assert track.get("subtitle"), "Expected track subtitle (artist)"


@pytest.mark.asyncio
async def test_scrape_artist_metadata():
    """Live integration test: resolve artist name and fetch metadata."""
    async with ShazamTransport() as transport:
        scraper = ShazamScraper(transport)
        result = await scraper.get_artist_metadata(TEST_ARTIST_ID)

    assert "error" not in result, f"Scraper returned error: {result.get('error')}"
    artists = result.get("results", {}).get("artists", {}).get("data", [])
    assert len(artists) > 0, "Expected at least one artist in search results"
    assert artists[0]["attributes"]["name"] == "Metallica"
