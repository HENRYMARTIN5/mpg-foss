from . import weight_over_time
from . import bigol_frf

ALL_PLOTTERS = {
    "Weight Over Time": weight_over_time.WeightOverTimePlotter,
    "Big Ol' FRF": bigol_frf.BigOlFRFPlotter
}