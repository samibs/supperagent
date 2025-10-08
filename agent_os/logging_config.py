import logging
import sys

def setup_logging():
    """
    Configures a centralized logging system.

    This setup directs logs to both the console and a file (agent_os.log),
    with different formatters for each to optimize for readability and
    detailed debugging.
    """
    # Create a top-level logger
    logger = logging.getLogger('AgentOS')
    logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

    # Prevent logs from propagating to the root logger
    logger.propagate = False

    # --- Console Handler ---
    # More readable, less verbose format for the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Show INFO and above in the console
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # --- File Handler ---
    # More detailed format for the log file, including timestamps
    file_handler = logging.FileHandler('agent_os.log', mode='w')
    file_handler.setLevel(logging.DEBUG)  # Log everything to the file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger if they are not already present
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Initialize and get the logger instance
log = setup_logging()