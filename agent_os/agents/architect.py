from .base import Agent, LLMModel
from ..memory_manager import memory_manager

class ProjectArchitectAgent(Agent):
    """
    The Project Architect Agent defines the high-level system design,
    data models, technology stack, and modular breakdown. It can query
    long-term memory to learn from past projects.
    """
    def __init__(self):
        super().__init__("ProjectArchitectAgent")

    def execute_task(self, task_description: str) -> str:
        """
        Generates the software architecture based on the project requirements,
        first consulting long-term memory for similar past projects.

        Args:
            task_description (str): The high-level requirements for the project.

        Returns:
            str: The generated architectural plan.
        """
        self.log.info("Generating system architecture...")

        # 1. Query long-term memory for relevant past projects.
        self.log.info("Querying long-term memory for relevant past projects...")
        relevant_memories = memory_manager.query_memory(task_description, n_results=2)

        memory_context = "No relevant past projects found."
        if relevant_memories.get('documents'):
            self.log.info(f"Found {len(relevant_memories['documents'][0])} relevant memories.")
            memory_context = "Here are some similar projects we've completed in the past:\n\n"
            for doc in relevant_memories['documents'][0]:
                memory_context += f"---\n{doc}\n---\n\n"
        else:
            self.log.info("No relevant memories found.")

        # 2. Construct a prompt that includes the retrieved memories.
        prompt = (
            "You are a world-class software architect. Your task is to design a high-level system architecture. "
            "Before you begin, review the following context from our long-term memory of past projects.\n\n"
            f"--- MEMORY CONTEXT ---\n{memory_context}\n\n"
            "--- CURRENT TASK ---\n"
            "Based on the memory context and the following requirements, design a high-level system "
            "architecture, including the technology stack, data models, and a modular breakdown:\n\n"
            f"'{task_description}'"
        )

        # 3. Invoke the LLM with the enhanced prompt.
        architecture_plan = self._invoke_llm(model="claude", prompt=prompt)

        self.log.info("Architecture plan generated successfully.")
        return architecture_plan