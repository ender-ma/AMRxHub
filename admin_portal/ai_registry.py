AI_AGENT_REGISTRY = {}

def register_agent(agent_class):
    AI_AGENT_REGISTRY[agent_class.key] = agent_class
    return agent_class

def get_agent(key):
    return AI_AGENT_REGISTRY.get(key)

def list_agents():
    return list(AI_AGENT_REGISTRY.values())