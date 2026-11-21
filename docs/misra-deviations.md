# Dérogations MISRA C:2012 — ThermoNode

| ID | Règle | Fichier | Justification | Approbation |
|---|---|---|---|---|
| DEV-001 | 11.4 (conversion pointeur ↔ entier) | hal/hal_stm32.c (via STM32Cube) | Accès aux registres mappés en mémoire par la bibliothèque HAL du fabricant | Responsable qualité |
| DEV-002 | 21.6 (`<stdio.h>`) | src/frame.c, src/node.c | `snprintf` utilisé pour la sérialisation JSON avec contrôle de la longueur ; alternative (sérialisation manuelle) jugée plus risquée | Responsable qualité |
| DEV-003 | 21.6 (`<stdio.h>`) | hal/hal_sim.c | Code de simulation hôte, non embarqué | — |
| DEV-004 | 15.5 | src/convert.c, src/filter.c, src/frame.c, src/node.c, src/ringbuf.c, src/threshold.c | Les retours anticipés arrêtent le traitement dès qu’une condition de garde échoue. | À valider |
| DEV-005 | 18.4 | src/frame.c | Les opérations sur les pointeurs servent à calculer des positions et à copier des segments des trames JSON. | À valider |
| DEV-006 | 21.1, 21.10 | src/main.c, bloc TN_SIM | Le simulateur hôte utilise `_POSIX_C_SOURCE` et `<time.h>` pour `nanosleep`. Le bloc est compilé uniquement en simulation. Le constat 2.5 est un faux positif : la macro est utilisée par les en-têtes système pour rendre nanosleep disponible. | À valider |
| DEV-007 | 8.9 | src/fault.c (`last_raw`), src/filter.c (`window`) | Ces données persistantes sont regroupées avec l’état interne de leur module. | À valider |
