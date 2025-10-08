import logging
import anthropic
import google.generativeai as genai
import openai
from . import config_loader

log = logging.getLogger('AgentOS.LLMClient')

# --- Client Initialization ---

def get_anthropic_client():
    """Initializes and returns the Anthropic client on demand."""
    try:
        config = config_loader.load_config()
        api_key = config.get('api_keys', {}).get('anthropic')
        if not api_key or api_key == "sk-ant-...":
            log.warning("Anthropic API key is not configured.")
            return None
        return anthropic.Anthropic(api_key=api_key)
    except (KeyError, TypeError, FileNotFoundError):
        return None

def get_gemini_client():
    """Configures the Google Gemini client and returns the module if available."""
    try:
        config = config_loader.load_config()
        api_key = config.get('api_keys', {}).get('google')
        if not api_key or api_key == "...":
            log.warning("Google Gemini API key is not configured.")
            return None
        genai.configure(api_key=api_key)
        return genai  # Return the configured module as a truthy value
    except Exception:
        return None

def get_openai_client():
    """Initializes and returns the OpenAI client on demand."""
    try:
        config = config_loader.load_config()
        api_key = config.get('api_keys', {}).get('openai')
        if not api_key or api_key == "sk-...":
            log.warning("OpenAI API key is not configured.")
            return None
        return openai.OpenAI(api_key=api_key)
    except (KeyError, TypeError, FileNotFoundError):
        return None

# --- API Call Functions ---

def call_anthropic(prompt: str, model: str) -> str:
    """Makes an API call to an Anthropic (Claude) model."""
    client = get_anthropic_client()
    if not client: raise ConnectionError("Anthropic client not configured.")
    log.info(f"Making API call to Anthropic model: {model}")
    message = client.messages.create(
        model=model, max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def call_gemini(prompt: str, model: str) -> str:
    """Makes an API call to a Google (Gemini) model."""
    client_module = get_gemini_client()
    if not client_module:
        raise ConnectionError("Gemini client not configured.")

    log.info(f"Making API call to Gemini model: {model}")
    # Instantiate the model with the correct model name here
    model_instance = client_module.GenerativeModel(model)
    response = model_instance.generate_content(prompt)
    return response.text

def call_openai(prompt: str, model: str) -> str:
    """Makes an API call to an OpenAI (Codex/GPT) model."""
    client = get_openai_client()
    if not client: raise ConnectionError("OpenAI client not configured.")
    log.info(f"Making API call to OpenAI model: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content