import aiohttp
import logging
import uuid
import time
from random import choice
from typing import Dict, Any, Optional

# Set up logging for debugging real requests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mobile-app user agents that Shazam's backend accepts.
# Modern browser UAs (e.g. Chrome 89+) trigger 405 on some endpoints.
USER_AGENTS = [
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G920F Build/MMB29K)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J500FN Build/LMY48B)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N910G Build/LMY47X)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SAMSUNG-SGH-I747 Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-G360H Build/KTU84P)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; SM-S920L Build/LRX22G)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G925T Build/MMB29K)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; SM-N9005 Build/LRX21V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-I9500 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G531H Build/LMY48B)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_5 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8L1 Safari/6533.18.5",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_5 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8L1 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
]

class Device:
    IPHONE = "iphone"
    ANDROID = "android"
    WEB = "web"

    @classmethod
    def random(cls) -> str:
        return choice([cls.IPHONE, cls.ANDROID, cls.WEB])

class ShazamTransport:
    def __init__(self, language="en-US", endpoint_country="GB"):
        self.session: Optional[aiohttp.ClientSession] = None
        self.language = language
        self.endpoint_country = endpoint_country
        self.TIME_ZONE = "Europe/Moscow" # Consistent with ShazamIO

    async def __aenter__(self):
        self.session = aiohttp.ClientSession() # Session without global headers
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def common_headers(self) -> Dict[str, str]:
        """Generates common headers for Shazam API requests."""
        return {
            "X-Shazam-Platform": "IPHONE",
            "X-Shazam-AppVersion": "14.1.0",
            "Accept": "*/*",
            "Accept-Language": self.language,
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": choice(USER_AGENTS),
        }

    async def request(self, method: str, url: str, headers: Dict[str, str], **kwargs):
        if not self.session:
            self.session = aiohttp.ClientSession() # Create session if not exists
        
        logger.info(f"Making {method} request to {url} with headers: {headers}")
        async with self.session.request(method, url, headers=headers, **kwargs) as response:
            logger.info(f"Response status: {response.status}")
            if response.status != 200:
                text = await response.text()
                logger.error(f"Error response ({response.status}): {text}")
                response.raise_for_status() # Raise an exception for bad status codes
            return await response.json()

    async def get_text(self, url: str, headers: Dict[str, str], **kwargs):
        if not self.session:
            self.session = aiohttp.ClientSession() # Create session if not exists
        async with self.session.get(url, headers=headers, **kwargs) as response:
            if response.status != 200:
                text = await response.text()
                logger.error(f"Error response ({response.status}): {text}")
                response.raise_for_status()
            return await response.text()
