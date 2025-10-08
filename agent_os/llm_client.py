import logging
import anthropic
from . import config_loader

log = logging.getLogger('AgentOS.LLMClient')

def get_anthropic_client():
    """
    Initializes and returns the Anthropic client on demand.

    This function gets the config only when needed, avoiding import-time errors.
    """
    try:
        config = config_loader.load_config()
        api_key = config.get('api_keys', {}).get('anthropic')
        if not api_key or api_key == "sk-ant-...":
            log.warning("Anthropic API key is not configured. Real API calls will fail.")
            return None
        return anthropic.Anthropic(api_key=api_key)
    except (KeyError, TypeError, FileNotFoundError):
        log.warning("Could not create Anthropic client due to missing config or key.")
        return None

def call_anthropic(prompt: str, model: str) -> str:
    """
    Makes an API call to an Anthropic (Claude) model.

    Args:
        prompt (str): The prompt to send to the model.
        model (str): The specific model to use (e.g., 'claude-3-haiku-20240307').

    Returns:
        str: The text response from the model.

    Raises:
        ConnectionError: If the Anthropic client is not configured.
        Exception: If the API call itself fails.
    """
    anthropic_client = get_anthropic_client()
    if not anthropic_client:
        raise ConnectionError("Anthropic client is not configured. Please check your config.yaml.")

    log.info(f"Making real API call to Anthropic model: {model}")
    try:
        message = anthropic_client.messages.create(
            model=model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        response_text = message.content[0].text
        log.info("Successfully received response from Anthropic.")
        return response_text
    except Exception as e:
        log.error(f"Anthropic API call failed: {e}")
        raise