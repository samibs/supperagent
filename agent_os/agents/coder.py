from .base import Agent, LLMModel

class CoderAgent(Agent):
    """
    The Coder Agent generates the actual implementation code for components
    defined by the Project Architect.
    """
    def __init__(self):
        super().__init__("CoderAgent")

    def execute_task(self, component_specification: str) -> str:
        """
        Generates Python code for a given component specification.

        Args:
            component_specification (str): A detailed description of the
                                           component to be built.

        Returns:
            str: The generated Python code for the component.
        """
        self.log.info("Generating code for component...")
        self.log.debug(f"Specification: {component_specification}")

        # For pure code generation, a specialized model like Codex is the best fit.
        prompt = (
            "Based on the following specification, write a clean, well-documented "
            "Python module. Adhere to PEP 8 standards and include docstrings "
            "for all public functions and classes."
            f"\n\n--- Specification ---\n{component_specification}"
        )

        generated_code = self._invoke_llm(model="codex", prompt=prompt)

        self.log.info("Code generation complete.")
        return generated_code