from matplotlib.figure import Figure
import pytest

from cmos_region_visualizer.model import evaluate_region
from cmos_region_visualizer.schematic import drain_saturation_boundary, draw_bias_schematic


def _assert_schematic_draws(tmp_path, device: str, vg: float, vd: float, vs: float) -> None:
    result = evaluate_region(device, vg=vg, vd=vd, vs=vs)
    figure = Figure(figsize=(5, 3), dpi=100)
    ax = figure.add_subplot(111)

    draw_bias_schematic(ax, result.device, result.vg, result.vd, result.vs, result)
    output_path = tmp_path / f"{device.lower()}_{result.region.value.replace(' ', '_').replace('/', '_')}.png"
    figure.savefig(output_path)

    assert len(figure.axes) == 1
    assert len(ax.lines) > 0
    assert len(ax.texts) > 0
    text_content = "\n".join(text.get_text() for text in ax.texts)
    assert "Device:" not in text_content
    assert "Boundary:" not in text_content
    assert "Since " not in text_content
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_nmos_cutoff_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "NMOS", vg=0.5, vd=3.3, vs=0.0)


def test_nmos_linear_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "NMOS", vg=2.0, vd=0.5, vs=0.0)


def test_nmos_saturation_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "NMOS", vg=2.0, vd=3.3, vs=0.0)


def test_pmos_cutoff_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "PMOS", vg=3.0, vd=0.0, vs=3.3)


def test_pmos_linear_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "PMOS", vg=1.0, vd=2.8, vs=3.3)


def test_pmos_saturation_schematic_draws(tmp_path) -> None:
    _assert_schematic_draws(tmp_path, "PMOS", vg=1.0, vd=0.0, vs=3.3)


def test_drain_saturation_boundary_direction() -> None:
    assert drain_saturation_boundary("NMOS", vg=2.0, vth_abs=0.7) == pytest.approx(1.3)
    assert drain_saturation_boundary("PMOS", vg=1.0, vth_abs=0.7) == pytest.approx(1.7)
