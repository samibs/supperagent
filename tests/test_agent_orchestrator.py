import unittest
import os
import logging
from unittest.mock import patch, MagicMock

# Import the config module so we can call its setup function.
from agent_os import logging_config
from agent_os.agents.base import Agent

# We patch `load_config` at the top level of the test module.
# This ensures that any import-time or runtime call to this function
# within the test session will be intercepted by our mock.
@patch('agent_os.config_loader.load_config', return_value={
    'api_keys': {'anthropic': 'test-key-is-mocked'},
    'models': {
        'claude': 'claude-test-model',
        'gemini': 'gemini-test-model',
        'codex': 'codex-test-model'
    }
})
class TestAgentOrchestrator(unittest.TestCase):
    """
    Unit tests for the Orchestrator and the agent workflow.
    """

    def setUp(self):
        """
        Set up a fresh environment for each test.
        The mock objects from the class decorator are not passed here.
        """
        logger = logging.getLogger('AgentOS')
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logging_config.setup_logging()

        # Clean up state files from previous runs
        for f in ["workflow_state.json", "claude.md", "gemini.md"]:
            if os.path.exists(f):
                os.remove(f)

    def tearDown(self):
        """Clean up created files after tests."""
        if os.path.exists("agent_os.log"):
            os.remove("agent_os.log")
        for f in ["workflow_state.json", "claude.md", "gemini.md"]:
            if os.path.exists(f):
                os.remove(f)

    def test_orchestrator_initialization(self, mock_load_config):
        """
        Test that the Orchestrator initializes correctly.
        This test method receives the mock from the class decorator.
        """
        from agent_os.orchestrator import Orchestrator
        orchestrator = Orchestrator({})
        self.assertEqual(len(orchestrator.agents), 0)
        self.assertEqual(orchestrator.workflow_phase, "Idle")

    @patch('builtins.input', return_value='approve')
    @patch('agent_os.agents.documentation.DocumentationAgent')
    @patch('agent_os.agents.troubleshooting_qa.TroubleshootingQAAgent')
    @patch('agent_os.agents.security.SecurityAgent')
    @patch('agent_os.agents.coder.CoderAgent')
    @patch('agent_os.agents.ui_ux_designer.UIUXDesignerAgent')
    @patch('agent_os.agents.database.DatabaseAgent')
    @patch('agent_os.agents.architect.ProjectArchitectAgent')
    def test_full_workflow_with_hil_approval(self, mock_architect_class, mock_db_class,
                                             mock_ui_class, mock_coder_class,
                                             mock_security_class, mock_qa_class,
                                             mock_docs_class, mock_input, mock_load_config):
        """
        Tests the full 7-phase workflow, mocking agent classes completely
        to focus on the Orchestrator's logic and state transitions.
        """
        # --- Arrange ---
        # Instantiate the mocked agent classes
        mock_architect = mock_architect_class.return_value
        mock_db = mock_db_class.return_value
        mock_ui = mock_ui_class.return_value
        mock_coder = mock_coder_class.return_value
        mock_security = mock_security_class.return_value
        mock_qa = mock_qa_class.return_value
        mock_docs = mock_docs_class.return_value

        # Set up return values for the mocked methods
        mock_architect.execute_task.return_value = "Architecture plan."
        mock_db.execute_task.return_value = "DB plan."
        mock_ui.execute_task.return_value = "UI plan."
        mock_coder.execute_task.side_effect = ["vulnerable_code", "fixed_code"]
        mock_security.execute_task.return_value = "Security feedback."
        mock_qa.execute_task.side_effect = ["QA feedback.", "Verification report."]
        mock_docs.execute_task.return_value = "Final documentation."

        from agent_os.orchestrator import Orchestrator
        orchestrator = Orchestrator({
            "architect": mock_architect, "coder": mock_coder,
            "database": mock_db, "documentation": mock_docs,
            "security": mock_security, "qa": mock_qa, "ui_ux": mock_ui,
        })

        # --- Act ---
        orchestrator.run_workflow("Test a full workflow.")

        # --- Assert ---
        self.assertEqual(orchestrator.workflow_phase, "Completed")
        mock_input.assert_called_once()
        self.assertEqual(mock_coder.execute_task.call_count, 2)

        logging.shutdown()
        self.assertTrue(os.path.exists("agent_os.log"))
        with open("agent_os.log", "r") as f:
            log_content = f.read()
            self.assertIn("Human operator approved agent feedback", log_content)

if __name__ == '__main__':
    unittest.main()


@patch('agent_os.config_loader.load_config', return_value={
    'api_keys': {'anthropic': 'test-key-is-mocked'},
    'models': {
        'claude': 'claude-test-model',
        'gemini': 'gemini-test-model',
        'codex': 'codex-test-model'
    }
})
class TestCoderAgentTRM(unittest.TestCase):
    """
    Unit tests specifically for the CoderAgent's TRM (Think, Reflect, Modify) logic.
    """

    def setUp(self):
        """
        Set up a fresh CoderAgent for each test.
        The mock from the class decorator is not passed to setUp.
        """
        from agent_os.agents.coder import CoderAgent
        self.coder_agent = CoderAgent()

    def tearDown(self):
        """Clean up knowledge base files if they are created."""
        if os.path.exists("codex.md"):
            os.remove("codex.md")

    @patch.object(Agent, '_invoke_llm')
    def test_trm_cycle_and_confidence_exit(self, mock_invoke_llm, mock_load_config):
        """
        Verify that the CoderAgent performs the TRM cycle correctly and
        exits when the confidence threshold is met.
        """
        # --- Arrange ---
        # This list simulates the sequence of LLM responses through two full TRM cycles.
        mock_invoke_llm.side_effect = [
            # --- Cycle 1 ---
            'Initial draft code.',          # 1. Draft
            'Refined reasoning 1.1',        # 2. Critique loop
            'Refined reasoning 1.2',
            'Refined reasoning 1.3',
            'Refined reasoning 1.4',
            'Refined reasoning 1.5',
            'Refined reasoning 1.6',
            'Revised draft 1.',             # 8. Revise
            '6',                            # 9. Confidence check (fails, score < 7)

            # --- Cycle 2 ---
            'Refined reasoning 2.1',        # 10. Critique loop
            'Refined reasoning 2.2',
            'Refined reasoning 2.3',
            'Refined reasoning 2.4',
            'Refined reasoning 2.5',
            'Refined reasoning 2.6',
            'Final revised draft.',         # 16. Revise
            '9',                            # 17. Confidence check (passes, score >= 7)
        ]

        # --- Act ---
        final_code = self.coder_agent.execute_task("Build a simple calculator.")

        # --- Assert ---
        # It should take 17 LLM calls to complete two cycles and exit.
        self.assertEqual(mock_invoke_llm.call_count, 17)

        # The final returned code should be the last revised draft.
        self.assertEqual(final_code, 'Final revised draft.')