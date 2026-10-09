import numpy as np
import pytest
from audit_reference import prior_adjust


def test_identity_inverse_and_order_preserved():
    p=np.array([.01,.2,.5,.9])
    np.testing.assert_allclose(prior_adjust(p,.3,.3),p)
    shifted=prior_adjust(p,.3,.05)
    assert np.all(np.diff(shifted)>0)
    np.testing.assert_allclose(prior_adjust(shifted,.05,.3),p)
    assert np.all(shifted<p)


def test_constant_prior_maps_to_target_prior():
    assert prior_adjust([.3],.3,.07)[0]==pytest.approx(.07)


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError): prior_adjust([.5],0,.2)
    with pytest.raises(ValueError): prior_adjust([float('nan')],.3,.2)
