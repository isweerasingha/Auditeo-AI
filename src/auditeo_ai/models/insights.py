from pydantic import BaseModel, Field


class InsightsKPIs(BaseModel):
    seo_score: int = Field(
        ge=0,
        le=100,
    )
    links_score: int = Field(
        ge=0,
        le=100,
    )
    usability_score: int = Field(
        ge=0,
        le=100,
    )
    social_score: int = Field(
        ge=0,
        le=100,
    )
