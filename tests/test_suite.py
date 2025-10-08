import unittest
import os
import logging
from unittest.mock import patch

from agent_os import logging_config
from agent_os.orchestrator import Orchestrator
from agent_os.agents.coder import CoderAgent

MOCK_CONFIG = {
    'api_keys': {'anthropic': 'test-key-is-mocked'},
    'models': {
        'claude': 'claude-test-model', 'gemini': 'gemini-test-model', 'codex': 'codex-test-model'
    }
}

@patch('agent_os.llm_client.config_loader.load_config', return_value=MOCK_CONFIG)
@patch('agent_os.agents.base.config_loader.load_config', return_value=MOCK_CONFIG)
class TestSuite(unittest.TestCase):
    """A stable, unified test suite for the main orchestrator and agent workflows."""

    def setUp(self):
        """Set up a clean environment for each test. This method does NOT receive class-level mocks."""
        logger = logging.getLogger('AgentOS')
        for handler in logger.handlers[:]: logger.removeHandler(handler)
        logging_config.setup_logging()
        for f in ["workflow_state.json", "claude.md", "gemini.md", "codex.md"]:
            if os.path.exists(f): os.remove(f)

    def tearDown(self):
        """Clean up any created files."""
        if os.path.exists("agent_os.log"): os.remove("agent_os.log")
        for f in ["workflow_state.json", "claude.md", "gemini.md", "codex.md"]:
            if os.path.exists(f): os.remove(f)

    @patch('agent_os.orchestrator.ProjectArchitectAgent')
    @patch('agent_os.orchestrator.DatabaseAgent')
    @patch('agent_os.orchestrator.UIUXDesignerAgent')
    @patch('agent_os.orchestrator.CoderAgent')
    @patch('agent_os.orchestrator.SecurityAgent')
    @patch('agent_os.orchestrator.TroubleshootingQAAgent')
    @patch('agent_os.orchestrator.DocumentationAgent')
    @patch('rich.console.Console.input', return_value='approve')
    @patch('agent_os.orchestrator.memory_manager.add_memory')
    def test_full_workflow_with_hil_approval(self, mock_add_memory, mock_input,
                                             mock_docs_class, mock_qa_class, mock_security_class,
                                             mock_coder_class, mock_ui_class, mock_db_class,
                                             mock_architect_class, mock_base_config, mock_llm_config):
        """Tests the full 7-phase workflow, mocking all external dependencies."""
        mock_architect_class.return_value.execute_task.return_value = "Mocked Arch Plan"
        mock_db_class.return_value.execute_task.return_value = "Mocked DB Plan"
        mock_ui_class.return_value.execute_task.return_value = "Mocked UI Plan"
        mock_coder_class.return_value.execute_task.side_effect = ["vulnerable_code", "fixed_code"]
        mock_security_class.return_value.execute_task.return_value = "Mocked Security Feedback"
        mock_qa_class.return_value.execute_task.side_effect = ["Mocked QA Feedback", "Mocked Verification"]
        mock_docs_class.return_value.execute_task.return_value = "Mocked Final Docs"

        orchestrator = Orchestrator({
            "architect": mock_architect_class.return_value, "coder": mock_coder_class.return_value,
            "database": mock_db_class.return_value, "documentation": mock_docs_class.return_value,
            "security": mock_security_class.return_value, "qa": mock_qa_class.return_value,
            "ui_ux": mock_ui_class.return_value,
        })

        orchestrator.run_workflow("Test a full workflow.")

        self.assertEqual(orchestrator.workflow_phase, "Completed")
        mock_input.assert_called_once()
        mock_add_memory.assert_called_once()
        logging.shutdown()
        with open("agent_os.log", "r") as f:
            self.assertIn("Human operator approved agent feedback", f.read())

    @patch.object(CoderAgent, '_run_linter', return_value=None)
    @patch('agent_os.agents.coder.CoderAgent._invoke_llm')
    def test_trm_cycle_and_confidence_exit(self, mock_invoke_llm, mock_run_linter, mock_base_config, mock_llm_config):
        """Tests the CoderAgent's internal TRM logic."""
        coder_agent = CoderAgent()
        mock_invoke_llm.side_effect = [
            'Initial draft.', 'Reasoning 1', 'Reasoning 2', 'Reasoning 3',
            'Reasoning 4', 'Reasoning 5', 'Reasoning 6', 'Revised draft.', '10',
        ]
        final_code = coder_agent.execute_task("Build a simple calculator.")
        self.assertEqual(mock_invoke_llm.call_count, 9)
        self.assertEqual(final_code, 'Revised draft.')

if __name__ == '__main__':
    unittest.main()