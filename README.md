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

-   **Project Architect Agent**: Defines the high-level system design.
-   **Coder Agent**: Generates implementation code using an advanced "Think, Reflect, Modify" (TRM) reasoning process.
-   **Security Agent**: Analyzes code for vulnerabilities.
-   **UI/UX Designer Agent**: Specifies accessible front-end structures and plans.
-   **Database Agent**: Designs the database schema and queries.
-   **Troubleshooting/QA Agent**: Critiques code and generates/executes unit tests.
-   **Documentation Agent**: Creates final documentation and usage guides.

## Setup and Installation

To get started with AgentOS, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure API Keys:**
    *   Copy the template file: `cp config.yaml.template config.yaml`
    *   Edit `config.yaml` and add your real API keys for the LLM services you wish to use.

## How to Run the System

The main entry point for the application is `agent_os/orchestrator.py`. You can run the entire agent-driven development workflow with the following command from the root directory:

```bash
python3 -m agent_os.orchestrator
```

This will execute the 7-phase workflow. The agents will generate plans, code, and feedback, which will be displayed in your console and saved to log files. The final output is the *source code* for the target application, not a running app itself.

The workflow is **resumable**. If it's interrupted, simply run the command again to continue from the last completed phase. To start a fresh workflow, delete the `workflow_state.json` file.

## How to Run the Unit Tests

The project includes a suite of unit tests to verify the core functionality of the orchestrator and its agents. To run the tests, use Python's built-in `unittest` module:

```bash
python3 -m unittest discover tests
```

The tests will run, and you will see a confirmation that all tests passed.

## Troubleshooting with `agent_os.log`

The platform features a robust, centralized logging system that captures detailed information about the entire workflow. All events are logged to the `agent_os.log` file in the root directory. This file is your primary tool for debugging and understanding the system's behavior.

## Acknowledgements

This project's architecture and agent-based reasoning concepts are inspired by the work of many in the AI community. A special acknowledgement goes to the `supperagent` project for its inspirational approach to multi-agent systems.

-   [supperagent on GitHub](https://github.com/samibs/supperagent)