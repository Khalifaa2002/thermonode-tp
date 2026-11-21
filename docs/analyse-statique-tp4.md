# Analyse statique du TP4 — ThermoNode

L’analyse de référence a été réalisée sur `main` au commit `1bcdfa0` avec Cppcheck 2.13.0. L’analyse classique a relevé 0 constat. L’addon MISRA C:2012 a relevé 65 constats dans `firmware/src/`. Après les corrections et l’application des suppressions documentées ensemble avant leur séparation dans `style/misra-required` et `docs/deviations`, le rapport affiche 0 constat résiduel. Les dérogations proposées restent à valider.

## Firmware

| Règle | Avant | Après | Classe | Action | Commit |
|---|---:|---:|---|---|---|
| 2.5 | 1 | 0 | Défaut de configuration et faux positif POSIX | Utiliser la limite configurée dans `set_period`. Justifier séparément le signalement de `_POSIX_C_SOURCE` apparu lors de l’analyse finale. | `ef0b5e4`, `7f117d3` |
| 5.9 | 4 | 0 | Violation de norme | Distinguer les noms internes du filtre et du tampon circulaire. | `d875353` |
| 7.4 | 1 | 0 | Faux positif | Le littéral initialise un tableau de caractères. Suppression au-dessus de la déclaration. | `1401161` |
| 8.7 | 2 | 0 | Violation de norme et faux positif | Restreindre `state_name` à son fichier. Justifier l’appel à `range_check` depuis les tests exclus de l’analyse. | `6db8982`, `1401161` |
| 8.9 | 2 | 0 | Dérogation justifiée | Documenter la portée des deux données persistantes et limiter les suppressions à leurs déclarations (DEV-007). | `7f117d3` |
| 10.8 | 4 | 0 | Violation de norme | Séparer le calcul et la conversion pour les trames. Comparer les échéances en non signé. | `9ee8d2c` |
| 12.1 | 3 | 0 | Violation de norme | Expliciter le groupement des opérations. | `7326529` |
| 12.3 | 3 | 0 | Violation de norme | Séparer les déclarations signalées par l’addon. | `f10fdcc` |
| 13.3 | 1 | 0 | Violation de norme | Séparer l’affectation du numéro de séquence et son incrément. | `9aadbf8` |
| 15.5 | 26 | 0 | Dérogation justifiée | Conserver les retours anticipés dans les fichiers recensés (DEV-004). | `7f117d3` |
| 17.7 | 9 | 0 | Violation de norme et défaut réel | Rendre explicites les retours ignorés et vérifier la construction des motifs JSON. | `83422ad` |
| 18.4 | 4 | 0 | Dérogation justifiée | Documenter les opérations sur pointeurs dans le traitement des trames JSON (DEV-005). | `7f117d3` |
| 21.1 | 1 | 0 | Dérogation justifiée | Réserver la macro POSIX au simulateur (DEV-006). | `7f117d3` |
| 21.6 | 2 | 0 | Dérogation existante | Appliquer DEV-002 aux deux fichiers utilisant `snprintf`. | `7f117d3` |
| 21.10 | 1 | 0 | Dérogation justifiée | Réserver `<time.h>` au simulateur (DEV-006). | `7f117d3` |
| 22.8 | 1 | 0 | Violation de norme | Contrôler `errno` et les bornes pour les conversions entières. Le contrôle couvre aussi la conversion du CRC signalée au dernier passage. | `22f79ba`, `520c6dd` |

Le relevé intermédiaire a signalé des occurrences supplémentaires après les réécritures, notamment des retours anticipés et des opérations sur pointeurs. Les nombres de la colonne « Après » correspondent au passage final avec `--inline-suppr` et `misra-suppressions.txt`. Après les corrections, les sept suites Unity passent avec 74 tests et le simulateur compile.

## Passerelle Python

Pylint 3.3.1 passe de **9,11/10** à **9,89/10** sur `chore/pylint` au commit `389baa5`. Les **23 tests unitaires pytest** passent.

| Message | Avant | Après | Traitement |
|---|---:|---:|---|
| C0115 | 5 | 0 | Ajouter les docstrings de classe. |
| C0207 | 1 | 0 | Limiter la séparation du texte au premier deux-points. |
| C0321 | 1 | 0 | Écrire une instruction par ligne dans le traitement HTTP 404. |
| C0103 | 1 | 0 | Justifier localement le nom `do_GET` imposé par le serveur HTTP. |
| W0613 | 5 | 0 | Justifier localement les arguments de rappel fournis par Paho MQTT. |
| R0913 | 2 | 1 | Justifier la signature du rappel MQTT. Conserver le constat sur `Storage.insert` pour préserver son interface. |
| R0917 | 2 | 1 | Même traitement pour le nombre d’arguments positionnels. |

Les messages C0115, C0207 et C0321 ont été traités comme des écarts de convention ou de lisibilité. Les messages liés aux signatures HTTP et MQTT relèvent de contraintes d’API et font l’objet d’exceptions locales. Les deux avis sur `Storage.insert` restent visibles comme pistes de refactoring. Une exception locale borne la justification à la méthode concernée et laisse le contrôle actif dans le reste du projet, comme une suppression MISRA ciblée.
