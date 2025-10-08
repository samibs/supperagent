# AgentOS: AI Agent Orchestration Platform

> **Project Status: Backend CLI Framework**
>
> Please note that AgentOS is currently a **backend command-line (CLI) framework**. It is a powerful tool for orchestrating AI agents to generate software, but it does not have its own graphical user interface (GUI).
>
> When you run AgentOS, it operates entirely within your terminal. The "output" of the system is the source code, documentation, and other artifacts for the application you've asked the agents to build.

AgentOS is a Python-based AI Agent Orchestration Platform designed to simulate a team of specialized, interconnected AI agents that collaboratively plan, design, implement, test, and document a software application. The platform enforces a structured, 7-phase iterative workflow, ensuring a systematic and verifiable development process.

This project demonstrates a robust framework for multi-agent collaboration, including key features like centralized logging, dynamic LLM selection, stateful workflows, and advanced agent reasoning models.

## Core Architecture

The system is built around a central `Orchestrator` that manages the workflow and communication between a team of specialized agents:

-   **Project Architect Agent**: Defines the high-level system design and learns from past projects stored in long-term memory.
-   **Coder Agent**: Generates implementation code using an advanced "Think, Reflect, Modify" (TRM) reasoning process and self-corrects with a linter.
-   **Security Agent**: Analyzes code for vulnerabilities.
-   **UI/UX Designer Agent**: Specifies accessible front-end structures and plans.
-   **Database Agent**: Designs the database schema and queries.
-   **Troubleshooting/QA Agent**: Critiques code and generates/executes unit tests.
-   **Documentation Agent**: Creates final documentation and usage guides.

## Flexible LLM Configuration

AgentOS is designed to be resilient and flexible. You can provide API keys for Anthropic (Claude), Google (Gemini), and/or OpenAI (for Codex/GPT models).

**Dynamic Client Fallback:**
The system is smart. If an agent requests a specific model (e.g., "claude") but its API key is not configured, the platform will automatically **fall back** to another available client. The priority is: **Claude -> Gemini -> OpenAI**. This means you can run the entire platform with just a single configured API key.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/samibs/supperagent.git
    cd supperagent
    ```
2.  **Create a virtual environment:** `python3 -m venv venv` and `source venv/bin/activate`.
3.  **Install dependencies:** `pip install -r requirements.txt`.
4.  **Configure API Keys:**
    *   Copy the template: `cp config.yaml.template config.yaml`
    *   Edit `config.yaml` and add your API key(s). You only need to provide a key for at least one service.

## How to Run the System

The main entry point is `agent_os/orchestrator.py`. Use command-line arguments to control the workflow:

-   **Run with a new goal:**
    ```bash
    python3 -m agent_os.orchestrator --goal "Your new project goal here"
    ```
-   **Start a fresh workflow (deletes previous progress):**
    ```bash
    python3 -m agent_os.orchestrator --fresh
    ```

The workflow is **resumable**. If it's interrupted, simply run the command again to continue.

## How to Run the Unit Tests

The project includes a comprehensive test suite. To run the tests:

```bash
python3 -m unittest discover tests
```

## Acknowledgements

This project's architecture is inspired by the work of many in the AI community. A special acknowledgement goes to the `supperagent` project for its inspirational approach to multi-agent systems.

-   [supperagent on GitHub](https://github.com/samibs/supperagent)