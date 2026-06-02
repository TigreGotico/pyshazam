import time
import uuid
from io import BytesIO

from shazamio_core import Recognizer, Signature

from .transport import ShazamTransport, Device
from .models import Track, RecognitionResult


class ShazamClient:
    def __init__(self, transport: ShazamTransport):
        self.transport = transport
        self.core_recognizer = Recognizer()  # Rust-based recognizer

    # ------------------------------------------------------------------ #
    # Identification
    # ------------------------------------------------------------------ #

    async def identify_track(self, audio_data: bytes):
        """Identify audio and return the raw Shazam JSON dict.

        This is the lowest-level method; see :meth:`identify` for a typed
        wrapper.
        """
        signature: Signature = await self.core_recognizer.recognize_bytes(
            value=audio_data
        )

        if not signature or not signature.signature.uri:
            return {"error": "Could not generate signature from audio data"}

        payload = {
            "timezone": self.transport.TIME_ZONE,
            "signature": {
                "uri": signature.signature.uri,
                "samplems": signature.signature.samples
            },
            "timestamp": signature.timestamp,
            "context": {},
            "geolocation": {},
        }

        url = (
            f"https://amp.shazam.com/discovery/v5/{self.transport.language}/"
            f"{self.transport.endpoint_country}/{Device.random()}/-/tag/"
            f"{str(uuid.uuid4()).upper()}/{str(uuid.uuid4()).upper()}?"
            f"sync=true&webv3=true&sampling=true&connected=&shazamapiversion=v3"
            f"&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
        )

        return await self.transport.request(
            "POST", url, headers=self.transport.common_headers(), json=payload
        )

    async def identify(self, audio_data: bytes) -> RecognitionResult:
        """Identify audio and return a typed :class:`RecognitionResult`."""
        raw = await self.identify_track(audio_data)
        if "error" in raw:
            return RecognitionResult()
        return RecognitionResult.from_dict(raw)

    # ------------------------------------------------------------------ #
    # Extra info
    # ------------------------------------------------------------------ #

    async def get_track_info(self, track_id: str) -> Track:
        """Fetch detailed track metadata from Shazam's web endpoint.

        This hits the same endpoint that Shazam's web player uses, so it
        returns full sections (lyrics, related videos, metadata, etc.).
        """
        url = (
            f"https://www.shazam.com/discovery/v5/"
            f"{self.transport.language}/{self.transport.endpoint_country}/"
            f"web/-/track/{track_id}?"
            f"shazamapiversion=v3&video=v3"
        )
        data = await self.transport.request(
            "GET", url, headers=self.transport.common_headers()
        )
        return Track.from_dict(data)
