"""PySide6 GUI for CMOS Region Visualizer."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .model import DeviceType, RegionResult, evaluate_region
from .plotter import draw_region_plot, save_region_plot
from .schematic import draw_bias_schematic


MODEL_NOTICE = (
    "This application uses a long-channel enhancement-mode MOSFET model. "
    "The body terminal is assumed to be tied to the source. Channel-length "
    "modulation, body effect, subthreshold conduction, velocity saturation, "
    "and short-channel effects are neglected. This is a teaching simplified "
    "model, not an advanced-process BSIM model."
)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CMOS Region Visualizer")
        self.resize(1240, 820)
        self.current_result: RegionResult | None = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QGridLayout(central)
        root.setColumnStretch(0, 1)
        root.setColumnStretch(1, 1)
        root.setRowStretch(0, 1)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._build_input_panel())
        left_layout.addWidget(self._build_output_panel(), 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self._build_plot_panel(), 1)
        right_layout.addWidget(self._build_schematic_panel(), 1)

        root.addWidget(left_panel, 0, 0)
        root.addWidget(right_panel, 0, 1)
        root.addWidget(self._build_model_notice_panel(), 2, 0, 1, 2)

        self.reset_inputs()

    def _build_input_panel(self) -> QGroupBox:
        group = QGroupBox("Input")
        layout = QVBoxLayout(group)
        form = QFormLayout()

        self.device_combo = QComboBox()
        self.device_combo.addItems([DeviceType.NMOS.value, DeviceType.PMOS.value])
        self.vg_edit = QLineEdit()
        self.vd_edit = QLineEdit()
        self.vs_edit = QLineEdit()
        self.vth_edit = QLineEdit("0.7")
        self.k_edit = QLineEdit("1")

        form.addRow("Device", self.device_combo)
        form.addRow("V_G (V)", self.vg_edit)
        form.addRow("V_D (V)", self.vd_edit)
        form.addRow("V_S (V)", self.vs_edit)
        form.addRow("|V_TH| (V)", self.vth_edit)
        form.addRow("K", self.k_edit)
        layout.addLayout(form)

        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.export_button = QPushButton("Export Figure")
        self.calculate_button.clicked.connect(self.calculate)
        self.reset_button.clicked.connect(self.reset_inputs)
        self.export_button.clicked.connect(self.export_figure)

        button_row = QHBoxLayout()
        button_row.addWidget(self.calculate_button)
        button_row.addWidget(self.reset_button)
        layout.addLayout(button_row)
        layout.addWidget(self.export_button)
        layout.addStretch(1)
        return group

    def _build_plot_panel(self) -> QGroupBox:
        group = QGroupBox("I-V Characteristic Plot")
        layout = QVBoxLayout(group)
        self.figure = Figure(figsize=(7.5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        return group

    def _build_schematic_panel(self) -> QGroupBox:
        group = QGroupBox("Device Bias Sketch")
        layout = QVBoxLayout(group)
        self.schematic_figure = Figure(figsize=(7.5, 3.7), dpi=100)
        self.schematic_canvas = FigureCanvas(self.schematic_figure)
        layout.addWidget(self.schematic_canvas)
        return group

    def _build_output_panel(self) -> QGroupBox:
        group = QGroupBox("Output")
        layout = QVBoxLayout(group)
        self.region_label = QLabel("Region: -")
        self.region_label.setAlignment(Qt.AlignCenter)
        self.region_label.setObjectName("regionLabel")
        self.region_label.setStyleSheet(
            "#regionLabel { font-size: 20px; font-weight: 700; padding: 8px; "
            "border: 1px solid #b8b8b8; background: #f4f6f8; }"
        )
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(145)
        layout.addWidget(self.region_label)
        layout.addWidget(self.output_text)
        return group

    def _build_model_notice_panel(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        title = QLabel("Model Note")
        title.setStyleSheet("font-weight: 700;")
        notice = QLabel(MODEL_NOTICE)
        notice.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(notice)
        return frame

    def reset_inputs(self) -> None:
        self.device_combo.setCurrentText(DeviceType.NMOS.value)
        self.vg_edit.setText("2.0")
        self.vd_edit.setText("3.3")
        self.vs_edit.setText("0")
        self.vth_edit.setText("0.7")
        self.k_edit.setText("1")
        self.calculate()

    def calculate(self) -> None:
        try:
            result = evaluate_region(
                self.device_combo.currentText(),
                vg=self._float_from(self.vg_edit, "V_G"),
                vd=self._float_from(self.vd_edit, "V_D"),
                vs=self._float_from(self.vs_edit, "V_S"),
                vth_abs=self._float_from(self.vth_edit, "|V_TH|"),
                k=self._float_from(self.k_edit, "K"),
            )
        except ValueError as exc:
            QMessageBox.critical(self, "Invalid Input", str(exc))
            return

        self.current_result = result
        self._render_result(result)
        draw_region_plot(self.figure, result)
        self._draw_schematic(result)
        self.canvas.draw_idle()
        self.schematic_canvas.draw_idle()

    def export_figure(self) -> None:
        if self.current_result is None:
            QMessageBox.information(self, "No Figure", "Please calculate an operating point first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Figure",
            str(Path.cwd() / "cmos_region_plot.png"),
            "PNG Images (*.png)",
        )
        if not path:
            return
        try:
            save_region_plot(path, self.current_result)
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            return
        QMessageBox.information(self, "Export Complete", f"Figure saved to:\n{path}")

    def _render_result(self, result: RegionResult) -> None:
        self.region_label.setText(f"Region: {result.region.value}")
        lines = [
            f"Device: {result.device.value}",
            f"V_G = {result.vg:.3f} V",
            f"V_D = {result.vd:.3f} V",
            f"V_S = {result.vs:.3f} V",
            f"|V_TH| = {result.vth_abs:.3f} V",
            f"K = {result.k:.3f}",
            "",
            "Key voltages:",
        ]
        lines.extend(f"{name} = {value:.3f} V" for name, value in result.key_voltages.items())
        lines.extend(
            [
                f"Boundary voltage = {result.boundary_voltage:.3f} V",
                f"Operating-point current = {result.current:.6f} (normalized)",
                "",
                "Inequality:",
            ]
        )
        lines.extend(f"- {item}" for item in result.inequalities)
        lines.extend(["", "Reason:", result.reason, "", "Note:", result.note])
        self.output_text.setPlainText("\n".join(lines))

    def _draw_schematic(self, result: RegionResult) -> None:
        self.schematic_figure.clear()
        ax = self.schematic_figure.add_subplot(111)
        draw_bias_schematic(ax, result.device, result.vg, result.vd, result.vs, result)
        self.schematic_figure.tight_layout(pad=0.5)

    @staticmethod
    def _float_from(edit: QLineEdit, name: str) -> float:
        text = edit.text().strip()
        try:
            value = float(text)
        except ValueError as exc:
            raise ValueError(f"{name} must be a valid number.") from exc
        return value
