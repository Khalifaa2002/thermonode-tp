# Rapport TP 3 — Concevoir et automatiser les tests de ThermoNode

Module EET3S1.3-TVD — Test, validation et DevOps pour les systèmes cyberphysiques · EET3 / S1 — 2026-2027
Auteur : Khalifa Bnouni ·



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
| ENF-05 | BVA 0/1/59/60/61 sur le tampon, mémorisation/retransmission, dédoublonnage | test_node.c, test_ringbuf.c, test_handler.py | 8 |

Les nombres de cas sont ceux de la matrice de traçabilité (section 4).

## 2. Journal des défauts

| ID | Étape | Exigence | Test révélateur | Symptôme | Cause (hypothèse) | Correction / commit |
|---|---|---|---|---|---|---|
| DEF-01 | 1 | EF-05 | test_EF05_range_check_bounds | Expected TRUE Was FALSE (ligne 33) | Comparaison stricte < au lieu de <= sur la borne 12500 | [À COMPLÉTER] |
| DEF-02 | 2 | EF-03 | test_EF03_transient_partial_window ; test_EF03_invalid_sample_is_excluded | Expected 100 Was 2600 ; Expected 2500 Was 2650 ; ASan : global-buffer-overflow (filter.c:30) | Accès à window[5] (indice 5 d'un tableau de 5 cases) | [À COMPLÉTER] |
| DEF-03 | 4 | EF-04 | test_EF04_counter_resets_below_threshold | Expected 0 Was 1 | Compteur de mesures consécutives non remis à zéro (règle R6) | [À COMPLÉTER] |
| DEF-04 | 6 | EI-02 | test_EI02_crc_check_value_123456789_is_29B1 ; test_EI02_crc_of_empty_is_FFFF | Écart avec les valeurs de contrôle normalisées — **[À VÉRIFIER]** : la capture montre 11 tests sans échec | Valeur initiale 0x0000 au lieu de 0xFFFF (CRC-16/XMODEM au lieu de CCITT-FALSE) | [À COMPLÉTER] |
| DEF-05 | 7 | ENF-05 | test_ENF05_push_61_keeps_60_and_drops_oldest | Expected 60 Was 61 ; ASan : global-buffer-overflow (ringbuf.c) | Dépassement de la capacité de 60 trames | [À COMPLÉTER] |
| DEF-06 | 5 | EF-05 | test_EF05_recovers_to_normal_after_5_valid_samples | Expected 1 Was 3 (NORMAL attendu, FAULT obtenu) | Transition de reprise DÉFAUT → NORMAL défaillante dans node.c (fault.c est correct, cf. Q9) | [À COMPLÉTER] |
| DEF-07 | 9 | EI-02 | test_EI02_invalid_frames_are_rejected[temp_string], [seq_negative] | DID NOT RAISE FrameError | Conversion trop tolérante (float() accepte "25.50") ; pas de contrôle du signe de seq | [À COMPLÉTER] |
| DEF-08 | 9 | ENF-05 | test_ENF05_duplicate_seq_is_ignored ; test_ENF05_out_of_order_old_frame_is_ignored ; test_last_seq_survives_restart | Nombre de trames stockées incorrect (2 au lieu de 1) | Dédoublonnage par seq défaillant ; dernier seq non conservé après redémarrage | [À COMPLÉTER] |

**[À COMPLÉTER]** Des branches `fix/DEF-12-node-init-transition`, `fix/DEF-13-node-order-fix` et `fix/DEF-14-node-periodic-check` apparaissent dans la capture du `git push` : si ce sont des défauts supplémentaires, ils doivent figurer dans ce journal.

## 3. Réponses aux questions Q1 à Q11

**Q1 — Quel code ADC donne exactement 12500 centièmes ? Pourquoi la BVA sur les codes ADC ne peut-elle pas l'atteindre ?**
Avec centi = ADC × 33000 / 4096 − 5000, 12500 correspond à ADC ≈ 2172,1. Le code 2172 donne 12499 et le code 2173 donne 12507 : aucun code ne donne exactement 12500. La limite de la plage ne peut donc être testée qu'en appliquant la BVA au niveau de la grandeur physique convertie (`range_check(12500)` / `range_check(12501)`), pas sur les codes bruts. **[À VÉRIFIER]** : le compte rendu Word cite un code 2355 et une formule différente, non conformes au sujet.

**Q2 — D'où vient 2600 ? En quoi le sanitizer est-il un autre oracle ?**
Le tableau `window` a 5 cases (indices 0 à 4) ; le défaut lit la case [5], donc la mémoire située juste après le tableau, d'où une valeur qu'aucun test n'a poussée (2600). Le test en régime établi passe car cinq valeurs identiques masquent l'effet arithmétique. L'assertion Unity est un oracle fonctionnel (le résultat est-il celui attendu ?) ; AddressSanitizer est un oracle structurel : il signale tout accès hors bornes même quand le résultat paraît correct. Type d'erreur (diapositive 11) : dépassement de tampon global.

**Q3 — Stub, spy ou fake ?**
`hal_adc_read` : stub (rejoue une séquence) ; `hal_clock_ms` : fake (horloge simulée) ; `hal_radio_send` / `hal_radio_recv` : spy (enregistrent les appels). La séquence épuisée répète la dernière valeur pour éviter une chute artificielle à zéro qui fausserait le filtre.

**Q4 — « Consécutives » suffit-il ? Reformulation d'EF-04.**
La séquence 7000, 7000, 2500, 7000, 7000 viole la règle R6 (remise à zéro du compteur). Reformulation proposée : « Le système déclenche une alerte si et seulement si trois mesures filtrées consécutives sont strictement supérieures au seuil ; toute mesure filtrée inférieure ou égale au seuil remet immédiatement le compteur à zéro. »

**Q5 — Si on avait mis ADC_130 au lieu de ADC_70 ?**
Le nœud serait passé en FAULT (valeur hors plage, EF-05 prioritaire) et non en ALERT. Règle de méthode : calculer l'oracle à la main et choisir des données qui ne déclenchent que le mécanisme visé.

**Q6 — Table d'états.**
Transitions couvertes : INIT → NORMAL, NORMAL → ALERT, ALERT → NORMAL, NORMAL → FAULT, FAULT → NORMAL (reprise). **[À COMPLÉTER]** : la transition de la diapositive 10 non testée et l'événement non spécifié, ainsi que la table états × événements demandée par le sujet.

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
| Lignes | [À COMPLÉTER] | 85,2 % (236/277) | 93,0 % (266/286) |
| Fonctions | [À COMPLÉTER] | non relevé | 92,1 % (35/38) |
| Branches | [À COMPLÉTER] (≈ 5 % selon le sujet) | 79,4 % (108/136) | 88,6 % (124/140) |

- **Tests unitaires après correction :** 68 réussis, 0 échec, 0 ignoré (3 + 8 + 6 + 11 + 25 + 6 + 9).
- **Empreinte :** Flash 10 176 / 49 152 octets, RAM 1 640 / 8 192 octets (statut OK).
- **Zones rouges :** le rapport HTML a mis en évidence dans `node.c` une zone non couverte contenant un `if (false)`, considérée comme du code mort. **[À VÉRIFIER]** avec `reports/coverage-fw.html` (lignes exactes).
- **Traçabilité :** 20 exigences, 12 couvertes, 8 orphelines (C-01, C-02, C-03, EI-01, ENF-02, ENF-03, ENF-04, ENF-06). **[À COMPLÉTER]** pourquoi cela est acceptable.

## 5. Tests CPS

- **Temps (ENF-01) :** test avec horloge simulée (`hal_double_advance_ms`) : la trame d'alerte est émise moins de 2 s après la troisième mesure filtrée ; le test passe.
- **Communication (étape 10) :** la coupure du broker est simulée (conteneurs Docker Compose). Le test `test_reconnect.py` échoue dans les captures (« tampon 0 < 3 après 60 s ») et la boucle de 10 exécutions affiche des échecs : la condition « 10/10 » n'est **pas** démontrée. **[À COMPLÉTER]** après correction ou analyse (échec systématique ou instable ?).
- **Capteur (EF-05) :** hors plage et capteur figé couverts par MC/DC (T1 à T4) et par les tests de `test_node.c`.
- **Ressources :** `size-check` validé (Flash/RAM ci-dessus) ; AddressSanitizer a révélé DEF-02 et DEF-05. **[À COMPLÉTER]** : capture de `grep -c AddressSanitizer` = 0 après correction.

## 6. Limites de la suite et temps passé

**Ce que la suite ne prouve pas :** le comportement sur le matériel réel (parasites sur l'ADC, vieillissement du capteur) ; les 8 exigences orphelines (cible, testabilité, passerelle, interface capteur, consommation, empreinte, règles de codage, robustesse réseau) ; l'absence totale de défaut (une suite verte ne le prouve pas).

**Temps passé (estimé) :** analyse et environnement ~2 h · modules de base (convert, filter, threshold, fault) ~4 h · machine à états et HAL de test ~5 h · derniers bugs et validation finale des 68 tests ~2 h.
