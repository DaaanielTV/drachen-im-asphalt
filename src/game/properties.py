from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Property:
    name: str
    property_type: str
    location: str
    purchase_price: int
    current_value: int
    security_level: int
    storage_capacity: int
    description: str
    owned: bool = False
    upgrades: list[str] = field(default_factory=list)
    monthly_cost: int = 0
    income_per_day: int = 0

    def calculate_value_change(self, days: int) -> int:
        market_change = int(self.current_value * 0.001 * days)
        upgrade_bonus = sum(u["value_bonus"] for u in self.upgrades if isinstance(u, dict))
        return market_change + upgrade_bonus

    def get_upgrade_cost(self, upgrade_name: str) -> int:
        upgrade_costs = {
            "security": 500,
            "storage": 300,
            "disguise": 400,
            "garage": 800,
            "safe_room": 600,
        }
        return upgrade_costs.get(upgrade_name, 200)

    def add_upgrade(self, upgrade_name: str) -> bool:
        if upgrade_name in self.upgrades:
            return False
        self.upgrades.append(upgrade_name)
        self.security_level += 10
        self.storage_capacity += 20
        return True

    def can_access(self, stealth_level: int, wanted_level: int) -> bool:
        detection_risk = wanted_level * 5
        base_threshold = 100 - self.security_level
        return stealth_level * 2 >= base_threshold + detection_risk

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "property_type": self.property_type,
            "location": self.location,
            "purchase_price": self.purchase_price,
            "current_value": self.current_value,
            "security_level": self.security_level,
            "storage_capacity": self.storage_capacity,
            "description": self.description,
            "owned": self.owned,
            "upgrades": self.upgrades,
            "monthly_cost": self.monthly_cost,
            "income_per_day": self.income_per_day,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Property":
        return cls(**data)


class PropertyManager:
    def __init__(self):
        self.properties: dict[str, Property] = {}
        self.owned_properties: list[str] = []
        self.current_property: Optional[str] = None
        self._initialize_properties()

    def _initialize_properties(self):
        self.properties = {
            "cheap_apartment": Property(
                name="Billige Wohnung",
                property_type="apartment",
                location="Washington Beach",
                purchase_price=2000,
                current_value=2000,
                security_level=10,
                storage_capacity=20,
                description="Eine schäbige Wohnung. Besser als nichts.",
                monthly_cost=100,
            ),
            "motel_room": Property(
                name="Motelzimmer",
                property_type="motel",
                location="Washington Beach",
                purchase_price=1500,
                current_value=1500,
                security_level=5,
                storage_capacity=15,
                description="Ein Zimmer im Vice Motel. Nicht sehr sicher.",
                monthly_cost=80,
            ),
            "beach_house": Property(
                name="Strandhaus",
                property_type="house",
                location="Ocean Beach",
                purchase_price=8000,
                current_value=8000,
                security_level=20,
                storage_capacity=40,
                description="Ein kleines Strandhaus mit tollem Ausblick.",
                income_per_day=50,
                monthly_cost=200,
            ),
            "warehouse": Property(
                name="Lagerhaus",
                property_type="warehouse",
                location="Viceport",
                purchase_price=15000,
                current_value=15000,
                security_level=30,
                storage_capacity=100,
                description="Ein großes Lagerhaus im Hafen. Perfekt für Geschäfte.",
                income_per_day=100,
                monthly_cost=300,
            ),
            "office_space": Property(
                name="Bürofläche",
                property_type="office",
                location="Downtown",
                purchase_price=25000,
                current_value=25000,
                security_level=40,
                storage_capacity=60,
                description="Ein Büro in der Innenstadt. Seriöse Fassade.",
                income_per_day=150,
                monthly_cost=500,
            ),
            "mansion": Property(
                name="Villa",
                property_type="mansion",
                location="Starfish Island",
                purchase_price=100000,
                current_value=100000,
                security_level=50,
                storage_capacity=150,
                description="Eine luxuriöse Villa auf Starfish Island.",
                income_per_day=500,
                monthly_cost=1000,
            ),
            "nightclub": Property(
                name="Nachtclub",
                property_type="business",
                location="Casino Strip",
                purchase_price=50000,
                current_value=50000,
                security_level=35,
                storage_capacity=80,
                description="Ein Nachtclub. Geldwäsche und Unterhaltung.",
                income_per_day=300,
                monthly_cost=800,
            ),
            "safe_house": Property(
                name="Safe House",
                property_type="safehouse",
                location="Little Haiti",
                purchase_price=5000,
                current_value=5000,
                security_level=60,
                storage_capacity=30,
                description="Ein verstecktes Safe House. Niemand weiß davon.",
            ),
            "boat_dock": Property(
                name=" Bootsanleger",
                property_type="dock",
                location="Vice Keys",
                purchase_price=12000,
                current_value=12000,
                security_level=25,
                storage_capacity=50,
                description="Ein Bootsanleger auf den Keys. Für Fluchten und Schmuggel.",
                income_per_day=80,
                monthly_cost=250,
            ),
            "garage": Property(
                name="Autowerkstatt",
                property_type="garage",
                location="Industrial Zone",
                purchase_price=10000,
                current_value=10000,
                security_level=30,
                storage_capacity=60,
                description="Eine Autowerkstatt. Hier kannst du Fahrzeuge verstecken.",
                income_per_day=75,
                monthly_cost=200,
            ),
        }

    def get_property(self, name: str) -> Optional[Property]:
        return self.properties.get(name)

    def get_all_properties(self) -> list[Property]:
        return list(self.properties.values())

    def get_owned_properties(self) -> list[Property]:
        return [self.properties[name] for name in self.owned_properties if name in self.properties]

    def get_available_properties(self, cash: int) -> list[Property]:
        return [p for p in self.properties.values() if not p.owned and p.purchase_price <= cash * 2]

    def buy_property(self, property_name: str, protagonist) -> tuple[bool, str]:
        prop = self.properties.get(property_name)
        if not prop:
            return False, "Immobilie nicht gefunden."

        if prop.owned:
            return False, "Diese Immobilie gehört dir bereits."

        price = prop.purchase_price
        if protagonist.cash < price:
            return False, f"Nicht genug Geld. Du brauchst ${price}."

        protagonist.cash -= price
        prop.owned = True
        self.owned_properties.append(property_name)

        if hasattr(protagonist, "achievement_manager"):
            protagonist.achievement_manager.unlock("first_property", protagonist.days)

        return True, f"Du hast {prop.name} gekauft!"

    def sell_property(self, property_name: str, protagonist) -> tuple[bool, str]:
        prop = self.properties.get(property_name)
        if not prop or not prop.owned:
            return False, "Du besitzt diese Immobilie nicht."

        sell_price = int(prop.current_value * 0.7)
        protagonist.cash += sell_price
        prop.owned = False
        self.owned_properties.remove(property_name)

        return True, f"Du hast {prop.name} für ${sell_price} verkauft!"

    def upgrade_property(self, property_name: str, upgrade_name: str, protagonist) -> tuple[bool, str]:
        prop = self.properties.get(property_name)
        if not prop or not prop.owned:
            return False, "Du besitzt diese Immobilie nicht."

        if upgrade_name in prop.upgrades:
            return False, "Dieses Upgrade ist bereits installiert."

        cost = prop.get_upgrade_cost(upgrade_name)
        if protagonist.cash < cost:
            return False, f"Nicht genug Geld. Du brauchst ${cost}."

        protagonist.cash -= cost
        prop.add_upgrade(upgrade_name)

        return True, f"{prop.name} wurde aufgerüstet mit {upgrade_name}!"

    def set_current_property(self, property_name: str) -> bool:
        if property_name in self.owned_properties:
            self.current_property = property_name
            return True
        return False

    def get_current_property(self) -> Optional[Property]:
        if self.current_property:
            return self.properties.get(self.current_property)
        return None

    def get_property_income(self) -> int:
        total = 0
        for prop_name in self.owned_properties:
            prop = self.properties.get(prop_name)
            if prop:
                total += prop.income_per_day
        return total

    def pay_maintenance(self, protagonist) -> int:
        total_cost = 0
        for prop_name in self.owned_properties:
            prop = self.properties.get(prop_name)
            if prop:
                total_cost += prop.monthly_cost

        if protagonist.cash >= total_cost:
            protagonist.cash -= total_cost
        else:
            for prop_name in self.owned_properties[:]:
                prop = self.properties.get(prop_name)
                if prop and protagonist.cash >= prop.monthly_cost:
                    protagonist.cash -= prop.monthly_cost
                else:
                    self.foreclose_property(prop_name, protagonist)

        return total_cost

    def foreclose_property(self, property_name: str, protagonist) -> None:
        prop = self.properties.get(property_name)
        if prop and prop.owned:
            prop.owned = False
            self.owned_properties.remove(property_name)
            print(f"\n[INFO] {prop.name} wurde wegen Zahlungsunfähigkeit enteignet!")

    def collect_income(self, protagonist) -> int:
        income = self.get_property_income()
        protagonist.cash += income
        return income

    def get_safe_houses(self) -> list[Property]:
        return [p for p in self.get_owned_properties() if p.property_type in ("safehouse", "apartment", "motel")]

    def to_dict(self) -> dict:
        return {
            "owned_properties": self.owned_properties,
            "current_property": self.current_property,
            "properties": {name: prop.to_dict() for name, prop in self.properties.items()},
        }

    def load_from_dict(self, data: dict) -> None:
        if "owned_properties" in data:
            self.owned_properties = data["owned_properties"]
            for prop_name in self.owned_properties:
                if prop_name in self.properties:
                    self.properties[prop_name].owned = True
        if "current_property" in data:
            self.current_property = data["current_property"]
        if "properties" in data:
            for name, prop_data in data["properties"].items():
                if name in self.properties:
                    self.properties[name].owned = prop_data.get("owned", False)
                    self.properties[name].upgrades = prop_data.get("upgrades", [])
                    self.properties[name].current_value = prop_data.get("current_value", self.properties[name].current_value)


class SafeHouse:
    def __init__(self, property: Property):
        self.property = property
        self.hidden = property.security_level >= 50
        self.beds: int = 1
        self.armory_level: int = 0
        self.healing_available: bool = True

    def heal(self, protagonist) -> None:
        if self.healing_available:
            protagonist.stamina = protagonist.level * 25
            protagonist.stress_level = max(0, protagonist.stress_level - 30)
            print(f"\n[AUFENTHALT] Du erholst dich in {self.property.name}.")
            print("Ausdauer regeneriert. Stress reduziert.")

    def rest(self, protagonist) -> None:
        self.heal(protagonist)
        protagonist.days += 1

    def upgrade_armory(self, level: int) -> None:
        self.armory_level = level

    def get_stash_value(self) -> int:
        total = 0
        for item in ["weapons", "drugs", "cash"]:
            total += getattr(self, f"{item}_stash", 0)
        return total