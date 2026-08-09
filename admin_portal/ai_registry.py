"""
AI registry supporting function or class registration and lazy discovery.
"""
import importlib
import pkgutil
from typing import Callable, Dict, List

AI_AGENT_REGISTRY: Dict[str, Dict] = {}


def _discover_agents():
    """Import all modules under admin_portal.agents to let them register themselves."""
    try:
        import admin_portal.agents as agents_pkg
    except Exception:
        return
    pkgpath = getattr(agents_pkg, '__path__', None)
    if not pkgpath:
        return
    for finder, name, ispkg in pkgutil.iter_modules(pkgpath):
        mod_name = f"admin_portal.agents.{name}"
        try:
            importlib.import_module(mod_name)
        except Exception:
            # discovery should be best-effort; agents may fail to import if dependencies missing
            continue


def register_agent(*dargs, **dkwargs):
    """
    Supports two usages:
      - @register_agent('key', 'Label', description='...') on a function that returns metadata
      - @register_agent on a class with .key and .label attributes
    """
    # if used without args: @register_agent class
    if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
        agent_class = dargs[0]
        key = getattr(agent_class, 'key', None)
        label = getattr(agent_class, 'label', None)
        if not key:
            raise ValueError('Agent class must have a .key attribute')
        AI_AGENT_REGISTRY[key] = {
            'key': key,
            'label': label or key,
            'description': getattr(agent_class, 'description', ''),
            'status': getattr(agent_class, 'status', 'active'),
            'callable': agent_class,
        }
        return agent_class

    def _decorator(fn: Callable = None):
        if fn is None:
            # called with parameters -> return decorator
            def _wrap(f):
                key = dargs[0] if len(dargs) > 0 else dkwargs.get('key')
                label = dargs[1] if len(dargs) > 1 else dkwargs.get('label')
                description = dkwargs.get('description', '')
                status = dkwargs.get('status', 'active')
                AI_AGENT_REGISTRY[key] = {
                    'key': key,
                    'label': label or key,
                    'description': description,
                    'status': status,
                    'callable': f,
                }
                return f
            return _wrap
        else:
            # decorator used as @register_agent('k','L')(fn)
            key = dargs[0] if len(dargs) > 0 else dkwargs.get('key')
            label = dargs[1] if len(dargs) > 1 else dkwargs.get('label')
            description = dkwargs.get('description', '')
            status = dkwargs.get('status', 'active')
            AI_AGENT_REGISTRY[key] = {
                'key': key,
                'label': label or key,
                'description': description,
                'status': status,
                'callable': fn,
            }
            return fn

    return _decorator


def get_agent(key: str):
    if key in AI_AGENT_REGISTRY:
        return AI_AGENT_REGISTRY[key]
    # try discovery
    _discover_agents()
    return AI_AGENT_REGISTRY.get(key)


def list_agents() -> List[Dict]:
    if not AI_AGENT_REGISTRY:
        _discover_agents()
    return [
        {"key": v["key"], "label": v["label"], "description": v.get("description", ""), "status": v.get("status", "active")}
        for v in AI_AGENT_REGISTRY.values()
    ]
