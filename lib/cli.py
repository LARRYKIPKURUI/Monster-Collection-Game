# lib/cli.py

import argparse
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from .models import Base, Player, MonsterSpecies, PlayerMonster, MonsterType, MonsterRarity, Session, engine
from .seed import seed_database
import random
import math
import os

# Constants for Game Mechanics
BASE_CATCH_RATE_COMMON = 0.60
BASE_CATCH_RATE_UNCOMMON = 0.45
BASE_CATCH_RATE_RARE = 0.30
BASE_CATCH_RATE_EPIC = 0.15
BASE_CATCH_RATE_LEGENDARY = 0.05
PLAYER_LEVEL_BONUS_PER_LEVEL = 0.02 # Each player level adds this much to catch rate

EXP_TO_NEXT_LEVEL_BASE = 100
EXP_TO_NEXT_LEVEL_MULTIPLIER = 1.2
STAT_GROWTH_PER_LEVEL = 0.1 # Percentage increase in base stats per monster level

# Helper Functions (Type Effectiveness, Stat Calculation)
# This dictionary defines type effectiveness: {ATTACKER_TYPE: {DEFENDER_TYPE: MULTIPLIER}}
# A multiplier > 1 means super effective, < 1 means not very effective, 0 means no effect.
TYPE_EFFECTIVENESS = {
    MonsterType.FIRE: {
        MonsterType.GRASS: 2.0, # Fire beats Grass
        MonsterType.WATER: 0.5, # Fire weak to Water
        MonsterType.AIR: 2.0, # Fire beats Air 
        MonsterType.EARTH: 0.5, # Fire weak to Earth 
        MonsterType.ELECTRIC: 1.0,
    },
    MonsterType.WATER: {
        MonsterType.FIRE: 2.0, # Water beats Fire
        MonsterType.ELECTRIC: 0.5, # Water weak to Electric
        MonsterType.EARTH: 2.0, # Water beats Earth 
        MonsterType.GRASS: 0.5, # Water weak to Grass
        MonsterType.AIR: 1.0,
    },
    MonsterType.GRASS: {
        MonsterType.WATER: 2.0, # Grass beats Water
        MonsterType.FIRE: 0.5, # Grass weak to Fire
        MonsterType.EARTH: 2.0, # Grass beats Earth 
        MonsterType.AIR: 0.5, # Grass weak to Air 
        MonsterType.ELECTRIC: 1.0,
    },
    MonsterType.ELECTRIC: {
        MonsterType.WATER: 2.0, # Electric beats Water
        MonsterType.EARTH: 0.5, # Electric weak to Earth 
        MonsterType.AIR: 2.0, # Electric beats Air
        MonsterType.FIRE: 1.0,
        MonsterType.GRASS: 1.0,
    },
    MonsterType.EARTH: {
        MonsterType.ELECTRIC: 2.0, # Earth beats Electric
        MonsterType.WATER: 0.5, # Earth weak to Water
        MonsterType.AIR: 0.5, # Earth weak to Air 
        MonsterType.FIRE: 2.0, # Earth beats Fire
        MonsterType.GRASS: 0.5, # Earth weak to Grass
    },
    MonsterType.AIR: {
        MonsterType.EARTH: 2.0, # Air beats Earth 
        MonsterType.FIRE: 0.5, # Air weak to Fire 
        MonsterType.ELECTRIC: 0.5, # Air weak to Electric
        MonsterType.WATER: 1.0,
        MonsterType.GRASS: 2.0, # Air beats Grass 
    }
}

def calculate_current_stats(base_stat, level):
    """
    Calculates a monster's current stat based on its base stat and level.
    Stats grow linearly for simplicity, with a slight exponential curve or other
    complex formulas possible for more nuanced balancing.
    """
    # Simple linear growth: base_stat + (level-1) * (base_stat * STAT_GROWTH_PER_LEVEL)
    # This ensures stats increase significantly with level
    return round(base_stat + (level - 1) * (base_stat * STAT_GROWTH_PER_LEVEL))

def get_type_effectiveness_multiplier(attacker_type, defender_type):
    """
    Returns the damage multiplier based on type effectiveness.
    """
    return TYPE_EFFECTIVENESS.get(attacker_type, {}).get(defender_type, 1.0)

# Game Functions 

def create_player(session, username):
    """
    Creates a new player in the database.
    """
    player = Player(username=username)
    session.add(player)
    try:
        session.commit()
        print(f"Player '{username}' created successfully!")
        return player
    except Exception as e:
        session.rollback()
        print(f"Error creating player: {e}")
        return None

def get_player_by_username(session, username):
    """
    Retrieves a player by their username.
    """
    return session.query(Player).filter_by(username=username).first()

def calculate_catch_rate(species_rarity, player_level):
    """
    Calculates the probability of catching a monster based on its rarity and player level.
    Higher rarity means lower base chance. Higher player level slightly increases chance.
    """
    base_chance = {
        MonsterRarity.COMMON: BASE_CATCH_RATE_COMMON,
        MonsterRarity.UNCOMMON: BASE_CATCH_RATE_UNCOMMON,
        MonsterRarity.RARE: BASE_CATCH_RATE_RARE,
        MonsterRarity.EPIC: BASE_CATCH_RATE_EPIC,
        MonsterRarity.LEGENDARY: BASE_CATCH_RATE_LEGENDARY,
    }.get(species_rarity, 0.10) # Default to a very low chance if rarity is unknown

    player_level_bonus = player_level * PLAYER_LEVEL_BONUS_PER_LEVEL
    catch_probability = base_chance + player_level_bonus

    # Cap the probability at 1.0 (100%)
    return min(catch_probability, 1.0)

def catch_monster(session, player_id, species_id):
    """
    Attempts to catch a wild monster.
    Returns True if successful, False otherwise.
    """
    player = session.query(Player).get(player_id)
    if not player:
        print("Player not found.")
        return False

    species = session.query(MonsterSpecies).get(species_id)
    if not species:
        print("Monster species not found.")
        return False

    catch_probability = calculate_catch_rate(species.rarity, player.level)
    print(f"Attempting to catch {species.name} (Rarity: {species.rarity.value})...")
    print(f"Your catch probability: {catch_probability:.2%}")

    if random.random() < catch_probability:
        # Calculate initial stats for the new monster based on its base stats and level 1
        initial_hp = calculate_current_stats(species.base_hp, 1)
        initial_attack = calculate_current_stats(species.base_attack, 1)
        initial_defense = calculate_current_stats(species.base_defense, 1)
        initial_speed = calculate_current_stats(species.base_speed, 1)

        new_monster = PlayerMonster(
            player_id=player.id,
            species_id=species.id,
            nickname=species.name, # Default nickname is species name
            level=1,
            current_hp=initial_hp,
            max_hp=initial_hp,
            attack=initial_attack,
            defense=initial_defense,
            speed=initial_speed,
            experience=0
        )
        session.add(new_monster)
        session.commit()
        print(f"Success! {species.name} joined your team!")
        return True
    else:
        print(f"Oh no! {species.name} escaped!")
        return False

def level_up_monster(session, player_monster_id):
    """
    Levels up a player's monster, increasing its stats.
    Returns a dictionary with updated monster info or None if not found.
    """
    monster = session.query(PlayerMonster).get(player_monster_id)
    if not monster:
        print("Monster not found.")
        return None

    species = monster.species # Access the associated MonsterSpecies
    
    # Check if monster has enough experience to level up
    exp_needed = math.ceil(EXP_TO_NEXT_LEVEL_BASE * (EXP_TO_NEXT_LEVEL_MULTIPLIER ** (monster.level - 1)))
    
    if monster.experience < exp_needed:
        print(f"{monster.nickname} (Lv.{monster.level}) needs {exp_needed - monster.experience} more EXP to level up.")
        return {"level": monster.level, "experience": monster.experience}

    monster.level += 1
    monster.experience = 0 # Reset experience for the new level

    # Recalculate stats based on new level and species base stats
    monster.max_hp = calculate_current_stats(species.base_hp, monster.level)
    monster.current_hp = monster.max_hp # Fully heal on level up
    monster.attack = calculate_current_stats(species.base_attack, monster.level)
    monster.defense = calculate_current_stats(species.base_defense, monster.level)
    monster.speed = calculate_current_stats(species.base_speed, monster.level)

    session.commit()
    print(f"{monster.nickname} leveled up to Lv.{monster.level}!")
    print(f"New Stats: HP: {monster.max_hp}, Atk: {monster.attack}, Def: {monster.defense}, Spd: {monster.speed}")
    return {
        "level": monster.level,
        "current_hp": monster.current_hp,
        "max_hp": monster.max_hp,
        "attack": monster.attack,
        "defense": monster.defense,
        "speed": monster.speed,
        "experience": monster.experience
    }

def get_player_collection(session, player_id):
    """
    Retrieves all monsters owned by a player.
    Uses joinedload to eagerly load the associated MonsterSpecies for each PlayerMonster.
    """
    player = session.query(Player).options(joinedload(Player.monsters).joinedload(PlayerMonster.species)).get(player_id)
    if not player:
        print("Player not found.")
        return []
    
    print(f"\n--- {player.username}'s Monster Collection ---")
    if not player.monsters:
        print("You don't have any monsters yet! Go explore to catch some.")
        return []

    for i, pm in enumerate(player.monsters):
        print(f"{i+1}. {pm.nickname} ({pm.species.name}) - Lv.{pm.level} | Type: {pm.species.type.value} | HP: {pm.current_hp}/{pm.max_hp} | Atk: {pm.attack} | Def: {pm.defense} | Spd: {pm.speed}")
    print("--------------")
    return player.monsters

# CLI Commands

def handle_start(args):
    """
    Handles the 'start' command, prompting for username and creating a player.
    """
    session = Session()
    username = input("Enter your desired username: ").strip()
    if not username:
        print("Username cannot be empty.")
        session.close()
        return

    player = get_player_by_username(session, username)
    if player:
        print(f"Welcome back, {username}!")
    else:
        player = create_player(session, username)
        if player:
            print("To get started, let's give you a starter monster!")
            # Automatically give a random common starter monster
            common_starters = session.query(MonsterSpecies).filter_by(rarity=MonsterRarity.COMMON).all()
            if common_starters:
                starter_species = random.choice(common_starters)
                catch_monster(session, player.id, starter_species.id)
            else:
                print("No common monsters available to give as a starter.")
        else:
            session.close()
            return
    
    session.close()
    print("\nType 'python -m lib.cli explore <username>' to find monsters or 'python -m lib.cli collection <username>' to view your monsters.")

def handle_explore(args):
    """
    Handles the 'explore' command, allowing players to encounter and catch monsters.
    """
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found. Please 'start' a new game.")
        session.close()
        return

    print(f"\n{player.username} is exploring the wild...")
    
    # Get a random monster species to encounter
    all_species = session.query(MonsterSpecies).all()
    if not all_species:
        print("No monster species defined in the database. Please run seed_database first.")
        session.close()
        return

    encountered_species = random.choice(all_species)
    print(f"You encounter a wild {encountered_species.name} ({encountered_species.type.value}, Rarity: {encountered_species.rarity.value})!")

    catch_monster(session, player.id, encountered_species.id)
    session.close()

def handle_collection(args):
    """
    Handles the 'collection' command, displaying the player's monster collection.
    """
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found. Please 'start' a new game.")
        session.close()
        return
    
    get_player_collection(session, player.id)
    session.close()

def handle_level_up(args):
    """
    Handles the 'level-up' command for a specific monster.
    """
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found.")
        session.close()
        return

    player_monsters = get_player_collection(session, player.id)
    if not player_monsters:
        session.close()
        return

    try:
        monster_index = int(input("Enter the number of the monster you want to level up: ")) - 1
        if 0 <= monster_index < len(player_monsters):
            selected_monster = player_monsters[monster_index]
            # For demonstration, we'll give it some experience to ensure it can level up
            # In a real game, EXP would come from battles.
            print(f"Giving {selected_monster.nickname} some experience for demonstration...")
            selected_monster.experience += 200 # Arbitrary EXP
            session.commit()
            level_up_monster(session, selected_monster.id)
        else:
            print("Invalid monster number.")
    except ValueError:
        print("Please enter a valid number.")
    
    session.close()

def main():
    parser = argparse.ArgumentParser(description="Monster Collection CLI Game")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start a new game or log in.')
    start_parser.set_defaults(func=handle_start)

    # Explore command
    explore_parser = subparsers.add_parser('explore', help='Explore the wild to find monsters.')
    explore_parser.add_argument('username', type=str, help='Your player username.')
    explore_parser.set_defaults(func=handle_explore)

    # Collection command
    collection_parser = subparsers.add_parser('collection', help='View your monster collection.')
    collection_parser.add_argument('username', type=str, help='Your player username.')
    collection_parser.set_defaults(func=handle_collection)

    # Level-up command (for demonstration)
    level_up_parser = subparsers.add_parser('level-up', help='Level up a monster (for demonstration).')
    level_up_parser.add_argument('username', type=str, help='Your player username.')
    level_up_parser.set_defaults(func=handle_level_up)

    # Database initialization command (optional, can be called once)
    init_db_parser = subparsers.add_parser('init-db', help='Initialize and seed the database.')
    init_db_parser.set_defaults(func=lambda args: seed_database())


    args = parser.parse_args()

    # If the user doesn't call init-db, ensure tables are created when they start the game.
    if args.command != 'init-db': 
        # Check if the database file exists. If not, create and seed it.
        if not os.path.exists('monster_game.db'):
            print("Database 'monster_game.db' not found. Initializing and seeding...")
            seed_database()

    if args.command:
        args.func(args)
    else:
        parser.print_help()
        print("\nWelcome to Monster Collector! To begin, type 'python -m lib.cli start'")

if __name__ == '__main__':
    main()
