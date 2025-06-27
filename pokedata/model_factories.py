import factory
from random import randint, choice
from pokedata.models import Pokemon

class PokemonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pokemon

    # Give each one a unique name
    pokemon_name = factory.Sequence(lambda n: f"Pokemon{n}")

    # If your app only supports gens I–VI, adjust this list
    generation = factory.Iterator([1, 2, 3, 4, 5, 6])

    # Legendary flag: roughly 50/50
    legendary = factory.LazyFunction(lambda: choice([True, False]))

    # Pull type choices straight from your model’s TYPE_CHOICES
    pokemon_type1 = factory.LazyFunction(
        lambda: choice([t[0] for t in Pokemon._meta.get_field("pokemon_type1").choices])
    )
    # Allow a second type or None
    pokemon_type2 = factory.LazyFunction(
        lambda: choice([None] + [t[0] for t in Pokemon._meta.get_field("pokemon_type2").choices])
    )

    # Stats between 1 and 255
    pokemon_HP      = factory.LazyFunction(lambda: randint(1, 255))
    attack          = factory.LazyFunction(lambda: randint(1, 255))
    defense         = factory.LazyFunction(lambda: randint(1, 255))
    special_attack  = factory.LazyFunction(lambda: randint(1, 255))
    special_defense = factory.LazyFunction(lambda: randint(1, 255))
    speed           = factory.LazyFunction(lambda: randint(1, 255))

    # Sum them up for total_stats
    total_stats = factory.LazyAttribute(
        lambda obj: (
            obj.pokemon_HP
            + obj.attack
            + obj.defense
            + obj.special_attack
            + obj.special_defense
            + obj.speed
        )
    )