from __future__ import unicode_literals
from parglare import get_collector

action = get_collector()


@action('number')
def NUMERIC(_, value):
    return float(value)
