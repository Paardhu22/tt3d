class UserProfile:
    def __init__(self):
        self.mood = None
        self.environment = None
        self.style = None
        self.scale = None

    def is_complete(self):
        return all([self.mood, self.environment, self.style, self.scale])

    def to_dict(self):
        return {
            "mood": self.mood,
            "environment": self.environment,
            "style": self.style,
            "scale": self.scale
        }

    def is_valid_value(self, value: str) -> bool:
        if not value:
            return False

        value = value.lower().strip()

        invalid_markers = [
            "?",
            "what do",
            "wdym",
            "like",
            "mean",
            "explain"
        ]

        return not any(marker in value for marker in invalid_markers)
