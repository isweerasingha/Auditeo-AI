from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from auditeo_ai.config import LLMs
from auditeo_ai.models import RecommendationCrewOutput
from auditeo_ai.utils import is_development


@CrewBase
class RecommendationCrew:
    """
    Recommendations Crew.

    Using the extracted Insights, generate recommendations for the client.
    """

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def strategy_lead(self) -> Agent:
        """
        Analyst Agent.
        Analyzes the metrics and page content.
        """
        return Agent(
            config=self.agents_config["strategy_lead"],
            verbose=self._enable_verbose(),
            llm=LLMs.gpt_5_4,
        )

    @agent
    def strategy_validator(self) -> Agent:
        """
        Reporter Agent.
        Formats the analysis into a report.
        """
        return Agent(
            config=self.agents_config["strategy_validator"],
            verbose=self._enable_verbose(),
            llm=LLMs.gpt_5_4_mini,
        )

    @task
    def recommendation_task(self) -> Task:
        """
        Analysis Task
        """
        return Task(
            config=self.tasks_config["recommendation_task"],
        )

    @task
    def validation_task(self) -> Task:
        """
        Reporting Task
        """
        return Task(
            config=self.tasks_config["validation_task"],
            output_pydantic=RecommendationCrewOutput,
        )

    @crew
    def crew(self) -> Crew:
        """
        Crew
        """

        print(f"Agents: {self.agents}")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self._enable_verbose(),
        )

    def _enable_verbose(self) -> bool:
        """Enable verbose mode."""
        return is_development()
