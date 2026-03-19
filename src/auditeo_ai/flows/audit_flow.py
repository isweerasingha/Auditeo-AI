"""
Audit Flow
"""

from crewai import Flow
from crewai.flow.flow import listen, start
from pydantic import BaseModel

from auditeo_ai.crews.insights.insights_crew import InsightsCrew, InsightsCrewOutput
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
    insights_crew_output: InsightsCrewOutput | None = None


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
    def run_insights_crew(self) -> str:
        """
        Run the insights crew
        """
        print("Running insights crew...")

        insights_crew = InsightsCrew().crew()
        inputs = {
            "website_url": self.state.website_url,
            "factual_metrics": self.state.factual_metrics,
            "page_content": self.state.page_content_clean,
        }
        crew_result = insights_crew.kickoff(inputs=inputs)

        print("Insights crew successfully run. \n")
        print(crew_result.pydantic.model_dump_json(indent=2))
