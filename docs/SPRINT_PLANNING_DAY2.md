# SPRINT PLANNING — Day 2

Date: 6/12/25

## Objectif du sprint

Finaliser les choix techniques et définir les tâches concrètes pour implémenter :
- les stratégies d'IA des héros,
- le système de scoring,
- l'éditeur TUI (placement / retrait d'objets),
- les contrôles utilisateur (boutons/actions),
- l'avancement tour-par-tour,
- l'intégration CI (pipelines de tests).


## Backlog / Tâches

- [ ] Choisir et documenter les algorithmes d'IA à implémenter (BFS, Dijkstra, Dijkstra pondéré par danger)
- [ ] Définir la fonction de scoring (critères : héros morts, trésor protégé, budget dépensé, temps)
- [ ] Implémenter l'éditeur TUI : affichage de la grille /placer / retirer objets sur la grille (sauvegarder position) 
-> Initialisation de la simulation
- [ ] Définir et implémenter les boutons/commandes utilisateur (réinitialiser vague, quitter, lancer vague, tour suivant)
- [ ] Concevoir le système d'avancement de tour (gestion des étapes d'un tour, mise à jour état des héros)
-> Logique de boucle d'action, gestion de controller / manager. Définir la fonction simulate_round.
-> Tour par tour ou déroulement automatique?
- [ ] Mettre en place pipelines CI sur GitLab pour lancer les tests automatiquement
- [ ] Revue et documentation (mettre à jour README/docs avec décisions prises)

## Priorités

1. Choix des algorithmes d'IA et fonction de scoring
2. Éditeur TUI (placement/retrait) + contrôles utilisateur
3. Système d'avancement de tour
4. Tests et CI


