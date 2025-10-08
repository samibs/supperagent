from .base import Agent, LLMModel

class ProjectArchitectAgent(Agent):
    """
    The Project Architect Agent defines the high-level system design,
    data models, technology stack, and modular breakdown.
    """
    def __init__(self):
        super().__init__("ProjectArchitectAgent")

    def execute_task(self, task_description: str) -> str:
        """
        Generates the software architecture based on the project requirements.

        Args:
            task_description (str): The high-level requirements for the project.

        Returns:
            str: The generated architectural plan.
        """
        self.log.info("Generating system architecture...")
        self.log.debug(f"Task: {task_description}")

        # For architectural planning, a creative and verbose model like Claude is ideal.
        prompt = (
            "Based on the following requirements, design a high-level system "
            "architecture, including the technology stack, data models, and a "
            f"modular breakdown:\n\n{task_description}"
        )

        architecture_plan = self._invoke_llm(model="claude", prompt=prompt)

        self.log.info("Architecture plan generated successfully.")
        return architecture_plan