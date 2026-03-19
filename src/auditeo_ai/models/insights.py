from pydantic import BaseModel, Field


class InsightsKPIs(BaseModel):
    """
    Insights KPIs
    """

    seo_score: int = Field(
        ge=0,
        le=100,
        description="The SEO score of the page (0-100)",
    )
    links_score: int = Field(
        ge=0,
        le=100,
        description="The links score of the page (0-100)",
    )
    usability_score: int = Field(
        ge=0,
        le=100,
        description="The usability score of the page (0-100)",
    )
    social_score: int = Field(
        ge=0,
        le=100,
        description="The social score of the page (0-100)",
    )


class InsightsCrewOutput(BaseModel):
    """
    Insights Crew Output
    """

    kpis: InsightsKPIs = Field(description="The KPIs of the page")
    structured_report: str = Field(
        description="The full Markdown report for the client."
    )

