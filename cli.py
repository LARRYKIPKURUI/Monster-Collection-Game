import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import argparse
import random
import re
from sqlalchemy.orm import joinedload
from lib.config import Session
from lib.models import Player, MonsterSpecies, PlayerMonster, Battle, Trade, Achievement
from lib.helpers import get_type_effectiveness_multiplier, calculate_current_stats

def start_game(args):
    session = Session()
    username = input("Enter your desired username: ").strip()

    if not re.match("^[A-Za-z0-9_]{3,20}$", username):
        print("Username must be 3-20 characters, letters/numbers/underscores only.")
        session.close()
        return

    existing_player = session.query(Player).filter_by(username=username).first()
    if existing_player:
        print(f"Welcome back, {username}!")
    else:
        new_player = Player(username=username)
        session.add(new_player)
        session.commit()
        print(f"New player '{username}' created successfully!")

    session.close()


def explore(args):
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found.")
        session.close()
        return

    species = session.query(MonsterSpecies).order_by(func.random()).first()
    print(f"\n🌿 A wild {species.name} appeared!")

    stats = calculate_current_stats(species.base_hp, species.base_attack, species.base_defense, 1)
    print(f"HP: {stats['hp']}, ATK: {stats['attack']}, DEF: {stats['defense']}")

    choice = input("Do you want to catch it? (yes/no): ").strip().lower()
    if choice == 'yes':
        nickname = input("Give it a nickname: ").strip()
        if not nickname:
            print("Nickname cannot be empty.")
        else:
            new_monster = PlayerMonster(
                player_id=player.id,
                species_id=species.id,
                level=1,
                nickname=nickname
            )
            session.add(new_monster)
            session.commit()
            print(f"🎉 {nickname} was caught successfully!")
    else:
        print("You let it go.")

    session.close()


def view_collection(args):
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found.")
        session.close()
        return

    player_monsters = session.query(PlayerMonster).options(joinedload(PlayerMonster.species)).filter_by(player_id=player.id).all()
    if not player_monsters:
        print("You have no monsters. Try 'explore' to catch one.")
    else:
        print(f"\n{player.username}'s Monster Collection:")
        for i, pm in enumerate(player_monsters, 1):
            stats = calculate_current_stats(pm.species.base_hp, pm.species.base_attack, pm.species.base_defense, pm.level)
            print(f"{i}. {pm.nickname} ({pm.species.name}, Lv.{pm.level}) - HP: {stats['hp']} ATK: {stats['attack']} DEF: {stats['defense']}")

    session.close()


def level_up(args):
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found.")
        session.close()
        return

    player_monsters = session.query(PlayerMonster).options(joinedload(PlayerMonster.species)).filter_by(player_id=player.id).all()
    if not player_monsters:
        print("You have no monsters to level up.")
        session.close()
        return

    print("\nSelect a monster to level up:")
    for i, pm in enumerate(player_monsters, 1):
        print(f"{i}. {pm.nickname} (Lv.{pm.level})")

    while True:
        try:
            index = int(input("Enter monster number: ")) - 1
            if 0 <= index < len(player_monsters):
                break
            print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")

    monster = player_monsters[index]
    old_level = monster.level
    old_stats = calculate_current_stats(monster.species.base_hp, monster.species.base_attack, monster.species.base_defense, old_level)
    monster.level += 1
    session.commit()

    new_stats = calculate_current_stats(monster.species.base_hp, monster.species.base_attack, monster.species.base_defense, monster.level)
    print(f"\n🎉 {monster.nickname} leveled up from Lv.{old_level} ➜ Lv.{monster.level}!")
    print(f"✨ HP: +{new_stats['hp'] - old_stats['hp']}, ATK: +{new_stats['attack'] - old_stats['attack']}, DEF: +{new_stats['defense'] - old_stats['defense']}")

    session.close()


def handle_status(args):
    session = Session()
    player = get_player_by_username(session, args.username)
    if not player:
        print(f"Player '{args.username}' not found.")
        session.close()
        return

    print(f"\n👤 Player: {player.username} | Lv.{player.level}")
    monsters = session.query(PlayerMonster).filter_by(player_id=player.id).all()
    print(f"🧟 Monsters Owned: {len(monsters)}")
    if monsters:
        highest = max(monsters, key=lambda m: m.level)
        print(f"⚔️ Highest Monster: {highest.nickname} (Lv.{highest.level})")

    session.close()


def get_player_by_username(session, username):
    return session.query(Player).filter_by(username=username).first()


def main():
    parser = argparse.ArgumentParser(description="Monster Collector CLI Game")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser('start', help='Start a new game')
    start_parser.set_defaults(func=start_game)

    explore_parser = subparsers.add_parser('explore', help='Explore and catch monsters')
    explore_parser.add_argument('username', type=str)
    explore_parser.set_defaults(func=explore)

    collection_parser = subparsers.add_parser('collection', help='View your monster collection')
    collection_parser.add_argument('username', type=str)
    collection_parser.set_defaults(func=view_collection)

    level_up_parser = subparsers.add_parser('level-up', help='Level up your monsters')
    level_up_parser.add_argument('username', type=str)
    level_up_parser.set_defaults(func=level_up)

    status_parser = subparsers.add_parser('status', help='View player status')
    status_parser.add_argument('username', type=str)
    status_parser.set_defaults(func=handle_status)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
