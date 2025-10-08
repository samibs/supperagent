import os
import subprocess
import tempfile
from .base import Agent, LLMModel

class TroubleshootingQAAgent(Agent):
    """
    The Troubleshooting/QA Agent analyzes generated code, generates unit tests,
    and then executes those tests to verify the code's correctness.
    """
    def __init__(self):
        super().__init__("TroubleshootingQAAgent")

    def _run_unit_tests(self, test_code: str) -> tuple[bool, str]:
        """
        A tool that executes a string of Python `unittest` code.

        This method saves the test code to a temporary file and runs it
        using `subprocess`. It captures the output and determines if the
        tests passed or failed.

        Args:
            test_code (str): The string containing the unit test code.

        Returns:
            tuple[bool, str]: A tuple containing a boolean for success
                              and a string with the captured output.
        """
        self.log.info("Executing generated unit tests...")
        # Use a temporary file to store and run the test code.
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            # Basic sanitization to remove markdown code fences if the LLM includes them
            cleaned_test_code = test_code.strip().removeprefix("```python").removesuffix("```").strip()
            tmp.write(cleaned_test_code)
            test_filename = tmp.name

        try:
            # Run the test file using the unittest module.
            process = subprocess.run(
                ["python3", "-m", "unittest", test_filename],
                capture_output=True,
                text=True,
                timeout=30  # Prevent hanging tests
            )

            output = process.stdout + "\n" + process.stderr
            # A simple success check: "OK" must be in the standard error output.
            success = "OK" in process.stderr

            if success:
                self.log.info("Unit tests passed successfully.")
            else:
                self.log.warning("Unit tests failed or had errors.")

            return success, output
        except FileNotFoundError:
            self.log.error("`python3` command not found. Cannot run unit tests.")
            return False, "`python3` not found. Please ensure it's in the system's PATH."
        except subprocess.TimeoutExpired:
            self.log.error("Unit test execution timed out.")
            return False, "Test execution timed out after 30 seconds."
        finally:
            # Clean up the temporary file
            os.remove(test_filename)

    def execute_task(self, code_to_review: str) -> str:
        """
        Reviews code, generates unit tests, and runs them.

        This method performs three key functions:
        1. Critiques the code for bugs and style issues.
        2. Generates `unittest` code based on the code to review.
        3. Executes the generated tests and reports the results.

        Args:
            code_to_review (str): The Python code to be reviewed.

        Returns:
            str: A combined report with the critique, tests, and test results.
        """
        self.log.info("Performing full QA cycle: critique, test generation, and execution.")

        critique_prompt = (
            "Critically review the following Python code. Identify potential bugs, "
            "inefficiencies, style violations (PEP 8), and areas with poor "
            "logging or error handling. Provide a clear, actionable list of "
            f"feedback.\n\n```python\n{code_to_review}\n```"
        )
        critique = self._invoke_llm(model="gemini", prompt=critique_prompt)

        test_generation_prompt = (
            "Based on the following Python code, generate a complete and runnable "
            "unit test file using Python's built-in `unittest` framework. "
            "The code must be self-contained, executable, and import all necessary modules. "
            "Do not use placeholder comments."
            f"\n\n--- Code to Test ---\n```python\n{code_to_review}\n```"
        )
        unit_tests = self._invoke_llm(model="gemini", prompt=test_generation_prompt)

        # Use the new tool to run the generated tests.
        tests_passed, test_output = self._run_unit_tests(unit_tests)
        test_result_summary = "PASSED ✅" if tests_passed else "FAILED ❌"

        self.log.info(f"QA cycle complete. Test result: {test_result_summary}")

        return (
            f"--- QA Critique ---\n{critique}\n\n"
            f"--- Generated Unit Tests ---\n```python\n{unit_tests}\n```\n\n"
            f"--- Test Execution Results ---\n"
            f"**Result:** {test_result_summary}\n\n"
            f"**Output:**\n```\n{test_output}\n```"
        )