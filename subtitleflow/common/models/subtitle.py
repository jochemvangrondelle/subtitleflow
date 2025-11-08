# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Subtitle domain models."""

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

import srt


@dataclass
class Subtitle:
    """Represents a single subtitle entry."""

    index: int
    start: timedelta
    end: timedelta
    content: str
    has_music: bool = False
    music_lines: list[str] = field(default_factory=list)
    text_lines: list[str] = field(default_factory=list)

    @classmethod
    def from_srt(cls, srt_subtitle: srt.Subtitle) -> "Subtitle":
        """Create from srt.Subtitle object."""
        return cls(
            index=srt_subtitle.index,
            start=srt_subtitle.start,
            end=srt_subtitle.end,
            content=srt_subtitle.content.strip(),
        )

    def to_srt(self) -> srt.Subtitle:
        """Convert to srt.Subtitle object."""
        return srt.Subtitle(
            index=self.index,
            start=self.start,
            end=self.end,
            content=self.content,
        )

    @property
    def duration(self) -> timedelta:
        """Get duration of subtitle."""
        return self.end - self.start


@dataclass
class SubtitleFile:
    """Represents a subtitle file with multiple entries."""

    path: str
    subtitles: list[Subtitle]
    encoding: str = "utf-8"

    @classmethod
    def load(cls, path: str, encoding: str = "utf-8") -> "SubtitleFile":
        """Load subtitle file from disk."""
        path_obj = Path(path)
        with path_obj.open(encoding=encoding) as f:
            content = f.read()

        srt_subtitles = list(srt.parse(content))
        subtitles = [Subtitle.from_srt(s) for s in srt_subtitles]

        return cls(path=path, subtitles=subtitles, encoding=encoding)

    def save(self, path: str, encoding: str = "utf-8") -> None:
        """Save subtitle file to disk."""
        srt_subtitles = [sub.to_srt() for sub in self.subtitles]
        content = srt.compose(srt_subtitles)

        path_obj = Path(path)
        with path_obj.open("w", encoding=encoding) as f:
            f.write(content)

    def __len__(self) -> int:
        return len(self.subtitles)

    def __getitem__(self, index: int) -> Subtitle:
        return self.subtitles[index]
