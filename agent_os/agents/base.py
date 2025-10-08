import logging
from abc import ABC, abstractmethod
from typing import Literal

# Get a logger for the base agent
log = logging.getLogger('AgentOS.Agent')

# Import the modules we need, but not the config object itself.
from .. import llm_client
from .. import config_loader
from ..knowledge_manager import knowledge_manager

LLMModel = Literal["claude", "gemini", "codex"]

class Agent(ABC):
    """
    An abstract base class for all specialized agents in the AgentOS.
    """
    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(f'AgentOS.{self.name}')
        self.log.debug(f"Agent '{self.name}' initialized.")

    def _invoke_llm(self, model: LLMModel, prompt: str) -> str:
        """
        Invokes a specified LLM and records the interaction in the knowledge base.

        This method now calls `load_config()` at runtime, avoiding import-time
        side effects.
        """
        self.log.info(f"Preparing to invoke LLM '{model}' for task...")
        self.log.debug(f"LLM Prompt: {prompt[:100]}...")

        response = ""
        success = False
        try:
            # Load config at runtime, just before it's needed.
            config = config_loader.load_config()
            specific_model_name = config['models'][model]

            if model == 'claude':
                response = llm_client.call_anthropic(prompt, model=specific_model_name)
            else: # Fallback for simulated models
                response = f"--- SIMULATED RESPONSE ({model.capitalize()}) ---\nModel '{specific_model_name}' would be called for: {prompt}"
                self.log.warning(f"{model.capitalize()} client not yet implemented. Returning simulated response.")

            success = True
            self.log.debug(f"LLM Response: {response[:100]}...")

        except FileNotFoundError as e:
            response = str(e)
            self.log.error(str(e), exc_info=True)
        except KeyError:
            response = f"ERROR: Model '{model}' is not configured."
            self.log.error(f"Model '{model}' not found in config.yaml. Please check your configuration.")
        except Exception as e:
            response = f"ERROR: Failed to get response from LLM. Check logs for details."
            self.log.error(f"An error occurred during LLM invocation: {e}", exc_info=True)
        finally:
            knowledge_manager.record_interaction(
                model_family=model,
                success=success,
                prompt=prompt,
                response=response
            )

        return response

    @abstractmethod
    def execute_task(self, task_description: str) -> str:
        pass