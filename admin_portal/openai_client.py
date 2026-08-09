"""
Simple OpenAI client wrapper for admin_portal.
Requires OPENAI_API_KEY in the environment or Django settings.OPENAI_API_KEY.
This wrapper uses the official openai package if installed, otherwise falls back to HTTP requests.
"""
import os
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or None
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE') or None

try:
    import openai
    HAS_OPENAI = True
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
    if OPENAI_API_BASE:
        openai.api_base = OPENAI_API_BASE
except Exception:
    HAS_OPENAI = False


def call_chat_model(model: str, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
    """Call a chat-style model and return a structured dict.
    messages: list of {role: 'system'|'user'|'assistant', 'content': str}
    """
    if not HAS_OPENAI:
        raise RuntimeError('openai package not available; install openai>=1.0')

    try:
        # prefer Responses API if available
        if hasattr(openai, 'ChatCompletion'):
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            # Extract text and usage
            choice = resp.choices[0]
            content = choice.message.get('content') if isinstance(choice.message, dict) else choice.message
            usage = resp.get('usage', {})
            return {'text': content, 'raw': resp, 'usage': usage}
        else:
            # fallback to older completion API
            prompt = '\n'.join([m['content'] for m in messages if m['role'] in ('system', 'user')])
            resp = openai.Completion.create(model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
            text = resp.choices[0].text
            usage = resp.get('usage', {})
            return {'text': text, 'raw': resp, 'usage': usage}
    except Exception as exc:
        logger.exception('OpenAI call failed')
        raise


def call_embeddings(model: str, texts: List[str]) -> Dict[str, Any]:
    if not HAS_OPENAI:
        raise RuntimeError('openai package not available; install openai>=1.0')
    try:
        resp = openai.Embedding.create(model=model, input=texts)
        return {'raw': resp}
    except Exception:
        logger.exception('OpenAI embeddings failed')
        raise
