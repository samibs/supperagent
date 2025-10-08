import datetime
import os
import logging

log = logging.getLogger('AgentOS.KnowledgeManager')

class KnowledgeManager:
    """
    Manages the creation and updating of knowledge base files for LLMs.

    This class is responsible for recording each interaction with an LLM
    into a dedicated markdown file (e.g., `claude.md`). This creates a
    persistent, human-readable log of model performance and usage over time.
    """
    def __init__(self, base_path: str = '.'):
        """
        Initializes the KnowledgeManager.

        Args:
            base_path (str): The root directory where knowledge base files
                             will be stored. Defaults to the current directory.
        """
        self.base_path = base_path
        log.info("KnowledgeManager initialized.")

    def record_interaction(self, model_family: str, success: bool, prompt: str, response: str):
        """
        Records a single LLM interaction to its corresponding markdown file.

        Args:
            model_family (str): The family of the model used (e.g., 'claude').
            success (bool): Whether the API call was successful.
            prompt (str): The prompt that was sent to the LLM.
            response (str): The response received from the LLM.
        """
        filename = os.path.join(self.base_path, f"{model_family}.md")
        timestamp = datetime.datetime.now().isoformat()
        status = "✅ SUCCESS" if success else "❌ FAILED"

        # Create a formatted markdown entry
        entry = (
            f"## Interaction at {timestamp}\n\n"
            f"**Status:** {status}\n\n"
            f"### Prompt Snippet:\n\n"
            f"```\n{prompt[:500]}...\n```\n\n"
            f"### Response Snippet:\n\n"
            f"```\n{response[:500]}...\n```\n\n"
            f"---\n\n"
        )

        try:
            with open(filename, 'a') as f:
                # If the file is new, write a header.
                if f.tell() == 0:
                    f.write(f"# Knowledge Base for {model_family.capitalize()}\n\n")
                f.write(entry)
            log.debug(f"Recorded interaction to '{filename}'.")
        except IOError as e:
            log.error(f"Failed to write to knowledge base file '{filename}': {e}")

# Create a singleton instance to be used across the application
knowledge_manager = KnowledgeManager()