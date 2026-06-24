"""SPICE-like dynamic bias schematic drawing helpers."""

from __future__ import annotations

from matplotlib.axes import Axes

from .model import DeviceType, Region, RegionResult


def map_voltage_to_y(
    voltage: float,
    v_min: float,
    v_max: float,
    y_min: float = 0.12,
    y_max: float = 0.88,
) -> float:
    """Map an electrical voltage to a schematic y-coordinate."""

    if abs(v_max - v_min) < 1e-12:
        v_max = v_min + 1.0
    return y_min + (voltage - v_min) / (v_max - v_min) * (y_max - y_min)


def draw_bias_schematic(
    ax: Axes,
    device_type: str | DeviceType,
    vg: float,
    vd: float,
    vs: float,
    result: RegionResult,
) -> None:
    """Draw a SPICE-like MOSFET bias schematic with dynamic external nodes."""

    device = DeviceType(device_type)
    ax.clear()
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    vd_sat_boundary = drain_saturation_boundary(device, vg, result.vth_abs)
    v_min = min(vg, vd, vs, vd_sat_boundary, 0.0)
    v_max = max(vg, vd, vs, vd_sat_boundary, result.vth_abs, 1.0)
    if abs(v_max - v_min) < 1e-12:
        v_max = v_min + 1.0

    node_y = {
        "G": map_voltage_to_y(vg, v_min, v_max),
        "D": map_voltage_to_y(vd, v_min, v_max),
        "S": map_voltage_to_y(vs, v_min, v_max),
    }
    port_y = {"G": 0.50, "D": 0.74 if device is DeviceType.NMOS else 0.24, "S": 0.24 if device is DeviceType.NMOS else 0.74}

    _draw_voltage_scale(ax, v_min, v_max)
    _draw_drain_boundary_line(ax, device, vd_sat_boundary, v_min, v_max)
    _draw_external_nodes(ax, node_y, {"G": vg, "D": vd, "S": vs})
    _draw_fixed_symbol(ax, device, port_y, result.region)
    _draw_leads(ax, node_y, port_y)
    _draw_region_label(ax, result.region)


def drain_saturation_boundary(device_type: str | DeviceType, vg: float, vth_abs: float) -> float:
    """Return the absolute drain potential at the linear/saturation boundary."""

    device = DeviceType(device_type)
    if device is DeviceType.NMOS:
        return vg - vth_abs
    return vg + vth_abs


def _draw_voltage_scale(ax: Axes, v_min: float, v_max: float) -> None:
    ax.plot([0.06, 0.06], [0.12, 0.88], color="#999999", linewidth=1.0)
    for voltage, label in ((v_min, f"{v_min:.2f} V"), (v_max, f"{v_max:.2f} V")):
        y = map_voltage_to_y(voltage, v_min, v_max)
        ax.plot([0.045, 0.075], [y, y], color="#999999", linewidth=1.0)
        ax.text(0.025, y, label, ha="right", va="center", fontsize=7, color="#666666")


def _draw_drain_boundary_line(
    ax: Axes,
    device: DeviceType,
    vd_sat_boundary: float,
    v_min: float,
    v_max: float,
) -> None:
    y = map_voltage_to_y(vd_sat_boundary, v_min, v_max)
    ax.hlines(y, 0.10, 0.94, color="#8a5a00", linewidth=1.4, linestyle="--", alpha=0.9)
    if device is DeviceType.NMOS:
        label = f"V_D,sat = V_G - V_TH = {vd_sat_boundary:.2f} V"
    else:
        label = f"V_D,sat = V_G + |V_TH| = {vd_sat_boundary:.2f} V"
    ax.text(
        0.94,
        y + 0.018,
        label,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#8a5a00",
    )


def _draw_external_nodes(ax: Axes, node_y: dict[str, float], voltages: dict[str, float]) -> None:
    x_positions = {"G": 0.20, "D": 0.84, "S": 0.84}
    colors = {"G": "#6f42c1", "D": "#d62728", "S": "#1f77b4"}
    for terminal in ("G", "D", "S"):
        x = x_positions[terminal]
        y = node_y[terminal]
        ax.scatter([x], [y], s=55, color=colors[terminal], zorder=5)
        label_side = "right" if terminal == "G" else "left"
        dx = -0.035 if terminal == "G" else 0.035
        ha = "right" if label_side == "right" else "left"
        ax.text(x + dx, y, f"{terminal}: {voltages[terminal]:.2f} V", ha=ha, va="center", fontsize=8)


def _draw_fixed_symbol(ax: Axes, device: DeviceType, port_y: dict[str, float], region: Region) -> None:
    gate_x = 0.42
    channel_x = 0.56
    right_x = 0.70
    d_y = port_y["D"]
    s_y = port_y["S"]
    g_y = port_y["G"]

    ax.plot([gate_x, gate_x], [0.28, 0.72], color="#222222", linewidth=2.2)
    if device is DeviceType.PMOS:
        circle = ax.add_patch(plt_circle((gate_x - 0.035, g_y), 0.022, fill=False, edgecolor="#222222", linewidth=1.7))
        circle.set_zorder(4)
        ax.plot([0.34, gate_x - 0.057], [g_y, g_y], color="#222222", linewidth=1.8)
    else:
        ax.plot([0.34, gate_x], [g_y, g_y], color="#222222", linewidth=1.8)

    _draw_channel(ax, channel_x, min(d_y, s_y), max(d_y, s_y), region, device)
    ax.plot([channel_x, right_x], [d_y, d_y], color="#222222", linewidth=1.8)
    ax.plot([channel_x, right_x], [s_y, s_y], color="#222222", linewidth=1.8)
    ax.plot([right_x, right_x], [d_y, s_y], color="#222222", linewidth=1.2, alpha=0.8)

    ax.text(0.33, g_y + 0.045, "G port", ha="center", va="bottom", fontsize=7, color="#555555")
    ax.text(right_x + 0.01, d_y, "D port", ha="left", va="center", fontsize=7, color="#555555")
    ax.text(right_x + 0.01, s_y, "S port", ha="left", va="center", fontsize=7, color="#555555")
    ax.text(0.53, 0.93, f"{device.value} fixed symbol", ha="center", va="center", fontsize=10, weight="bold")


def _draw_channel(ax: Axes, x: float, y_low: float, y_high: float, region: Region, device: DeviceType) -> None:
    if region is Region.CUTOFF:
        ax.plot([x, x], [y_low, y_high], color="#777777", linewidth=1.4, linestyle="--", alpha=0.45)
        return
    if region is Region.NON_STANDARD:
        ax.plot([x, x], [y_low, y_high], color="#b00020", linewidth=1.4, linestyle=":", alpha=0.8)
        return
    if region is Region.LINEAR:
        ax.plot([x, x], [y_low, y_high], color="#198754", linewidth=5.0, solid_capstyle="round")
        return

    pinch_y = y_high if device is DeviceType.NMOS else y_low
    body_y = y_low if device is DeviceType.NMOS else y_high
    ax.plot([x, x], [body_y, (body_y + pinch_y) * 0.58], color="#fd7e14", linewidth=5.0, solid_capstyle="round")
    ax.plot([x, x], [(body_y + pinch_y) * 0.58, pinch_y], color="#fd7e14", linewidth=2.0, solid_capstyle="round")


def _draw_leads(ax: Axes, node_y: dict[str, float], port_y: dict[str, float]) -> None:
    ports = {"G": (0.34, port_y["G"]), "D": (0.70, port_y["D"]), "S": (0.70, port_y["S"])}
    nodes = {"G": (0.20, node_y["G"]), "D": (0.84, node_y["D"]), "S": (0.84, node_y["S"])}
    colors = {"G": "#6f42c1", "D": "#d62728", "S": "#1f77b4"}
    for terminal in ("G", "D", "S"):
        node_x, node_y_value = nodes[terminal]
        port_x, port_y_value = ports[terminal]
        mid_x = (node_x + port_x) * 0.5
        ax.plot(
            [node_x, mid_x, mid_x, port_x],
            [node_y_value, node_y_value, port_y_value, port_y_value],
            color=colors[terminal],
            linewidth=1.5,
            alpha=0.95,
        )


def _draw_region_label(ax: Axes, region: Region) -> None:
    label = {
        Region.CUTOFF: "CUT OFF",
        Region.LINEAR: "LINEAR / TRIODE",
        Region.SATURATION: "SATURATION",
        Region.NON_STANDARD: "NON-STANDARD BIAS",
    }[region]
    color = {
        Region.CUTOFF: "#555555",
        Region.LINEAR: "#198754",
        Region.SATURATION: "#fd7e14",
        Region.NON_STANDARD: "#b00020",
    }[region]
    ax.text(
        0.50,
        0.045,
        label,
        ha="center",
        va="bottom",
        fontsize=13,
        weight="bold",
        color=color,
    )


def plt_circle(center: tuple[float, float], radius: float, **kwargs):
    """Create a Matplotlib circle without importing pyplot."""

    from matplotlib.patches import Circle

    return Circle(center, radius, **kwargs)
