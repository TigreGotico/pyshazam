import asyncio
import json
import os
import pytest

from shazampy import (
    ShazamClient,
    ShazamTransport,
    ShazamScraper,
    RecognitionResult,
    Track,
)

# Path to a known audio file for live integration tests.
TEST_AUDIO = os.getenv(
    "PYSHAZAM_TEST_AUDIO",
    "/mnt/hdd16/Library/music/Metallica/Nothing Else Matters (1992)/Metallica - Nothing Else Matters - 01 - Nothing Else Matters.mp3",
)

TEST_ARTIST_ID = os.getenv("PYSHAZAM_TEST_ARTIST_ID", "3996865")


@pytest.fixture
async def transport():
    async with ShazamTransport() as t:
        yield t


# --------------------------------------------------------------------------- #
# Identification
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
@pytest.mark.skipif(not os.path.exists(TEST_AUDIO), reason="Test audio not found")
async def test_identify_track_raw():
    """Legacy method still returns a raw dict."""
    with open(TEST_AUDIO, "rb") as f:
        audio_data = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify_track(audio_data)

    assert "matches" in result
    assert len(result["matches"]) > 0
    track = result.get("track", {})
    assert track.get("title")
    assert track.get("subtitle")


@pytest.mark.asyncio
@pytest.mark.skipif(not os.path.exists(TEST_AUDIO), reason="Test audio not found")
async def test_identify_typed():
    """New typed API returns a RecognitionResult with rich models."""
    with open(TEST_AUDIO, "rb") as f:
        audio_data = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        result = await client.identify(audio_data)

    assert isinstance(result, RecognitionResult)
    assert result.matched is True
    assert result.track is not None
    track = result.track
    assert isinstance(track, Track)
    assert track.title
    assert track.subtitle
    assert track.confidence > 0
    # Rich fields that were invisible before
    assert track.images.coverart or track.images.coverarthq
    assert track.hub.displayname
    assert track.share.href or track.share.text


@pytest.mark.asyncio
@pytest.mark.skipif(not os.path.exists(TEST_AUDIO), reason="Test audio not found")
async def test_get_track_info():
    """Extra info endpoint returns the same Track model."""
    with open(TEST_AUDIO, "rb") as f:
        audio_data = f.read()

    async with ShazamTransport() as transport:
        client = ShazamClient(transport)
        rec = await client.identify(audio_data)
        assert rec.track is not None
        track_id = rec.track.key
        assert track_id

        # Fetch extra info — this is the new method
        extra = await client.get_track_info(track_id)

    assert isinstance(extra, Track)
    assert extra.title == rec.track.title
    assert extra.subtitle == rec.track.subtitle
    assert extra.hub.displayname
    # Sections (lyrics, related, videos) only appear via this endpoint
    assert extra.sections


# --------------------------------------------------------------------------- #
# Scraper
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_scrape_artist_metadata():
    """Live integration test: resolve artist name and fetch metadata."""
    async with ShazamTransport() as transport:
        scraper = ShazamScraper(transport)
        result = await scraper.get_artist_metadata(TEST_ARTIST_ID)

    assert "error" not in result
    artists = result.get("results", {}).get("artists", {}).get("data", [])
    assert len(artists) > 0
    assert artists[0]["attributes"]["name"] == "Metallica"
