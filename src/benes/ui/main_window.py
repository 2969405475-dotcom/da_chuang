"""Main desktop window for interactive path planning."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from benes.metrics import compute_path_metrics
from benes.routing import compute_switch_states, enumerate_paths, find_path
from benes.topology import build_benes_network, randomize_edge_lengths
from benes.ui.graph_view import BenesGraphView


class MainWindow(QMainWindow):
    """Coordinate controls, edge editing, routing, and results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Benes 8×8 最短路径规划器")
        self.resize(1380, 760)
        self.setMinimumSize(1100, 650)
        self.graph = build_benes_network(8)
        self._has_result = False
        self._build_ui()
        self._connect_signals()
        self.statusBar().showMessage("请选择输入、输出端口，然后开始规划")

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(12)

        controls = QHBoxLayout()
        title = QLabel("Benes 8×8 路径规划")
        title_font = QFont("Microsoft YaHei UI", 15)
        title_font.setBold(True)
        title.setFont(title_font)
        controls.addWidget(title)
        controls.addStretch()
        controls.addWidget(QLabel("输入端口"))
        self.source_combo = QComboBox()
        self.source_combo.addItems([f"I{i}" for i in range(8)])
        self.source_combo.setCurrentText("I3")
        controls.addWidget(self.source_combo)
        controls.addWidget(QLabel("输出端口"))
        self.target_combo = QComboBox()
        self.target_combo.addItems([f"O{i}" for i in range(8)])
        self.target_combo.setCurrentText("O6")
        controls.addWidget(self.target_combo)
        self.plan_button = QPushButton("开始规划")
        self.plan_button.setObjectName("primaryButton")
        controls.addWidget(self.plan_button)
        self.randomize_button = QPushButton("重新随机权重")
        controls.addWidget(self.randomize_button)
        root_layout.addLayout(controls)

        self.graph_view = BenesGraphView(self.graph)
        result_panel = self._build_result_panel()
        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.addWidget(self.graph_view)
        upper_splitter.addWidget(result_panel)
        upper_splitter.setStretchFactor(0, 4)
        upper_splitter.setStretchFactor(1, 1)

        root_layout.addWidget(upper_splitter)

        self.setCentralWidget(root)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #F7F8FA; color: #24313A; font-family: 'Microsoft YaHei UI'; font-size: 10pt; }
            QComboBox { background: white; border: 1px solid #C9D0D6; padding: 5px; }
            QPushButton { background: white; border: 1px solid #AEB8C2; padding: 7px 12px; }
            QPushButton:hover { background: #EEF1F3; }
            QPushButton:disabled { color: #929AA1; background: #E8EAEC; }
            QPushButton#primaryButton { background: #167D7F; color: white; border: 1px solid #126466; font-weight: 600; }
            QPushButton#primaryButton:hover { background: #126E70; }
            QLabel#sectionTitle { font-size: 11pt; font-weight: 600; }
            QFrame#resultPanel { background: white; border-left: 1px solid #D6DCE1; }
            QListWidget { background: white; border: 1px solid #D6DCE1; }
            """
        )

    def _build_result_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("resultPanel")
        panel.setMinimumWidth(330)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 8, 8, 8)
        heading = QLabel("规划结果")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        layout.addWidget(QLabel("路径"))
        self.path_value = QLabel("尚未规划")
        self.path_value.setWordWrap(True)
        self.path_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.path_value)
        layout.addWidget(QLabel("指标"))
        self.metrics_value = QLabel("总长度：—\n跳数：—")
        layout.addWidget(self.metrics_value)
        layout.addWidget(QLabel("交换单元状态"))
        self.states_list = QListWidget()
        layout.addWidget(self.states_list, 1)
        layout.addWidget(QLabel("全部可行路径"))
        self.all_paths_list = QListWidget()
        self.all_paths_list.setWordWrap(True)
        self.all_paths_list.setSpacing(3)
        layout.addWidget(self.all_paths_list, 2)
        return panel

    def _connect_signals(self) -> None:
        self.plan_button.clicked.connect(self.plan_route)
        self.randomize_button.clicked.connect(self.randomize_weights)
        self.graph_view.weight_changed.connect(self._on_weight_changed)

    def _on_weight_changed(self, _source: str, _target: str, _value: float) -> None:
        if self._has_result:
            self.all_paths_list.clear()
            self.statusBar().showMessage("权重已变化，请重新规划")
        else:
            self.statusBar().showMessage("路径长度已更新")

    def plan_route(self) -> None:
        source = self.source_combo.currentText()
        target = self.target_combo.currentText()
        try:
            path = find_path(
                self.graph, source, target, method="dijkstra", weight="length"
            )
            metrics = compute_path_metrics(self.graph, path)
            states = compute_switch_states(self.graph, path)
            ranked_paths = enumerate_paths(
                self.graph, source, target, weight="length"
            )
        except Exception as exc:  # UI boundary: keep the desktop app alive.
            self.clear_result()
            QMessageBox.warning(self, "规划失败", str(exc))
            self.statusBar().showMessage("规划失败，请检查网络设置")
            return

        self.graph_view.set_route(path, states)
        self.path_value.setText(" → ".join(path))
        self.metrics_value.setText(
            f"总长度：{metrics['length']:g}\n跳数：{metrics['hop_count']}"
        )
        self.states_list.clear()
        for switch, state in states.items():
            self.states_list.addItem(f"{switch}    {state.title()}")
        self.all_paths_list.clear()
        for index, (candidate, length) in enumerate(ranked_paths, start=1):
            selected = "（当前规划）" if candidate == path else ""
            self.all_paths_list.addItem(
                f"路径 {index}{selected}　总长度：{length:g}\n"
                f"{' → '.join(candidate)}"
            )
        self._has_result = True
        self.statusBar().showMessage(f"规划完成：{source} → {target}")

    def clear_result(self) -> None:
        self.graph_view.clear_route()
        self.path_value.setText("尚未规划")
        self.metrics_value.setText("总长度：—\n跳数：—")
        self.states_list.clear()
        self.all_paths_list.clear()
        self._has_result = False

    def randomize_weights(self) -> None:
        randomize_edge_lengths(self.graph)
        self.graph_view.refresh_edge_weights()
        self.clear_result()
        self.statusBar().showMessage("已重新生成 1–10 的随机路径权重")
