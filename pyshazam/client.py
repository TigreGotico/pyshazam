import time
import uuid
from io import BytesIO
from shazamio_core import Recognizer, Signature

from .transport import ShazamTransport, Device

class ShazamClient:
    def __init__(self, transport: ShazamTransport):
        self.transport = transport
        self.core_recognizer = Recognizer() # Instantiate the Rust-based recognizer

    async def identify_track(self, audio_data: bytes):
        # shazamio_core handles audio processing internally
        signature: Signature = await self.core_recognizer.recognize_bytes(value=audio_data)
        
        if not signature or not signature.signature.uri:
            return {"error": "Could not generate signature from audio data"}

        # Use the exact payload structure from Converter.data_search in ShazamIO
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
        
        return await self.transport.request("POST", url, headers=self.transport.common_headers(), json=payload)
