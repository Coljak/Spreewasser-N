from django.db.models import Min, Max
import math

def get_bounds(qs, field):
    agg = qs.aggregate(min_val=Min(field), max_val=Max(field))
    if agg['min_val'] is None or agg['max_val'] is None:
        return [0, 1]
    return [math.floor(agg['min_val']), math.ceil(agg['max_val'])]