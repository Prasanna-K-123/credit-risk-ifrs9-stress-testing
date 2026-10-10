import numpy as np
import pytest
from benchmark_card_clients import cost,fit_calibration,logits,partition,select_threshold


def test_duplicate_inputs_stay_together_across_all_partitions():
    groups=np.repeat(np.arange(100),3)
    p=partition(groups)
    assert len(set(np.concatenate(list(p.values()))))==300
    seen={}
    for name,idx in p.items():
        for g in groups[idx]:
            assert g not in seen or seen[g]==name
            seen[g]=name


def test_prespecified_cost_equals_direct_confusion_accounting():
    assert cost([1,0,1,0],[.1,.9,.9,.1],.5).tolist()==[5,1,0,0]
    t,total=select_threshold([1,0,1,0],[.1,.9,.9,.1])
    assert total==min(int(cost([1,0,1,0],[.1,.9,.9,.1],x/100).sum()) for x in range(1,100))
    assert total==int(cost([1,0,1,0],[.1,.9,.9,.1],t).sum())


def test_log_odds_are_finite_at_probability_edges():
    assert np.isfinite(logits([0,1,.5])).all()
    with pytest.raises(ValueError):logits([np.nan])


def test_calibration_refuses_single_class_and_uses_only_supplied_calibration():
    with pytest.raises(ValueError):fit_calibration([.1,.2],[0,0])
    model=fit_calibration([.1,.2,.8,.9],[0,0,1,1])
    assert model.predict_proba(logits([.1,.9]))[0,1]<model.predict_proba(logits([.1,.9]))[1,1]
