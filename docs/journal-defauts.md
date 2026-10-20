# Journal des défauts révélés - TP 3
| ID Étape | Exigence | Test révélateur | Symptôme observé (message Unity/pytest) | Hypothèse de cause | Technique qui l'a révélé |
| --- | --- | --- | --- | --- | --- |
| DEF-01 | EF-05 | test_EF05_range_check_bounds | FAIL: Expected TRUE Was FALSE | Borne supérieure restrictive dans range_check (< 12500 au lieu de <=) | BVA (Valeurs Limites) |
