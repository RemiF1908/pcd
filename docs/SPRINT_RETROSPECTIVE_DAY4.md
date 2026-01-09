# 🌀 Rétrospective de Backlog – Fin de Sprint

**Sprint n° :** 4
**Jour :** Jeudi

---

## 1️⃣ Objectif du sprint (rappel)

> Quel était l’objectif principal du sprint ?

- 🎯 **Objectif annoncé :** Finaliser la boucle de jeu principale, incluant l'éditeur TUI, la gestion de fin de vague, la sélection d'algorithme, et commencer l'intégration de l'interface Web.
- ✅ **Objectif atteint ?** Partiellement
- 📝 **Commentaire :** La boucle de jeu et le TUI sont maintenant robustes et fonctionnels. Le travail sur l'interface Web a bien commencé, avec un serveur et une base d'interface, mais l'interaction complète n'est pas terminée.

---

## 2️⃣ État du backlog à la fin du sprint
| Tâche | Etat |
|------|------|
| Finaliser l'éditeur TUI et la liaison avec le GameController | DONE |
| Gestion de la fin d'une vague (arrêt, reset, résumé) | DONE |
| Permettre au joueur de choisir l'algorithme de pathfinding dans l'UI | DONE |
| Vérifier la correction des paths des héros via des tests | DONE |
| Créer le croquis de l'UI (implicitement fait avec l'UI Web) | DONE |
| Implémenter la fonction de scoring | DOING |
| Implémenter les niveaux de jeu (US19) | DOING |
| [US10] UI Web : placer/retirer des objets | DOING |
| [US13, US17] Import/Export de donjons | DOING |


### 📊 Vue d’ensemble

| Élément | Nombre |
|------|------|
| Tâches prévues | 9 |
| Tâches terminées | 5 |
| Tâches partiellement terminées | 4 |
| Tâches non commencées | 0 |

### 📌 Observations

**Points positifs :**
- La boucle de jeu principale est stable et fonctionnelle.
- L'interface TUI est complète et permet de jouer une partie de A à Z.
- Le démarrage de l'interface Web est un succès, avec un serveur FastAPI fonctionnel et une communication de base établie.
- Les commandes du `GameInvoker` (placer, start, etc.) sont bien intégrées et testées.

**Points d'amélioration :**
- L'interface Web n'est pas encore interactive ; il manque la gestion des clics pour placer/retirer des entités.
- La gestion de campagne (enchaînement des niveaux) n'est pas encore implémentée.
- La fonction de scoring reste à finaliser et à intégrer dans les deux interfaces.

**Décisions prises :**
- Prioriser la finalisation de l'interface Web pour le dernier jour.
- Implémenter un mode "Campagne" simple qui charge les niveaux séquentiellement.
- L'équilibrage et la vidéo de démo seront les dernières tâches.

---