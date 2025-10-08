import yaml
import os
import logging

log = logging.getLogger('AgentOS.ConfigLoader')

_config = None
_config_loaded = False

def load_config():
    """
    Loads the application configuration from `config.yaml` on first call.

    This function implements a lazy-loading singleton pattern. It loads the
    config from the file only on the first call and caches it for all
    subsequent calls. This prevents import-time side effects and makes
    the system more testable.

    Returns:
        dict: A dictionary containing the loaded configuration.
    """
    global _config, _config_loaded
    if _config_loaded:
        return _config

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

    if not os.path.exists(config_path):
        log.error("Configuration file `config.yaml` not found!")
        raise FileNotFoundError(
            "CRITICAL: The `config.yaml` file was not found. "
            "Please create it by copying `config.yaml.template` and "
            "filling in your API keys."
        )

    try:
        with open(config_path, 'r') as f:
            _config = yaml.safe_load(f)
            _config_loaded = True
            log.info("Configuration loaded successfully.")
            return _config
    except yaml.YAMLError as e:
        log.error(f"Error parsing `config.yaml`: {e}")
        raise