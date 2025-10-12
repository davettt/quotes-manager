"""Quote data model."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AIMetadata:
    """AI-generated metadata for a quote."""

    author_confidence: float = 0.0
    suggested_categories: List[str] = field(default_factory=list)
    category_confidence: float = 0.0
    duplicate_check_date: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "author_confidence": self.author_confidence,
            "suggested_categories": self.suggested_categories,
            "category_confidence": self.category_confidence,
            "duplicate_check_date": self.duplicate_check_date,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AIMetadata":
        """Create from dictionary."""
        return cls(
            author_confidence=data.get("author_confidence", 0.0),
            suggested_categories=data.get("suggested_categories", []),
            category_confidence=data.get("category_confidence", 0.0),
            duplicate_check_date=data.get("duplicate_check_date"),
        )


@dataclass
class Quote:
    """A quote with metadata and tracking information."""

    text: str
    author: str = "Anonymous"
    source: str = ""
    personal_note: str = ""
    categories: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date_added: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    date_modified: Optional[str] = None
    last_shown: Optional[str] = None
    times_shown: int = 0
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author,
            "source": self.source,
            "personal_note": self.personal_note,
            "categories": self.categories,
            "date_added": self.date_added,
            "date_modified": self.date_modified,
            "last_shown": self.last_shown,
            "times_shown": self.times_shown,
            "ai_metadata": self.ai_metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Quote":
        """Create Quote from dictionary."""
        ai_metadata = AIMetadata.from_dict(data.get("ai_metadata", {}))
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            text=data["text"],
            author=data.get("author", "Anonymous"),
            source=data.get("source", ""),
            personal_note=data.get("personal_note", ""),
            categories=data.get("categories", []),
            date_added=data.get("date_added", datetime.utcnow().isoformat()),
            date_modified=data.get("date_modified"),
            last_shown=data.get("last_shown"),
            times_shown=data.get("times_shown", 0),
            ai_metadata=ai_metadata,
        )

    def mark_shown(self) -> None:
        """Update tracking info when quote is displayed."""
        self.last_shown = datetime.utcnow().isoformat()
        self.times_shown += 1
