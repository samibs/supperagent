import unittest
import os
import logging
from unittest.mock import patch, MagicMock

# Import the config module so we can call its setup function.
from agent_os import logging_config

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