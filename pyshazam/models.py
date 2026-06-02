from dataclasses import dataclass
from typing import Optional

@dataclass
class Artist:
    id: str
    name: str

@dataclass
class Track:
    id: str
    title: str
    artist: Optional[Artist] = None
