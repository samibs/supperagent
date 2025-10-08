from .base import Agent, LLMModel

class SecurityAgent(Agent):
    """
    The Security Agent focuses on vulnerability detection and secure coding
    practices, suggesting security-focused fixes.
    """
    def __init__(self):
        super().__init__("SecurityAgent")

    def execute_task(self, code_snippet: str) -> str:
        """
        Analyzes a code snippet for potential security vulnerabilities.

        Args:
            code_snippet (str): The source code to analyze.

        Returns:
            str: A report of security vulnerabilities and suggested fixes.
        """
        self.log.info("Analyzing code for security vulnerabilities...")

        # A model with strong analytical and code-review capabilities would be best.
        prompt = (
            "Review the following Python code for security vulnerabilities. "
            "Focus on common issues like injection flaws, improper error handling, "
            "and insecure dependencies. Provide a list of findings with "
            f"suggested fixes:\n\n```python\n{code_snippet}\n```"
        )

        security_report = self._invoke_llm(model="gemini", prompt=prompt)

        self.log.info("Security analysis complete.")
        return security_report