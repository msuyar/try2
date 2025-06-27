from rest_framework import serializers
from .models import *

class PokemonSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pokemon
        fields = [
            "id",
            "pokemon_name",
            "pokemon_type1",
            "pokemon_type2",
            "total_stats",
            "pokemon_HP",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
            "generation",
            "legendary",
        ]
        extra_kwargs = {
            'pokemon_HP':      {'min_value': 1},
            'attack':          {'min_value': 1},
            'defense':         {'min_value': 1},
            'special_attack':  {'min_value': 1},
            'special_defense': {'min_value': 1},
            'speed':           {'min_value': 1},
            'total_stats':     {'min_value': 1},
        }

