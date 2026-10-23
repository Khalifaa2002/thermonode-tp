# Analyse MC/DC — Décision de défaut (EF-05)

La décision de détection de défaut est régie par l'expression booléenne :
$$D = A \lor B \lor C$$

Où :
* **A** : `centi < -4000` (Température inférieure au seuil bas)
* **B** : `centi > 12500` (Température supérieure au seuil haut)
* **C** : `frozen_count >= 5` (Capteur figé après 5 échantillons identiques)

## Tableau MC/DC

| Test | A | B | C | D | Indique l'influence de |
| :--- | :-: | :-: | :-: | :-: | :--- |
| **T1** | F | F | F | F | *(Référence)* |
| **T2** | **V** | F | F | **V** | **A** (en comparant avec T1) |
| **T3** | F | **V** | F | **V** | **B** (en comparant avec T1) |
| **T4** | F | F | **V** | **V** | **C** (en comparant avec T1) |

## Combinaisons irréalisables et vecteurs de test
* **Combinaison irréalisable :** $A$ et $B$ ne peuvent pas être vrais simultanément (`V` et `V`), car une même valeur de température ne peut pas être à la fois inférieure à $-4000$ et supérieure à $12500$.
* **Vecteurs concrets choisis :**
  * **T2** (`A` vrai) : Valeur de température de `-4001` (ADC `124`).
  * **T3** (`B` vrai) : Valeur de température de `12507` (ADC `2173`).
  * **T4** (`C` vrai) : Série de cinq échantillons identiques (ADC `931`).