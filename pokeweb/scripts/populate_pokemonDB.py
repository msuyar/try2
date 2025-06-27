#!/usr/bin/env python
import os
import sys
import csv

# 1) Compute the project root (where manage.py lives)
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))          # …/scripts
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)                         # …/

# 2) Make sure Python can import your Django project package
sys.path.append(PROJECT_ROOT)

# 3) Point at the correct settings module
#    Your settings.py lives at PROJECT_ROOT/pokeweb/settings.py,
#    so the DJANGO_SETTINGS_MODULE should be 'pokeweb.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokeweb.settings')

# 4) Bootstrap Django
import django
django.setup()

# 5) Import your model
from pokedata.models import Pokemon

def run():
    csv_path = os.path.join(SCRIPT_DIR, 'Pokemon_Data.csv')
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        return

    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name'].strip()
            if Pokemon.objects.filter(pokemon_name=name).exists():
                continue

            Pokemon.objects.create(
                pokemon_name   = name,
                pokemon_type1  = row['Type 1'],
                pokemon_type2  = row.get('Type 2') or None,
                pokemon_HP     = int(row['HP']),
                attack         = int(row['Attack']),
                defense        = int(row['Defense']),
                special_attack = int(row['Sp. Atk']),
                special_defense= int(row['Sp. Def']),
                speed          = int(row['Speed']),
                generation     = int(row['Generation']),
                legendary      = row['Legendary'].strip().lower() in ('1','true','yes')
            )
            count += 1

    print(f"{count} Pokémon imported.")

if __name__ == '__main__':
    run()
