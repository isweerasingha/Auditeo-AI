from typing import Any

from pydantic import BaseModel, Field

from auditeo_ai.models import (
    FactualMetrics,
    InsightsKPIs,
    RecommendationItem,
)


class APIResponse(BaseModel):
    """
    API Response
    """

    success: bool = Field(description="Whether the API response was successful")
    trace_id: str = Field(description="The trace ID of the API response")
    message: str = Field(description="The message of the API response")
    data: Any | None = Field(default=None, description="The data of the API response")


class AuditRunResponse(BaseModel):
    """
    Audit Response
    """

    website_url: str | None = Field(
        default=None, description="The website URL of the audit"
    )
    factual_metrics: FactualMetrics | None = Field(
        default=None, description="The factual metrics of the audit"
    )
    kpis: InsightsKPIs | None = Field(default=None, description="The KPIs of the audit")
    insights_report: str | None = Field(
        default=None, description="The insights report of the audit"
    )
    recommendations: list[RecommendationItem] | None = Field(
        default=None, description="The recommendations of the audit"
    )


class AuditRunRequest(BaseModel):
    """
    Audit Run Request
    """

    website_url: str = Field(description="The website URL of the audit")
