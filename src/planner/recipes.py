"""Recipe data model and loader."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Recipe:
    item: str
    machine: str
    time: float
    output: float
    inputs: dict[str, float]

    @property
    def rate_per_machine(self) -> float:
        """Items per minute from one machine running at 100%."""
        return self.output * 60 / self.time


@dataclass(frozen=True)
class RecipeBook:
    recipes: dict[str, Recipe]
    raw_resources: set[str]
    machines: set[str]


def validate(book: RecipeBook) -> None:
    """Raise ValueError if the recipe data is inconsistent."""
    for item, recipe in book.recipes.items():
        if recipe.machine not in book.machines:
            raise ValueError(f"Recipe '{item}' uses unknown machine '{recipe.machine}'")
        if recipe.time <= 0:
            raise ValueError(f"Recipe '{item}' must have a positive time, got {recipe.time}")
        if recipe.output <= 0:
            raise ValueError(f"Recipe '{item}' must have a positive output, got {recipe.output}")
        for name in recipe.inputs:
            if name not in book.recipes and name not in book.raw_resources:
                raise ValueError(f"Recipe '{item}' uses unknown input '{name}'")


def load_recipes(path: str | Path) -> RecipeBook:
    with open(path) as f:
        data = json.load(f)

    recipes = {
        item: Recipe(
            item=item,
            machine=r["machine"],
            time=r["time"],
            output=r["output"],
            inputs=r["inputs"],
        )
        for item, r in data["recipes"].items()
    }

    book = RecipeBook(
        recipes=recipes,
        raw_resources=set(data["raw_resources"]),
        machines=set(data["machines"]),
    )
    validate(book)
    return book