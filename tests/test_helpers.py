import pandas as pd
import pytest

import utils.helpers as helpers


def test_compute_nstrtini():
    forcing_start_date = pd.Timestamp("2014-07-01")
    start_date = pd.Timestamp("2014-06-30")
    pytest.raises(ValueError, helpers.compute_nstrtini, start_date, forcing_start_date)
    start_date = pd.Timestamp("2014-07-01 03:00")
    pytest.raises(ValueError, helpers.compute_nstrtini, start_date, forcing_start_date)
    start_date = pd.Timestamp("2014-07-02")
    assert helpers.compute_nstrtini(start_date, forcing_start_date) == 5
    assert helpers.compute_nstrtini(start_date, forcing_start_date, 3) == 9
