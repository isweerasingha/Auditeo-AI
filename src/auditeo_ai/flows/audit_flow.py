"""
Audit Flow
"""

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from crewai import Flow
from crewai.flow.flow import listen, start
from pydantic import BaseModel

from auditeo_ai.crews.insights.insights_crew import InsightsCrew
from auditeo_ai.crews.recommendations.recommendations_crew import RecommendationCrew
from auditeo_ai.models import (
    FactualMetrics,
    InsightsCrewOutput,
    RecommendationCrewOutput,
)
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
    recommendations_crew_output: RecommendationCrewOutput | None = None


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

    def _save_crew_kickoff_debug(self, crew_result, website_url: str | None) -> Path:
        domain = (
            urlparse(website_url).netloc if website_url else "unknown-site"
        ) or "unknown-site"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_path = Path("reports")
        reports_path.mkdir(parents=True, exist_ok=True)
        path = reports_path / f"audit_crew_kickoff_{domain}_{timestamp}.txt"

        parts: list[str] = []
        parts.append("=== Raw Output ===\n")
        parts.append(str(crew_result.raw))
        parts.append("\n\n=== JSON Output ===\n")
        if crew_result.json_dict:
            parts.append(json.dumps(crew_result.json_dict, indent=2))
        else:
            parts.append("(none)")
        parts.append("\n\n=== Pydantic Output ===\n")
        if crew_result.pydantic:
            p = crew_result.pydantic
            parts.append(
                p.model_dump_json(indent=2) if hasattr(p, "model_dump_json") else str(p)
            )
        else:
            parts.append("(none)")
        parts.append("\n\n=== Tasks Output ===\n")
        parts.append(str(crew_result.tasks_output))
        parts.append("\n\n=== Token Usage ===\n")
        parts.append(str(crew_result.token_usage))

        path.write_text("".join(parts), encoding="utf-8")
        return path

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
            "total_word_count": self.state.factual_metrics.total_word_count,
            "images_missing_alt_text_pct": (
                self.state.factual_metrics.images_missing_alt_text_pct
            ),
        }
        insights_crew = InsightsCrew().crew()
        crew_result = insights_crew.kickoff(inputs=inputs)
        self.state.insights_crew_output = InsightsCrewOutput(
            kpis=crew_result["kpis"],
            structured_report=crew_result["structured_report"],
        )

        debug_path = self._save_crew_kickoff_debug(crew_result, self.state.website_url)
        print(f"Crew kickoff debug saved to {debug_path}")

        print("Insights crew successfully run. \n")

    @listen("run_insights_crew")
    def run_recommendations_crew(self):
        """
        Run the recommendations crew
        """
        print("Running recommendations crew...")

        inputs = {
            "website_url": self.state.website_url,
            "factual_metrics": self.state.factual_metrics.model_dump_json(indent=2),
            "page_content": self.state.page_content,
            "cta_count": self.state.factual_metrics.cta_count,
            "total_word_count": self.state.factual_metrics.total_word_count,
            "images_missing_alt_text_pct": (
                self.state.factual_metrics.images_missing_alt_text_pct
            ),
            "insights_crew_output": self.state.insights_crew_output.model_dump_json(
                indent=2
            ),
        }
        recommendations_crew = RecommendationCrew().crew()
        crew_result = recommendations_crew.kickoff(inputs=inputs)
        self.state.recommendations_crew_output = RecommendationCrewOutput(
            recommendations=crew_result["recommendations"],
            validation_status=crew_result["validation_status"],
        )

        debug_path = self._save_crew_kickoff_debug(crew_result, self.state.website_url)
        print(f"Crew kickoff debug saved to {debug_path}")

        print("Recommendations crew successfully run. \n")
