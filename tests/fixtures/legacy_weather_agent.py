from agents.basic_agent import BasicAgent


class WeatherLookupAgent(BasicAgent):
    def __init__(self):
        self.name = "Weather Lookup"
        self.metadata = {
            "name": self.name,
            "description": "Looks up a forecast for a city from invented sample data.",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return {"Paris": "Sunny, 21C"}.get(kwargs.get("city", ""), "No forecast for that city.")
