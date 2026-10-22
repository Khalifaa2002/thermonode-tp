#include "filter.h"

static int32_t window[FILTER_WINDOW];
static size_t  count;     /* nombre de valeurs valides présentes (<= FILTER_WINDOW) */
static size_t  head;      /* prochain index d'écriture */

void filter_reset(void)
{
    count = 0u;
    head = 0u;
}

size_t filter_count(void) { return count; }

int32_t filter_push(int32_t centi, bool valid)
{
    int32_t sum = 0;
    size_t i;
    
    if (valid) {
        window[head] = centi;
        head = (head + 1u) % FILTER_WINDOW;
        if (count < FILTER_WINDOW) {
            count++;
        }
    }
    
    if (count == 0u) {
        return 0;
    }
    
    /* Somme des 'count' éléments valides du filtre en partant du plus ancien */
    for (i = 0u; i < count; i++) {
        /* Calcul de l'index en partant du début de la fenêtre glissante */
        size_t idx = (head + FILTER_WINDOW - count + i) % FILTER_WINDOW;
        sum += window[idx];
    }
    
    return sum / (int32_t)count;
}