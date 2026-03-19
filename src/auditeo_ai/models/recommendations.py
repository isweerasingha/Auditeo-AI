from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    priority: int = Field(ge=1, le=5, description="Priority level (1 being highest).")
    title: str = Field(description="Concise, actionable title of the recommendation.")
    action: str = Field(description="Step-by-step instructions on what to implement.")
    reasoning: str = Field(
        description="Logical justification tied strictly to the extracted metrics."
    )
    expected_impact: str = Field(
        description="The predicted outcome for SEO or Conversion."
    )


class RecommendationCrewOutput(BaseModel):
    recommendations: list[RecommendationItem] = Field(
        description="3-5 prioritized strategic actions."
    )
    validation_status: str = Field(
        description="A brief note from the validator confirming metric accuracy."
    )
