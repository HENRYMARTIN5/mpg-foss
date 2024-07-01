from . import weight_over_time
from . import frf_grid
from .libplotter import * # incase it's needed externally

ALL_PLOTTERS = {
    "Weight Over Time": weight_over_time.WeightOverTimePlotter,
    "Grid of FRFs": frf_grid.FRFGridPlotter
}