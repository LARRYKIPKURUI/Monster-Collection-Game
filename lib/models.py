from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Enum as SqlEnum, MetaData
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from enum import Enum

# Custom constraint naming convention (for cleaner migrations)
convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Enum for monster types
class MonsterType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    EARTH = "Earth"
    AIR = "Air"

# Enum for monster rarity
class MonsterRarity(Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"

# MonsterSpecies: acts as a template for PlayerMonsters
class MonsterSpecies(Base):
    __tablename__ = 'monster_species'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(SqlEnum(MonsterType), nullable=False)
    base_hp = Column(Integer, nullable=False)
    base_attack = Column(Integer, nullable=False)
    base_defense = Column(Integer, nullable=False)
    base_speed = Column(Integer, nullable=False)
    rarity = Column(SqlEnum(MonsterRarity), nullable=False)
    abilities = Column(String)

    player_monsters = relationship("PlayerMonster", back_populates="species", cascade="all, delete")

    def __repr__(self):
        return f"<MonsterSpecies(id={self.id}, name='{self.name}', type='{self.type.value}')>"

# PlayerMonster: user-owned monsters
class PlayerMonster(Base):
    __tablename__ = 'player_monsters'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('monster_species.id'), nullable=False)

    nickname = Column(String)
    level = Column(Integer, default=1)
    current_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    experience = Column(Integer, default=0)

    player = relationship("Player", back_populates="monsters")
    species = relationship("MonsterSpecies", back_populates="player_monsters")

    def __repr__(self):
        return (f"<PlayerMonster(id={self.id}, nickname='{self.nickname or self.species.name}', "
                f"level={self.level}, player_id={self.player_id})>")

# Player: main user profile
class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    money = Column(Integer, default=0)

    monsters = relationship("PlayerMonster", back_populates="player", cascade="all, delete-orphan")
    achievements = relationship("Achievement", secondary="player_achievements", back_populates="players")

    battles_as_player1 = relationship("Battle", foreign_keys="[Battle.player1_id]", back_populates="player1", cascade="all, delete")
    battles_as_player2 = relationship("Battle", foreign_keys="[Battle.player2_id]", back_populates="player2", cascade="all, delete")
    trades_as_from_player = relationship("Trade", foreign_keys="[Trade.from_player_id]", back_populates="from_player", cascade="all, delete")
    trades_as_to_player = relationship("Trade", foreign_keys="[Trade.to_player_id]", back_populates="to_player", cascade="all, delete")

    def __repr__(self):
        return f"<Player(id={self.id}, username='{self.username}', level={self.level})>"

# Battle: PvP logs
class Battle(Base):
    __tablename__ = 'battles'

    id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player2_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    winner_id = Column(Integer, ForeignKey('players.id'))

    battle_log = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="battles_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="battles_as_player2")
    winner = relationship("Player", foreign_keys=[winner_id])

    def __repr__(self):
        return f"<Battle(id={self.id}, p1={self.player1_id}, p2={self.player2_id}, winner={self.winner_id})>"

# Trade: monster exchange system
class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    from_player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    to_player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    offered_monster_id = Column(Integer, ForeignKey('player_monsters.id'), nullable=False)
    requested_monster_id = Column(Integer, ForeignKey('player_monsters.id'), nullable=False)

    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    from_player = relationship("Player", foreign_keys=[from_player_id], back_populates="trades_as_from_player")
    to_player = relationship("Player", foreign_keys=[to_player_id], back_populates="trades_as_to_player")
    offered_monster = relationship("PlayerMonster", foreign_keys=[offered_monster_id])
    requested_monster = relationship("PlayerMonster", foreign_keys=[requested_monster_id])

    def __repr__(self):
        return (f"<Trade(id={self.id}, from={self.from_player_id}, to={self.to_player_id}, "
                f"status='{self.status}')>")

# Achievement: unlockable player rewards
class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    players = relationship("Player", secondary="player_achievements", back_populates="achievements")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}')>"

# Join table: Player <-> Achievement
class PlayerAchievement(Base):
    __tablename__ = 'player_achievements'

    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
