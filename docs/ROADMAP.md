 # Groupe 24 - Javapagnan
 ROADMAP – Projet Dungeon Manager

## 1. Vision du projet
- Objectif général : 
     Concevoir et développer "Dungeon Manager", un jeu de simulation et de stratégie (type Tower Defense inversé). Le but est de créer un jeu où le joueur doit défendre un trésor contre des vagues de héros autonomes controlés par un algorithme d'intelligence artificielle L'objectif est de bâtir un moteur de jeu capable de supporter deux interfaces  (Terminal et Web) en respectant une architecture MVC tout en produisant un code propre et évolutif.
- Public cible / utilisateur : 
    Le jeu s'adresse aux amateurs de jeux de stratégie et de type Tower Defense. Ce sont des joueurs qui préfèrent la planification, la logique et l'optimisation plutôt que l'action rapide. Il vise également un public Rétrogaming, sensible à l'esthétique minimaliste (interface Terminal) et intéressé par la mécanique algorithmique (comprendre comment piéger une IA).
- Résultat attendu en fin de semaine : 
  Un MVP comprenant :

    - Le Moteur de jeu gérant la simulation, le pathfinding et les règles.

    - Deux interfaces connectées au même moteur : une dans un terminale et une interface graphique dans un navigateur.

    - Un code clair, structuré, documenté, évolutif et testé

    - Une vidéo de démonstration
## 2. Conventions
- *# Statuts des tâches*# :
- `TODO` : à faire
- `DOING` : en cours
- `DONE` : terminé
- *#Sprints*# :
- `DAY_1` à `DAY_5` (1 sprint par jour)
- Les détails de chaque sprint sont dans :
`SPRINT_PLANNING_DAY_X.md` et `SPRINT_RETROSPECTIVE_DAY_X.md`.
- Les niveaux de priorité sont relatifs au sprint et non au projet. 
## 3. Backlog global



| ID   | User story / tâche                                                                              | Sprint cible | Priorité | Etat  |
| ---- | ----------------------------------------------------------------------------------------------- | ------------ | -------- | ----- |
| US1  | Structurer le repo GIT                                                                          | DAY1         | Haute    | DONE  |
| US2  | Réfléchir à une architecture logiciel                                                           | DAY1         | Haute    | DONE |
| US3  | Réflechir à une librairie UI                                                                    | DAY1         | Haute    | DONE  |
| US4  | Implémentation de donjon                                                                        | DAY1         | Moyenne  | DONE  |
| US5  | Implémenter les entités de base                                                                 | DAY1         | Moyenne  | DONE  |
| US6  | Choisir les algorithmes d'IA                                                                    | DAY2         | Haute    | DOING  |
| US7  | Choisir une fonction de scoring                                                                 | DAY2         | Moyenne  | DOING  |
| US8  | Croquis de l'UI                                                                                 | DAY3         | Moyenne  | TODO  |
| US9  | En tant que joueur sur le TUI je dois pouvoir placer/retirer des objets sur la map              | DAY2         | Haute    | DOING  |
| US10 | En tant que joueur sur le WEB je dois pouvoir placer/retier des objets sur la map               | DAY4         | Haute    | TODO  |
| US11 | En tant que joueur sur le TUI je dois pouvoir choisir l'algorithme de pathfinding               | DAY3         | Moyenne  | TODO  |
| US12 | En tant que joueur sur le WEB je dois pouvoir choisir l'algorithme de pathfinding               | DAY4         | Moyenne  | TODO  |
| US13 | Exportation de la configuration du donjon                                                       | DAY4         | Faible   | TODO  |
| US14 | gestion des niveaux avec 3 modes (facile choix libre, normal avec checkpoint, expert sans mort) | DAY5         | Faible   | TODO  |
| US15 | Choix des boutons pour l'utilisateur (réinitialiser vague, quitter etc)                         | DAY2         | Haute    | DOING  |
| US16 | Système d'avancement de tour                                                                    | DAY2         | Haute    | DOING  |
| US17 | Chargement de donjon                                                                            | DAY4         | Moyenne  | TODO  |
| US18 | Vérifier l'équilibre des niveaux                                                                | DAY5         | Faible   | TODO  |
| US19 | Implémenter les niveaux                                                                         | DAY3         | Moyenne  | TODO  |
| US20 | Mettre en place des pipelines de test sur Gitlab                                                | DAY2         | Moyenne  | DOING  |
| US21 | Affichage TUI                                              | DAY2         | Haute  | DONE  |

## 4. Dette technique et améliorations futures
