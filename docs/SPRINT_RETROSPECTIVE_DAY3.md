# 🌀 Rétrospective de Backlog – Fin de Sprint

**Sprint n° :** 2  
**Jour :** Mardi

---

## 1️⃣ Objectif du sprint (rappel)

> Quel était l’objectif principal du sprint ?

- 🎯 **Objectif annoncé :** Implémenter le moteur de simulation avec éditeur TUI et système de tours, mettre en place CI/CD et documenter les algorithmes d'IA
- ✅ **Objectif atteint ?** Presque atteint
- 📝 **Commentaire :** L'affichage TUI à été modifié pour être MVC friendly. CI/CD opérationnel. Restent à finaliser l'édition via le TUI et la visualisation de la simulation via la boucle, la documentation des algorithmes d'IA et la fonction de scoring La tâche prioritaire pour le prochain sprint est la mise en place d'une boucle principale de jeu.

---

## 2️⃣ État du backlog à la fin du sprint
| Tâche | Etat |
|------|------|
|Choisir et documenter les algorithmes d'IA à implémenter (BFS, Dijkstra, Dijkstra pondéré par danger)| DOING |
|Définir la fonction de scoring (critères : héros morts, trésor protégé, budget dépensé, temps)| DOING |
|Implémenter l'éditeur TUI : affichage de la grille /placer / retirer objets sur la grille (sauvegarder position) -> Initialisation de la simulation | DOING |
|En tant que joueur sur le TUI je dois pouvoir choisir l'algorithme de pathfinding | DOING|
|Implémenter les niveaux |DOING|
### 📊 Vue d’ensemble

| Élément | Nombre |
|------|------|
| Tâchesprévues | 5 |
| Tâches terminées | 0 |
| Tâches partiellement terminées | 4 |
| Tâches non commencées | 1 |

### 📌 Observations

**Points positifs :**
- Affichage TUI MVC friendly et fonctionnel
- Système d'avancement de tours implémenté et opérationnel
- Commandes utilisateur complètes (réinitialiser, lancer vague, tour suivant, quitter)


**Points d'amélioration :**
- Documentation des algorithmes d'IA non finalisée (BFS, Dijkstra, Dijkstra pondéré)
- Fonction de scoring partiellement définie, reste à implémenter
- L'édition du donjon en TUI n'est pas encore implémentée
- Mise en lien TUI (View) et GameController partiellement implémenté

**Décisions prises :**
- Critères de scoring définis : héros morts, trésor protégé, budget dépensé, temps


---

