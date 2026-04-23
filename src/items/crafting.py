from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CraftingIngredient:
    item_id: str
    name: str
    quantity: int = 1


@dataclass
class CraftingRecipe:
    recipe_id: str
    name: str
    description: str
    category: str
    ingredients: list[CraftingIngredient]
    result_item: str
    result_quantity: int = 1
    required_level: int = 1
    required_reputation: int = 0
    crafting_time: int = 1

    def can_craft(self, inventory: list, level: int, reputation: int) -> tuple[bool, list[str]]:
        missing = []
        if self.required_level > level:
            missing.append(f"Level {self.required_level} benötigt")
        if self.required_reputation > reputation:
            missing.append(f"Reputation {self.required_reputation} benötigt")

        available_items = {item.name if hasattr(item, 'name') else str(item): 0 for item in inventory}

        for item in inventory:
            item_name = getattr(item, 'name', str(item))
            if item_name in available_items:
                available_items[item_name] += 1

        for ingredient in self.ingredients:
            available = available_items.get(ingredient.name, 0)
            if available < ingredient.quantity:
                missing.append(f"{ingredient.name} ({available}/{ingredient.quantity})")

        return len(missing) == 0, missing


@dataclass
class CraftedItem:
    item_id: str
    name: str
    item_type: str
    stats: dict
    description: str


class CraftingSystem:
    def __init__(self):
        self.recipes: dict[str, CraftingRecipe] = {}
        self.crafted_items_cache: dict[str, CraftedItem] = {}
        self.crafting_station_level: int = 1
        self._initialize_recipes()

    def _initialize_recipes(self):
        self.recipes = {
            "molotov_cocktail": CraftingRecipe(
                recipe_id="molotov_cocktail",
                name="Molotow-Cocktail",
                description="Selbstgemachter Brandsatz.",
                category="Explosives",
                ingredients=[
                    CraftingIngredient(item_id="alcohol", name="Alkohol", quantity=1),
                    CraftingIngredient(item_id="rag", name="Lappen", quantity=1),
                ],
                result_item="Molotow-Cocktail",
                result_quantity=1,
                required_level=1,
            ),
            " lockpick": CraftingRecipe(
                recipe_id="lockpick",
                name="Dietrich-Set",
                description="Werkzeug zum Knacken von Schlössern.",
                category="Tools",
                ingredients=[
                    CraftingIngredient(item_id="metal_pieces", name="Metallstücke", quantity=3),
                ],
                result_item="Dietrich-Set",
                result_quantity=1,
                required_level=2,
            ),
            "stimpack": CraftingRecipe(
                recipe_id="stimpack",
                name="Medizinisches Stimpack",
                description="Notfall-Medikament zur sofortigen Heilung.",
                category="Medical",
                ingredients=[
                    CraftingIngredient(item_id="painkillers", name="Schmerzmittel", quantity=2),
                    CraftingIngredient(item_id="adrenaline", name="Adrenalin-Spritze", quantity=1),
                ],
                result_item="Stimpack",
                result_quantity=1,
                required_level=3,
            ),
            "silenced_pistol": CraftingRecipe(
                recipe_id="silenced_pistol",
                name="Schalldämpfer-Pistole",
                description="Pistole mit montiertem Schalldämpfer.",
                category="Weapons",
                ingredients=[
                    CraftingIngredient(item_id="pistol", name="Pistole", quantity=1),
                    CraftingIngredient(item_id="silencer", name="Schalldämpfer", quantity=1),
                ],
                result_item="Schalldämpfer-Pistole",
                result_quantity=1,
                required_level=4,
                required_reputation=20,
            ),
            "speedball_drug": CraftingRecipe(
                recipe_id="speedball_drug",
                name="Speedball-Mischung",
                description="Gefährliche Droge mit extremem Kick.",
                category="Drugs",
                ingredients=[
                    CraftingIngredient(item_id="cocaine", name="Crack", quantity=1),
                    CraftingIngredient(item_id="heroin", name="Heroin", quantity=1),
                ],
                result_item="Speedball",
                result_quantity=1,
                required_level=5,
                required_reputation=30,
            ),
            "emp_device": CraftingRecipe(
                recipe_id="emp_device",
                name="EMP-Gerät",
                description="Elektromagnetischer Puls. Deaktiviert Elektronik.",
                category="Tech",
                ingredients=[
                    CraftingIngredient(item_id="battery", name="Batterie", quantity=2),
                    CraftingIngredient(item_id="circuit", name="Schaltkreis", quantity=1),
                    CraftingIngredient(item_id="wire", name="Kabel", quantity=3),
                ],
                result_item="EMP-Gerät",
                result_quantity=1,
                required_level=5,
                required_reputation=25,
            ),
            "armor_vest": CraftingRecipe(
                recipe_id="armor_vest",
                name="Schutzweste",
                description="Körperschutz vor Kugeln.",
                category="Armor",
                ingredients=[
                    CraftingIngredient(item_id="kevlar", name="Kevlar-Platten", quantity=4),
                    CraftingIngredient(item_id="fabric", name="Stoff", quantity=2),
                ],
                result_item="Schutzweste",
                result_quantity=1,
                required_level=3,
            ),
            "flash_grenade": CraftingRecipe(
                recipe_id="flash_grenade",
                name="Blendgranate",
                description="Erzeugt hellen Blitz. Ideal für Escape.",
                category="Explosives",
                ingredients=[
                    CraftingIngredient(item_id="flash_powder", name="Blitzpulver", quantity=2),
                    CraftingIngredient(item_id="container", name="Behälter", quantity=1),
                ],
                result_item="Blendgranate",
                result_quantity=2,
                required_level=4,
            ),
            "drinking_kit": CraftingRecipe(
                recipe_id="drinking_kit",
                name="Trink-Set",
                description="Erlaubt das Herstellen von verfälschten Getränken.",
                category="Tools",
                ingredients=[
                    CraftingIngredient(item_id="bottle", name="Flasche", quantity=1),
                    CraftingIngredient(item_id="chemicals", name="Chemikalien", quantity=2),
                ],
                result_item="Trink-Set",
                result_quantity=1,
                required_level=2,
            ),
            "explosive_charge": CraftingRecipe(
                recipe_id="explosive_charge",
                name="Sprengladung",
                description="Konzentrierter Sprengstoff für Wände.",
                category="Explosives",
                ingredients=[
                    CraftingIngredient(item_id="gunpowder", name="Schießpulver", quantity=3),
                    CraftingIngredient(item_id="timer", name="Timer", quantity=1),
                    CraftingIngredient(item_id="container", name="Behälter", quantity=1),
                ],
                result_item="Sprengladung",
                result_quantity=1,
                required_level=5,
                required_reputation=35,
            ),
        }

    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        return self.recipes.get(recipe_id)

    def get_all_recipes(self) -> list[CraftingRecipe]:
        return list(self.recipes.values())

    def get_recipes_by_category(self, category: str) -> list[CraftingRecipe]:
        return [r for r in self.recipes.values() if r.category == category]

    def get_available_recipes(self, level: int, reputation: int) -> list[CraftingRecipe]:
        available = []
        for recipe in self.recipes.values():
            can_craft, _ = recipe.can_craft([], level, reputation)
            if can_craft or (recipe.required_level <= level and recipe.required_reputation <= reputation):
                available.append(recipe)
        return available

    def craft_item(self, recipe_id: str, inventory: list, level: int, reputation: int) -> tuple[bool, str, Optional[CraftedItem]]:
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return False, "Rezept nicht gefunden.", None

        can_craft, missing = recipe.can_craft(inventory, level, reputation)
        if not can_craft:
            return False, f"Fehlende Zutaten: {', '.join(missing)}", None

        for ingredient in recipe.ingredients:
            for _ in range(ingredient.quantity):
                for i, item in enumerate(inventory):
                    if getattr(item, 'name', str(item)) == ingredient.name:
                        inventory.pop(i)
                        break

        crafted = CraftedItem(
            item_id=recipe.result_item.lower().replace(" ", "_"),
            name=recipe.result_item,
            item_type=recipe.category,
            stats=self._generate_item_stats(recipe),
            description=recipe.description,
        )
        self.crafted_items_cache[crafted.item_id] = crafted

        return True, f"{recipe.result_quantity}x {recipe.result_item} hergestellt!", crafted

    def _generate_item_stats(self, recipe: CraftingRecipe) -> dict:
        stats = {}
        if recipe.category == "Weapons":
            stats = {"damage_bonus": 5 + (recipe.required_level * 2)}
        elif recipe.category == "Explosives":
            stats = {"damage": 20 + (recipe.required_level * 5)}
        elif recipe.category == "Medical":
            stats = {"healing": 25 + (recipe.required_level * 10)}
        elif recipe.category == "Armor":
            stats = {"defense": 15 + (recipe.required_level * 5)}
        return stats

    def get_ingredient_requirements(self, recipe_id: str) -> list[CraftingIngredient]:
        recipe = self.recipes.get(recipe_id)
        return recipe.ingredients if recipe else []

    def get_categories(self) -> list[str]:
        categories = set()
        for recipe in self.recipes.values():
            categories.add(recipe.category)
        return sorted(list(categories))

    def to_dict(self) -> dict:
        return {
            "recipes": {rid: recipe.ingredients for rid, recipe in self.recipes.items()},
            "crafted_items": {cid: item.__dict__ for cid, item in self.crafted_items_cache.items()},
            "crafting_station_level": self.crafting_station_level,
        }

    def load_from_dict(self, data: dict) -> None:
        if "crafting_station_level" in data:
            self.crafting_station_level = data["crafting_station_level"]


class CraftingStation:
    def __init__(self, location: str = "mobile"):
        self.location = location
        self.level = 1
        self.unlocked_recipes: list[str] = []
        self.bonus_multiplier = 1.0

    def upgrade(self, new_level: int) -> bool:
        if new_level > self.level:
            self.level = new_level
            self.bonus_multiplier = 1.0 + (new_level * 0.1)
            return True
        return False

    def unlock_recipe(self, recipe_id: str) -> bool:
        if recipe_id not in self.unlocked_recipes:
            self.unlocked_recipes.append(recipe_id)
            return True
        return False

    def is_recipe_unlocked(self, recipe_id: str) -> bool:
        return recipe_id in self.unlocked_recipes