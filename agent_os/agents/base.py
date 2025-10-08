import logging
from abc import ABC, abstractmethod
from typing import Literal, Callable, List, Tuple

# Get a logger for the base agent
log = logging.getLogger('AgentOS.Agent')

from .. import llm_client
from .. import config_loader
from ..knowledge_manager import knowledge_manager

LLMModel = Literal["claude", "gemini", "codex"]

class Agent(ABC):
    """An abstract base class for all specialized agents in the AgentOS."""
    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(f'AgentOS.{self.name}')
        self.log.debug(f"Agent '{self.name}' initialized.")

    def _get_available_clients(self) -> List[Tuple[LLMModel, Callable]]:
        """Checks which LLM clients are configured and returns them in a preferred order."""
        available = []
        # The order here defines the fallback priority: Claude -> Gemini -> Codex
        if llm_client.get_anthropic_client():
            available.append(("claude", llm_client.call_anthropic))
        if llm_client.get_gemini_client():
            available.append(("gemini", llm_client.call_gemini))
        if llm_client.get_openai_client():
            available.append(("codex", llm_client.call_openai))
        return available

    def _invoke_llm(self, preferred_model: LLMModel, prompt: str) -> str:
        """
        Invokes an LLM with dynamic fallback and records the interaction.

        If the preferred model's client is not available, it will intelligently
        fall back to another configured client.
        """
        self.log.info(f"Invocation requested for preferred model '{preferred_model}'.")

        available_clients = self._get_available_clients()
        if not available_clients:
            error_msg = "No LLM clients are configured. Please check your config.yaml."
            log.error(error_msg)
            return f"ERROR: {error_msg}"

        # Find the preferred client, or fall back to the first available one.
        client_to_use = None
        model_family_to_use = None

        # Check if preferred client is available
        for family, client_func in available_clients:
            if family == preferred_model:
                client_to_use = client_func
                model_family_to_use = family
                break

        # If preferred is not found, fall back to the first available one
        if not client_to_use:
            model_family_to_use, client_to_use = available_clients[0]
            self.log.warning(
                f"Preferred model '{preferred_model}' is not available. "
                f"Falling back to '{model_family_to_use}'."
            )

        response = ""
        success = False
        try:
            config = config_loader.load_config()
            specific_model_name = config['models'][model_family_to_use]

            self.log.info(f"Dispatching to actual client '{model_family_to_use}' with model '{specific_model_name}'.")
            response = client_to_use(prompt, model=specific_model_name)

            success = True
            log.debug(f"LLM Response: {response[:100]}...")

        except Exception as e:
            response = f"ERROR: API call to '{model_family_to_use}' failed. Details: {e}"
            log.error(response, exc_info=True)
        finally:
            knowledge_manager.record_interaction(
                model_family=model_family_to_use,
                success=success,
                prompt=prompt,
                response=response
            )

        return response

    @abstractmethod
    def execute_task(self, task_description: str) -> str:
        pass