# 🏰 Dungeon Manager

> "Vous n'êtes pas le héros… Vous êtes le seigneur du donjon qui construit les pièges et organise la défense."

## 📖 Description

**Dungeon Manager** est un jeu de gestion/simulation où vous incarnez le maître du donjon. Votre objectif est de concevoir un labyrinthe rempli de pièges et de monstres pour empêcher les héros d'atteindre votre trésor.


## 🚀 Installation

### Prérequis

- Python 3.10+
- pip

Optionnel : Création d'un environnement virtuel python
```bash
python -m venv venv
```
### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 🎯 Lancement

### Interface Terminal (TUI)

```bash
python -m src.main --tui
```

### Interface Web (GUI)

```bash
python -m src.main --web
```

Puis ouvrez votre navigateur à l'adresse : `http://localhost:8000`

## 💻 Usage

### Interface Terminal

Le jeu se contrôle entièrement au clavier avec les commandes suivantes :

- **Flèches directionnelles** : Déplacer le curseur sur la grille
- **T** : Placer un piège 
- **M** : Placer un mur 
- **B** : Placer un mur 
- **U** : Placer un dragon vers le haut
- **H** : Placer un dragon vers le gauche
- **J** : Placer un dragon vers le bas
- **K** : Placer un murdragon vers le droite

- **N** : Passer au niveau suivant
- **S** : Faire avancer les héro d'un pas
- **I** : Importer un donjon
- **E** : Exporter le donjon actuel
- **R** : Réinitialiser le donjon
- **Q** : Quitter le jeu

### Objectif du jeu

1. **Construire** votre donjon en plaçant des murs et des pièges
2. **Lancer** des vagues de héros avec la touche S
3. **Empêcher** les héros d'atteindre la sortie en les tuant avec vos pièges
4. **Progresser** à travers les niveaux en réussissant à tuer tous les héros

### Système de campagne

Le jeu propose une campagne avec plusieurs niveaux :
- Chaque niveau a un budget différent
- Le niveau actuel et l'or disponible sont affichés dans le panneau de statut
- Réussissez tous les niveaux pour gagner la campagne




## 👥 Équipe

- Malo GRUYERE
- Mathis PACCOUD
- Noah ANDRIAMAMPIANINA
- Rémi FERRATO


