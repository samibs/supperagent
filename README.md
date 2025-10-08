# AgentOS: AI Agent Orchestration Platform

AgentOS is a Python-based AI Agent Orchestration Platform designed to simulate a team of specialized, interconnected AI agents that collaboratively plan, design, implement, test, and document a software application. The platform enforces a structured, 7-phase iterative workflow, ensuring a systematic and verifiable development process.

This project demonstrates a robust framework for multi-agent collaboration, including key features like centralized logging, dynamic LLM selection, and automated testing.

## Core Architecture

The system is built around a central `Orchestrator` that manages the workflow and communication between a team of specialized agents:

-   **Project Architect Agent**: Defines the high-level system design.
-   **Coder Agent**: Generates implementation code.
-   **Security Agent**: Analyzes code for vulnerabilities.
-   **UI/UX Designer Agent**: Specifies accessible front-end structures.
-   **Database Agent**: Designs the database schema and queries.
-   **Troubleshooting/QA Agent**: Critiques code and generates unit tests.
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

## How to Run the System

The main entry point for the application is `agent_os/orchestrator.py`. You can run the entire simulated development workflow with the following command from the root directory:

```bash
python3 -m agent_os.orchestrator
```

This will execute the 7-phase workflow, with each agent performing its simulated task. The output will be printed to the console, including generated unit tests and final documentation.

## How to Run the Unit Tests

The project includes a suite of unit tests to verify the core functionality of the orchestrator and its interaction with the agents. To run the tests, use Python's built-in `unittest` module:

```bash
python3 -m unittest discover tests
```

The tests will run, and you will see a confirmation that all tests passed.

## Troubleshooting with `agent_os.log`

The platform features a robust, centralized logging system that captures detailed information about the entire workflow. All events are logged to the `agent_os.log` file in the root directory.

This file is essential for troubleshooting and understanding the system's behavior. It contains:
-   **Timestamps** for every event.
-   **Agent-specific entries**, showing which agent is performing which action (e.g., `AgentOS.CoderAgent`).
-   **LLM invocations**, including the model chosen for a specific task.
-   **Debug-level messages**, providing granular detail on the inputs and outputs of each step.

**To analyze the log file:**
```bash
# View the entire log
cat agent_os.log

# Follow the log in real-time (if the application were long-running)
tail -f agent_os.log

# Filter for entries from a specific agent (e.g., the Security Agent)
grep "SecurityAgent" agent_os.log
```
By inspecting this file, you can trace the entire lifecycle of a development task, from planning to final documentation.