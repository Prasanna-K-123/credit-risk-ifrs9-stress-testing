import pytest

from src.ecl import assign_stage, compute_ead, lifetime_ecl


def test_ead_drawn_plus_ccf():
    assert compute_ead(100.0, 40.0, 0.5) == pytest.approx(120.0)


def test_stage3_default():
    assert assign_stage(0.02, default_flag=1) == 3


def test_sicr_ratio_stage2():
    assert assign_stage(0.08, origination_pd=0.03) == 2


def test_stage1_twelve_month_ecl():
    assert lifetime_ecl(0.10, 100.0, lgd=0.40, stage=1) == pytest.approx(4.0)


def test_stage2_exceeds_stage1_for_multiyear_exposure():
    ecl1 = lifetime_ecl(0.08, 100.0, lgd=0.40, stage=1, remaining_months=36)
    ecl2 = lifetime_ecl(0.08, 100.0, lgd=0.40, stage=2, remaining_months=36)
    assert ecl2 > ecl1
