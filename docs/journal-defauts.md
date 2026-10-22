# Journal des défauts révélés — TP 3

| ID | Étape | Exigence | Test révélateur | Symptôme observé (message Unity/pytest) | Hypothèse de cause | Technique qui l'a révélé |
|---|---|---|---|---|---|---|
| DEF-01 | Étape 1 | EF-05 | test_EF05_range_check_bounds | Expected TRUE Was FALSE (ligne 33) | Comparaison stricte < au lieu de <= sur la borne supérieure à 12500 | BVA (Analyse des Valeurs Limites) |
