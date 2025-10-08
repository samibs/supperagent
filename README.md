# AgentOS: AI Agent Orchestration Platform

> **Project Status: Backend CLI Framework**
>
> AgentOS is a **backend command-line (CLI) framework** for orchestrating AI agents. It does not have its own graphical user interface (GUI). The "output" of the system is the source code and documentation for the application you've asked the agents to build.

AgentOS is a Python-based platform that simulates a team of specialized AI agents who collaboratively plan, design, implement, test, and document software. It enforces a structured, 7-phase iterative workflow, including advanced features like dynamic LLM selection, stateful workflows, and sophisticated agent reasoning models.

## Core Architecture

The system is built around a central `Orchestrator` that manages a team of specialized agents:

-   **Project Architect Agent**: Defines the high-level system design and learns from past projects.
-   **Coder Agent**: Generates code using an advanced "Think, Reflect, Modify" (TRM) reasoning process and self-corrects with a linter.
-   **And 5+ other specialized agents** for security, UI/UX, database, QA, and documentation.

## Key Features

-   **Dynamic Client Fallback:** Provide API keys for Claude, Gemini, and/or OpenAI. The platform is resilient and will intelligently fall back to an available client if a preferred one is not configured.
-   **Configurable Long-Term Memory:** AgentOS can learn from past projects using a local vector database. **Warning:** This feature requires significant RAM. If the application is killed unexpectedly, you can disable it in `config.yaml`.
-   **Resumable Workflows:** The orchestrator saves its progress after each phase, so you can resume an interrupted workflow.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/samibs/supperagent.git
    cd supperagent
    ```
2.  **Create a virtual environment:** `python3 -m venv venv` and `source venv/bin/activate`.
3.  **Install dependencies:** `pip install -r requirements.txt`.
4.  **Configure the Platform:**
    *   Copy the template: `cp config.yaml.template config.yaml`
    *   Edit `config.yaml` to add your API key(s) and enable/disable long-term memory.

## How to Run the System

Use command-line arguments to control the workflow:

-   **Run with a new goal:**
    ```bash
    python3 -m agent_os.orchestrator --goal "Your new project goal here"
    ```
-   **Start a fresh workflow (deletes previous progress):**
    ```bash
    python3 -m agent_os.orchestrator --fresh
    ```

## How to Run the Unit Tests

The project includes a comprehensive test suite. To run the tests:

```bash
python3 -m unittest discover tests
```

## Acknowledgements

This project's architecture is inspired by the work of many in the AI community. A special acknowledgement goes to the `supperagent` project for its inspirational approach to multi-agent systems.

-   [supperagent on GitHub](https://github.com/samibs/supperagent)