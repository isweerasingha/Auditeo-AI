from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from auditeo_ai.utils import is_development


@CrewBase
class AuditCrew(Crew):
    """
    Audit Crew
    """

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def analyst_agent(self) -> BaseAgent:
        """
        Analyst Agent
        """
        return Agent(
            config=self.agents_config["analyst_agent"],
            verbose=self._enable_verbose(),
        )

    @agent
    def reporter_agent(self) -> BaseAgent:
        """
        Reporter Agent
        """
        return Agent(
            config=self.agents_config["reporter_agent"],
            verbose=self._enable_verbose(),
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
        Audit Crew
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
