# CMOS Region Visualizer

中文名称：CMOS 工作区判定与可视化演示系统

CMOS Region Visualizer is a teaching desktop application for judging and visualizing the operating region of long-channel enhancement-mode NMOS and PMOS transistors. It is designed for short-term integrated-circuit practice courses where students need something more relevant than a generic calculator, but still simple enough to read, modify, test, and package as a Windows executable.

本项目适合用于集成电路专业短学期教学演示：学生可以输入三端电压，观察截止区、线性区/三极管区、饱和区和非标准偏置的判定过程，并在 I-V 曲线上看到当前工作点。

## Teaching Model Assumptions

This application uses a long-channel enhancement-mode MOSFET model. The body terminal is assumed to be tied to the source. Channel-length modulation, body effect, subthreshold conduction, velocity saturation, and short-channel effects are neglected.

This is a teaching simplified model, not an advanced-process BSIM model. It is intended for conceptual visualization, not silicon-accurate circuit simulation.

Default threshold voltage:

$$
|V_{TH}| = 0.7\,\mathrm{V}
$$

The normalized conduction coefficient defaults to:

$$
K = 1
$$

## NMOS Region Rules

For NMOS:

$$
V_{GS}=V_G-V_S
$$

$$
V_{DS}=V_D-V_S
$$

$$
V_{OV}=V_{GS}-V_{TH},\quad V_{TH}=+|V_{TH}|
$$

If $V_{DS}<0$, the app reports **Non-standard Bias**, because the drain/source definition is inconsistent with the conventional NMOS teaching direction.

Cutoff:

$$
V_{GS}<V_{TH}
$$

Linear / Triode:

$$
V_{GS}\ge V_{TH},\quad 0\le V_{DS}<V_{GS}-V_{TH}
$$

Saturation:

$$
V_{GS}\ge V_{TH},\quad V_{DS}\ge V_{GS}-V_{TH}
$$

The boundary case $V_{DS}=V_{OV}$ is assigned to saturation by using the $\ge$ condition.

The normalized current used for plotting is:

$$
I_D=K_n\left[(V_{GS}-V_{TH})V_{DS}-\frac{1}{2}V_{DS}^2\right]
$$

in the linear region, and:

$$
I_{D,sat}=\frac{1}{2}K_n(V_{GS}-V_{TH})^2
$$

in saturation.

## PMOS Region Rules

For PMOS, the app uses first-quadrant teaching variables instead of forcing negative $V_{GS}$ and $V_{DS}$:

$$
V_{SG}=V_S-V_G
$$

$$
V_{SD}=V_S-V_D
$$

$$
V_{OV,p}=V_{SG}-|V_{TH}|
$$

If $V_{SD}<0$, the app reports **Non-standard Bias**, because the drain/source definition is inconsistent with the conventional PMOS teaching direction.

Cutoff:

$$
V_{SG}<|V_{TH}|
$$

Linear / Triode:

$$
V_{SG}\ge |V_{TH}|,\quad 0\le V_{SD}<V_{SG}-|V_{TH}|
$$

Saturation:

$$
V_{SG}\ge |V_{TH}|,\quad V_{SD}\ge V_{SG}-|V_{TH}|
$$

The boundary case $V_{SD}=V_{OV,p}$ is assigned to saturation by using the $\ge$ condition.

The normalized current used for plotting is:

$$
I_{SD}=K_p\left[(V_{SG}-|V_{TH}|)V_{SD}-\frac{1}{2}V_{SD}^2\right]
$$

in the linear region, and:

$$
I_{SD,sat}=\frac{1}{2}K_p(V_{SG}-|V_{TH}|)^2
$$

in saturation.

## Dynamic Bias Schematic

The GUI includes a SPICE-like dynamic bias schematic panel. The MOSFET core symbol stays fixed, while the external G/D/S voltage nodes move vertically according to the current input voltages.

The node positions are normalized from the current voltage range:

$$
V_{\min}=\min(V_G,V_D,V_S,0)
$$

$$
V_{\max}=\max(V_G,V_D,V_S,|V_{TH}|,1)
$$

Each terminal voltage is mapped into the drawing window:

$$
y_x=y_{\min}+\frac{V_x-V_{\min}}{V_{\max}-V_{\min}}(y_{\max}-y_{\min})
$$

The fixed G/D/S ports are connected to the dynamic voltage nodes through leads. This keeps the MOSFET symbol stable and makes voltage relationships easy to see during teaching.

The channel appearance changes with the operating region:

- **Cutoff**: the channel is drawn as a faint dashed line.
- **Linear / Triode**: the channel is drawn as a full continuous channel.
- **Saturation**: the channel is narrowed near the drain-side pinch-off end.
- **Non-standard Bias**: the channel is shown with a warning style and the result text explains the drain/source direction issue.

For PMOS, the schematic still displays the real terminal voltages $V_G$, $V_D$, and $V_S$, while the result block uses the teaching variables $V_{SG}$, $V_{SD}$, and $V_{OV,p}$.

This panel is a teaching schematic. It is not an exact layout drawing and it is not a SPICE simulation result.

## Drain Boundary Line in Dynamic Bias Schematic

The dynamic bias schematic also shows a dashed drain boundary line. This line helps students compare the absolute drain potential with the critical drain potential for the linear/saturation boundary.

For NMOS, after the device is on:

$$
V_{DS}=V_{GS}-V_{TH}
$$

Substituting $V_{DS}=V_D-V_S$ and $V_{GS}=V_G-V_S$ gives:

$$
V_D=V_G-V_{TH}
$$

Therefore, the NMOS drain boundary is:

$$
V_{D,sat}=V_G-V_{TH}
$$

If the NMOS is on, $V_D<V_{D,sat}$ indicates the linear/triode region, while $V_D\ge V_{D,sat}$ indicates saturation.

For PMOS, the first-quadrant teaching variables are:

$$
V_{SD}=V_{SG}-|V_{TH}|
$$

Substituting $V_{SD}=V_S-V_D$ and $V_{SG}=V_S-V_G$ gives:

$$
V_D=V_G+|V_{TH}|
$$

Therefore, the PMOS drain boundary is:

$$
V_{D,sat}=V_G+|V_{TH}|
$$

If the PMOS is on, $V_D>V_{D,sat}$ indicates the linear/triode region, while $V_D\le V_{D,sat}$ indicates saturation. This direction is opposite to NMOS.

The boundary line is included in the schematic's voltage scaling range, so it remains visible even when input voltages are negative or exceed the usual 3.3 V teaching range. In cutoff and non-standard bias cases, the line is still shown as a reference, but the text explains why the transistor is off or why the drain/source direction is non-standard.

This visualization is a teaching aid for absolute potential comparison. It is not a SPICE waveform, a silicon-accurate model, or a layout-level drawing.

## Repository Structure

```text
CMOS_Region_Visualizer/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   └── cmos_region_visualizer/
│       ├── __init__.py
│       ├── app.py
│       ├── main.py
│       ├── model.py
│       ├── plotter.py
│       └── resources/
├── tests/
│   ├── test_model_nmos.py
│   └── test_model_pmos.py
└── scripts/
    ├── run_app.bat
    └── build_exe.bat
```

## Installation

Create and activate a virtual environment if desired, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
set PYTHONPATH=%CD%\src
python -m cmos_region_visualizer.main
```

On Windows, you can also run:

```bat
scripts\run_app.bat
```

## Test

From the project root:

```bash
python -m pytest
```

The tests cover NMOS and PMOS cutoff, linear/triode, saturation, non-standard bias, and boundary assignment to saturation.

## Build Windows EXE

Install dependencies and run PyInstaller:

```bat
scripts\build_exe.bat
```

The script runs:

```bat
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --windowed --name CMOSRegionVisualizer --paths src src\cmos_region_visualizer\main.py
```

After packaging, check the generated `dist` directory. Generated build artifacts are intentionally ignored by Git.

## Example Inputs and Outputs

NMOS saturation example:

```text
Device: NMOS
V_G = 2.0 V
V_D = 3.3 V
V_S = 0 V
|V_TH| = 0.7 V

V_GS = 2.000 V
V_DS = 3.300 V
V_OV = 1.300 V

Region: Saturation

Reason:
Because V_GS >= V_TH and V_DS >= V_GS - V_TH, the transistor operates in the saturation region.
```

PMOS linear example:

```text
Device: PMOS
V_S = 3.3 V
V_G = 1.0 V
V_D = 2.8 V
|V_TH| = 0.7 V

V_SG = 2.300 V
V_SD = 0.500 V
V_OV,p = 1.600 V

Region: Linear / Triode
```

## Extension Ideas

- Add a sweep mode for multiple gate voltages.
- Add a small quiz mode for students to predict the region before calculation.
- Add export of the numeric result as CSV or Markdown.
- Add optional channel-length modulation as an advanced teaching toggle.
- Add SPICE comparison later, while keeping this teaching model separate.
