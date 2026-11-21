#include "filter.h"

static int32_t window[FILTER_WINDOW];
static size_t  flt_count;     /* nombre de valeurs valides présentes (<= FILTER_WINDOW) */
static size_t  flt_head;      /* prochain index d'écriture */

void filter_reset(void)
{
    flt_count = 0u;
    flt_head = 0u;
}

size_t filter_count(void) { return flt_count; }

int32_t filter_push(int32_t centi, bool valid)
{
    int32_t sum = 0;
    size_t i;
    
    if (valid) {
        window[flt_head] = centi;
        flt_head = (flt_head + 1u) % FILTER_WINDOW;
        if (flt_count < FILTER_WINDOW) {
            flt_count++;
        }
    }
    
    if (flt_count == 0u) {
        return 0;
    }
    
    /* Somme des 'flt_count' éléments valides du filtre en partant du plus ancien */
    for (i = 0u; i < flt_count; i++) {
        /* Calcul de l'index en partant du début de la fenêtre glissante */
        size_t idx = (flt_head + FILTER_WINDOW - flt_count + i) % FILTER_WINDOW;
        sum += window[idx];
    }
    
    return sum / (int32_t)flt_count;
}