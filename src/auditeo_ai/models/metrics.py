"""
Factual Metrics Model
"""

from pydantic import BaseModel, Field, field_validator


class HeadingCounts(BaseModel):
    """Counts for heading tags H1-H3."""

    h1: int = Field(default=0, ge=0, description="Number of H1 headings")
    h2: int = Field(default=0, ge=0, description="Number of H2 headings")
    h3: int = Field(default=0, ge=0, description="Number of H3 headings")


class LinkCounts(BaseModel):
    """Counts for links."""

    internal: int = Field(default=0, ge=0, description="Number of internal links")
    external: int = Field(default=0, ge=0, description="Number of external links")

    @property
    def total(self) -> int:
        return self.internal + self.external


class FactualMetrics(BaseModel):
    """
    Factual metrics extracted from a web page.
    """

    total_word_count: int = Field(
        default=0,
        ge=0,
        description="Total number of words in the page content",
    )
    heading_counts: HeadingCounts = Field(
        default_factory=HeadingCounts,
        description="Counts for heading tags H1-H3",
    )
    cta_count: int = Field(
        default=0,
        ge=0,
        description="Number of calls-to-action (buttons or primary action links)",
    )
    link_counts: LinkCounts = Field(
        default_factory=LinkCounts,
        description="Counts for links",
    )
    image_count: int = Field(
        default=0,
        ge=0,
        description="Total number of images",
    )
    images_missing_alt_text_pct: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Percentage of images missing alt text",
    )
    meta_title: str | None = Field(
        default=None,
        description="Content of the <title> tag",
    )
    meta_description: str | None = Field(
        default=None,
        description="Content of the meta description tag",
    )

    @field_validator("images_missing_alt_text_pct")
    @classmethod
    def round_percentage(cls, v: float) -> float:
        return round(v, 2)
