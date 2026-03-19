from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field

from auditeo_ai.config import LLMs
from auditeo_ai.models import InsightsKPIs
from auditeo_ai.utils import is_development


@CrewBase
class InsightsCrew(Crew):
    """
    Insights Crew.

    Using the extracted Factual Metrics and page content, generate a structured analysis
    covering:
    - SEO structure
    - Messaging clarity
    - CTA usage
    - Content depth
    - Obvious UX or structural concerns
    """

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def analyst_agent(self) -> BaseAgent:
        """
        Analyst Agent.
        Analyzes the metrics and page content.
        """
        return Agent(
            config=self.agents_config["analyst_agent"],
            verbose=self._enable_verbose(),
            llm=LLMs.gpt_5,
        )

    @agent
    def reporter_agent(self) -> BaseAgent:
        """
        Reporter Agent.
        Formats the analysis into a report.
        """
        return Agent(
            config=self.agents_config["reporter_agent"],
            verbose=self._enable_verbose(),
            output_pydantic=InsightsCrewOutput,
            llm=LLMs.gpt_5,
        )

    @task
    def analysis_task(self) -> Task:
        """
        Analysis Task
        """
        return Task(
            config=self.tasks_config["analysis_task"],
        )

    @task
    def reporting_task(self) -> Task:
        """
        Reporting Task
        """
        return Task(
            config=self.tasks_config["reporting_task"],
        )

    @crew
    def crew(self) -> Crew:
        """
        Crew
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self._enable_verbose(),
        )

    def _enable_verbose(self) -> bool:
        """Enable verbose mode."""
        return is_development()


class InsightsCrewOutput(BaseModel):
    kpis: InsightsKPIs
    structured_report: str = Field(
        description="The full Markdown report for the client."
    )
