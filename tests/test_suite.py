import unittest
import os
import logging
from unittest.mock import patch

from agent_os import logging_config
from agent_os.orchestrator import Orchestrator
from agent_os.agents.coder import CoderAgent
from agent_os.agents.base import Agent
from agent_os import llm_client

MOCK_CONFIG = {
    'api_keys': {'anthropic': 'key', 'google': 'key', 'openai': 'key'},
    'models': {
        'claude': 'claude-model', 'gemini': 'gemini-model', 'codex': 'codex-model'
    }
}

@patch('agent_os.llm_client.config_loader.load_config', return_value=MOCK_CONFIG)
@patch('agent_os.agents.base.config_loader.load_config', return_value=MOCK_CONFIG)
class TestAgentOS(unittest.TestCase):
    """A stable, unified test suite for the main orchestrator and agent workflows."""

    def setUp(self):
        """Set up a clean environment for each test. This method does NOT receive class-level mocks."""
        logger = logging.getLogger('AgentOS')
        for handler in logger.handlers[:]: logger.removeHandler(handler)
        logging_config.setup_logging()
        for f in ["workflow_state.json", "claude.md", "gemini.md", "codex.md"]:
            if os.path.exists(f): os.remove(f)
        self.agent = CoderAgent()

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

    @patch('agent_os.llm_client.call_anthropic', return_value="Claude says hi")
    def test_invoke_llm_dispatches_to_claude(self, mock_call_anthropic, mock_base_config, mock_llm_config):
        with patch.object(self.agent, '_get_available_clients', return_value=[("claude", llm_client.call_anthropic)]):
            response = self.agent._invoke_llm(preferred_model="claude", prompt="test")
            mock_call_anthropic.assert_called_once_with("test", model="claude-model")
            self.assertEqual(response, "Claude says hi")

    @patch('agent_os.llm_client.call_gemini', return_value="Gemini says hi")
    def test_invoke_llm_dispatches_to_gemini(self, mock_call_gemini, mock_base_config, mock_llm_config):
        with patch.object(self.agent, '_get_available_clients', return_value=[("gemini", llm_client.call_gemini)]):
            response = self.agent._invoke_llm(preferred_model="gemini", prompt="test")
            mock_call_gemini.assert_called_once_with("test", model="gemini-model")
            self.assertEqual(response, "Gemini says hi")

    @patch('agent_os.llm_client.call_openai', return_value="OpenAI says hi")
    def test_invoke_llm_dispatches_to_openai(self, mock_call_openai, mock_base_config, mock_llm_config):
        with patch.object(self.agent, '_get_available_clients', return_value=[("codex", llm_client.call_openai)]):
            response = self.agent._invoke_llm(preferred_model="codex", prompt="test")
            mock_call_openai.assert_called_once_with("test", model="codex-model")
            self.assertEqual(response, "OpenAI says hi")

    @patch('agent_os.llm_client.call_gemini', return_value="Gemini fallback")
    @patch('agent_os.llm_client.call_anthropic')
    def test_invoke_llm_falls_back_to_available_client(self, mock_call_anthropic, mock_call_gemini, mock_base_config, mock_llm_config):
        """Tests that the agent falls back to a working client if the preferred one is unavailable."""
        with patch.object(self.agent, '_get_available_clients', return_value=[("gemini", llm_client.call_gemini)]):
            response = self.agent._invoke_llm(preferred_model="claude", prompt="test")
            mock_call_anthropic.assert_not_called()
            mock_call_gemini.assert_called_once_with("test", model="gemini-model")
            self.assertEqual(response, "Gemini fallback")

if __name__ == '__main__':
    unittest.main()