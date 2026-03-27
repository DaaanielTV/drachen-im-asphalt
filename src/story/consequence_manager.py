class ConsequenceManager:
    """
    Verwaltet persistente Entscheidungs-Flags und deren Auswirkungen.
    Neue Konsequenzen lassen sich zentral erweitern, indem lediglich
    weitere Flags und Modifikatoren ergänzt werden.
    """

    def __init__(self, decision_flags=None):
        self.decision_flags = decision_flags or {}
        self._mission_modifiers = {
            "First Taste of Vice City": {
                "loyal_to_rico": {"action_success_bonus": 0.1},
                "skeptical_of_rico": {"action_success_bonus": -0.05, "escape_success_bonus": 0.05},
            },
            "*": {
                "silent_operator": {"stealth_success_bonus": 0.1},
                "police_heat_high": {"escape_success_bonus": -0.15},
                "corrupt_contacts": {"escape_success_bonus": 0.08},
            }
        }

    def record_decision(self, flag, source, value=True, metadata=None):
        self.decision_flags[flag] = {
            "value": value,
            "source": source,
            "metadata": metadata or {}
        }

    def has_flag(self, flag):
        return self.decision_flags.get(flag, {}).get("value", False)

    def meets_requirements(self, require_all=None, require_any=None, block_if_any=None):
        require_all = require_all or []
        require_any = require_any or []
        block_if_any = block_if_any or []

        if any(self.has_flag(flag) for flag in block_if_any):
            return False
        if require_all and not all(self.has_flag(flag) for flag in require_all):
            return False
        if require_any and not any(self.has_flag(flag) for flag in require_any):
            return False
        return True

    def get_mission_modifiers(self, mission_name):
        modifiers = {}
        for scope in ("*", mission_name):
            scope_modifiers = self._mission_modifiers.get(scope, {})
            for flag, values in scope_modifiers.items():
                if self.has_flag(flag):
                    for key, value in values.items():
                        modifiers[key] = modifiers.get(key, 0) + value
        return modifiers

    def get_chapter_events(self, chapter, shown_event_ids=None):
        shown_event_ids = shown_event_ids or []
        events = []

        chapter_events = {
            3: [
                ("chapter3_police_pressure", "Die Polizei ist wegen deiner aggressiven Methoden aufmerksamer denn je."),
                ("chapter3_quiet_respect", "Flüsternd spricht die Unterwelt von deiner ruhigen, sauberen Arbeitsweise.")
            ],
            4: [
                ("chapter4_corrupt_network", "Deine Bestechungsgelder zahlen sich aus: Informanten in Uniform warnen dich frühzeitig."),
                ("chapter4_broken_trust", "Rico hält Abstand - dein Misstrauen vom Beginn verfolgt jede Verhandlung.")
            ],
            5: [
                ("chapter5_loyalty_dividend", "Alte Loyalität zahlt sich aus: Verbündete stehen hinter dir, obwohl die Stadt brennt.")
            ]
        }

        flag_requirements = {
            "chapter3_police_pressure": "police_heat_high",
            "chapter3_quiet_respect": "silent_operator",
            "chapter4_corrupt_network": "corrupt_contacts",
            "chapter4_broken_trust": "skeptical_of_rico",
            "chapter5_loyalty_dividend": "loyal_to_rico",
        }

        for event_id, event_text in chapter_events.get(chapter, []):
            required_flag = flag_requirements.get(event_id)
            if event_id not in shown_event_ids and required_flag and self.has_flag(required_flag):
                events.append((event_id, event_text))

        return events
