import random


class DayNightCycle:
    def __init__(self, start_hour=8):
        self.hour = start_hour
        self.day = 1
        self.time_speed = 1.0

    @property
    def period(self):
        if 6 <= self.hour < 12:
            return "morning"
        elif 12 <= self.hour < 17:
            return "afternoon"
        elif 17 <= self.hour < 21:
            return "evening"
        elif 21 <= self.hour < 24 or 0 <= self.hour < 6:
            return "night"

    @property
    def period_name(self):
        names = {
            "morning": "Morgen",
            "afternoon": "Nachmittag",
            "evening": "Abend",
            "night": "Nacht"
        }
        return names.get(self.period, "Unbekannt")

    @property
    def is_night(self):
        return self.period == "night"

    @property
    def is_day(self):
        return not self.is_night

    @property
    def police_modifier(self):
        if self.is_night:
            return 1.3
        elif self.period == "evening":
            return 1.15
        elif self.period == "morning":
            return 0.9
        return 1.0

    @property
    def encounter_modifier(self):
        if self.is_night:
            return 1.4
        elif self.period == "evening":
            return 1.2
        elif self.period == "afternoon":
            return 1.0
        return 0.85

    @property
    def market_price_modifier(self):
        if self.is_night:
            return 1.2
        elif self.period == "evening":
            return 1.1
        elif self.period == "morning":
            return 0.95
        return 1.0

    @property
    def danger_modifier(self):
        if self.is_night:
            return 1.25
        elif self.period == "evening":
            return 1.1
        elif self.period == "morning":
            return 0.85
        return 1.0

    def advance_hours(self, hours):
        self.hour = (self.hour + hours) % 24
        if self.hour < hours:
            self.day += 1

    def get_time_display(self):
        return f"Tag {self.day}, {self.hour:02d}:00 - {self.period_name}"

    def get_period_emoji(self):
        emojis = {
            "morning": "🌅",
            "afternoon": "☀️",
            "evening": "🌆",
            "night": "🌙"
        }
        return emojis.get(self.period, "")

    def get_narrative_flavor(self):
        flavors = {
            "morning": [
                "Die Sonne geht über Vice City auf. Die Straßen erwachen langsam zum Leben.",
                "Morgennebel hängt über den Stränden. Die Stadt ist noch ruhig.",
                "Das erste Licht der Dämmerung erfasst die Skyline von Downtown."
            ],
            "afternoon": [
                "Volle Straßenn und geschäftiges Treiben in der Innenstadt.",
                "Die Hitze des Tages liegt über der Stadt. Touristen bevölkern die Strände.",
                "Mittagsverkehr in Vice City. Die Zeit für Geschäfte ist günstig."
            ],
            "evening": [
                "Die Neonlichter erwachen zum Leben. Die Stadt belongs den Kriminellen.",
                "Sonnenuntergang über der Skyline. Die Schatten werden länger.",
                "Abendstimmung in Vice City. Die gefährlichste Zeit des Tages beginnt."
            ],
            "night": [
                "Die dunklen Seiten von Vice City erwachen. Hier gelten andere Regeln.",
                "Nachts gehört die Stadt denen, die das Licht scheuen.",
                "Der Mond scheint über Vice City. Gefahr lauert in jeder Gasse."
            ]
        }
        return random.choice(flavors.get(self.period, [""]))

    def to_dict(self):
        return {
            "hour": self.hour,
            "day": self.day,
            "time_speed": self.time_speed
        }

    @classmethod
    def from_dict(cls, data):
        cycle = cls(start_hour=data.get("hour", 8))
        cycle.day = data.get("day", 1)
        cycle.time_speed = data.get("time_speed", 1.0)
        return cycle
