from .base import Agent, LLMModel

class UIUXDesignerAgent(Agent):
    """
    The UI/UX Designer Agent specifies accessible front-end structures,
    component interaction, and ensures WCAG compliance.
    """
    def __init__(self):
        super().__init__("UIUXDesignerAgent")

    def execute_task(self, component_description: str) -> str:
        """
        Generates a UI/UX specification for a component with a focus on accessibility.

        Args:
            component_description (str): A description of the UI component needed.

        Returns:
            str: A specification including HTML structure and accessibility notes.
        """
        self.log.info("Generating UI/UX specification...")
        self.log.debug(f"Component to design: {component_description}")

        # A model that is good at following structured rules like WCAG is needed.
        prompt = (
            "Design the HTML structure for the following UI component. "
            "Ensure it is fully WCAG compliant. Specifically, include `<label>` "
            "tags for all form inputs and use appropriate ARIA roles where necessary. "
            "Provide the HTML structure and a list of accessibility considerations."
            f"\n\n--- Component Description ---\n{component_description}"
        )

        ui_spec = self._invoke_llm(model="claude", prompt=prompt)

        self.log.info("UI/UX specification generated.")
        return ui_spec