import os
from dataclasses import dataclass

from crewai import LLM


@dataclass
class LLMCollection:
    gpt_5: LLM
    gpt_4o_mini: LLM
    gpt_4o: LLM


LLMs = LLMCollection(
    gpt_5=LLM(
        model="gpt-5",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    gpt_4o_mini=LLM(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    gpt_4o=LLM(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
)
