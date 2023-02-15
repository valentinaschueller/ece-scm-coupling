import pandas as pd

from create_perturbed_rstas_files import generate_rstas_name


def test_generate_rstas_name():
    start_date = pd.Timestamp("2014-07-01 06:00")
    source = "par"
    expected_name = "rstas_2014-07-01_06_par.nc"
    assert generate_rstas_name(start_date, source) == expected_name

    start_date = pd.Timestamp("2014-07-01 12:00")
    source = "era"
    expected_name = "rstas_2014-07-01_12_era.nc"
    assert generate_rstas_name(start_date, source) == expected_name
