# Rapport TP 3 — Concevoir et automatiser les tests de ThermoNode

Module EET5S1.3-TVD — Test, validation et DevOps pour les systèmes cyberphysiques · EET5 / S1 — 2026-2027
Auteur : Khalifa Bnouni · Travail individuel (sans binôme)

> Les résultats et limites ci-dessous sont distingués selon les preuves disponibles dans le dépôt. Les mesures non réalisées ne sont pas estimées.

---

## 1. Techniques appliquées, par exigence

| Exigence | Technique appliquée | Fichier de test | Cas |
|---|---|---|---|
| EF-01 | Vérification de la période d'acquisition par défaut (1000 ms) | test_node.c | 1 |
| EF-02 | Partitions d'équivalence + valeurs limites (codes ADC) | test_convert.c | 3 |
| EF-03 | Partitions de séquences + AddressSanitizer | test_filter.c | 6 |
| EF-04 | Table de décision (module seuil) + transitions d'états (nœud complet) | test_threshold.c, test_node.c | 13 |
| EF-05 | MC/DC sur la décision de défaut, capteur figé / hors plage | test_fault.c, test_node.c | 12 |
| EF-06 | Trame périodique avec horloge simulée | test_node.c | 1 |
| EF-07 | EP + BVA sur la plage de commande (19/20/100/101 °C) | test_node.c, test_threshold.c | 4 |
| EF-08 | Limites de la période d'acquisition | test_node.c | 2 |
| EI-02 | Oracle externe (valeur de contrôle CRC), trames malformées, paramétrage pytest | test_frame.c, test_frame.py | 9 |
| EI-03 | Décodage JSON, ACK/NACK | test_node.c, test_frame.c | 5 |
| ENF-01 | Contrainte temporelle (< 2 s) avec horloge simulée | test_node.c | 1 |
| ENF-05 | BVA 0/1/59/60/61 sur le tampon, mémorisation/retransmission, dédoublonnage et test système après coupure du broker | test_node.c, test_ringbuf.c, test_handler.py, tests/integration/test_reconnect.py | 8 cas unitaires + 1 intégration |

Les nombres de cas sont ceux de la matrice de traçabilité (section 4).

## 2. Journal des défauts

| ID | Étape | Exigence | Test révélateur | Symptôme | Cause (hypothèse) | Correction / commit |
|---|---|---|---|---|---|---|
| DEF-01 | 1 | EF-05 | test_EF05_range_check_bounds | Expected TRUE Was FALSE (ligne 33) | Comparaison stricte < au lieu de <= sur la borne 12500 | `47b7ba1` — comparaison rendue inclusive |
| DEF-02 | 2 | EF-03 | test_EF03_transient_partial_window ; test_EF03_invalid_sample_is_excluded | Expected 100 Was 2600 ; Expected 2500 Was 2650 ; ASan : global-buffer-overflow (filter.c:30) | Parcours du filtre dépassant les éléments valides et indexation incorrecte | `1b6cc7d` — correction de la boucle et de l'indexation circulaire |
| DEF-03 | 4 | EF-04 | test_EF04_counter_resets_below_threshold | Expected 0 Was 1 | Compteur de mesures consécutives non remis à zéro (règle R6) | `18c4425` — réinitialisation du compteur |
| DEF-04 | 6 | EI-02 | test_EI02_crc_check_value_123456789_is_29B1 ; test_EI02_crc_of_empty_is_FFFF | Vérification des valeurs de référence CRC | Défaut d'initialisation suspecté lors de l'analyse, mais non démontré par une version historique du code | `8daf94f` — implémentation CRC-16/CCITT-FALSE conforme ; causalité historique non démontrée |
| DEF-05 | 7 | ENF-05 | test_ENF05_push_61_keeps_60_and_drops_oldest | Expected 60 Was 61 ; ASan : global-buffer-overflow (ringbuf.c) | Mauvaise vérification de la capacité maximale du tampon | `82feca5` — correction de la condition de capacité avec >= RINGBUF_CAP |
| DEF-06 | 5 | EF-05 | test_EF05_recovers_to_normal_after_5_valid_samples | Expected 1 Was 3 (NORMAL attendu, FAULT obtenu) | Logique de reprise DÉFAUT → NORMAL absente dans node.c | `f1d6d41` — implémentation de la reprise après échantillons valides |
| DEF-07 | 9 | EI-02 | test_EI02_invalid_frames_are_rejected[temp_string], [seq_negative] | DID NOT RAISE FrameError | Validation trop permissive des types et absence de contrôle du signe de seq | `73e0a9d` — validation stricte des champs |
| DEF-08 | 9 | ENF-05 | test_ENF05_duplicate_seq_is_ignored ; test_ENF05_out_of_order_old_frame_is_ignored ; test_last_seq_survives_restart | Nombre de trames stockées incorrect (2 au lieu de 1) | Dédoublonnage défaillant et dernier numéro de séquence non conservé après redémarrage | `73e0a9d` — rejet des séquences anciennes et dupliquées |

**Note sur les branches DEF-12 à DEF-14 :** les commits de fusion `e151efc`, `5514afd` et `5b93929` correspondent à des étapes intermédiaires de stabilisation de la machine à états dans `firmware/src/node.c` : restauration de l'état initial `STATE_INIT`, réorganisation de `node_step()` après `emit()` et clarification de la condition d'émission périodique. L'analyse des différences ne met pas en évidence trois défauts indépendants supplémentaires ni de nouveaux tests associés. Ces commits sont donc considérés comme des corrections et ajustements intermédiaires liés à la stabilisation du firmware, et non comme trois défauts supplémentaires dans le journal.

## 3. Réponses aux questions Q1 à Q11

**Q1 — Quel code ADC donne exactement 12500 centièmes ? Pourquoi la BVA sur les codes ADC ne peut-elle pas l'atteindre ?**
Avec centi = ADC × 33000 / 4096 − 5000, 12500 correspond à ADC ≈ 2172,1. Le code 2172 donne 12499 et le code 2173 donne 12507 : aucun code ne donne exactement 12500. La limite de la plage ne peut donc être testée qu'en appliquant la BVA au niveau de la grandeur physique convertie (`range_check(12500)` / `range_check(12501)`), pas sur les codes bruts. La valeur 2355 figurant dans une ancienne capture n'est pas retenue : le calcul présenté ici suit la formule spécifiée dans `docs/requirements.md`.

**Q2 — D'où vient 2600 ? En quoi le sanitizer est-il un autre oracle ?**
Le tableau `window` a 5 cases (indices 0 à 4) ; le défaut lit la case [5], donc la mémoire située juste après le tableau, d'où une valeur qu'aucun test n'a poussée (2600). Le test en régime établi passe car cinq valeurs identiques masquent l'effet arithmétique. L'assertion Unity est un oracle fonctionnel (le résultat est-il celui attendu ?) ; AddressSanitizer est un oracle structurel : il signale tout accès hors bornes même quand le résultat paraît correct. Type d'erreur (diapositive 11) : dépassement de tampon global.

**Q3 — Stub, spy ou fake ?**
`hal_adc_read` : stub (rejoue une séquence) ; `hal_clock_ms` : fake (horloge simulée) ; `hal_radio_send` / `hal_radio_recv` : spy (enregistrent les appels). La séquence épuisée répète la dernière valeur pour éviter une chute artificielle à zéro qui fausserait le filtre.

**Q4 — « Consécutives » suffit-il ? Reformulation d'EF-04.**
La séquence 7000, 7000, 2500, 7000, 7000 viole la règle R6 (remise à zéro du compteur). Reformulation proposée : « Le système déclenche une alerte si et seulement si trois mesures filtrées consécutives sont strictement supérieures au seuil ; toute mesure filtrée inférieure ou égale au seuil remet immédiatement le compteur à zéro. »

**Q5 — Si on avait mis ADC_130 au lieu de ADC_70 ?**
Le nœud serait passé en FAULT (valeur hors plage, EF-05 prioritaire) et non en ALERT. Règle de méthode : calculer l'oracle à la main et choisir des données qui ne déclenchent que le mécanisme visé.

**Q6 — Table d'états.**
Transitions couvertes : INIT → NORMAL, NORMAL → ALERT, ALERT → NORMAL, ALERT → FAULT, NORMAL → FAULT, FAULT → NORMAL (reprise). La transition ALERT → FAULT est vérifiée par `test_EF05_alert_enters_fault_with_frame`. Limite documentaire : la table complète états × événements devra être confrontée au diagramme original de la diapositive 10, qui n'est pas présent parmi les documents repérés dans le dépôt.

**Q7 — CRC.**
La seule différence entre CRC-16/CCITT-FALSE et CRC-16/XMODEM est la valeur initiale (0xFFFF contre 0x0000). `frame_build` et `frame_crc_ok` utilisent la même fonction : elles se trompent de la même façon, donc les tests de cohérence interne passent. Seul l'oracle normalisé (valeur de contrôle 0x29B1 pour « 123456789 ») détecte l'écart ; le firmware avait tort et la passerelle était conforme.

**Q8 — Tampon de 60 trames.**
La variante à deux valeurs (60 et 61) suffit : 60 passe, 61 échoue. Sur un microcontrôleur sans protection mémoire, le débordement écrase des variables voisines (corruption silencieuse, HardFault).

**Q9 — Pourquoi la reprise échoue à l'étape 5 mais passe en MC/DC ?**
Le test unitaire de `fault.c` passe : la logique de détection et de reprise est correcte. DEF-06 est donc dans l'intégration (`node.c`), ce qui justifie de tester à plusieurs niveaux (unitaire puis intégration).

**Q10 — Une seule trame cumulant trois anomalies.**
On observerait seulement un rejet global, sans savoir quelle règle l'a provoqué ; on conclurait à tort que toutes les validations fonctionnent, alors que `temp_string` et `seq_negative` ne sont pas rejetés. Une anomalie par vecteur isole la cause.

**Q11 — Pourquoi le test système ne révèle ni DEF-05 ni DEF-08 ?**
Il injecte 30 mesures (moins que les 60 du tampon) et ne rejoue pas de messages. Pour DEF-05 il faudrait injecter plus de 60 mesures pendant la coupure ; pour DEF-08, redémarrer le nœud ou provoquer des reconnexions multiples. On préfère les révéler au niveau unitaire (rapide, déterministe, sans Docker).

## 4. Couverture, ressources et traçabilité

| Mesure | TP 0 | Avant correction | Après correction |
|---|---|---|---|
| Lignes | non relevé | 85,2 % (236/277) | 93,7 % (268/286) |
| Fonctions | non relevé | non relevé | 92,1 % (35/38) |
| Branches | non relevé | 79,4 % (108/136) | 89,3 % (125/140) |

- **Tests unitaires après correction :** 91 réussis, 0 échec, 0 ignoré : 69 tests firmware (3 + 8 + 6 + 11 + 26 + 6 + 9) et 22 tests unitaires Gateway. Avec 1 test d'intégration et 2 tests smoke, le total est de 94 tests automatisés réussis.
- **Empreinte :** Flash 10 232 / 49 152 octets, RAM 1 640 / 8 192 octets (statut OK).
- **Branches non couvertes :** 15 branches sur 140 ne sont pas couvertes par les tests (89,3 % de couverture). Aucune instruction `if (false)` n'a été retrouvée dans `firmware/src/node.c`.
- **Traçabilité :** 20 exigences, 12 couvertes, 8 orphelines (C-01, C-02, C-03, EI-01, ENF-02, ENF-03, ENF-04, ENF-06). Ces 8 exigences ne sont pas validées par la suite actuelle ; elles restent des limites de couverture et leur acceptabilité doit être justifiée selon le périmètre du TP.

## 5. Tests CPS

- **Temps (ENF-01) :** test avec horloge simulée (`hal_double_advance_ms`) : la trame d'alerte est émise moins de 2 s après la troisième mesure filtrée ; le test passe.
- **Communication (ENF-05) :** le test d'intégration `gateway/tests/integration/test_reconnect.py` simule une coupure du broker avec Docker Compose, produit des mesures pendant l'interruption, puis vérifie leur retransmission après reconnexion. Dernière exécution : 1 test réussi en 110,33 s. Le diagnostic MQTT a observé un maximum de 6 trames en buffer. Après reconnexion, les séquences 1 à 7 ont été reçues sans trou ni doublon. Cette validation démontre le scénario testé, mais pas une réussite de 10 exécutions sur 10.
- **Capteur (EF-05) :** hors plage et capteur figé couverts par MC/DC (T1 à T4) et par les tests de `test_node.c`.
- **Persistance SQLite :** la passerelle utilise `DB_PATH=/data/gw.sqlite`, dans le volume Docker nommé `ci_gwdata`. Le teardown des tests utilise `docker compose down` sans supprimer le volume. Vérification en lecture seule : table `measures` présente et `PRAGMA integrity_check` retourne `ok`. Les données observées comprennent les nœuds `TN01` et `SMOKE` ; ce contrôle ne démontre pas la conservation des données pendant 90 jours. Le service `gateway-init` attribue les permissions du volume à l'UID/GID 1000:1000 avant le démarrage de la Gateway, exécutée sous l'utilisateur non privilégié `gw`. Ce mécanisme a été validé sur le volume existant et sur un volume temporaire.
- **Ressources :** `size-check` validé (Flash/RAM ci-dessus) ; AddressSanitizer a révélé DEF-02 et DEF-05. Les exécutions précédentes d'AddressSanitizer ont permis d'identifier DEF-02 et DEF-05. Une exécution complète de toutes les suites avec sanitizer après correction n'est pas revendiquée.

## 6. Limites de la suite et temps passé

**Ce que la suite ne prouve pas :** le comportement sur le matériel réel (parasites sur l'ADC, vieillissement du capteur) ; les 8 exigences orphelines (cible, testabilité, passerelle, interface capteur, consommation, empreinte, règles de codage, robustesse réseau) ; l'absence totale de défaut (une suite verte ne le prouve pas).

**Temps passé (estimé) :** analyse et environnement ~2 h · modules de base (convert, filter, threshold, fault) ~4 h · machine à états et HAL de test ~5 h · derniers bugs, validation des 94 tests automatisés et intégration ENF-05 ~2 h.

## 7. Validation finale et version du projet

- **Tests firmware :** 69 réussis, 0 échec.
- **Tests unitaires Gateway :** 22 réussis, 0 échec.
- **Test d'intégration ENF-05 :** 1 réussi ; retransmission vérifiée après reconnexion du broker.
- **Tests smoke Gateway :** 2 réussis, 0 échec.
- **Bilan global :** 94 tests réussis, 0 échec, 0 erreur et 0 ignoré.
- **Rapports JUnit :** `reports/junit-fw.xml`, `reports/junit-gateway-core.xml` et `reports/junit-smoke.xml`.
- **Initialisation Docker :** `gateway-init` prépare les permissions du volume SQLite avant le démarrage de la Gateway.
- **Historique Git :** `dcf6c11` est le commit antérieur de validation ENF-05. HEAD est `d3130ee` sur `main`. Les modifications locales présentées ici ne sont pas encore commitées ni poussées.
