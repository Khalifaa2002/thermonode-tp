# TP4 — Qualité et gestion de configuration de ThermoNode

## 1. Revue de la demande de fusion simulée

La base du TP3 exécutait 74 tests Unity et 23 tests pytest avec succès. Sur la MR !7 du sujet (`e8633f5`), sept suites Unity étaient vertes, mais seulement 73 tests étaient exécutés. La proposition a été examinée sur une branche dédiée, puis écartée. Les cinq constats et les deux fiches de défaut sont détaillés dans [la revue MR !7](review-MR7.md).

| Constat | Mise en évidence | Demande de correction |
|---|---|---|
| Hystérésis fixée à 5 °C dans le code | Diff et test isolé à 3 °C | Réutiliser la valeur configurée. |
| Terminaison de l’identifiant supprimée | Inspection de la copie dans le tableau | Rétablir la copie bornée et la terminaison NUL. |
| Test de l’hystérésis configurable désactivé | Diff de `RUN_TEST` et baisse du nombre de tests | Réactiver le test. |
| Accolades et précédence peu explicites | Lecture et diagnostics MISRA 15.6 et 12.1 | Rétablir les blocs et parenthéser le calcul. |
| Opérateur virgule | Inspection du diff | Séparer les deux affectations. |

Avec un seuil de 60 °C et une hystérésis de 3 °C, le test isolé renvoyait `THR_NONE` à 56,99 °C alors que le résultat attendu était `THR_CLEAR`. La décision de revue a été de demander des changements.

**Q1.** Les tests exécutés sur la MR utilisaient l’hystérésis de 5 °C et la CI pouvait rester verte après la désactivation du cas discriminant. Le test isolé montre la régression fonctionnelle. La revue identifie aussi le test désactivé, le changement de copie et l’opérateur virgule. L’addon MISRA signale les écarts de forme observés sans connaître l’exigence EF-04.

## 2. Analyse statique

Le [tableau par règle](analyse-statique-tp4.md) donne les occurrences, classes, décisions et commits. Cppcheck classique a relevé 0 constat sur la base et sur la version intégrée. L’addon MISRA passe de **65 constats sur 16 règles à 0 constat résiduel** après correction et application des suppressions documentées. Les exceptions restent traçables dans le [registre des dérogations](misra-deviations.md), où les nouvelles propositions sont indiquées comme étant à valider.

Pylint passe de **9,11 à 9,89/10**. Les signatures imposées par Paho et `BaseHTTPRequestHandler` utilisent des exceptions locales. Les deux avis de complexité qui restent concernent le nombre d’arguments de `Storage.insert`. La signature publique a été conservée. Après intégration et ajout des tests ciblés, les **75 tests Unity** et **35 tests pytest** réussissent et le simulateur compile.

**Q2.** Les docstrings, le découpage de la réponse HTTP et la séparation de texte étaient des écarts de convention ou de lisibilité. Les signatures HTTP et MQTT relèvent des API utilisées. Les exceptions locales expliquent la contrainte à l’endroit où elle s’applique, comme les suppressions MISRA ciblées pour `node_id` et `range_check`.

## 3. SonarQube et couverture

Le projet local utilise la clé `thermoNode`. La Quality Gate `TVD` porte sur le nouveau code et demande une couverture d’au moins 80 %, zéro nouveau constat, 100 % de points sensibles de sécurité revus, une maintenabilité A et au plus 3,0 % de duplication avec l’opérateur disponible dans l’interface. Le seuil de duplication du sujet est strictement inférieur à 3 %. La définition du nouveau code est « Previous version ».

| Mesure | Référence `tp3` | Version intégrée |
|---|---:|---|
| Couverture globale SonarQube | 65,6 % | 100,0 % |
| Couverture des lignes du firmware, rapport gcovr | 94,83 % | 94,12 % |
| Couverture des branches du firmware, rapport gcovr | 90,85 % | 85,80 % |
| Tests pytest réussis | 23 | 35 |
| Constats de fiabilité, sécurité et maintenabilité | 0 | 0 |
| Points sensibles de sécurité | 0 | 0 |
| Duplication | 0,0 % | 0,0 % |
| Dette estimée | 0 min | 0 min |
| Constats Cppcheck importés | 0 | 0 |
| Verdict TVD | Passed | Passed |

Le premier passage après fusion sur `fbdd119` affichait 65,1 % de couverture SonarQube. Une comparaison du diff Git avec le rapport Cobertura montrait une ligne modifiée couverte sur quatre. Les trois lignes restantes concernaient la réponse HTTP 404. Les nouveaux tests du commit `4c2b521` couvrent désormais ces quatre lignes, les réponses HTTP, les rappels MQTT avec une doublure du client Paho, le démarrage Python et les cas de rejet des trames. La mesure inclut maintenant aussi le module MQTT et le point d’entrée. Coverage.py mesure 191 lignes sur 191 et 40 branches sur 40. SonarQube affiche également 100 % sur la passerelle.

Les analyses ne signalent aucun constat à classer. La Quality Gate TVD affiche Passed sur la référence et sur la livraison. Pour la dernière analyse, SonarQube compte 166 lignes nouvelles et 0 ligne nouvelle à couvrir. Les ajouts de cette dernière passe concernent les tests et leur configuration. Les dates Git des corrections Python sont antérieures au début de la période de référence du 21 novembre 2026 à 11 h 25 UTC. Le seuil de 80 % de couverture du nouveau code n’a donc pas été évalué. Les conditions de duplication, de maintenabilité et d’absence de nouveau constat ont été évaluées avec succès. [Documentation SonarQube sur le calcul du nouveau code](https://docs.sonarsource.com/sonarqube-community-build/project-administration/adjusting-analysis/configuring-new-code-calculation)

**Q3.** L’analyseur Python importe la couverture de la passerelle au format Cobertura. Pour le C, l’option Community utilisée importe les constats Cppcheck. La couverture du firmware est calculée séparément par `make -C firmware coverage`, qui produit le rapport gcovr. Le Jenkinsfile appelle cette cible et conserve les rapports du firmware. Il faut donc lire la couverture C dans ces rapports.

## 4. Gestion de configuration

| PR | Objet | Commit de fusion |
|---|---|---|
| [#1](https://github.com/Khalifaa2002/thermonode-tp/pull/1) | Corrections MISRA du firmware | `9071ab1` |
| [#2](https://github.com/Khalifaa2002/thermonode-tp/pull/2) | Corrections Pylint de la passerelle | `00b3420` |
| [#3](https://github.com/Khalifaa2002/thermonode-tp/pull/3) | Dérogations MISRA et analyse statique | `fbdd119` |
| [#4](https://github.com/Khalifaa2002/thermonode-tp/pull/4) | Hystérésis par défaut à 4 °C | `5c86db7` |

Le travail a été réalisé individuellement. Les PR ont servi à relire et intégrer les changements séparément. La revue croisée et les approbations externes prévues par le sujet n’ont pas été réalisées. Les PR ne disposaient pas de vérifications CI affichées sur GitHub. Les résultats de tests proviennent des exécutions dans la VM. Aucun artefact de compilation ou rapport généré n’est suivi par Git. Les quatre PR ont été intégrées à `main` au commit `fbdd119`. Les vérifications de livraison ont été refaites après l’ajout des nouveaux tests au commit `4c2b521`.

**Q4.** Le rebase de `feat/threshold-defaults-doc` sur la branche du patch enseignant a provoqué un conflit dans `threshold.h`. La résolution `4d63801` conserve la valeur 400 et le commentaire indiquant 4 °C. Les 74 tests Unity passent après le rebase. Le premier push utilisait la nouvelle histoire directement. Si une branche rebasée a déjà été publiée, `--force-with-lease` protège les mises à jour distantes concurrentes. Les tests existants initialisaient explicitement le seuil à 6000 et l’hystérésis à 500. Le test ajouté appelle `node_init` avec les constantes par défaut, vérifie la valeur de 4 °C et contrôle les deux côtés du seuil de sortie à 56 °C.

**Q5.** Le tag `v0.2.0` marque un incrément mineur pour les améliorations et la valeur par défaut ajustée, avec le même format de trame. Une correction isolée compatible correspondrait à `0.1.1` depuis `0.1.0`, ou à `0.2.1` après ce rendu. `1.0.0` annoncerait une interface publique stabilisée. Après cette stabilisation, une modification incompatible du format de trame impose un incrément majeur.

## 5. Actions à prioriser

1. Ajouter un scénario de démarrage complet du simulateur pour vérifier l’utilisation de l’hystérésis par défaut de bout en bout.
2. Examiner les branches C ajoutées aux traitements de conversion, notamment les erreurs et les limites, pour remonter la couverture de branches.
3. Évaluer l’import de la couverture C dans SonarQube. Le rapport gcovr reste la référence pour le firmware.

Références supplémentaires : [exigences](requirements.md), [contrat d’interface](icd.md), [dépôt GitHub](https://github.com/Khalifaa2002/thermonode-tp) et [tableau de bord SonarQube local](http://127.0.0.1:9000/project/overview?id=thermoNode).

L’[historique Git](git-history.txt) retrace les commits de code et les fusions utilisés pour la validation.
