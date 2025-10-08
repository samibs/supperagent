import logging
import json
import os
import sys
import argparse
import uuid
import datetime
from collections import deque
from typing import Dict, List, Any
import concurrent.futures
from rich.console import Console
from rich.panel import Panel

from . import logging_config
from .agents.base import Agent
from .memory_manager import memory_manager
from .agents.architect import ProjectArchitectAgent
from .agents.coder import CoderAgent
from .agents.database import DatabaseAgent
from .agents.documentation import DocumentationAgent
from .agents.security import SecurityAgent
from .agents.troubleshooting_qa import TroubleshootingQAAgent
from .agents.ui_ux_designer import UIUXDesignerAgent
from .banner import get_banner

log = logging.getLogger('AgentOS.Orchestrator')
STATE_FILE = 'workflow_state.json'

class Orchestrator:
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.console = Console()
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
        state = {
            'project_requirements': self.project_requirements, 'workflow_phase': self.workflow_phase,
            'architect_plan': self.architect_plan, 'db_plan': self.db_plan, 'ui_plan': self.ui_plan,
            'full_plan': self.full_plan, 'generated_code': self.generated_code,
            'qa_feedback': self.qa_feedback, 'security_feedback': self.security_feedback,
            'pending_tasks': self.pending_tasks, 'fixed_code': self.fixed_code,
            'qa_verification': self.qa_verification, 'final_documentation': self.final_documentation,
        }
        with open(STATE_FILE, 'w') as f: json.dump(state, f, indent=4)
        log.info(f"State saved at phase '{self.workflow_phase}'.")

    def _load_state(self):
        if not os.path.exists(STATE_FILE): return
        try:
            with open(STATE_FILE, 'r') as f: state = json.load(f)
            for key, value in state.items():
                if hasattr(self, key): setattr(self, key, value)
            log.info(f"Resuming from phase '{self.workflow_phase}'.")
        except (IOError, json.JSONDecodeError):
            log.error("Could not load state file. Starting fresh.")
            self.workflow_phase = "Idle"

    def _execute_agent_task(self, agent_name, task_title, *args):
        with self.console.status(f"[bold green]🧠 Agent '{agent_name}' is {task_title}...", spinner="dots"):
            return self.agents[agent_name].execute_task(*args)

    def _add_project_to_memory(self):
        self.console.print("\n[bold]Phase 8: Storing Project in Long-Term Memory[/bold]")
        if not all([self.full_plan, self.fixed_code, self.final_documentation]):
            self.console.print("[yellow]Could not save to memory, essential artifacts missing.[/yellow]")
            return
        memory_document = (
            f"Project Goal: {self.project_requirements}\n\n"
            f"--- ARCHITECTURE & PLANNING ---\n{self.full_plan}\n\n"
            f"--- FINAL IMPLEMENTATION ---\n```python\n{self.fixed_code}\n```\n\n"
            f"--- FINAL DOCUMENTATION ---\n{self.final_documentation}"
        )
        metadata = {"project_goal": self.project_requirements, "completion_date": datetime.datetime.now().isoformat()}
        doc_id = f"project_{uuid.uuid4()}"
        with self.console.status("[bold green]🧠 Embedding and storing project memories...", spinner="dots"):
            memory_manager.add_memory(memory_document, metadata, doc_id)
        self.console.print("[green]✅ Project successfully stored in long-term memory.[/green]")

    def run_workflow(self, project_requirements: str, fresh_start: bool = False):
        if fresh_start and os.path.exists(STATE_FILE):
            self.console.print("[bold yellow]--fresh flag detected. Deleting old state file.[/bold yellow]")
            os.remove(STATE_FILE)
            self.__init__(self.agents)

        if self.workflow_phase == "Idle":
            self.project_requirements = project_requirements
            self.workflow_phase = "Phase 1: Planning"
            self._save_state()

        self.console.print(Panel(f"🚀 Starting Workflow For: [bold cyan]{self.project_requirements}[/bold cyan]", title="Project Goal", border_style="blue"))

        if self.workflow_phase == "Phase 1: Planning":
            self.console.print("\n[bold]Phase 1: Planning[/bold]")
            self.architect_plan = self._execute_agent_task("architect", "designing system architecture", self.project_requirements)
            self.db_plan = self._execute_agent_task("database", "designing database schema", self.architect_plan)
            self.ui_plan = self._execute_agent_task("ui_ux", "designing UI/UX specifications", "User authentication page.")
            self.full_plan = f"{self.architect_plan}\n\n{self.db_plan}\n\n{self.ui_plan}"
            self.workflow_phase = "Phase 2: Generation"; self._save_state()

        if self.workflow_phase == "Phase 2: Generation":
            self.console.print("\n[bold]Phase 2: Code Generation[/bold]")
            self.generated_code = self._execute_agent_task("coder", "generating initial code", self.full_plan)
            self.workflow_phase = "Phase 3: Initial Review"; self._save_state()

        if self.workflow_phase == "Phase 3: Initial Review":
            self.console.print("\n[bold]Phase 3: Initial Review (Parallel Execution)[/bold]")
            with self.console.status("[bold green]🔬 Agents performing parallel reviews...", spinner="dots"):
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_qa = executor.submit(self.agents["qa"].execute_task, self.generated_code)
                    future_security = executor.submit(self.agents["security"].execute_task, self.generated_code)
                    self.qa_feedback, self.security_feedback = future_qa.result(), future_security.result()
            self.workflow_phase = "Phase 4: Feedback & Refinement"; self._save_state()

        if self.workflow_phase == "Phase 4: Feedback & Refinement":
            self.console.print("\n[bold]Phase 4: Feedback & Refinement (Human-in-the-Loop)[/bold]")
            self.console.print(Panel(self.qa_feedback, title="[cyan]QA Agent Feedback[/cyan]", border_style="cyan"))
            self.console.print(Panel(self.security_feedback, title="[magenta]Security Agent Feedback[/magenta]", border_style="magenta"))
            user_input = self.console.input("\n[bold yellow]❓ Review feedback. 'approve' or add comments: [/bold yellow]")
            self.pending_tasks = [{"source": "QA", "feedback": self.qa_feedback}, {"source": "Security", "feedback": self.security_feedback}]
            if user_input.lower().strip() == 'approve':
                log.info("Human operator approved agent feedback.")
            else:
                self.pending_tasks.append({"source": "Human Operator", "feedback": user_input})
                log.info("Human operator added custom feedback.")
            self.workflow_phase = "Phase 5: Fix & Optimization"; self._save_state()

        if self.workflow_phase == "Phase 5: Fix & Optimization":
            self.console.print("\n[bold]Phase 5: Fix & Optimization[/bold]")
            fix_prompt = f"Original Code:\n{self.generated_code}\n\nReview Feedback:\n{self.pending_tasks}"
            self.fixed_code = self._execute_agent_task("coder", "applying fixes", fix_prompt)
            self.pending_tasks.clear()
            self.workflow_phase = "Phase 6: Verification & Testing"; self._save_state()

        if self.workflow_phase == "Phase 6: Verification & Testing":
            self.console.print("\n[bold]Phase 6: Verification & Testing[/bold]")
            self.qa_verification = self._execute_agent_task("qa", "verifying fixes", self.fixed_code)
            self.console.print(Panel(self.qa_verification, title="[green]Verification & Test Report[/green]", border_style="green"))
            self.workflow_phase = "Phase 7: Finalization"; self._save_state()

        if self.workflow_phase == "Phase 7: Finalization":
            self.console.print("\n[bold]Phase 7: Finalization[/bold]")
            self.final_documentation = self._execute_agent_task("documentation", "generating final documentation", self.fixed_code)
            self.console.print(Panel(self.final_documentation, title="[blue]Final Documentation[/blue]", border_style="blue"))
            self.workflow_phase = "Completed"; self._save_state()

        if self.workflow_phase == "Completed":
            self._add_project_to_memory()
            self.console.print(Panel("[bold green]✅ Workflow Finished Successfully![/bold green]", border_style="green"))
            self.console.print("To run a new workflow, use the [bold cyan]--fresh[/bold cyan] flag.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AgentOS: AI Agent Orchestration Platform")
    parser.add_argument('--goal', type=str, default="Develop a Python Flask web application for a simple blog.", help="The high-level goal for the project.")
    parser.add_argument('--fresh', action='store_true', help="Start a fresh workflow by deleting the existing state file.")
    args = parser.parse_args()
    console = Console()
    console.print(get_banner(), style="bold blue")
    specialized_agents = {
        "architect": ProjectArchitectAgent(), "coder": CoderAgent(),
        "database": DatabaseAgent(), "documentation": DocumentationAgent(),
        "security": SecurityAgent(), "qa": TroubleshootingQAAgent(),
        "ui_ux": UIUXDesignerAgent(),
    }
    orchestrator = Orchestrator(specialized_agents)
    orchestrator.run_workflow(args.goal, args.fresh)