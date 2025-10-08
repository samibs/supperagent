import unittest
import os
import logging
from unittest.mock import patch, MagicMock

from agent_os import logging_config
from agent_os.orchestrator import Orchestrator

# Mock configs for different test scenarios
MOCK_CONFIG_MEM_ENABLED = {
    'memory': {'enabled': True}, 'models': {}, 'api_keys': {}
}
MOCK_CONFIG_MEM_DISABLED = {
    'memory': {'enabled': False}, 'models': {}, 'api_keys': {}
}

class TestAgentOS(unittest.TestCase):
    """A stable, unified test suite for the main orchestrator and agent workflows."""

    def setUp(self):
        """Set up a clean environment for each test."""
        logger = logging.getLogger('AgentOS')
        for handler in logger.handlers[:]: logger.removeHandler(handler)
        logging_config.setup_logging()
        if os.path.exists("workflow_state.json"): os.remove("workflow_state.json")

    def tearDown(self):
        """Clean up any created files."""
        if os.path.exists("agent_os.log"): os.remove("agent_os.log")
        if os.path.exists("workflow_state.json"): os.remove("workflow_state.json")

    def test_full_workflow_with_memory_enabled(self):
        """Tests the full workflow and verifies that memory is saved when enabled."""
        with patch('agent_os.config_loader.load_config', return_value=MOCK_CONFIG_MEM_ENABLED), \
             patch('agent_os.orchestrator.memory_manager.is_enabled', return_value=True), \
             patch('agent_os.orchestrator.ProjectArchitectAgent') as MockPA, \
             patch('agent_os.orchestrator.DatabaseAgent') as MockDB, \
             patch('agent_os.orchestrator.UIUXDesignerAgent') as MockUI, \
             patch('agent_os.orchestrator.CoderAgent') as MockCoder, \
             patch('agent_os.orchestrator.SecurityAgent') as MockSec, \
             patch('agent_os.orchestrator.TroubleshootingQAAgent') as MockQA, \
             patch('agent_os.orchestrator.DocumentationAgent') as MockDoc, \
             patch('rich.console.Console.input', return_value='approve'), \
             patch('agent_os.orchestrator.memory_manager.add_memory') as mock_add_memory:

            # Arrange
            mock_agents = { "architect": MockPA(), "coder": MockCoder(), "database": MockDB(), "documentation": MockDoc(), "security": MockSec(), "qa": MockQA(), "ui_ux": MockUI() }
            for agent in mock_agents.values():
                agent.execute_task.return_value = "mocked task result"

            # Act
            orchestrator = Orchestrator(mock_agents)
            orchestrator.run_workflow("Test a full workflow.")

            # Assert
            mock_add_memory.assert_called_once()

    def test_full_workflow_with_memory_disabled(self):
        """Tests the full workflow and verifies that memory is skipped when disabled."""
        with patch('agent_os.config_loader.load_config', return_value=MOCK_CONFIG_MEM_DISABLED), \
             patch('agent_os.orchestrator.memory_manager.is_enabled', return_value=False), \
             patch('agent_os.orchestrator.ProjectArchitectAgent') as MockPA, \
             patch('agent_os.orchestrator.DatabaseAgent') as MockDB, \
             patch('agent_os.orchestrator.CoderAgent') as MockCoder, \
             patch('agent_os.orchestrator.SecurityAgent') as MockSec, \
             patch('agent_os.orchestrator.TroubleshootingQAAgent') as MockQA, \
             patch('agent_os.orchestrator.DocumentationAgent') as MockDoc, \
             patch('rich.console.Console.input', return_value='approve'), \
             patch('agent_os.orchestrator.memory_manager.add_memory') as mock_add_memory:

            # Arrange
            mock_agents = { "architect": MockPA(), "coder": MockCoder(), "database": MockDB(), "documentation": MockDoc(), "security": MockSec(), "qa": MockQA(), "ui_ux": MagicMock() }
            for agent in mock_agents.values():
                agent.execute_task.return_value = "mocked task result"

            # Act
            orchestrator = Orchestrator(mock_agents)
            orchestrator.run_workflow("Test a full workflow.")

            # Assert
            mock_add_memory.assert_not_called()

if __name__ == '__main__':
    unittest.main()