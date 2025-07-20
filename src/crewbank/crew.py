from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
from crewbank.tools.custom_tool import NERTool, CSVReaderTool

load_dotenv()


# llm = LLM(
#     model = "ollama/mistral:latest",
#     base_url="http://localhost:11434",
#     temperature=0.7
# )

llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.7
)


@CrewBase
class Crewbank():
    """Crewbank crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def csv_reader(self) -> Agent:
        return Agent(
            config={**self.agents_config['csv_reader'], "tool_only": True},
            verbose=True,
            tools=[CSVReaderTool()],
            llm=llm
        )

    @agent
    def ner(self) -> Agent:
        return Agent(
            config={**self.agents_config['ner'], "tool_only": True},
            verbose=True,
            tools=[NERTool()],
            llm=llm
        )

    @task
    def read_csv_task(self) -> Task:
        return Task(
            config=self.tasks_config['read_csv_task'], # type: ignore[index]
        )

    @task
    def ner_task(self) -> Task:
        return Task(
            config=self.tasks_config['ner_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Crewbank crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
