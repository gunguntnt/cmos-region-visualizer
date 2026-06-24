"""Long-channel MOSFET operating-region judgement logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DeviceType(str, Enum):
    """Supported MOSFET device types."""

    NMOS = "NMOS"
    PMOS = "PMOS"


class Region(str, Enum):
    """Teaching operating regions."""

    CUTOFF = "Cutoff"
    LINEAR = "Linear / Triode"
    SATURATION = "Saturation"
    NON_STANDARD = "Non-standard Bias"


@dataclass(frozen=True)
class RegionResult:
    """Result returned by the MOSFET region evaluator."""

    device: DeviceType
    region: Region
    vg: float
    vd: float
    vs: float
    vth_abs: float
    k: float
    control_voltage: float
    output_voltage: float
    overdrive: float
    current: float
    boundary_voltage: float
    key_voltages: dict[str, float]
    inequalities: list[str]
    reason: str
    note: str


def validate_inputs(vth_abs: float, k: float) -> None:
    """Validate positive model parameters."""

    if vth_abs <= 0:
        raise ValueError("|V_TH| must be greater than 0.")
    if k <= 0:
        raise ValueError("K must be greater than 0.")


def evaluate_region(
    device: str | DeviceType,
    vg: float,
    vd: float,
    vs: float,
    vth_abs: float = 0.7,
    k: float = 1.0,
) -> RegionResult:
    """Evaluate the operating region using a teaching long-channel model."""

    validate_inputs(vth_abs, k)
    device_type = DeviceType(device)
    if device_type is DeviceType.NMOS:
        return _evaluate_nmos(vg, vd, vs, vth_abs, k)
    return _evaluate_pmos(vg, vd, vs, vth_abs, k)


def _region_current(output_voltage: float, overdrive: float, k: float, region: Region) -> float:
    if region is Region.CUTOFF or region is Region.NON_STANDARD or overdrive <= 0:
        return 0.0
    if region is Region.LINEAR:
        return k * (overdrive * output_voltage - 0.5 * output_voltage**2)
    return 0.5 * k * overdrive**2


def _evaluate_nmos(vg: float, vd: float, vs: float, vth_abs: float, k: float) -> RegionResult:
    vgs = vg - vs
    vds = vd - vs
    vov = vgs - vth_abs
    key_voltages = {"V_GS": vgs, "V_DS": vds, "V_OV": vov, "V_TH": vth_abs}

    if vds < 0:
        region = Region.NON_STANDARD
        inequalities = ["V_DS < 0"]
        reason = (
            "Because V_DS < 0, the drain/source definition is inconsistent with "
            "the conventional NMOS teaching direction."
        )
    elif vgs < vth_abs:
        region = Region.CUTOFF
        inequalities = ["V_GS < V_TH"]
        reason = "Because V_GS < V_TH, the channel is not strongly inverted and I_D is approximated as 0."
    elif vds < vov:
        region = Region.LINEAR
        inequalities = ["V_GS >= V_TH", "0 <= V_DS < V_GS - V_TH"]
        reason = (
            "Because V_GS >= V_TH and 0 <= V_DS < V_GS - V_TH, the transistor "
            "operates in the linear/triode region."
        )
    else:
        region = Region.SATURATION
        inequalities = ["V_GS >= V_TH", "V_DS >= V_GS - V_TH"]
        reason = (
            "Because V_GS >= V_TH and V_DS >= V_GS - V_TH, the transistor operates "
            "in the saturation region. The boundary uses >= for saturation."
        )

    current = _region_current(vds, vov, k, region)
    return RegionResult(
        device=DeviceType.NMOS,
        region=region,
        vg=vg,
        vd=vd,
        vs=vs,
        vth_abs=vth_abs,
        k=k,
        control_voltage=vgs,
        output_voltage=vds,
        overdrive=vov,
        current=current,
        boundary_voltage=max(vov, 0.0),
        key_voltages=key_voltages,
        inequalities=inequalities,
        reason=reason,
        note="NMOS uses V_GS = V_G - V_S and V_DS = V_D - V_S.",
    )


def _evaluate_pmos(vg: float, vd: float, vs: float, vth_abs: float, k: float) -> RegionResult:
    vsg = vs - vg
    vsd = vs - vd
    vov = vsg - vth_abs
    key_voltages = {"V_SG": vsg, "V_SD": vsd, "V_OV,p": vov, "|V_TH|": vth_abs}

    if vsd < 0:
        region = Region.NON_STANDARD
        inequalities = ["V_SD < 0"]
        reason = (
            "Because V_SD < 0, the drain/source definition is inconsistent with "
            "the conventional PMOS teaching direction."
        )
    elif vsg < vth_abs:
        region = Region.CUTOFF
        inequalities = ["V_SG < |V_TH|"]
        reason = "Because V_SG < |V_TH|, the channel is not strongly inverted and I_SD is approximated as 0."
    elif vsd < vov:
        region = Region.LINEAR
        inequalities = ["V_SG >= |V_TH|", "0 <= V_SD < V_SG - |V_TH|"]
        reason = (
            "Because V_SG >= |V_TH| and 0 <= V_SD < V_SG - |V_TH|, the transistor "
            "operates in the linear/triode region."
        )
    else:
        region = Region.SATURATION
        inequalities = ["V_SG >= |V_TH|", "V_SD >= V_SG - |V_TH|"]
        reason = (
            "Because V_SG >= |V_TH| and V_SD >= V_SG - |V_TH|, the transistor operates "
            "in the saturation region. The boundary uses >= for saturation."
        )

    current = _region_current(vsd, vov, k, region)
    return RegionResult(
        device=DeviceType.PMOS,
        region=region,
        vg=vg,
        vd=vd,
        vs=vs,
        vth_abs=vth_abs,
        k=k,
        control_voltage=vsg,
        output_voltage=vsd,
        overdrive=vov,
        current=current,
        boundary_voltage=max(vov, 0.0),
        key_voltages=key_voltages,
        inequalities=inequalities,
        reason=reason,
        note="PMOS is plotted with first-quadrant variables V_SG and V_SD.",
    )
