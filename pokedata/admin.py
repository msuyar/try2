from django.contrib import admin
from .models import Pokemon

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = (
        'pokemon_name',
        'pokemon_type1',
        'pokemon_type2',
        'total_stats',
        'pokemon_HP',
        'attack',
        'defense',
        'special_attack',
        'special_defense',
        'speed',
        'generation',
        'legendary',
    )
    list_filter = (
        'pokemon_type1',
        'pokemon_type2',
        'generation',
        'legendary',
    )
    search_fields = ('pokemon_name',)