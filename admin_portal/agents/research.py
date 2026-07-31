from .base import BaseAgent
from admin_portal.ai_registry import register_agent

@register_agent
class ResearchAgent(BaseAgent):
    key = "research"
    label = "Research Agent"
    description = "Extracts content and metadata from submitted URLs."

    def run(self, payload):
        return {"status": "ok", "data": payload}