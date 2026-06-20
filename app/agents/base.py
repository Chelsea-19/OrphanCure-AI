"""Base agent abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.config.settings import Settings
from app.models.state import UnifiedRunState
from app.services.llm_provider import GeminiProvider


class BaseAgent(ABC):
    """
    Abstract base for all domain-specific agents.

    Every agent receives the shared run state and an LLM provider.
    Agents read from and write to the state during `execute()`.
    """

    name: str = "BaseAgent"

    def __init__(self, state: UnifiedRunState, llm: GeminiProvider, settings: Settings):
        self.state = state
        self.llm = llm
        self.settings = settings

    @abstractmethod
    def execute(self) -> None:
        """Run the agent's primary workload, mutating `self.state` in place."""
        ...

    def log(self, message: str, status: str = "INFO", details=None) -> None:
        self.state.log(agent=self.name, message=message, status=status, details=details)
