# CMOS 工作区判定与可视化演示系统

## 1. 项目简介

`CMOS Region Visualizer` 是一个用于 CMOS / MOSFET 工作区教学的交互式可视化 App。它面向 CMOS 与模拟集成电路课程，帮助学习者输入 MOSFET 的三端电压，判断 NMOS / PMOS 当前处于截止区、线性区/三极管区、饱和区或非标准偏置状态。

本项目不是普通电压计算器。它把公式判定、动态偏置示意图和 I-V 曲线放在同一个界面中，让学习者把三端电压、工作区边界和图形变化对应起来。

GitHub 地址：<https://github.com/gunguntnt/cmos-region-visualizer>

## 2. 教学目标

通过本项目，你可以理解：

- NMOS / PMOS 的开启条件；
- 截止区、线性区/三极管区、饱和区的判定；
- 三端电压与工作区之间的关系；
- I-V 曲线和当前工作点的含义；
- 教材图示与公式判定之间的对应关系；
- 非标准偏置为什么需要单独提示。

## 3. 模型假设

本项目使用长沟道增强型 MOSFET 教学模型，默认体端与源端相连。为了突出课堂中的基本工作区概念，模型忽略沟道长度调制、体效应、亚阈值导通、速度饱和和短沟道效应。

默认阈值电压为：

$$
|V_{TH}| = 0.7\,\mathrm{V}
$$

归一化导电系数默认取：

$$
K = 1
$$

本项目是教学演示工具，不是 SPICE 仿真器，也不是先进工艺的 BSIM 精确模型。

## 4. NMOS 工作区判定规则

对 NMOS，项目使用以下变量：

$$
V_{GS}=V_G-V_S
$$

$$
V_{DS}=V_D-V_S
$$

$$
V_{OV}=V_{GS}-V_{TH},\quad V_{TH}=+|V_{TH}|
$$

如果 $V_{DS}<0$，项目判定为非标准偏置，因为此时漏端与源端方向不符合课堂中常用的 NMOS 判定方向。

截止区：

$$
V_{GS}<V_{TH}
$$

线性区 / 三极管区：

$$
V_{GS}\ge V_{TH},\quad 0\le V_{DS}<V_{GS}-V_{TH}
$$

饱和区：

$$
V_{GS}\ge V_{TH},\quad V_{DS}\ge V_{GS}-V_{TH}
$$

边界点 $V_{DS}=V_{OV}$ 按饱和区处理。绘图时使用归一化电流表达式。线性区电流为：

$$
I_D=K_n\left[(V_{GS}-V_{TH})V_{DS}-\frac{1}{2}V_{DS}^2\right]
$$

饱和区电流为：

$$
I_{D,sat}=\frac{1}{2}K_n(V_{GS}-V_{TH})^2
$$

## 5. PMOS 工作区判定规则

对 PMOS，项目采用第一象限教学变量，避免在入门教学中强行使用负的 $V_{GS}$ 和 $V_{DS}$：

$$
V_{SG}=V_S-V_G
$$

$$
V_{SD}=V_S-V_D
$$

$$
V_{OV,p}=V_{SG}-|V_{TH}|
$$

如果 $V_{SD}<0$，项目判定为非标准偏置，因为此时漏端与源端方向不符合课堂中常用的 PMOS 判定方向。

截止区：

$$
V_{SG}<|V_{TH}|
$$

线性区 / 三极管区：

$$
V_{SG}\ge |V_{TH}|,\quad 0\le V_{SD}<V_{SG}-|V_{TH}|
$$

饱和区：

$$
V_{SG}\ge |V_{TH}|,\quad V_{SD}\ge V_{SG}-|V_{TH}|
$$

边界点 $V_{SD}=V_{OV,p}$ 按饱和区处理。绘图时使用归一化电流表达式。线性区电流为：

$$
I_{SD}=K_p\left[(V_{SG}-|V_{TH}|)V_{SD}-\frac{1}{2}V_{SD}^2\right]
$$

饱和区电流为：

$$
I_{SD,sat}=\frac{1}{2}K_p(V_{SG}-|V_{TH}|)^2
$$

## 6. 动态偏置示意图

界面包含一个类似教材图示的动态偏置示意图。MOSFET 核心符号保持稳定，外部 G/D/S 电压节点会根据当前输入电压上下移动。

节点位置根据当前电压范围归一化：

$$
V_{\min}=\min(V_G,V_D,V_S,0)
$$

$$
V_{\max}=\max(V_G,V_D,V_S,|V_{TH}|,1)
$$

每个端口电压被映射到绘图区：

$$
y_x=y_{\min}+\frac{V_x-V_{\min}}{V_{\max}-V_{\min}}(y_{\max}-y_{\min})
$$

通道显示会随工作区变化：截止区显示为较弱虚线，线性区/三极管区显示为连续通道，饱和区在靠近漏端一侧显示夹断效果，非标准偏置使用警示样式并解释源漏方向问题。

图中还会显示漏端边界线，用于比较当前漏端电位与线性 / 饱和边界。

## 7. I-V 曲线与工作点

I-V 曲线用于展示在给定栅压和阈值电压下，漏端电压变化时电流如何变化。当前输入对应的工作点会标在曲线上。

这条曲线帮助学习者理解线性区到饱和区的边界、当前工作点所在位置，以及公式判定和图形结果之间的关系。本项目中的 I-V 曲线基于简化长沟道模型，仅用于课堂概念演示。

## 8. 安装与运行

建议使用 Python 3.10 或以上版本。

安装依赖：

```bash
pip install -r requirements.txt
```

从项目根目录运行：

```bash
set PYTHONPATH=%CD%\src
python -m cmos_region_visualizer.main
```

Windows 下也可以运行项目自带脚本：

```bat
scripts\run_app.bat
```

## 9. 测试

从项目根目录运行：

```bash
python -m pytest
```

现有测试覆盖 NMOS 与 PMOS 的截止区、线性区/三极管区、饱和区、非标准偏置，以及边界点归入饱和区等情况。

## 10. 打包与发布

项目包含 Windows 打包脚本：

```bat
scripts\build_exe.bat
```

该脚本会安装依赖，并使用 PyInstaller 打包主程序。打包完成后，请检查 `dist` 目录中的输出文件。构建产物属于生成文件，通常不需要提交到 Git 仓库。

## 11. 项目结构

```text
CMOS_Region_Visualizer/
├── README.md
├── requirements.txt
├── pyproject.toml
├── CMOSRegionVisualizer.spec
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
│   ├── test_model_pmos.py
│   └── test_schematic.py
└── scripts/
    ├── run_app.bat
    └── build_exe.bat
```

主要文件说明：

| 文件 / 目录 | 作用 |
|---|---|
| `src/` | 存放主程序源码 |
| `src/cmos_region_visualizer/model.py` | MOSFET 工作区判定与教学模型逻辑 |
| `src/cmos_region_visualizer/app.py` | 图形界面主体 |
| `src/cmos_region_visualizer/plotter.py` | I-V 曲线与示意图绘制相关逻辑 |
| `tests/` | NMOS、PMOS 和示意图相关测试 |
| `scripts/run_app.bat` | Windows 运行脚本 |
| `scripts/build_exe.bat` | Windows 打包脚本 |
| `requirements.txt` | 运行、测试和打包所需依赖 |
| `pyproject.toml` | Python 项目配置 |
| `CMOSRegionVisualizer.spec` | PyInstaller 打包配置 |

## 12. 适用范围与局限

本项目适合用于 CMOS / MOSFET 工作区的课堂演示、短学期实践和入门教学。它强调概念清晰、图示直观和公式可检查。

它不适合替代 SPICE 电路仿真、BSIM 等先进工艺器件模型、真实芯片设计中的精确电流预测，也不适合做版图级或工艺级分析。

如果后续加入沟道长度调制、体效应或 SPICE 对比，应明确标注为进阶功能，并保持与当前教学简化模型的边界。
