from dataclasses import dataclass, field
from typing import Optional
import random
from datetime import datetime


@dataclass
class MarketListing:
    item_id: str
    item_name: str
    item_type: str
    price: int
    quantity: int
    seller_rating: float
    listed_at: str
    district: str


@dataclass
class BlackMarketTrend:
    item_category: str
    trend_direction: str
    price_modifier: float
    demand_level: str


class UndergroundEconomy:
    def __init__(self):
        self.market_listings: list[MarketListing] = []
        self.price_trends: dict[str, BlackMarketTrend] = {}
        self.district_markets: dict[str, list[str]] = {}
        self.event_multipliers: dict[str, float] = {}
        self.market_events: list[dict] = []
        self.last_update: str = ""
        self._initialize_trends()
        self._initialize_events()

    def _initialize_trends(self):
        categories = ["weapons", "drugs", "vehicles", "intel", "services", "properties"]
        for category in categories:
            self.price_trends[category] = BlackMarketTrend(
                item_category=category,
                trend_direction="stable",
                price_modifier=1.0,
                demand_level="normal"
            )

    def _initialize_events(self):
        self.market_events = [
            {
                "name": "Polizei-Razzia",
                "description": "Die Polizei hat einen Razzia durchgeführt! Die Preise steigen.",
                "affected_categories": ["weapons", "drugs"],
                "price_increase": 1.5,
                "duration": 3
            },
            {
                "name": "Schmugglerlieferung",
                "description": "Eine große Lieferung ist angekommen. Die Preise fallen!",
                "affected_categories": ["weapons", "drugs"],
                "price_decrease": 0.7,
                "duration": 2
            },
            {
                "name": "Gang-Krieg",
                "description": "Eine Gang-Krieg eskaliert. Die Nachfrage steigt.",
                "affected_categories": ["weapons", "services"],
                "price_increase": 1.3,
                "duration": 5
            },
            {
                "name": "Wirtschaftsflaut",
                "description": "Die Wirtschaft stagniert. Weniger Käufer, niedrigere Preise.",
                "affected_categories": ["properties", "vehicles"],
                "price_decrease": 0.8,
                "duration": 4
            },
            {
                "name": "Neue Konkurrenz",
                "description": "Ein neuer Markt hat eröffnet. Bessere Preise!",
                "affected_categories": ["weapons", "drugs"],
                "price_decrease": 0.85,
                "duration": 3
            },
        ]

    def get_base_price(self, item_type: str, base_value: int) -> int:
        trend = self.price_trends.get(item_type)
        modifier = 1.0

        if trend:
            if trend.trend_direction == "rising":
                modifier = trend.price_modifier
            elif trend.trend_direction == "falling":
                modifier = trend.price_modifier

        for event in self.market_events:
            if item_type in event.get("affected_categories", []):
                if "price_increase" in event:
                    modifier *= event["price_increase"]
                elif "price_decrease" in event:
                    modifier *= event["price_decrease"]

        for mult in self.event_multipliers.values():
            modifier *= mult

        return int(base_value * modifier)

    def get_sell_price(self, item_type: str, base_value: int, condition: int = 100) -> int:
        buy_price = self.get_base_price(item_type, base_value)
        condition_factor = condition / 100
        return int(buy_price * 0.6 * condition_factor)

    def update_market(self) -> None:
        self.last_update = datetime.now().isoformat()

        for category, trend in self.price_trends.items():
            roll = random.random()
            if roll < 0.2:
                trend.trend_direction = "rising"
                trend.price_modifier = random.uniform(1.1, 1.3)
                trend.demand_level = "high" if trend.price_modifier > 1.2 else "moderate"
            elif roll < 0.35:
                trend.trend_direction = "falling"
                trend.price_modifier = random.uniform(0.7, 0.9)
                trend.demand_level = "low"
            else:
                trend.trend_direction = "stable"
                trend.price_modifier = 1.0
                trend.demand_level = "normal"

        active_events = [e for e in self.market_events if e.get("duration", 0) > 0]
        for event in active_events:
            event["duration"] -= 1

        if random.random() < 0.3 and len(active_events) < 2:
            new_event = random.choice(self.market_events)
            if new_event not in self.market_events:
                self.market_events.append({**new_event, "duration": new_event.get("duration", 3)})

        self._generate_new_listings()

    def _generate_new_listings(self):
        district_list = ["Ocean Beach", "Washington Beach", "Viceport", "Downtown", "Little Haiti"]

        if random.random() < 0.5:
            item_types = [
                ("Pistole", "weapons", 200),
                ("Schrotflinte", "weapons", 600),
                ("Schutzweste", "weapons", 150),
                ("Speed", "drugs", 80),
                ("Crack", "drugs", 150),
                ("Pillen", "drugs", 100),
                ("Alkohol", "drugs", 20),
                ("Informationen", "intel", 500),
                ("Fahrzeug", "vehicles", 3000),
            ]

            item = random.choice(item_types)
            base_price = self.get_base_price(item[1], item[2])

            listing = MarketListing(
                item_id=f"{item[0].lower()}_{random.randint(100, 999)}",
                item_name=item[0],
                item_type=item[1],
                price=base_price,
                quantity=random.randint(1, 3),
                seller_rating=random.uniform(3.0, 5.0),
                listed_at=datetime.now().isoformat(),
                district=random.choice(district_list),
            )
            self.market_listings.append(listing)

        if len(self.market_listings) > 50:
            self.market_listings = self.market_listings[-50:]

    def get_listings_by_type(self, item_type: str) -> list[MarketListing]:
        return [l for l in self.market_listings if l.item_type == item_type]

    def get_listings_by_district(self, district: str) -> list[MarketListing]:
        return [l for l in self.market_listings if l.district == district]

    def purchase_listing(self, listing_id: str, protagonist) -> tuple[bool, str]:
        for i, listing in enumerate(self.market_listings):
            if listing.item_id == listing_id:
                if protagonist.cash < listing.price:
                    return False, "Nicht genug Geld!"

                if listing.quantity <= 0:
                    return False, "Artikel nicht mehr verfügbar!"

                protagonist.cash -= listing.price
                listing.quantity -= 1

                if listing.quantity <= 0:
                    self.market_listings.pop(i)

                return True, f"Du hast {listing.item_name} für ${listing.price} gekauft!"

        return False, "Angebot nicht gefunden."

    def sell_to_market(self, item_name: str, item_type: str, base_value: int, quantity: int, protagonist, district: str) -> tuple[bool, str]:
        sell_price = self.get_sell_price(item_type, base_value)

        listing = MarketListing(
            item_id=f"{item_name.lower()}_{random.randint(1000, 9999)}",
            item_name=item_name,
            item_type=item_type,
            price=sell_price,
            quantity=quantity,
            seller_rating=4.0,
            listed_at=datetime.now().isoformat(),
            district=district,
        )

        self.market_listings.append(listing)
        return True, f"{item_name} wurde zum Markt hinzugefügt!"

    def get_market_report(self) -> str:
        report = "\n[SCHWARZMARKT] Marktbericht:\n"
        report += f"Letzte Aktualisierung: {self.last_update}\n\n"

        report += "Preistrends:\n"
        for category, trend in self.price_trends.items():
            arrow = {"rising": "↑", "falling": "↓", "stable": "→"}[trend.trend_direction]
            report += f"  {category.capitalize()}: {arrow} ({trend.demand_level})\n"

        active = [e for e in self.market_events if e.get("duration", 0) > 0]
        if active:
            report += "\nAktive Ereignisse:\n"
            for event in active:
                report += f"  - {event['name']}: {event['description']}\n"

        return report

    def get_favorable_deals(self, max_price: int) -> list[MarketListing]:
        return [l for l in self.market_listings if l.price <= max_price and l.seller_rating >= 4.0]


class PriceCalculator:
    DISTINCT_FEES = {
        "Ocean Beach": 1.1,
        "Washington Beach": 1.0,
        "Vice Point": 1.15,
        "Viceport": 0.9,
        "Downtown": 1.2,
        "Little Haiti": 0.95,
        "Starfish Island": 1.5,
        "Everglades": 0.85,
        "Vice Keys": 0.8,
        "Industrial Zone": 0.9,
        "Airport": 1.1,
        "Suburbs": 0.85,
        "Casino Strip": 1.3,
    }

    @classmethod
    def calculate_price(cls, base_price: int, district: str, time_of_day: str = "day", reputation: int = 0) -> int:
        district_fee = cls.DISTINCT_FEES.get(district, 1.0)

        time_multiplier = 1.0
        if time_of_day == "night":
            time_multiplier = 1.2
        elif time_of_day == "dawn":
            time_multiplier = 0.9

        rep_discount = 1.0 - (reputation * 0.001)

        final_price = base_price * district_fee * time_multiplier * rep_discount
        return int(final_price)

    @classmethod
    def get_best_district_for_price(cls, base_price: int, item_type: str) -> tuple[str, int]:
        best_district = "Vice Keys"
        best_price = float('inf')

        for district, fee in cls.DISTINCT_FEES.items():
            price = int(base_price * fee)
            if price < best_price:
                best_price = price
                best_district = district

        return best_district, best_price

    @classmethod
    def calculate_bulk_discount(cls, quantity: int) -> float:
        if quantity >= 10:
            return 0.8
        elif quantity >= 5:
            return 0.9
        elif quantity >= 3:
            return 0.95
        return 1.0

    @classmethod
    def calculate_urgency_fee(cls, is_urgent: bool, base_price: int) -> int:
        if is_urgent:
            return int(base_price * 0.25)
        return 0