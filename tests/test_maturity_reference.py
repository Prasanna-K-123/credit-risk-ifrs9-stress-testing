"""Independent mathematical and refusal tests (no original studies run)."""
import math
import numpy as np
import pytest
from src.maturity_reference import maturity_respecting_ecl_reference as ecl


def call(p=.08, ead=100.0, lgd=.45, stage=2, months=36, r=.05):
    return ecl(p, ead, lgd, stage, months, r)


@pytest.mark.parametrize('p', [0.00000001, .005, .08, .37, .95])
@pytest.mark.parametrize('months', [1, 3, 11, 12, 13, 18, 24, 36, 120])
def test_undiscounted_closed_form_against_survival_probability(p, months):
    loss = call(p=p, months=months, r=0)
    expected = 100 * .45 * (1 - (1-p)**(months/12))
    assert loss == pytest.approx(expected, rel=2e-9, abs=1e-12)


def test_stage1_truncates_at_12_months_and_short_maturities_do_not_round_up():
    assert call(stage=1, months=1, r=0) < call(stage=1, months=12, r=0)
    assert call(stage=1, months=12, r=0) == pytest.approx(call(stage=1, months=36, r=0))
    assert call(stage=1, months=3, r=0) == pytest.approx(100*.45*(1-(1-.08)**.25))


def test_stage2_accounts_for_fractional_extra_months_and_stage2_exceeds_stage1():
    assert call(stage=2, months=13) > call(stage=2, months=12)
    assert call(stage=2, months=24) > call(stage=2, months=13)
    assert call(stage=2, months=36) > call(stage=1, months=36)


def test_discount_rate_reduces_loss_and_integral_matches_quadrature():
    p, r, horizon = .13, .07, 31/12
    h = -math.log1p(-p)
    grid = np.linspace(0, horizon, 20001)
    density_discounted = h*np.exp(-h*grid)/(1+r)**grid
    expected = 100*.45*float(np.trapezoid(density_discounted, grid))
    assert call(p=p, months=31, r=r) == pytest.approx(expected, rel=1e-8)
    assert call(p=p, months=31, r=r) < call(p=p, months=31, r=0)


@pytest.mark.parametrize('p,expected', [(0,0), (1,45)])
def test_endpoint_default_probabilities(p,expected):
    assert call(p=p) == expected


@pytest.mark.parametrize('overrides,match', [
    ({'p':-.1},'pd_12m'), ({'p':1.1},'pd_12m'),
    ({'ead':-1},'ead'), ({'lgd':-0.01},'lgd'), ({'lgd':1.01},'lgd'),
    ({'months':0},'positive integer'), ({'months':-1},'positive integer'),
    ({'months':1.5},'positive integer'), ({'months':True},'positive integer'),
    ({'stage':3},'Only stages'), ({'stage':0},'Only stages'),
    ({'r':-.01},'nonnegative'), ({'r':float('inf')},'finite'),
    ({'p':float('nan')},'finite'), ({'ead':float('nan')},'finite'),
    ({'p':'0.1'},'finite'), ({'r':float('-inf')},'finite'),
])
def test_rejects_invalid_and_unsupported_inputs(overrides,match):
    with pytest.raises(ValueError, match=match):
        call(**overrides)


def test_no_negative_ecl_and_no_exceedance_for_positive_discounting():
    for p in [0, .0001, .3, .9, 1]:
        for r in [0, .05, 1.0]:
            for m in [1,12,120]:
                value = call(p=p, r=r, months=m)
                assert 0 <= value <= 45 + 1e-12


def test_stage1_caps_an_extreme_integer_term_before_float_conversion():
    assert call(stage=1, months=10**1000) == call(stage=1, months=12)


@pytest.mark.parametrize('p,ead', [(.08, 100), (0, 100), (.08, 0)])
def test_unrepresentable_stage2_term_is_refused_even_at_zero_loss(p, ead):
    with pytest.raises(ValueError, match='finite horizon'):
        call(p=p, ead=ead, months=10**1000)


@pytest.mark.parametrize('key', ['p', 'ead', 'lgd', 'r'])
def test_unrepresentable_scalar_is_refused_as_a_domain_error(key):
    with pytest.raises(ValueError, match='finite real'):
        call(**{key: 10**1000})


@pytest.mark.parametrize('key', ['p', 'ead', 'lgd', 'r'])
def test_boolean_scalars_are_not_probabilities_or_amounts(key):
    with pytest.raises(ValueError, match='finite real'):
        call(**{key: True})


def test_near_zero_probability_is_positive_and_stably_matches_first_order_loss():
    value = call(p=1e-16, months=12, r=0)
    assert value > 0
    assert value == pytest.approx(45e-16, rel=1e-12, abs=0)
