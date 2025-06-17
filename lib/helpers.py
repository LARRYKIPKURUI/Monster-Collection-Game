# helpers.py
from sqlalchemy.orm import Session
from lib.models import PlayerMonster, Trade, Battle
from lib.models import MonsterType, MonsterRarity
import random

# ---- Trading System ----
def propose_trade(session, from_player_id, to_player_id, offered_monster_id, requested_monster_id):
    """(See code above)"""
    pass

def accept_trade(session, trade_id):
    """Completes a pending trade."""
    trade = session.query(Trade).get(trade_id)
    if not trade or trade.status != "pending":
        return False
    
    # Swap monsters
    offered = trade.offered_monster
    requested = trade.requested_monster
    offered.player_id, requested.player_id = requested.player_id, offered.player_id
    
    trade.status = "completed"
    session.commit()
    return True

# ---- Battle System ----
def create_ai_opponent(session, difficulty="easy"):
    """Generates an AI opponent with monsters based on difficulty."""
    levels = {"easy": 5, "medium": 10, "hard": 15}
    ai_monsters = (
        session.query(PlayerMonster)
        .filter(PlayerMonster.level <= levels.get(difficulty, 5))
        .limit(3)
        .all()
    )
    return ai_monsters

# ---- Achievement System ----
def check_achievements(session, player_id):
    """Checks if player unlocked any achievements."""
    player = session.query(Player).get(player_id)
    if len(player.monsters) >= 5:
        unlock_achievement(session, player_id, "Collector")
    # Add more checks...

def unlock_achievement(session, player_id, achievement_name):
    """Grants an achievement to a player."""
    achievement = session.query(Achievement).filter_by(name=achievement_name).first()
    if achievement and achievement not in player.achievements:
        player.achievements.append(achievement)
        session.commit()