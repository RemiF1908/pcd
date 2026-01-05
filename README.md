# 🏰 Dungeon Manager

> "Vous n'êtes pas le héros… Vous êtes le seigneur du donjon qui construit les pièges et organise la défense."

## 📖 Description

**Dungeon Manager** est un jeu de gestion/simulation où vous incarnez le maître du donjon. Votre objectif est de concevoir un labyrinthe rempli de pièges et de monstres pour empêcher les héros d'atteindre votre trésor.

## 🎮 Fonctionnalités

### Implémentées ✅

- **Système d'entités** :
  - Classe abstraite `Entity` (ABC) comme contrat pour toutes les entités
  - Entités concrètes : `Floor` (sol), `Wall` (mur), `Trap` (piège)
  - Factory Pattern pour créer facilement les entités
- **Case du donjon (`Cell`)** :
  - Gestion des coordonnées et entité associée
  - Méthodes : `is_walkable()`, `is_dangerous()`, `get_damage()`
- **Tests unitaires** : Suite complète avec pytest

### En développement 🚧

- **Éditeur de donjon** : Créez votre donjon sur une grille 2D
- **Placement d'éléments** : Murs, pièges, monstres
- **Gestion de budget** : Chaque élément a un coût
- **Simulation de vagues** : Lancez des héros contre votre donjon
- **Stratégies d'IA** : Les héros utilisent différentes stratégies de déplacement
  - Plus court chemin (BFS/Dijkstra)
  - Chemin le moins dangereux
- **Système de score** : Évaluez vos performances
- **Persistance** : Sauvegardez et chargez vos donjons

## 🖥️ Interfaces

Le jeu propose deux interfaces :
- **Interface Terminal (TUI)** : Interface textuelle ergonomique
- **Interface Web** : Application web avec serveur local

## 🚀 Installation

### Prérequis

- Python 3.10+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 🎯 Lancement

### Interface Terminal

```bash
python -m src.main --tui
```

### Interface Web

```bash
python -m src.main --web
```

Puis ouvrez votre navigateur à l'adresse : `http://localhost:5000`

## 🏗️ Architecture

Le projet suit une architecture MVC (Modèle-Vue-Contrôleur) :

```text
src/
├── model/              # Modèle de données
│   ├── entity.py       # Classe abstraite Entity (ABC)
│   ├── floor.py        # Entité Floor (sol)
│   ├── wall.py         # Entité Wall (mur)
│   ├── trap.py         # Entité Trap (piège)
│   ├── entity_factory.py  # Factory Pattern pour créer les entités
│   ├── cell.py         # Case du donjon
│   └── ...             # (Donjon, Héros, etc.)
├── view/
│   ├── terminal/       # Interface TUI
│   └── web/            # Interface Web (Flask)
├── controller/         # Logique de contrôle
├── strategies/         # Stratégies d'IA des héros
└── main.py             # Point d'entrée

tests/
├── test_entities.py    # Tests des entités
├── test_factory.py     # Tests du Factory Pattern
└── ...
```

## 🧪 Tests

```bash
pytest tests/
```

## 📚 Documentation

- [ROADMAP.md](docs/ROADMAP.md) - Planning et progression du projet
- [IA_USAGE.md](docs/IA_USAGE.md) - Journal d'utilisation de l'IA
- [docs/](docs/) - Documentation technique et UML

## 👥 Équipe

Groupe 24 - TELECOM Nancy - CodingWeek 2026

## 📝 Licence

Projet académique - TELECOM Nancy
