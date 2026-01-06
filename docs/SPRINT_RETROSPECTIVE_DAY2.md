# 🌀 Rétrospective de Backlog – Fin de Sprint

**Sprint n° :** 2  
**Jour :** Mardi

---

## 1️⃣ Objectif du sprint (rappel)

> Quel était l’objectif principal du sprint ?

- 🎯 **Objectif annoncé :** Implémenter le moteur de simulation avec éditeur TUI et système de tours, mettre en place CI/CD et documenter les algorithmes d'IA
- ✅ **Objectif atteint ?** Partiellement
- 📝 **Commentaire :** L'éditeur TUI, le système de tours et les commandes utilisateur sont fonctionnels. CI/CD opérationnel. Restent à finaliser la documentation des algorithmes d'IA et la fonction de scoring 

---

## 2️⃣ État du backlog à la fin du sprint
| Tâche | Etat |
|------|------|
|Choisir et documenter les algorithmes d'IA à implémenter (BFS, Dijkstra, Dijkstra pondéré par danger)| DOING |
|Définir la fonction de scoring (critères : héros morts, trésor protégé, budget dépensé, temps)| DOING |
|Implémenter l'éditeur TUI : affichage de la grille /placer / retirer objets sur la grille (sauvegarder position) -> Initialisation de la simulation | DONE |
| Définir et implémenter les boutons/commandes utilisateur (réinitialiser vague, quitter, lancer vague, tour suivant)| DONE |
|Concevoir le système d'avancement de tour (gestion des étapes d'un tour, mise à jour état des héros) -> Logique de boucle d'action, gestion de controller / manager. Définir la fonction simulate_round. -> Tour par tour ou déroulement automatique? | DONE |
|Mettre en place pipelines CI sur GitLab pour lancer les tests automatiquement| DONE |
|Revue et documentation (mettre à jour README/docs avec décisions prises)|  |
### 📊 Vue d’ensemble

| Élément | Nombre |
|------|------|
| Tâchesprévues | 7 |
| Tâches terminées | 4 |
| Tâches partiellement terminées | 2 |
| Tâches non commencées | 1 |

### 📌 Observations

**Points positifs :**
- Éditeur TUI fonctionnel avec placement et suppression d'objets
- Système d'avancement de tours implémenté et opérationnel
- Commandes utilisateur complètes (réinitialiser, lancer vague, tour suivant, quitter)
- CI/CD GitLab configuré pour l'exécution automatique des tests
- Bonne communication d'équipe
- Bonne répartition des tâches 

**Points d'amélioration :**
- Documentation des algorithmes d'IA non finalisée (BFS, Dijkstra, Dijkstra pondéré)
- Fonction de scoring partiellement définie, reste à implémenter
- Tâche de revue et documentation non commencée
- Mise en lien TUI (View) et GameController à  

**Décisions prises :**
- Choix des algorithmes d'IA identifiés mais restent à documenter en détail
- Critères de scoring définis : héros morts, trésor protégé, budget dépensé, temps


---

