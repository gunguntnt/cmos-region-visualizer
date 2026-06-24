import pytest

from cmos_region_visualizer.model import Region, evaluate_region


def test_nmos_cutoff() -> None:
    result = evaluate_region("NMOS", vg=0.5, vd=3.3, vs=0.0)
    assert result.region is Region.CUTOFF
    assert result.key_voltages["V_GS"] == pytest.approx(0.5)


def test_nmos_linear() -> None:
    result = evaluate_region("NMOS", vg=2.0, vd=0.5, vs=0.0)
    assert result.region is Region.LINEAR
    assert result.key_voltages["V_OV"] == pytest.approx(1.3)
    assert result.current == pytest.approx(0.525)


def test_nmos_saturation() -> None:
    result = evaluate_region("NMOS", vg=2.0, vd=3.3, vs=0.0)
    assert result.region is Region.SATURATION
    assert result.current == pytest.approx(0.845)


def test_nmos_non_standard_bias() -> None:
    result = evaluate_region("NMOS", vg=2.0, vd=-0.2, vs=0.0)
    assert result.region is Region.NON_STANDARD


def test_nmos_boundary_goes_to_saturation() -> None:
    result = evaluate_region("NMOS", vg=2.0, vd=1.3, vs=0.0)
    assert result.region is Region.SATURATION
