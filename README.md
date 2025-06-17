# 🐉 Monster Collector CLI Game

Welcome to **Monster Collector** — a command-line RPG-style game where players explore, catch, battle, and trade powerful elemental monsters. Built with Python and SQLAlchemy ORM, this game is an engaging offline experience with real database persistence.

---

##  Features

-  **Explore:** Discover and encounter random monsters from various elemental types.
-  **Catch Monsters:** Attempt to capture monsters with unique base stats and abilities.
- ⚔️ **Battle:** Fight wild monsters or duel against other players’ collections.
-  **Trade System:** Safely trade monsters with other players.
-  *Level Up:** Earn XP and evolve your monster team over time.
-  **Achievements:** Unlock titles based on in-game progress and performance.
- 🧠 **SQLAlchemy ORM:** Full integration with a persistent SQLite database.

---

## 📁 Folder Structure
monster-collector/
│
├── lib/
│ ├── models/ # All SQLAlchemy models: Player, MonsterSpecies, etc.
│ ├── cli/ # Game logic and user interface
│ ├── helpers/ # Utility functions (battle logic, seeding utils, etc.)
│ ├── debug.py # DB init and session manager
│
├── db/
│ ├── migrations/ # Alembic migrations (optional)
│ └── seed.py # Initial seed script for monster species
│
├── main.py # Entry point for the game (CLI launcher)
├── README.md # You're here!
└── requirements.txt # Project dependencies

##  Tech Stack

- **Python 3.8+**
- **SQLAlchemy** (ORM)
- **SQLite** (default, can be swapped)
- **Rich / Colorama** (for terminal styling,)

---

##  Setup Instructions

1. **Clone the repository**
   ```bash
   git clone 'git repository given'
   cd monster-collector

2. **Install dependencies**
   pipenv install
   pipenv shell

3. **seed database**

  python db/seed.py

  **LICENCE**
  The project is licensed under Apache

  **Authors;**

  1. Jared 
  2. Larry