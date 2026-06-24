"""Matplotlib plotting helpers for CMOS Region Visualizer."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .model import DeviceType, Region, RegionResult


def _axis_labels(result: RegionResult) -> tuple[str, str, str]:
    if result.device is DeviceType.NMOS:
        return "V_DS (V)", "I_D (normalized)", "NMOS I_D - V_DS"
    return "V_SD (V)", "I_SD (normalized)", "PMOS I_SD - V_SD"


def compute_curve(result: RegionResult, point_count: int = 400) -> tuple[np.ndarray, np.ndarray]:
    """Return the teaching I-V curve for the current gate/control voltage."""

    vov = max(result.overdrive, 0.0)
    point_x = max(result.output_voltage, 0.0)
    x_max = max(3.3, point_x * 1.2, vov * 1.6, 1.0)
    x = np.linspace(0.0, x_max, point_count)

    if result.region is Region.CUTOFF or vov <= 0:
        y = np.zeros_like(x)
        return x, y

    linear = result.k * (vov * x - 0.5 * x**2)
    saturation = np.full_like(x, 0.5 * result.k * vov**2)
    y = np.where(x < vov, linear, saturation)
    return x, np.maximum(y, 0.0)


def draw_region_plot(figure: Figure, result: RegionResult) -> None:
    """Draw the region curve and current operating point on a Matplotlib figure."""

    figure.clear()
    ax = figure.add_subplot(111)
    _draw_on_axes(ax, result)
    figure.tight_layout()


def save_region_plot(path: str | Path, result: RegionResult, dpi: int = 160) -> None:
    """Save the current region plot as a PNG image."""

    figure = Figure(figsize=(8, 5), dpi=dpi)
    draw_region_plot(figure, result)
    figure.savefig(path, dpi=dpi)


def _draw_on_axes(ax: Axes, result: RegionResult) -> None:
    x, y = compute_curve(result)
    x_label, y_label, title = _axis_labels(result)
    ax.plot(x, y, color="#1f77b4", linewidth=2.2, label="Teaching I-V curve")

    boundary = max(result.boundary_voltage, 0.0)
    y_top = max(float(np.max(y)) * 1.2, 0.2)
    point_x = result.output_voltage
    point_y = result.current

    if result.region is Region.NON_STANDARD:
        point_x = result.output_voltage
        point_y = 0.0
        ax.text(
            0.5,
            0.55,
            "Non-standard bias\nCheck drain/source direction",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color="#b00020",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "#fff0f0", "edgecolor": "#b00020"},
        )
    elif result.region is Region.CUTOFF:
        ax.text(
            0.5,
            0.55,
            "Cutoff: current approximated as 0",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color="#555555",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f6f6f6", "edgecolor": "#aaaaaa"},
        )

    if boundary > 0:
        ax.axvline(boundary, color="#d62728", linestyle="--", linewidth=1.7, label="Boundary V_OV")
        ax.text(boundary, y_top * 0.92, "Boundary", rotation=90, va="top", ha="right", color="#d62728")
        ax.axvspan(0, boundary, color="#2ca02c", alpha=0.08)
        ax.axvspan(boundary, max(float(x[-1]), boundary), color="#ff7f0e", alpha=0.08)
        ax.text(boundary * 0.45, y_top * 0.84, "Linear/Triode\nRegion", ha="center", color="#2b6b2b")
        ax.text((boundary + float(x[-1])) * 0.5, y_top * 0.84, "Saturation\nRegion", ha="center", color="#9a5700")

    ax.scatter([point_x], [point_y], s=70, color="#111111", zorder=5, label="Operating point")
    ax.annotate(
        f"OP: ({point_x:.3g} V, {point_y:.3g})",
        xy=(point_x, point_y),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#111111"},
        fontsize=9,
    )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim(left=min(0.0, point_x * 1.1), right=max(float(x[-1]), boundary * 1.1, 1.0))
    ax.set_ylim(bottom=min(0.0, point_y * 1.1), top=max(y_top, point_y * 1.2, 0.2))
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.8)
    ax.legend(loc="best")
