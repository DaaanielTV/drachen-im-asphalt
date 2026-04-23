from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class JournalEntry:
    entry_id: str
    date: int
    chapter: int
    category: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    is_secret: bool = False
    importance: str = "normal"

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "date": self.date,
            "chapter": self.chapter,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "is_secret": self.is_secret,
            "importance": self.importance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JournalEntry":
        return cls(**data)


class SearchableJournal:
    CATEGORIES = ["mission", "story", "character", "location", "intel", "personal", "secret"]
    IMPORTANCE_LEVELS = ["low", "normal", "high", "critical"]

    def __init__(self):
        self.entries: list[JournalEntry] = []
        self.search_index: dict[str, list[int]] = {}
        self.last_entry_id: int = 0

    def add_entry(self, category: str, title: str, content: str, date: int = 0, chapter: int = 1,
                  tags: list[str] = None, is_secret: bool = False, importance: str = "normal") -> JournalEntry:
        self.last_entry_id += 1
        entry = JournalEntry(
            entry_id=f"entry_{self.last_entry_id}",
            date=date,
            chapter=chapter,
            category=category,
            title=title,
            content=content,
            tags=tags or [],
            is_secret=is_secret,
            importance=importance,
        )
        self.entries.append(entry)
        self._update_index(entry)
        return entry

    def _update_index(self, entry: JournalEntry) -> None:
        words = self._tokenize(f"{entry.title} {entry.content}")
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = []
            self.search_index[word].append(len(self.entries) - 1)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) >= 3]

    def search(self, query: str, category: str = None, tags: list[str] = None,
               importance: str = None) -> list[JournalEntry]:
        query = query.lower()
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        result_indices = set()
        for token in query_tokens:
            if token in self.search_index:
                if not result_indices:
                    result_indices = set(self.search_index[token])
                else:
                    result_indices &= set(self.search_index[token])

        if not query_tokens:
            result_indices = set(range(len(self.entries)))

        results = []
        for idx in result_indices:
            entry = self.entries[idx]
            matches = True

            if category and entry.category != category:
                matches = False
            if tags and not any(tag in entry.tags for tag in tags):
                matches = False
            if importance and entry.importance != importance:
                matches = False

            if matches:
                results.append(entry)

        results.sort(key=lambda e: (e.importance in self.IMPORTANCE_LEVELS and
                                   self.IMPORTANCE_LEVELS.index(e.importance)), reverse=True)
        return results

    def get_by_category(self, category: str) -> list[JournalEntry]:
        return [e for e in self.entries if e.category == category]

    def get_by_tag(self, tag: str) -> list[JournalEntry]:
        return [e for e in self.entries if tag in e.tags]

    def get_by_date_range(self, start_date: int, end_date: int) -> list[JournalEntry]:
        return [e for e in self.entries if start_date <= e.date <= end_date]

    def get_by_chapter(self, chapter: int) -> list[JournalEntry]:
        return [e for e in self.entries if e.chapter == chapter]

    def get_all_tags(self) -> list[str]:
        tags = set()
        for entry in self.entries:
            tags.update(entry.tags)
        return sorted(list(tags))

    def get_statistics(self) -> dict:
        stats = {
            "total_entries": len(self.entries),
            "by_category": {},
            "by_importance": {},
            "total_tags": len(self.get_all_tags()),
        }
        for entry in self.entries:
            stats["by_category"][entry.category] = stats["by_category"].get(entry.category, 0) + 1
            stats["by_importance"][entry.importance] = stats["by_importance"].get(entry.importance, 0) + 1
        return stats

    def display_entry(self, entry: JournalEntry) -> str:
        importance_indicator = {
            "low": "[•]",
            "normal": "[■]",
            "high": "[■■]",
            "critical": "[■■■]",
        }
        indicator = importance_indicator.get(entry.importance, "[■]")
        secret_indicator = " [GEHEIM]" if entry.is_secret else ""

        display = f"""
{'=' * 60}
{indicator} {entry.title}{secret_indicator}
{'=' * 60}
Datum: Tag {entry.date} | Kapitel: {entry.chapter} | Kategorie: {entry.category.upper()}
{'=' * 60}
{entry.content}
{'=' * 60}"""

        if entry.tags:
            display += f"\nTags: {', '.join(entry.tags)}"
        return display

    def display_search_results(self, results: list[JournalEntry]) -> str:
        if not results:
            return "[JOURNAL] Keine Einträge gefunden."

        display = f"\n[JOURNAL] Suchergebnisse ({len(results)} gefunden):\n"
        for entry in results[:20]:
            indicator = {"low": "[•]", "normal": "[■]", "high": "[■■]", "critical": "[■■■]"}.get(entry.importance, "[■]")
            display += f"\n{indicator} {entry.title}"
            display += f"\n  {entry.content[:100]}..."
        return display

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "last_entry_id": self.last_entry_id,
        }

    def load_from_dict(self, data: dict) -> None:
        if "entries" in data:
            self.entries = [JournalEntry.from_dict(e) for e in data["entries"]]
        if "last_entry_id" in data:
            self.last_entry_id = data["last_entry_id"]
        for entry in self.entries:
            self._update_index(entry)


class StatusDisplay:
    COLORS = {
        "reset": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "dim": "\033[2m",
    }

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def colorize(self, text: str, color: str) -> str:
        if not self.use_colors or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"

    def get_color_for_stat(self, stat_name: str, value: int, max_value: int = 100) -> str:
        ratio = value / max_value
        if stat_name in ["wanted_level", "stress_level"]:
            if ratio > 0.7:
                return "red"
            elif ratio > 0.4:
                return "yellow"
            else:
                return "green"
        else:
            if ratio < 0.3:
                return "red"
            elif ratio < 0.6:
                return "yellow"
            else:
                return "green"

    def create_bar(self, value: int, max_value: int, length: int = 20, filled_char: str = "█",
                   empty_char: str = "░") -> str:
        filled = int((value / max_value) * length)
        return f"{filled_char * filled}{empty_char * (length - filled)}"

    def display_stat_bar(self, label: str, value: int, max_value: int, show_numbers: bool = True) -> str:
        color = self.get_color_for_stat(label, value, max_value)
        bar = self.create_bar(value, max_value)
        if show_numbers:
            return f"{label}: {self.colorize(bar, color)} ({value}/{max_value})"
        return f"{label}: {self.colorize(bar, color)}"

    def format_cash(self, amount: int) -> str:
        if amount >= 1000000:
            return f"${amount / 1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount / 1000:.1f}K"
        return f"${amount}"

    def display_character_status(self, protagonist) -> str:
        display = f"""
{self.colorize('=' * 60, 'bold')}
{self.colorize(f'  {protagonist.name.upper()} - {protagonist.character_type.upper()}', 'cyan')}
{self.colorize('=' * 60, 'bold')}

{self.display_stat_bar('Ausdauer', protagonist.stamina, protagonist.level * 25)}
{self.display_stat_bar('Stress', protagonist.stress_level, 100, show_numbers=True)}
{self.display_stat_bar('Partner-Trust', protagonist.partner_trust, 100)}

{self.colorize(f'  Cash: {self.format_cash(protagonist.cash)}', 'yellow')}
{self.colorize(f'  Level: {protagonist.level} | Kapitel: {protagonist.chapter}', 'blue')}
{self.colorize(f'  Tage: {protagonist.days}', 'dim')}

{self.colorize('  Inventar: ' + ', '.join([i.name if hasattr(i, 'name') else str(i) for i in protagonist.inventory[:5]]) if protagonist.inventory else 'Leer', 'white')}
"""

        wanted_color = "green" if protagonist.wanted_level < 2 else "yellow" if protagonist.wanted_level < 4 else "red"
        display += f"{self.display_stat_bar('Wanted', protagonist.wanted_level, 5)}\n"
        display += f"{self.display_stat_bar('Reputation', protagonist.reputation, 100)}\n"

        if hasattr(protagonist, 'hallucination_intensity'):
            display += f"{self.display_stat_bar('Halluzination', int(protagonist.hallucination_intensity * 100), 100)}\n"

        return display

    def display_mission_status(self, mission_manager) -> str:
        display = f"\n{self.colorize('[AKTUELLE MISSIONEN]', 'bold')}\n"
        active_missions = [m for m in mission_manager.all_missions.values() if m.available and not m.completed]

        if not active_missions:
            return display + "  Keine aktiven Missionen.\n"

        for mission in active_missions[:5]:
            status = "[ ]"
            display += f"  {status} {mission.name} (Kapitel {mission.chapter})\n"
        return display

    def display_district_status(self, district_manager) -> str:
        display = f"\n{self.colorize('[STADTTEILE]', 'bold')}\n"
        for name, district in list(district_manager.districts.items())[:5]:
            rep_indicator = "+" if district.reputation > 0 else "-" if district.reputation < 0 else "="
            rep_color = "green" if district.reputation > 0 else "red" if district.reputation < 0 else "white"
            display += f"  {name}: {self.colorize(rep_indicator, rep_color)}{abs(district.reputation)}\n"
        return display

    def display_quick_status(self, protagonist) -> str:
        return f"""[{protagonist.name}] L{protagonist.level} | ${protagonist.cash} | {'★' * protagonist.wanted_level} | {protagonist.stamina}STA | Tag {protagonist.days}"""