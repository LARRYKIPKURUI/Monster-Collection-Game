from lib.models import MonsterSpecies, Player, PlayerMonster, Battle, Trade, Achievement, MonsterType, MonsterRarity
from sqlalchemy.exc import IntegrityError
from lib.debug import init_db, Session


# Seed data for Monster Species
# Base stats (HP, Attack, Defense, Speed) are kept relatively low for initial levels
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

def seed_database():
    """
    Creates all tables and populates the MonsterSpecies table with initial data.
    """
    init_db()
 # Ensure all tables are created

    session = Session()
    try:
        print("Seeding Monster Species data...")
        for monster_data in seed_monster_species_data:
            # Check if monster already exists to prevent duplicates
            existing_monster = session.query(MonsterSpecies).filter_by(name=monster_data['name']).first()
            if not existing_monster:
                monster = MonsterSpecies(
                    name=monster_data['name'],
                    type=monster_data['type'],
                    base_hp=monster_data['base_hp'],
                    base_attack=monster_data['base_attack'],
                    base_defense=monster_data['base_defense'],
                    base_speed=monster_data['base_speed'],
                    rarity=monster_data['rarity'],
                    abilities=monster_data['abilities']
                )
                session.add(monster)
                print(f"Added: {monster.name} ({monster.type.value})")
            else:
                print(f"Skipped: {monster_data['name']} (already exists)")
        session.commit()
        print("Monster Species seeding complete.")
    except IntegrityError as e:
        session.rollback()
        print(f"Database seeding failed due to integrity error: {e}")
        print("This might happen if you try to add duplicate unique entries.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred during seeding: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    seed_database()