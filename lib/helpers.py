# helpers.py

import random
from sqlalchemy.orm import Session, joinedload
from lib.models import Player, PlayerMonster, Trade, Battle, MonsterType, MonsterRarity, MonsterSpecies, Achievement

# ---- Stat Calculation ----
def calculate_current_stats(base_hp, base_attack, base_defense, level):
    """Returns scaled stats for a monster based on its level."""
    return {
        'hp': base_hp + level * 2,
        'attack': base_attack + level * 2,
        'defense': base_defense + level * 2,
    }

# ---- Type Effectiveness (Example logic) ----
def get_type_effectiveness_multiplier(attacker_type, defender_type):
    """Returns damage multiplier based on types (example logic)."""
    type_chart = {
        'Fire': {'Grass': 2.0, 'Water': 0.5},
        'Water': {'Fire': 2.0, 'Electric': 0.5},
        'Grass': {'Water': 2.0, 'Fire': 0.5},
    }
    return type_chart.get(attacker_type, {}).get(defender_type, 1.0)


# ---- Trading System ----
def propose_trade(session, from_player_id, to_player_id, offered_monster_id, requested_monster_id):
    """Proposes a trade between two players."""
    trade = Trade(
        from_player_id=from_player_id,
        to_player_id=to_player_id,
        offered_monster_id=offered_monster_id,
        requested_monster_id=requested_monster_id,
        status="pending"
    )
    session.add(trade)
    session.commit()
    return trade


def accept_trade(session, trade_id):
    """Completes a pending trade."""
    trade = session.query(Trade).get(trade_id)
    if not trade or trade.status != "pending":
        return False

    offered = trade.offered_monster
    requested = trade.requested_monster
    offered.player_id, requested.player_id = requested.player_id, offered.player_id

    trade.status = "completed"
    session.commit()
    return True


# ---- Battle System ----
def create_ai_opponent(session, difficulty="easy"):
    """Generates an AI opponent with monsters based on difficulty."""
    level_limits = {"easy": 5, "medium": 10, "hard": 15}
    max_level = level_limits.get(difficulty, 5)

    ai_monsters = (
        session.query(PlayerMonster)
        .filter(PlayerMonster.level <= max_level)
        .order_by(func.random())
        .limit(3)
        .all()
    )
    return ai_monsters


# ---- Achievement System ----
def check_achievements(session, player_id):
    """Checks if player unlocked any achievements."""
    player = session.query(Player).options(joinedload(Player.monsters)).get(player_id)

    if len(player.monsters) >= 5:
        unlock_achievement(session, player_id, "Collector")
    
    if any(pm.level >= 10 for pm in player.monsters):
        unlock_achievement(session, player_id, "Trainer")

 


def unlock_achievement(session, player_id, achievement_name):
    """Grants an achievement to a player."""
    player = session.query(Player).get(player_id)
    achievement = session.query(Achievement).filter_by(name=achievement_name).first()

    if achievement and achievement not in player.achievements:
        player.achievements.append(achievement)
        session.commit()
