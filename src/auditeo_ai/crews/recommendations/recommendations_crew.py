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
        Strategy Lead Agent.
        Formulates 3-5 high-impact, prioritized recommendations for the website.
        """
        return Agent(
            config=self.agents_config["strategy_lead"],
            verbose=self._enable_verbose(),
            llm=LLMs.gpt_5_4,
        )

    @agent
    def strategy_validator(self) -> Agent:
        """
        Strategy Validator Agent.
        Critically validates that every recommendation is 100% grounded in the factual
        metrics.

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
