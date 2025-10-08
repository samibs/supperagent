from .base import Agent, LLMModel

class DocumentationAgent(Agent):
    """
    The Documentation Agent creates docstrings, setup guides, and operational
    documentation for the generated code.
    """
    def __init__(self):
        super().__init__("DocumentationAgent")

    def execute_task(self, code_module_content: str) -> str:
        """
        Generates comprehensive documentation for a given code module.

        Args:
            code_module_content (str): The content of the Python module to document.

        Returns:
            str: A documentation report including docstrings and a README section.
        """
        self.log.info("Generating documentation for the code module...")

        # A model excelling at prose and structured text is best for documentation.
        prompt = (
            "Given the following Python code, please generate comprehensive "
            "documentation. This should include: "
            "1. A high-level description of the module's purpose. "
            "2. Docstrings for all public classes and functions. "
            "3. A 'How to Run' section, including how to run the unit tests. "
            "4. A list of dependencies."
            f"\n\n--- Code ---\n{code_module_content}"
        )

        documentation = self._invoke_llm(model="claude", prompt=prompt)

        self.log.info("Documentation generation complete.")
        return documentation