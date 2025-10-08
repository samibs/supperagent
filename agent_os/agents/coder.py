import os
import subprocess
import tempfile
from .base import Agent, LLMModel

# Constants for the TRM process
MAX_CYCLES = 16
CRITIQUE_LOOPS = 6

class CoderAgent(Agent):
    """
    The Coder Agent uses an advanced "Think, Reflect, Modify" (TRM)
    reasoning model and self-correction tools to generate high-quality code.
    """
    def __init__(self):
        super().__init__("CoderAgent")

    def _run_linter(self, code_to_lint: str) -> str | None:
        """A tool to run the ruff linter on code and return issues."""
        self.log.info("TRM Tool: Running linter on generated code...")

        # --- Linter Guard ---
        # Check if the input looks like Python code before trying to lint.
        # This prevents errors if the LLM returns a prose explanation instead of code.
        if not any(kw in code_to_lint for kw in ['def ', 'class ', 'import ']):
            self.log.warning("Linter skipped: Input does not appear to be Python code.")
            return "Linter skipped: The provided text was not valid Python code."

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            # Clean up potential markdown fences from the LLM output
            cleaned_code = code_to_lint.strip().removeprefix("```python").removesuffix("```").strip()
            tmp.write(cleaned_code)
            filename = tmp.name

        try:
            process = subprocess.run(
                ["ruff", "check", filename],
                capture_output=True, text=True, timeout=30
            )
            if not process.stdout:
                self.log.info("Linter found no issues.")
                return None

            self.log.warning(f"Linter found issues:\n{process.stdout}")
            return process.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.log.error(f"Failed to run ruff linter: {e}")
            return f"Linter execution failed: {e}"
        finally:
            os.remove(filename)

    def _draft_initial_answer(self, component_specification: str) -> str:
        """Generates a quick, rough draft of the code."""
        self.log.info("TRM: Drafting initial answer...")
        prompt = (
            "Generate a complete, rough draft of a Python module for the "
            f"following specification. Focus on getting a full implementation "
            f"down quickly; refinement will happen later.\n\n{component_specification}"
        )
        return self._invoke_llm(model="codex", prompt=prompt)

    def _self_critique_loop(self, draft: str, component_specification: str) -> str:
        """The 'thinking' scratchpad to refine logic."""
        self.log.info("TRM: Entering self-critique loop...")
        reasoning_scratchpad = "Initial thoughts on the draft."
        for i in range(CRITIQUE_LOOPS):
            self.log.debug(f"  Critique loop {i+1}/{CRITIQUE_LOOPS}...")
            prompt = (
                "You are self-critiquing a draft solution. Your goal is to improve your reasoning. "
                f"The original problem was: '{component_specification}'\n"
                f"The current draft is:\n```python\n{draft}\n```\n"
                f"Your current reasoning is: '{reasoning_scratchpad}'\n\n"
                "Provide a new, more refined line of reasoning."
            )
            reasoning_scratchpad = self._invoke_llm(model="claude", prompt=prompt)
        return reasoning_scratchpad

    def _revise_answer(self, component_specification: str, original_draft: str, refined_reasoning: str) -> str:
        """Revises the draft based on the refined logic."""
        self.log.info("TRM: Revising answer based on refined reasoning...")
        prompt = (
            "You will revise a code draft. Use your refined reasoning to create a new, much better version of the code.\n"
            f"Original Specification:\n{component_specification}\n"
            f"Original (Flawed) Draft:\n```python\n{original_draft}\n```\n"
            f"Your Final, Refined Reasoning:\n{refined_reasoning}\n\n"
            "Now, write the new, complete, and correct Python module."
        )
        return self._invoke_llm(model="codex", prompt=prompt)

    def _check_confidence(self, cycle_number: int, new_draft: str) -> bool:
        """Performs a self-assessment to generate a confidence score for the draft."""
        self.log.info("TRM: Performing self-assessment for confidence score...")
        prompt = (
            "You are a code reviewer. On a scale of 1 to 10, rate the following code. "
            "Your answer must be a single integer and nothing else.\n"
            f"--- Code to Rate ---\n```python\n{new_draft}\n```"
        )

        try:
            score_response = self._invoke_llm(model="gemini", prompt=prompt)
            score_str = ''.join(filter(str.isdigit, score_response))
            if not score_str:
                self.log.warning("Confidence check failed: LLM did not return a digit. Assuming low confidence.")
                return False
            score = int(score_str)
            self.log.info(f"TRM: Received confidence score of {score}/10.")
            confidence_threshold = 7 + (cycle_number // 4)
            is_confident = score >= confidence_threshold
            if is_confident:
                self.log.info(f"TRM: Confidence score {score} meets or exceeds threshold {confidence_threshold}.")
            else:
                self.log.info(f"TRM: Confidence score {score} is below threshold {confidence_threshold}.")
            return is_confident
        except Exception as e:
            self.log.error(f"Could not parse confidence score due to an error: {e}. Assuming low confidence.")
            return False

    def execute_task(self, component_specification: str) -> str:
        """Generates Python code using the full TRM and self-correction process."""
        self.log.info("Starting TRM code generation process...")
        current_draft = ""
        for i in range(MAX_CYCLES):
            self.log.info(f"TRM Cycle {i+1}/{MAX_CYCLES}...")
            if not current_draft:
                current_draft = self._draft_initial_answer(component_specification)

            refined_reasoning = self._self_critique_loop(current_draft, component_specification)
            new_draft = self._revise_answer(component_specification, current_draft, refined_reasoning)

            linter_issues = self._run_linter(new_draft)
            if linter_issues and "Linter skipped" not in linter_issues:
                self.log.info("TRM: Linter found issues. Performing self-correction.")
                correction_prompt = (
                    "Your previous code draft has been reviewed by the `ruff` linter, which found the following issues. "
                    "Please fix these specific issues and provide the complete, corrected code.\n\n"
                    f"--- Linter Issues ---\n{linter_issues}\n\n"
                    f"--- Original Code with Issues ---\n```python\n{new_draft}\n```"
                )
                new_draft = self._invoke_llm(model="codex", prompt=correction_prompt)
                self.log.info("TRM: Self-correction applied.")

            current_draft = new_draft
            if self._check_confidence(i, current_draft):
                break

        self.log.info("TRM process complete. Returning final code.")
        return current_draft