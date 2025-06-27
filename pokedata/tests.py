import io
import json
import os

from django.urls import reverse
from django.core.management import call_command
from django.test import TestCase
from django import forms

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Pokemon
from .serializers import PokemonSerializer
from .forms import PokemonForm
from .model_factories import PokemonFactory

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Pokemon
from .model_factories import PokemonFactory
import scripts.populate_pokemonDB as pop_mod

class PokemonDetailTest(APITestCase):
    def setUp(self):
        # create some Pokémon to test against
        self.p1 = PokemonFactory.create(pokemon_name="Mono1")
        self.p2 = PokemonFactory.create(pokemon_name="Mono2")

        # the URL names you registered
        self.delete_url = reverse('api_pokemon-detail-api', kwargs={'pk': self.p1.pk})
        self.good_url   = reverse('api_pokemon-detail-api', kwargs={'pk': self.p2.pk})
        # non‐existent PK
        self.bad_url    = '/api/pokemon/9999/'

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_pokemonDetailReturnsSuccess(self):
        response = self.client.get(self.good_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # assert at least your key field is returned correctly
        self.assertIn('pokemon_name', data)
        self.assertEqual(data['pokemon_name'], self.p2.pokemon_name)

    def test_pokemonDetailReturnFailOnBadPk(self):
        response = self.client.get(self.bad_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pokemonDetailDeleteIsSuccessful(self):
        response = self.client.delete(self.delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # and now it’s really gone
        self.assertEqual(self.client.get(self.delete_url, format='json').status_code,
                         status.HTTP_404_NOT_FOUND)
        
class PokemonListTest(APITestCase):
    def setUp(self):
        # create three Pokémon to list
        self.p1 = PokemonFactory.create(pokemon_name="One")
        self.p2 = PokemonFactory.create(pokemon_name="Two")
        self.p3 = PokemonFactory.create(pokemon_name="Three")
        # your list endpoint
        self.url = reverse('api_pokemon-list-api')

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_pokemonListReturnsSuccess(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pokemonListReturnsAll(self):
        response = self.client.get(self.url, format='json')
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        # ensure each created Pokémon is present
        names = {p['pokemon_name'] for p in data}
        self.assertTrue({"One", "Two", "Three"}.issubset(names))

class PokemonCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('api_create-pokemon')
        # A fully valid payload, including total_stats
        self.valid_payload = {
            "pokemon_name":   "CreateMon",
            "pokemon_HP":     15,
            "attack":         10,
            "defense":        8,
            "special_attack": 12,
            "special_defense":9,
            "speed":          7,
            "generation":     3,
            "pokemon_type1":  "Electric",
            "pokemon_type2":  "",         
            "legendary":      False,
            "total_stats":    15+10+8+12+9+7
        }

    def tearDown(self):
        Pokemon.objects.all().delete()

    def test_create_pokemon_success(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        # it should return at least an ID and echo the name
        self.assertIn('id', data)
        self.assertEqual(data['pokemon_name'], self.valid_payload['pokemon_name'])
        # DB should have the new object
        self.assertTrue(Pokemon.objects.filter(pk=data['id']).exists())

    def test_create_pokemon_invalid_hp(self):
        bad = self.valid_payload.copy()
        bad['pokemon_HP'] = -5
        bad['total_stats'] = sum([
            bad['pokemon_HP'], bad['attack'], bad['defense'],
            bad['special_attack'], bad['special_defense'], bad['speed']
        ])
        response = self.client.post(self.url, bad, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.json()
        self.assertIn('pokemon_HP', errors)       
        
class PokemonByGenerationTest(APITestCase):
    def setUp(self):
        # Create Pokémon in two different generations
        self.gen1_p1 = PokemonFactory.create(generation=1, pokemon_name="G1One")
        self.gen1_p2 = PokemonFactory.create(generation=1, pokemon_name="G1Two")
        self.gen2_p1 = PokemonFactory.create(generation=2, pokemon_name="G2One")

        # URL builder for the gen‐filter endpoint
        self.url = lambda gen: reverse(
            'api_pokemon_by_generation', kwargs={'gen': gen}
        )

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_by_generation_returns_only_requested(self):
        response = self.client.get(self.url(1), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should only return the two gen-1 Pokémon
        self.assertEqual(len(data), 2)
        names = {p['pokemon_name'] for p in data}
        self.assertSetEqual(names, {"G1One", "G1Two"})

    def test_by_generation_empty(self):
        # No Pokémon in generation 99
        response = self.client.get(self.url(99), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

class PokemonLegendaryTest(APITestCase):
    def setUp(self):
        # Create some Pokémon, mixing legendary flags
        self.non_leg = PokemonFactory.create(pokemon_name="RegularOne", legendary=False)
        self.leg1    = PokemonFactory.create(pokemon_name="LegendOne",   legendary=True)
        self.leg2    = PokemonFactory.create(pokemon_name="LegendTwo",   legendary=True)
        # URL for the legendary-only endpoint
        self.url = reverse('api_pokemon_legendary')

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_legendary_returns_only_legendary(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should only include the two legendary Pokémon
        names = {p['pokemon_name'] for p in data}
        self.assertSetEqual(names, {"LegendOne", "LegendTwo"})
        # Every returned record must have legendary=True
        self.assertTrue(all(p['legendary'] for p in data))

    def test_legendary_empty_if_none(self):
        # Remove all and create only non-legendary ones
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)
        PokemonFactory.create_batch(3, legendary=False)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

class PokemonSingleTypeTest(APITestCase):
    def setUp(self):
        # Create Pokémon with various primary and secondary types
        self.fire_only    = PokemonFactory.create(
            pokemon_type1='Fire', pokemon_type2=None, pokemon_name='OnlyFire'
        )
        self.fire_water   = PokemonFactory.create(
            pokemon_type1='Fire', pokemon_type2='Water', pokemon_name='FireWater'
        )
        self.water_fire   = PokemonFactory.create(
            pokemon_type1='Water', pokemon_type2='Fire', pokemon_name='WaterFire'
        )
        self.grass_poison = PokemonFactory.create(
            pokemon_type1='Grass', pokemon_type2='Poison', pokemon_name='GrassPoison'
        )

        # Endpoint for single-type filter
        self.url = '/api/pokemon/type/Fire/'

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_filter_by_single_type_returns_all_with_type(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        names = {p['pokemon_name'] for p in data}
        # Should include any Pokémon where Fire is primary or secondary
        self.assertSetEqual(names, {'OnlyFire', 'FireWater', 'WaterFire'})

    def test_filter_by_single_type_empty(self):
        # No Pokémon of type Dragon
        response = self.client.get('/api/pokemon/type/Dragon/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

class PokemonTwoTypeTest(APITestCase):
    def setUp(self):
        # Create Pokémon with various type combinations
        self.fire_only    = PokemonFactory.create(
            pokemon_type1='Fire', pokemon_type2=None, pokemon_name='OnlyFire'
        )
        self.fire_water   = PokemonFactory.create(
            pokemon_type1='Fire', pokemon_type2='Water', pokemon_name='FireWater'
        )
        self.water_fire   = PokemonFactory.create(
            pokemon_type1='Water', pokemon_type2='Fire', pokemon_name='WaterFire'
        )
        self.grass_poison = PokemonFactory.create(
            pokemon_type1='Grass', pokemon_type2='Poison', pokemon_name='GrassPoison'
        )

        # endpoint for two‐type filter
        self.url = '/api/pokemon/type/Fire/Water/'

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_filter_by_two_types_returns_both_orders(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        names = {p['pokemon_name'] for p in data}
        # Both Fire/Water and Water/Fire should be returned:
        self.assertSetEqual(names, {'FireWater', 'WaterFire'})
        # Pure Fire and Grass/Poison should not appear
        self.assertNotIn('OnlyFire', names)
        self.assertNotIn('GrassPoison', names)

    def test_filter_by_two_types_empty_when_no_match(self):
        # No Pokémon with Ice/Dragon
        response = self.client.get('/api/pokemon/type/Ice/Dragon/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

class PokemonHTMLUpdateTest(TestCase):
    def setUp(self):
        self.p = PokemonFactory.create(pokemon_name="OldName")
        self.url = reverse('pokemon_update', args=[self.p.pk])

    def tearDown(self):
        Pokemon.objects.all().delete()
        PokemonFactory.reset_sequence(0)

    def test_update_view_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<form')  # your template’s form tag

    def test_update_view_post_changes_object(self):
        data = {
            'pokemon_name':   'NewName',
            'pokemon_HP':     self.p.pokemon_HP,
            'attack':         self.p.attack,
            'defense':        self.p.defense,
            'special_attack': self.p.special_attack,
            'special_defense':self.p.special_defense,
            'speed':          self.p.speed,
            'generation':     self.p.generation,
            'pokemon_type1':  self.p.pokemon_type1,
            'pokemon_type2':  self.p.pokemon_type2 or '',
            'legendary':      self.p.legendary,
            'total_stats':    self.p.total_stats,
        }
        resp = self.client.post(self.url, data)
        # Typically a redirect on success:
        self.assertEqual(resp.status_code, 302)
        self.p.refresh_from_db()
        self.assertEqual(self.p.pokemon_name, 'NewName')


class BulkLoadTest(TestCase):
    def setUp(self):
        # Path to the CSV your script reads by default
        self.csv_path = os.path.join(pop_mod.SCRIPT_DIR, 'Pokemon_Data.csv')

        # Back up any real data there
        self.backup = None
        if os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                self.backup = f.read()

        # Write our tiny 2-row CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write(
                "Name,Type 1,Type 2,Total,HP,Attack,Defense,Sp. Atk,Sp. Def,Speed,Generation,Legendary\n"
                "A,Normal,,6,1,1,1,1,1,1,1,False\n"
                "B,Water,,12,2,2,2,2,2,2,2,True\n"
            )

    def tearDown(self):
        # Restore original CSV (or delete if none existed)
        if self.backup is not None:
            with open(self.csv_path, 'w', encoding='utf-8') as f:
                f.write(self.backup)
        else:
            os.remove(self.csv_path)

        # Clean out the table
        Pokemon.objects.all().delete()

    def test_load_once(self):
        # Call your script’s run(), which will import exactly those two rows
        pop_mod.run()
        self.assertEqual(Pokemon.objects.count(), 2)

    def test_idempotent(self):
        # Run twice—duplicates should be skipped
        pop_mod.run()
        pop_mod.run()
        self.assertEqual(Pokemon.objects.count(), 2)




class PokemonForm(forms.ModelForm):
    class Meta:
        model = Pokemon
        fields = [
            'pokemon_name',
            'pokemon_type1', 'pokemon_type2',
            'total_stats',
            'pokemon_HP', 'attack', 'defense',
            'special_attack', 'special_defense', 'speed',
            'generation', 'legendary',
        ]

    def clean_total_stats(self):
        total = self.cleaned_data.get('total_stats')
        # Gather the six individual stats
        stats = [
            self.cleaned_data.get('pokemon_HP'),
            self.cleaned_data.get('attack'),
            self.cleaned_data.get('defense'),
            self.cleaned_data.get('special_attack'),
            self.cleaned_data.get('special_defense'),
            self.cleaned_data.get('speed'),
        ]
        # If any are missing/invalid, skip this check (other validators will catch those)
        if any(s is None for s in stats):
            return total

        expected = sum(stats)
        if total != expected:
            raise forms.ValidationError(
                f"Total stats must be the sum of the six stats ({expected})."
            )
        return total