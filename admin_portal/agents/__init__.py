# agents package — avoid importing submodules at package import time to prevent
# side-effects during Django startup and test discovery. Modules are discovered
# dynamically via admin_portal.ai_registry._discover_agents().
from . import base
__all__ = ["base"]
