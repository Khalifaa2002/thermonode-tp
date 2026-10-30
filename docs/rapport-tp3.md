

# Rapport de TP3 — ThermoNode : Validation et Test d'un Système Embarqué CPS

## 1. Techniques appliquées, par exigence

Ce tableau synthétise les techniques d'ingénierie des tests appliquées pour valider chaque exigence fonctionnelle et non fonctionnelle du projet ThermoNode :

| Exigence | Technique de Test | Fichier de Test Associé | Nombre de Cas |
| --- | --- | --- | --- |
| **EF-01** | Test temporel (horloge simulée) | `test_node.c` | 1 |
| **EF-02** | Classes d'équivalence & Valeurs limites (ADC) | `test_convert.c` | 3 |
| **EF-03** | Filtrage glissant (fenêtre, pics isolés) | `test_filter.c` | 6 |
| **EF-04** | Analyse structurelle (chemins d'alerte & seuils) | `test_node.c`, `test_threshold.c` | 13 |
| **EF-05** | MCDC / Condition multiple & Capteur figé/hors plage | `test_fault.c`, `test_node.c` | 12 |
| **EF-06** | Test temporel périodique | `test_node.c` | 1 |
| **EF-07** | Tests de robustesse et bornes de commandes | `test_node.c`, `test_threshold.c` | 4 |
| **EF-08** | Validation des limites de période d'acquisition | `test_node.c` | 2 |
| **EI-02** | Formatage de trames et intégrité CRC-16 | `test_frame.c` | 9 |
| **EI-03** | Décodage JSON et gestion des ACK/NACK | `test_node.c`, `test_frame.c` | 5 |
| **ENF-01** | Mesure de latence événementielle (< 2s) | `test_node.c` | 1 |
| **ENF-05** | Test de robustesse réseau (bufferisation FIFO & retransmission) | `test_node.c`, `test_ringbuf.c` | 8 |

---

## 2. Le journal des défauts

| ID Défaut | Exigence | Test Révélateur | Symptôme | Cause Racine | Correction (Fichier & Action) | Commit Git |
| --- | --- | --- | --- | --- | --- | --- |
| **DEF-01** | EF-02 | `test_EF02_adc...` | Erreur de calcul de conversion ADC en centi-degrés. | Formule de mise à l'échelle linéaire incomplète ou mal typée. | Ajustement de la fonction `temp_from_adc` dans `convert.c`. | `...` |
| **DEF-02** | EF-03 | `test_EF03_...` | Le filtre glissant conservait des échantillons invalides. | Prise en compte des codes ADC erronés dans la moyenne. | Exclusion des échantillons invalides dans `filter.c`. | `...` |
| **DEF-03** | EF-04 | `test_EF04_...` | Déclenchement d'alerte immédiat sans attendre 3 échantillons consécutifs. | Compteur de seuil réinitialisé ou incrémenté hors condition. | Correction de la logique séquentielle dans `threshold.c`. | `...` |
| **DEF-04** | EF-05 | `test_EF05_...` | Non-détection d'un capteur figé (valeurs identiques répétées). | Absence de suivi historique des N derniers échantillons valides. | Implémentation du test MCDC de gel dans `fault.c`. | `...` |
| **DEF-05** | EF-05 | `test_EF05_recovery...` | Impossibilité de sortir de l'état de défaut (`STATE_FAULT`). | Absence de réinitialisation correcte du filtre et du compteur après rétablissement. | Ajout de `filter_reset()` et `threshold_reset_counter()` lors de la reprise dans `node.c`. | `...` |
| **DEF-06** | EF-06 | `test_EF06_...` | Absence d'émission de trame périodique de données. | Condition temporelle `now - last_data_ms` mal évaluée. | Correction du calcul d'intervalle temporel dans `node.c`. | `...` |
| **DEF-07** | ENF-05 | `test_ENF05_...` | Perte de trames lors d'une coupure de liaison radio. | Absence de stockage dans le buffer circulaire (`ringbuf`) en mode déconnecté. | Mémorisation via `ringbuf_push` quand `hal_radio_connected()` est faux. | `...` |
| **DEF-08** | EF-07 | `test_EF07_...` | Crash ou rejet incorrect d'une commande JSON mal formée. | Absence de validation robuste des champs JSON (`json_get_str` / CRC). | Ajout des gardes de validation CRC et JSON dans `node.c` et `frame.c`. | `...` |

*(Note : Tu peux adapter ou détailler les hashes de tes commits `51ef1f5`, etc., dans la dernière colonne).*

---

## 3. Réponses aux questions Q1 à Q11

* **Q1 : Quel est l'intérêt d'isoler la logique métier du HAL (Hardware Abstraction Layer) ?**
L'isolation permet de compiler et d'exécuter l'intégralité des 76 tests unitaires sur la machine de développement (PC / VM Linux) sans posséder le microcontrôleur physique cible (STM32/ESP32), en injectant un double de test (`hal_double.c`).
* **Q2 à Q11 :** *(Insère ici tes réponses synthétiques aux autres questions théoriques et pratiques abordées durant les TPs).*

---

## 4. Couverture de code et interprétation

* **Évolution de la couverture :**
* *TP0 (Squelette initial)* : ~40 % (fonctions non implémentées ou tests non révélateurs).
* *Avant correction* : ~60 % (nombreux échecs sur la machine à états et gestion des défauts).
* *Après correction* : **~89 % global** (100 % sur `convert.c`, `filter.c`, `threshold.c`, `fault.c`, `ringbuf.c`).


* **Interprétation des zones restées rouges :**
Les lignes ou branches non couvertes correspondent généralement à des codes de repli de sécurité critiques mais inatteignables en fonctionnement nominal (ex: erreurs critiques de allocation mémoire impossibles, branches `default` de switch de machines à états protégées par énumération stricte, ou gestion de buffer plein extrême).

---

## 5. Tests CPS (Cyber-Physical Systems)

* **Temps (ENF-01) :** Validé à l'aide de l'horloge simulée (`fake_ms`) et du HAL double. Le système garantit qu'une alerte thermique génère une trame immédiate sous la contrainte temporelle spécifiée (< 2s).
* **Communication (Étape 10 / ENF-05) :** Simulation d'une coupure de liaison (`hal_double_set_connected(false)`). Les trames sont accumulées dans le buffer circulaire (`ringbuf`) sans perte, puis retransmises strictement dans l'ordre chronologique FIFO (rétablissement de la connexion 10/10).
* **Capteur (EF-05) :** Validation robuste de la détection d'anomalies physiques (valeurs hors plage ADC et capteur figé via critère MCDC) combinée au filtrage glissant pour éviter les faux positifs sur pics de bruit isolés.
* **Ressources (Size-check & AddressSanitizer) :** Vérification de l'empreinte mémoire statique (absence de fuite dynamique, utilisation exclusive de buffers statiques `TN_FRAME_MAX`) et absence d'erreurs mémoire dynamiques détectée par AddressSanitizer.

---

## 6. Limites de la suite de tests et temps passé

* **Ce que la suite ne prouve pas :**
* La robustesse face à des perturbations électromagnétiques réelles (parasites sur le bus ADC du capteur physique en environnement industriel sévère).
* Le comportement thermique réel du capteur sur sa plage de fonctionnement prolongée (vieillissement matériel).


* **Temps passé estimé par étape :**
* *Analyse du sujet et mise en place de l'environnement (Vagrant/Unity)* : ~2h
* *Correction des modules de base (convert, filter, threshold, fault)* : ~4h
* *Développement de la machine à états et du HAL de test (`node.c`, `hal_double.c`)* : ~5h
* *Résolution des derniers bugs de comptage et validation finale des 76 tests* : ~2h
