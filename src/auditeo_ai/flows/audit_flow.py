"""
Audit Flow
"""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from crewai import Flow
from crewai.flow.flow import listen, start
from pydantic import BaseModel

from auditeo_ai.crews.insights.insights_crew import InsightsCrew
from auditeo_ai.models import FactualMetrics, InsightsCrewOutput
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

    def _write_crew_result_to_report(
        self, output: InsightsCrewOutput, website_url: str | None
    ) -> Path:
        domain = (
            urlparse(website_url).netloc if website_url else "unknown-site"
        ) or "unknown-site"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_path = Path("reports")
        reports_path.mkdir(parents=True, exist_ok=True)
        json_path = reports_path / f"audit_insights_{domain}_{timestamp}.json"
        json_path.write_text(output.model_dump_json(indent=2))
        md_path = reports_path / f"audit_insights_{domain}_{timestamp}.md"
        md_path.write_text(output.structured_report)
        return json_path

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
    def run_insights_crew(self):
        """
        Run the insights crew
        """
        print("Running insights crew...")

        inputs = {
            "website_url": self.state.website_url,
            "factual_metrics": self.state.factual_metrics.model_dump_json(indent=2),
            "page_content": self.state.page_content,
            "cta_count": self.state.factual_metrics.cta_count,
            "word_count": self.state.factual_metrics.total_word_count,
            "images_missing_alt_text_pct": self.state.factual_metrics.images_missing_alt_text_pct,
        }
        print(f"Insights crew inputs: {inputs}")
        insights_crew = InsightsCrew().crew()
        crew_result = insights_crew.kickoff(inputs=inputs)
        self.state.insights_crew_output = crew_result.pydantic

        print("Insights crew successfully run. \n")
