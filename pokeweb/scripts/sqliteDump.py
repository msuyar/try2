import sqlite3
import os

# Find paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'db.sqlite3')
output_path = os.path.join(BASE_DIR, 'db_dump.txt')

# Dump DB
con = sqlite3.connect(db_path)
with open(output_path, 'w', encoding='utf-8') as f:
    for line in con.iterdump():
        f.write(f"{line}\n")
con.close()

print(f"✅ Database dumped to: {output_path}")