from django import forms
from .models import Pokemon, PokemonType, Generation

class PokemonForm(forms.ModelForm):
    class Meta:
        model = Pokemon
        fields = [
            'pokemon_name',
            'pokemon_type1',
            'pokemon_type2',
            'pokemon_HP',
            'attack',
            'defense',
            'special_attack',
            'special_defense',
            'speed',
            'generation',
            'legendary',
        ]
        widgets = {
            'pokemon_type1': forms.Select(choices=PokemonType.choices),
            'pokemon_type2': forms.Select(
                choices=[('', '---------')] + list(PokemonType.choices),
            ),
            'generation': forms.Select(choices=Generation.choices),
        }

    def clean(self):
        cleaned = super().clean()
        # Example additional check: ensure total_stats matches the sum
        # (optional since your model save() handles it)
        total = (
            cleaned.get('pokemon_HP', 0)
            + cleaned.get('attack', 0)
            + cleaned.get('defense', 0)
            + cleaned.get('special_attack', 0)
            + cleaned.get('special_defense', 0)
            + cleaned.get('speed', 0)
        )
        # You could compare to cleaned.get('total_stats') here,
        # but since total_stats is auto-calculated, you may skip it.
        return cleaned