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

# Prefer the modern OpenAI client (OpenAI class with Responses API) when available.
# Fall back to the legacy openai package module if necessary.
try:
    from openai import OpenAI as OpenAIClient
    HAS_OPENAI = True
    USE_MODERN_CLIENT = True
    if OPENAI_API_KEY:
        client = OpenAIClient(api_key=OPENAI_API_KEY, api_base=OPENAI_API_BASE) if OPENAI_API_BASE else OpenAIClient(api_key=OPENAI_API_KEY)
    else:
        client = OpenAIClient()
except Exception:
    try:
        import openai
        HAS_OPENAI = True
        USE_MODERN_CLIENT = False
        client = openai
        if OPENAI_API_KEY:
            client.api_key = OPENAI_API_KEY
        if OPENAI_API_BASE:
            client.api_base = OPENAI_API_BASE
    except Exception:
        HAS_OPENAI = False
        USE_MODERN_CLIENT = False
        client = None


def call_chat_model(model: str, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
    """Call a chat-style model and return a structured dict.
    messages: list of {role: 'system'|'user'|'assistant', 'content': str}
    """
    if not HAS_OPENAI:
        raise RuntimeError('openai package not available; install openai>=1.0')

    try:
        # Modern OpenAI client (Responses API)
        if HAS_OPENAI and (USE_MODERN_CLIENT and hasattr(client, 'responses')):
            # Responses API prefers a single input string; combine messages into a single prompt.
            prompt = '\n'.join([m.get('content', '') for m in messages if m.get('content')])
            resp = client.responses.create(model=model, input=prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
            # Try multiple ways to extract text depending on SDK shape
            content = ''
            try:
                content = getattr(resp, 'output_text', '') or ''
            except Exception:
                content = ''
            if not content:
                try:
                    output = getattr(resp, 'output', None)
                    if isinstance(output, list) and len(output) > 0:
                        pieces = []
                        for item in output:
                            if isinstance(item, dict):
                                for c in item.get('content', []):
                                    if isinstance(c, dict) and c.get('type') == 'output_text':
                                        pieces.append(c.get('text', ''))
                        content = '\n'.join(pieces)
                except Exception:
                    content = ''
            usage = getattr(resp, 'usage', {}) if hasattr(resp, 'usage') else (resp.get('usage', {}) if isinstance(resp, dict) else {})
            return {'text': content, 'raw': resp, 'usage': usage}

        # Legacy openai module path (client acts as the openai module)
        if HAS_OPENAI and hasattr(client, 'ChatCompletion'):
            resp = client.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            choice = resp.choices[0]
            content = choice.message.get('content') if isinstance(choice.message, dict) else choice.message
            usage = resp.get('usage', {})
            return {'text': content, 'raw': resp, 'usage': usage}
        else:
            # fallback to older completion API
            prompt = '\n'.join([m['content'] for m in messages if m['role'] in ('system', 'user')])
            resp = client.Completion.create(model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
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
        if HAS_OPENAI and (USE_MODERN_CLIENT and hasattr(client, 'embeddings')):
            resp = client.embeddings.create(model=model, input=texts)
            return {'raw': resp}
        else:
            resp = client.Embedding.create(model=model, input=texts)
            return {'raw': resp}
    except Exception:
        logger.exception('OpenAI embeddings failed')
        raise
