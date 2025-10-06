"""Configuration data model."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AIConfig:
    """AI-related configuration settings."""

    enable_explanations: bool = True
    enable_author_lookup: bool = True
    enable_duplicate_detection: bool = True
    duplicate_threshold: int = 85

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "enable_explanations": self.enable_explanations,
            "enable_author_lookup": self.enable_author_lookup,
            "enable_duplicate_detection": self.enable_duplicate_detection,
            "duplicate_threshold": self.duplicate_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AIConfig":
        """Create from dictionary."""
        return cls(
            enable_explanations=data.get("enable_explanations", True),
            enable_author_lookup=data.get("enable_author_lookup", True),
            enable_duplicate_detection=data.get("enable_duplicate_detection", True),
            duplicate_threshold=data.get("duplicate_threshold", 85),
        )


@dataclass
class Preferences:
    """User preferences."""

    daily_quote_enabled: bool = True
    daily_quote_time: str = "08:00"
    shell_integration: bool = False
    show_quote_id: bool = False
    display_style: str = "boxed"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "daily_quote_enabled": self.daily_quote_enabled,
            "daily_quote_time": self.daily_quote_time,
            "shell_integration": self.shell_integration,
            "show_quote_id": self.show_quote_id,
            "display_style": self.display_style,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Preferences":
        """Create from dictionary."""
        return cls(
            daily_quote_enabled=data.get("daily_quote_enabled", True),
            daily_quote_time=data.get("daily_quote_time", "08:00"),
            shell_integration=data.get("shell_integration", False),
            show_quote_id=data.get("show_quote_id", False),
            display_style=data.get("display_style", "boxed"),
        )


@dataclass
class Config:
    """Application configuration."""

    version: str = "1.0"
    custom_categories: List[str] = field(default_factory=list)
    preferences: Preferences = field(default_factory=Preferences)
    ai: AIConfig = field(default_factory=AIConfig)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "custom_categories": self.custom_categories,
            "preferences": self.preferences.to_dict(),
            "ai": self.ai.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Config":
        """Create from dictionary."""
        preferences = Preferences.from_dict(data.get("preferences", {}))
        ai_config = AIConfig.from_dict(data.get("ai", {}))
        return cls(
            version=data.get("version", "1.0"),
            custom_categories=data.get("custom_categories", []),
            preferences=preferences,
            ai=ai_config,
        )
