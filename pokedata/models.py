from enum import Enum
from django.db import models

class PokemonType(models.TextChoices):
    NORMAL   = "Normal",   "Normal"
    FIRE     = "Fire",     "Fire"
    WATER    = "Water",    "Water"
    ELECTRIC = "Electric", "Electric"
    GRASS    = "Grass",    "Grass"
    ICE      = "Ice",      "Ice"
    FIGHTING = "Fighting", "Fighting"
    POISON   = "Poison",   "Poison"
    GROUND   = "Ground",   "Ground"
    FLYING   = "Flying",   "Flying"
    PSYCHIC  = "Psychic",  "Psychic"
    BUG      = "Bug",      "Bug"
    ROCK     = "Rock",     "Rock"
    GHOST    = "Ghost",    "Ghost"
    DRAGON   = "Dragon",   "Dragon"
    DARK     = "Dark",     "Dark"
    STEEL    = "Steel",    "Steel"
    FAIRY    = "Fairy",    "Fairy"


class Generation(models.IntegerChoices):
    GEN1 = 1, "Generation I"
    GEN2 = 2, "Generation II"
    GEN3 = 3, "Generation III"
    GEN4 = 4, "Generation IV"
    GEN5 = 5, "Generation V"
    GEN6 = 6, "Generation VI"

class Pokemon(models.Model):
    #Name,Type 1,Type 2,Total,HP,Attack,Defense,Sp. Atk,Sp. Def,Speed,Generation,Legendary
    pokemon_name = models.CharField(max_length=256, null=False, blank=False)
    pokemon_type1 = models.CharField(
        max_length=8,
        choices=PokemonType.choices,   
    )
    pokemon_type2 = models.CharField(
        max_length=8,
        choices=PokemonType.choices,
        blank=True,
        null=True,
    )
    total_stats = models.PositiveIntegerField()
    pokemon_HP = models.PositiveIntegerField()
    attack = models.PositiveIntegerField()
    defense = models.PositiveIntegerField()
    special_attack = models.PositiveIntegerField()
    special_defense = models.PositiveIntegerField()
    speed = models.PositiveIntegerField()
    generation = models.PositiveSmallIntegerField(
        choices=Generation.choices,
        default=Generation.GEN1,
        help_text="Which main-series generation this Pokémon debuted in"
    )
    legendary = models.BooleanField(
        default=False,
        help_text="True if this Pokémon is legendary"
    )

    def __str__(self):
        # Makes Django admin, the shell, and any dropdowns show the name
        return self.pokemon_name

    def save(self, *args, **kwargs):
        # Auto-compute total_stats before saving,
        # so you never have to fill it in by hand
        self.total_stats = (
            self.pokemon_HP
            + self.attack
            + self.defense
            + self.special_attack
            + self.special_defense
            + self.speed
        )
        super().save(*args, **kwargs)

    class Meta:
        # Optional: default ordering, e.g. by Pokédex order (generation → name)
        ordering = ['generation', 'pokemon_name']
        verbose_name = 'Pokémon'
        verbose_name_plural = 'Pokémon'

    def delete(self, using=None, keep_parents=False):
        # custom cleanup, logging, or preventing deletion
        # e.g. log to a file, revoke related resources, etc.
        super().delete(using=using, keep_parents=keep_parents)

