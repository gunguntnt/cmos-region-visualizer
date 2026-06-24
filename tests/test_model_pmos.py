import pytest

from cmos_region_visualizer.model import Region, evaluate_region


def test_pmos_cutoff() -> None:
    result = evaluate_region("PMOS", vg=3.0, vd=0.0, vs=3.3)
    assert result.region is Region.CUTOFF
    assert result.key_voltages["V_SG"] == pytest.approx(0.3)


def test_pmos_linear() -> None:
    result = evaluate_region("PMOS", vg=1.0, vd=2.8, vs=3.3)
    assert result.region is Region.LINEAR
    assert result.key_voltages["V_OV,p"] == pytest.approx(1.6)
    assert result.current == pytest.approx(0.675)


def test_pmos_saturation() -> None:
    result = evaluate_region("PMOS", vg=1.0, vd=0.0, vs=3.3)
    assert result.region is Region.SATURATION
    assert result.current == pytest.approx(1.28)


def test_pmos_non_standard_bias() -> None:
    result = evaluate_region("PMOS", vg=1.0, vd=3.5, vs=3.3)
    assert result.region is Region.NON_STANDARD


def test_pmos_boundary_goes_to_saturation() -> None:
    result = evaluate_region("PMOS", vg=1.0, vd=1.7, vs=3.3)
    assert result.region is Region.SATURATION
