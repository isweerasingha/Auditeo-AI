"""
Audit Flow
"""

from crewai import Flow
from crewai.flow.flow import listen, start
from pydantic import BaseModel

from auditeo_ai.models import FactualMetrics
from auditeo_ai.tools.scraper_tool import AuditeoScraperTool, AuditeoScraperToolOutput


class AuditFlowState(BaseModel):
    """
    Audit Flow State
    """

    website_url: str | None = None
    factual_metrics: FactualMetrics | None = None
    page_content: str | None = None
    page_content_clean: str | None = None


class AuditFlow(Flow[AuditFlowState]):
    """
    Audit Flow
    """

    @start()
    def get_metrics(self) -> str:
        """
        Scrape the page
        """

        website_url = self.state.website_url
        print(f"Scraping {website_url}...")

        scraper = AuditeoScraperTool()
        raw_json = scraper._run(website_url)

        result = AuditeoScraperToolOutput.model_validate_json(raw_json)

        self.state.factual_metrics = result.factual_metrics
        self.state.page_content = result.page_content
        self.state.page_content_clean = result.page_content_clean

        print("Scraper tool result successfully set to State.")

    @listen("get_metrics")
    def analyze_metrics(self) -> str:
        """
        Analyze the metrics
        """
        print("Analyzing metrics...")

        print("Metrics successfully analyzed.")
