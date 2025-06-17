import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from lib.models import (
    MonsterSpecies, Player, PlayerMonster, Battle,
    Trade, Achievement, MonsterType, MonsterRarity
)
from sqlalchemy.exc import IntegrityError
from lib.debug import init_db, Session


# -------------------- Seed Data --------------------
seed_monster_species_data = [
    # Fire Type
    {"name": "Flamewyrm", "type": MonsterType.FIRE, "base_hp": 45, "base_attack": 55, "base_defense": 40, "base_speed": 60, "rarity": MonsterRarity.COMMON, "abilities": "Blaze, Intimidate"},
    {"name": "Pyrogon", "type": MonsterType.FIRE, "base_hp": 60, "base_attack": 70, "base_defense": 50, "base_speed": 45, "rarity": MonsterRarity.UNCOMMON, "abilities": "Fiery Aura, Heatwave"},
    {"name": "Cinderling", "type": MonsterType.FIRE, "base_hp": 30, "base_attack": 40, "base_defense": 30, "base_speed": 75, "rarity": MonsterRarity.COMMON, "abilities": "Flash Fire"},
    {"name": "Volcanite", "type": MonsterType.FIRE, "base_hp": 70, "base_attack": 85, "base_defense": 65, "base_speed": 30, "rarity": MonsterRarity.RARE, "abilities": "Magma Armor, Eruption"},

    # Water Type
    {"name": "Aquafin", "type": MonsterType.WATER, "base_hp": 50, "base_attack": 40, "base_defense": 55, "base_speed": 50, "rarity": MonsterRarity.COMMON, "abilities": "Torrent, Hydration"},
    {"name": "Hydrobeast", "type": MonsterType.WATER, "base_hp": 65, "base_attack": 50, "base_defense": 70, "base_speed": 40, "rarity": MonsterRarity.UNCOMMON, "abilities": "Drizzle, Swift Swim"},
    {"name": "Bubblie", "type": MonsterType.WATER, "base_hp": 35, "base_attack": 30, "base_defense": 45, "base_speed": 65, "rarity": MonsterRarity.COMMON, "abilities": "Water Absorb"},
    {"name": "Neptune", "type": MonsterType.WATER, "base_hp": 75, "base_attack": 60, "base_defense": 80, "base_speed": 35, "rarity": MonsterRarity.RARE, "abilities": "Oceanic Blessing, Tidal Wave"},

    # Grass Type
    {"name": "Vinewhip", "type": MonsterType.GRASS, "base_hp": 55, "base_attack": 50, "base_defense": 45, "base_speed": 40, "rarity": MonsterRarity.COMMON, "abilities": "Overgrow, Leaf Guard"},
    {"name": "Floradrake", "type": MonsterType.GRASS, "base_hp": 70, "base_attack": 60, "base_defense": 50, "base_speed": 30, "rarity": MonsterRarity.UNCOMMON, "abilities": "Chlorophyll, Photosynthesis"},
    {"name": "Sproutling", "type": MonsterType.GRASS, "base_hp": 40, "base_attack": 35, "base_defense": 30, "base_speed": 50, "rarity": MonsterRarity.COMMON, "abilities": "Sap Sipper"},
    {"name": "Gaiasaur", "type": MonsterType.GRASS, "base_hp": 80, "base_attack": 70, "base_defense": 60, "base_speed": 25, "rarity": MonsterRarity.RARE, "abilities": "Thick Fat, Giga Drain"},

    # Electric Type
    {"name": "Sparkbolt", "type": MonsterType.ELECTRIC, "base_hp": 40, "base_attack": 60, "base_defense": 35, "base_speed": 70, "rarity": MonsterRarity.COMMON, "abilities": "Static, Lightning Rod"},
    {"name": "Voltra", "type": MonsterType.ELECTRIC, "base_hp": 50, "base_attack": 75, "base_defense": 40, "base_speed": 60, "rarity": MonsterRarity.UNCOMMON, "abilities": "Motor Drive, Electrify"},
    {"name": "Ampereon", "type": MonsterType.ELECTRIC, "base_hp": 65, "base_attack": 80, "base_defense": 50, "base_speed": 75, "rarity": MonsterRarity.RARE, "abilities": "Surge, Thunderbolt"},

    # Earth Type
    {"name": "Rockgrinder", "type": MonsterType.EARTH, "base_hp": 60, "base_attack": 55, "base_defense": 70, "base_speed": 20, "rarity": MonsterRarity.COMMON, "abilities": "Sturdy, Sand Stream"},
    {"name": "Terragon", "type": MonsterType.EARTH, "base_hp": 75, "base_attack": 65, "base_defense": 85, "base_speed": 15, "rarity": MonsterRarity.UNCOMMON, "abilities": "Solid Rock, Quake"},

    # Air Type
    {"name": "Skywing", "type": MonsterType.AIR, "base_hp": 40, "base_attack": 45, "base_defense": 30, "base_speed": 80, "rarity": MonsterRarity.COMMON, "abilities": "Gale Wings, Aerilate"},
    {"name": "Cloudstrider", "type": MonsterType.AIR, "base_hp": 55, "base_attack": 50, "base_defense": 40, "base_speed": 90, "rarity": MonsterRarity.UNCOMMON, "abilities": "Cloud Nine, Tailwind"},
]


# -------------------- Seeding Function --------------------
def seed_database():
    """Create tables and insert initial MonsterSpecies seed data."""
    init_db()  # Make sure tables are created
    session = Session()

    try:
        print("🌱 Seeding MonsterSpecies...")

        for monster_data in seed_monster_species_data:
            # Check for existing monster to avoid duplicates
            monster = session.query(MonsterSpecies).filter_by(name=monster_data["name"]).first()

            if monster:
                print(f"⚠️  Skipped: {monster.name} (already exists)")
            else:
                new_monster = MonsterSpecies(**monster_data)
                session.add(new_monster)
                print(f"✅ Added: {new_monster.name} ({new_monster.type.value})")

        session.commit()
        print("✅ MonsterSpecies seeding complete.")

    except IntegrityError as e:
        session.rollback()
        print("❌ IntegrityError during seeding:", e)
    except Exception as e:
        session.rollback()
        print("❌ Error during seeding:", e)
    finally:
        session.close()


# -------------------- Run Seeding --------------------
if __name__ == "__main__":
    seed_database()
