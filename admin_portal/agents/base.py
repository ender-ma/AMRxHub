class BaseAgent:
    key = "base"
    label = "Base Agent"
    description = ""

    def run(self, payload):
        raise NotImplementedError