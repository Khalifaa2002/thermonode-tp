# Revue de MR !7 « fix hysteresis »

Commit examiné `e8633f5`. Base TP3 `4ef768b`.
Environnement VM Ubuntu 24.04, GCC 13.3.0 et Cppcheck 2.13.0.

| # | Fichier:ligne | Constat | Règle / source | Gravité | Demande à l’auteur |
|---|---|---|---|---|---|
| 1 | `firmware/src/threshold.c:31` | Le seuil de sortie soustrait toujours 500 centièmes de degré et ignore `hyst_centi`. | EF-04, constantes | Bloquant | Réutiliser `hyst_centi` et parenthéser la soustraction. |
| 2 | `firmware/src/node.c:22` | La copie occupe potentiellement tout `node_id` et la terminaison NUL explicite disparaît. Une chaîne non terminée peut ensuite être lue au-delà du tableau. Cette modification élargit aussi le périmètre de la MR. | EI-02, chaînes et tampons | Bloquant | Copier au plus `TN_ID_LEN - 1u` caractères, terminer le tableau explicitement et couvrir la limite dans une modification dédiée. |
| 3 | `firmware/test/test_threshold.c:25`, `:45` | Le test de l’hystérésis configurée est renommé et son appel Unity est commenté. La suite passe de 9 à 8 tests. | EF-04, couverture de la régression | Majeur | Réactiver le test et conserver les assertions à 57,00 °C et 56,99 °C. |
| 4 | `firmware/src/threshold.c:31`, `:34–38` | Les corps de plusieurs structures de contrôle perdent leurs accolades. L’addon remonte trois violations 15.6 et signale aussi la précédence de l’expression ligne 31. | MISRA C:2012 15.6 et 12.1 | Majeur | Remettre les accolades autour des corps et les parenthèses autour de la soustraction. |
| 5 | `firmware/src/threshold.c:32` | L’opérateur virgule réunit la mise à jour de l’événement et la remise à zéro du compteur. | MISRA C:2012 12.3 | Mineur | Écrire deux instructions distinctes dans le même bloc. |

## DR-TP4-01 — Hystérésis configurée ignorée

- Version `e8633f5`, VM Ubuntu 24.04, GCC 13.3.0.
- Configurer `threshold_set(6000, 300)`, puis appeler `threshold_step(5699, true)` dans un exécutable lié à `firmware/src/threshold.c`.
- Attendu `THR_CLEAR` (2), puisque 56,99 °C est inférieur à 57,00 °C.
- Obtenu `THR_NONE` (0). Le programme de vérification sort avec le code 1.
- Sévérité majeure, priorité haute. Le maintien de l’alerte ne suit pas le paramétrage EF-04.

## DR-TP4-02 — Terminaison du champ identifiant

- Version `e8633f5`, VM Ubuntu 24.04, revu par inspection du diff.
- Suivre `node_set_id` avec un identifiant contenant au moins `TN_ID_LEN` caractères et vérifier la copie jusqu’à la dernière case du tableau.
- Attendu, une chaîne bornée terminée par NUL. Observé par lecture, `strncpy` reçoit la capacité totale et l’affectation explicite du dernier octet a été retirée.
- Sévérité majeure, priorité haute. Risque de lecture hors des limites du tableau lors du traitement de l’identifiant comme chaîne C.
- Pièce de revue `git diff main...e8633f5 -- firmware/src/node.c`.

## Décision — Demander des changements

Rétablir le paramétrage de l’hystérésis et le test de non-régression qui l’exerce. Conserver la terminaison explicite de l’identifiant et corriger les écarts MISRA dans le diff. Utiliser un message de commit qui référence EF-04.

## Q1 — Complémentarité des vérifications

| Constat | Mise en évidence | Limite observée |
|---|---|---|
| Hystérésis en dur | Lecture du diff, puis test isolé à 3 °C | Les cas Unity restants utilisent 5 °C. Cppcheck ignore l’intention de configuration d’EF-04. |
| Terminaison de l’identifiant | Lecture de la taille de copie et de la ligne supprimée | La suite ne couvre pas ici la longueur limite. Cppcheck classique n’a émis aucun défaut sur cette analyse ciblée. |
| Test désactivé | Lecture de `RUN_TEST` et comparaison du nombre de tests Unity | Unity signale les échecs des cas exécutés. Ce cas n’est plus enregistré. |
| Accolades et précédence | Liste de contrôle, confirmée par l’addon MISRA | La suite Unity contrôle le comportement exercé et ne vérifie pas la forme du code. |
| Opérateur virgule | Liste de contrôle par lecture | Cppcheck 2.13.0 n’a pas remonté 12.3 dans l’analyse ciblée. Les deux effets s’exécutent en C. |

Les sept suites passent sur la MR avec 73 tests et zéro échec, contre 74 sur sa base. La revue vérifie le lien entre la modification et les exigences. L’analyse statique signale des écarts de règles. Le test isolé confirme le comportement pour une configuration précise.
