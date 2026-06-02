"""Typed data models for Shazam API responses."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TrackImage:
    """Album/artist artwork URLs."""
    coverart: str = ""
    coverarthq: str = ""
    background: str = ""
    joecolor: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TrackImage":
        if not d:
            return cls()
        return cls(
            coverart=d.get("coverart", ""),
            coverarthq=d.get("coverarthq", ""),
            background=d.get("background", ""),
            joecolor=d.get("joecolor", ""),
        )


@dataclass
class TrackShare:
    """Social sharing metadata."""
    subject: str = ""
    text: str = ""
    href: str = ""
    image: str = ""
    twitter: str = ""
    html: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TrackShare":
        if not d:
            return cls()
        return cls(
            subject=d.get("subject", ""),
            text=d.get("text", ""),
            href=d.get("href", ""),
            image=d.get("image", ""),
            twitter=d.get("twitter", ""),
            html=d.get("html", ""),
        )


@dataclass
class HubProvider:
    """A streaming/link provider (Spotify, Deezer, Apple Music…)."""
    type: str = ""
    caption: str = ""
    uri: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "HubProvider":
        if not d:
            return cls()
        return cls(
            type=d.get("type", ""),
            caption=d.get("caption", ""),
            uri=d.get("uri", ""),
        )


@dataclass
class TrackHub:
    """The 'hub' block with deep-links and provider actions."""
    type: str = ""
    displayname: str = ""
    image: str = ""
    explicit: bool = False
    providers: List[HubProvider] = field(default_factory=list)
    apple_music_uri: str = ""
    apple_music_id: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TrackHub":
        if not d:
            return cls()
        providers = []
        for prov in d.get("providers", []):
            for action in prov.get("actions", []):
                providers.append(
                    HubProvider(
                        type=prov.get("type", ""),
                        caption=prov.get("caption", ""),
                        uri=action.get("uri", ""),
                    )
                )
        apple_uri = ""
        apple_id = ""
        for action in d.get("actions", []):
            if action.get("type") == "applemusicopen":
                apple_uri = action.get("uri", "")
            elif action.get("type") == "applemusicplay":
                apple_id = str(action.get("id", ""))
        return cls(
            type=d.get("type", ""),
            displayname=d.get("displayname", ""),
            image=d.get("image", ""),
            explicit=d.get("explicit", False),
            providers=providers,
            apple_music_uri=apple_uri,
            apple_music_id=apple_id,
        )


@dataclass
class SectionMetaPage:
    """A page inside a section (e.g. artist image + album cover)."""
    image: str = ""
    caption: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "SectionMetaPage":
        return cls(image=d.get("image", ""), caption=d.get("caption", ""))


@dataclass
class TrackSection:
    """A content section (SONG, LYRICS, VIDEO, RELATED…)."""
    type: str = ""
    text: str = ""
    tabname: str = ""
    metadata: List[Dict[str, str]] = field(default_factory=list)
    metapages: List[SectionMetaPage] = field(default_factory=list)
    youtubeurl: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TrackSection":
        meta = []
        for m in d.get("metadata", []):
            meta.append({"title": m.get("title", ""), "text": m.get("text", "")})
        pages = [SectionMetaPage.from_dict(p) for p in d.get("metapages", [])]
        return cls(
            type=d.get("type", ""),
            text="\n".join(d.get("text", [])) if isinstance(d.get("text"), list) else d.get("text", ""),
            tabname=d.get("tabname", ""),
            metadata=meta,
            metapages=pages,
            youtubeurl=d.get("youtubeurl", ""),
        )


@dataclass
class TrackMatch:
    """A single fingerprint match returned by the discovery endpoint."""
    id: str = ""
    offset: float = 0.0
    channel: str = ""
    timeskew: float = 0.0
    frequencyskew: float = 0.0

    @classmethod
    def from_dict(cls, d: dict) -> "TrackMatch":
        return cls(
            id=d.get("id", ""),
            offset=d.get("offset", 0.0),
            channel=d.get("channel", ""),
            timeskew=d.get("timeskew", 0.0),
            frequencyskew=d.get("frequencyskew", 0.0),
        )


@dataclass
class Track:
    """Rich Shazam track record."""
    key: str = ""
    title: str = ""
    subtitle: str = ""          # Artist name
    url: str = ""               # Shazam web URL
    genres: List[str] = field(default_factory=list)
    images: TrackImage = field(default_factory=TrackImage)
    share: TrackShare = field(default_factory=TrackShare)
    hub: TrackHub = field(default_factory=TrackHub)
    sections: List[TrackSection] = field(default_factory=list)
    matches: List[TrackMatch] = field(default_factory=list)
    confidence: int = 0           # Number of matches

    @classmethod
    def from_dict(cls, d: dict) -> "Track":
        if not d:
            return cls()
        sections = [TrackSection.from_dict(s) for s in d.get("sections", [])]
        matches = [TrackMatch.from_dict(m) for m in d.get("matches", [])]
        genres = d.get("genres", {}).get("primary", "")
        return cls(
            key=str(d.get("key", "")),
            title=d.get("title", ""),
            subtitle=d.get("subtitle", ""),
            url=d.get("url", ""),
            genres=[g.strip() for g in genres.split(",")] if genres else [],
            images=TrackImage.from_dict(d.get("images", {})),
            share=TrackShare.from_dict(d.get("share", {})),
            hub=TrackHub.from_dict(d.get("hub", {})),
            sections=sections,
            matches=matches,
            confidence=len(matches),
        )

    @property
    def artist(self) -> str:
        """Convenience alias for subtitle."""
        return self.subtitle

    @property
    def cover_art(self) -> str:
        """Highest-quality cover art URL available."""
        return self.images.coverarthq or self.images.coverart

    @property
    def apple_music_url(self) -> str:
        return self.hub.apple_music_uri

    @property
    def spotify_uri(self) -> str:
        for p in self.hub.providers:
            if p.type == "SPOTIFY":
                return p.uri
        return ""

    @property
    def deezer_uri(self) -> str:
        for p in self.hub.providers:
            if p.type == "DEEZER":
                return p.uri
        return ""

    @property
    def lyrics(self) -> str:
        for s in self.sections:
            if s.type == "LYRICS":
                return s.text
        return ""

    @property
    def metadata_table(self) -> Dict[str, str]:
        """Flattened key-value metadata from the SONG section."""
        table: Dict[str, str] = {}
        for s in self.sections:
            if s.type == "SONG":
                for m in s.metadata:
                    table[m.get("title", "")] = m.get("text", "")
        return table

    @property
    def related_videos(self) -> List[str]:
        urls = []
        for s in self.sections:
            if s.type == "VIDEO" and s.youtubeurl:
                urls.append(s.youtubeurl)
        return urls


@dataclass
class RecognitionResult:
    """Top-level response from the discovery endpoint."""
    track: Optional[Track] = None
    location: Dict[str, Any] = field(default_factory=dict)
    timezone: str = ""
    timestamp: int = 0
    tagid: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "RecognitionResult":
        track = Track.from_dict(d.get("track", {})) if d.get("track") else None
        return cls(
            track=track,
            location=d.get("location", {}),
            timezone=d.get("timezone", ""),
            timestamp=d.get("timestamp", 0),
            tagid=d.get("tagid", ""),
        )

    @property
    def matched(self) -> bool:
        return self.track is not None and bool(self.track.matches)
