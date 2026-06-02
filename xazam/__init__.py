from .client import ShazamClient
from .models import (
    HubProvider,
    RecognitionResult,
    SectionMetaPage,
    Track,
    TrackHub,
    TrackImage,
    TrackMatch,
    TrackSection,
    TrackShare,
)
from .scraper import ShazamScraper
from .transport import ShazamTransport

__all__ = [
    "ShazamClient",
    "ShazamScraper",
    "ShazamTransport",
    "RecognitionResult",
    "Track",
    "TrackImage",
    "TrackShare",
    "TrackHub",
    "HubProvider",
    "TrackSection",
    "SectionMetaPage",
    "TrackMatch",
]
