#!/usr/bin/env python3

import logging
import json
import os
import sys
from collections import deque
from typing import Dict, List, Any
import concurrent.futures

# This import is crucial to configure the logging system as soon as the app starts.
from . import logging_config
from .agents.base import Agent
from .agents.architect import ProjectArchitectAgent
from .agents.coder import CoderAgent
from .agents.database import DatabaseAgent
from .agents.documentation import DocumentationAgent
from .agents.security import SecurityAgent
from .agents.troubleshooting_qa import TroubleshootingQAAgent
from .agents.ui_ux_designer import UIUXDesignerAgent

# Get a logger for the orchestrator
log = logging.getLogger('AgentOS.Orchestrator')

STATE_FILE = 'workflow_state.json'

class Orchestrator:
    """
    The central orchestrator for the AI agent team.

    This class manages the entire software development lifecycle, assigning tasks
    to specialized agents and ensuring the workflow proceeds in a structured,
    iterative, and resumable manner.
    """
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.log_history = deque(maxlen=50)
        self._setup_log_history_handler()

        # Initialize state attributes
        self.project_requirements: str = ""
        self.architect_plan: str | None = None
        self.db_plan: str | None = None
        self.ui_plan: str | None = None
        self.full_plan: str | None = None
        self.generated_code: str | None = None
        self.qa_feedback: str | None = None
        self.security_feedback: str | None = None
        self.pending_tasks: List[Dict[str, Any]] = []
        self.fixed_code: str | None = None
        self.qa_verification: str | None = None
        self.final_documentation: str | None = None
        self.workflow_phase: str = "Idle"

        self._load_state()
        log.info("Orchestrator initialized with %d agents.", len(agents))

    def _save_state(self):
        """Saves the current workflow state to a JSON file."""
        state = {
            'project_requirements': self.project_requirements,
            'workflow_phase': self.workflow_phase,
            'architect_plan': self.architect_plan,
            'db_plan': self.db_plan,
            'ui_plan': self.ui_plan,
            'full_plan': self.full_plan,
            'generated_code': self.generated_code,
            'qa_feedback': self.qa_feedback,
            'security_feedback': self.security_feedback,
            'pending_tasks': self.pending_tasks,
            'fixed_code': self.fixed_code,
            'qa_verification': self.qa_verification,
            'final_documentation': self.final_documentation,
        }
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=4)
            log.info(f"Workflow state saved to '{STATE_FILE}' at phase '{self.workflow_phase}'.")
        except IOError as e:
            log.error(f"Failed to save state: {e}")

    def _load_state(self):
        """Loads the workflow state from a JSON file if it exists."""
        if not os.path.exists(STATE_FILE):
            log.info("No previous state file found. Starting a fresh workflow.")
            return

        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)

            self.project_requirements = state.get('project_requirements', "")
            self.workflow_phase = state.get('workflow_phase', 'Idle')
            # ... and so on for all other state attributes
            for key, value in state.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            log.info(f"Successfully loaded state. Resuming workflow from phase '{self.workflow_phase}'.")
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to load state from '{STATE_FILE}': {e}. Starting fresh.")
            self.workflow_phase = "Idle"

    def _setup_log_history_handler(self):
        # (omitted for brevity - same as before)
        pass

    def get_system_state(self) -> str:
        # (omitted for brevity - same as before)
        pass

    def run_workflow(self, project_requirements: str):
        """
        Executes the main 7-phase iterative development loop in a resumable manner.
        """
        if self.workflow_phase == "Idle":
            self.project_requirements = project_requirements
            self.workflow_phase = "Phase 1: Planning"
            self._save_state()

        log.info("Starting workflow for: '%s'", self.project_requirements)

        if self.workflow_phase == "Phase 1: Planning":
            log.info("Entering Planning Phase.")
            self.architect_plan = self.agents["architect"].execute_task(self.project_requirements)
            self.db_plan = self.agents["database"].execute_task(self.architect_plan)
            self.ui_plan = self.agents["ui_ux"].execute_task("User authentication and profile page.")
            self.full_plan = f"{self.architect_plan}\n\n{self.db_plan}\n\n{self.ui_plan}"
            log.info("Planning complete. Combined plan created.")
            self.workflow_phase = "Phase 2: Generation"
            self._save_state()

        if self.workflow_phase == "Phase 2: Generation":
            log.info("Entering Generation Phase.")
            self.generated_code = self.agents["coder"].execute_task(self.full_plan)
            log.info("Initial code generated.")
            self.workflow_phase = "Phase 3: Initial Review"
            self._save_state()

        if self.workflow_phase == "Phase 3: Initial Review":
            log.info("Entering Initial Review Phase (with parallel execution).")
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Submit the QA and Security analysis tasks to run in parallel
                log.info("Submitting QA and Security analysis tasks to executor.")
                future_qa = executor.submit(self.agents["qa"].execute_task, self.generated_code)
                future_security = executor.submit(self.agents["security"].execute_task, self.generated_code)

                # Wait for the results
                log.info("Waiting for parallel reviews to complete...")
                self.qa_feedback = future_qa.result()
                self.security_feedback = future_security.result()
                log.info("Parallel reviews completed.")

            log.info("Code review complete. Aggregating feedback.")
            self.workflow_phase = "Phase 4: Feedback & Refinement"
            self._save_state()

        if self.workflow_phase == "Phase 4: Feedback & Refinement":
            log.info("Entering Feedback & Refinement Phase.")

            # --- Human-in-the-Loop (HIL) Integration ---
            print("\n--- PENDING AGENT FEEDBACK ---")
            print("\n[--- QA Agent Feedback ---]")
            print(self.qa_feedback)
            print("\n[--- Security Agent Feedback ---]")
            print(self.security_feedback)
            print("\n---------------------------------")

            print("\nPlease review the feedback. You can approve it or add your own.")
            user_input = input("Type 'approve' to continue, or type your additional feedback: ")

            self.pending_tasks = [
                {"source": "QA", "feedback": self.qa_feedback},
                {"source": "Security", "feedback": self.security_feedback}
            ]

            if user_input.lower().strip() == 'approve':
                log.info("Human operator approved agent feedback.")
            else:
                human_feedback = {"source": "Human Operator", "feedback": user_input}
                self.pending_tasks.append(human_feedback)
                log.info("Human operator added custom feedback.")

            log.info("Feedback aggregated into %d tasks.", len(self.pending_tasks))
            self.workflow_phase = "Phase 5: Fix & Optimization"
            self._save_state()

        if self.workflow_phase == "Phase 5: Fix & Optimization":
            log.info("Entering Fix & Optimization Phase.")
            fix_prompt = f"Original Code:\n{self.generated_code}\n\nReview Feedback:\n{self.pending_tasks}"
            self.fixed_code = self.agents["coder"].execute_task(fix_prompt)
            self.pending_tasks.clear()
            log.info("Code has been fixed based on feedback.")
            self.workflow_phase = "Phase 6: Verification & Testing"
            self._save_state()

        if self.workflow_phase == "Phase 6: Verification & Testing":
            log.info("Entering Verification & Testing Phase.")
            self.qa_verification = self.agents["qa"].execute_task(self.fixed_code)
            log.info("Verification complete. Unit tests generated.")
            print("\n--- Generated Unit Tests (for verification) ---\n")
            print(self.qa_verification)
            self.workflow_phase = "Phase 7: Finalization"
            self._save_state()

        if self.workflow_phase == "Phase 7: Finalization":
            log.info("Entering Finalization Phase.")
            self.final_documentation = self.agents["documentation"].execute_task(self.fixed_code)
            log.info("Final documentation generated.")
            print("\n--- Generated Documentation ---\n")
            print(self.final_documentation)
            self.workflow_phase = "Completed"
            self._save_state()

        if self.workflow_phase == "Completed":
            log.info("Workflow finished successfully.")
            print("\nWorkflow is complete. To run a new workflow, delete 'workflow_state.json' and run this script again.")


if __name__ == '__main__':
    # Instantiate all the specialized agents
    specialized_agents = {
        "architect": ProjectArchitectAgent(),
        "coder": CoderAgent(),
        "database": DatabaseAgent(),
        "documentation": DocumentationAgent(),
        "security": SecurityAgent(),
        "qa": TroubleshootingQAAgent(),
        "ui_ux": UIUXDesignerAgent(),
    }

    orchestrator = Orchestrator(specialized_agents)

    # Define the high-level goal for the project
    # This is only used if no state file is found.
    project_goal = "Develop a Python Flask web application for a simple blog."

    # The orchestrator now manages its own state.
    orchestrator.run_workflow(project_goal)

    # Print the final system state
    print(orchestrator.get_system_state())