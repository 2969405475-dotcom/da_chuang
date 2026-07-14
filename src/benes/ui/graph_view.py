"""Port-accurate Qt rendering for the fixed 8x8 Benes topology."""

from __future__ import annotations

import networkx as nx
from PySide6.QtCore import QLineF, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QInputDialog,
)


def state_segments(state: str, width: float, height: float) -> tuple[QLineF, QLineF]:
    """Return centered internal lines for a Bar or Cross switch state."""
    left = -width / 2 + 5
    right = width / 2 - 5
    offset = height * 0.28
    if state == "bar":
        return (
            QLineF(left, -offset, right, -offset),
            QLineF(left, offset, right, offset),
        )
    if state == "cross":
        return (
            QLineF(left, -offset, right, offset),
            QLineF(left, offset, right, -offset),
        )
    raise ValueError(f"未知交换单元状态：{state}")


class EdgeGraphicsItem(QGraphicsPathItem):
    """A wide-hit-target edge that opens its weight editor on double-click."""

    def __init__(self, source: str, target: str, path: QPainterPath, owner):
        super().__init__(path)
        self.source = source
        self.target = target
        self.owner = owner
        self._on_path = False
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setZValue(-10)
        self.refresh_tooltip()
        self._apply_pen()

    def shape(self) -> QPainterPath:
        stroker = QPainterPathStroker()
        stroker.setWidth(14.0)
        return stroker.createStroke(self.path())

    def set_path_highlighted(self, highlighted: bool) -> None:
        self._on_path = highlighted
        self._apply_pen()

    def refresh_tooltip(self) -> None:
        data = self.owner.graph.edges[self.source, self.target]
        self.setToolTip(
            f"{self.source}.out{data['source_port']} → "
            f"{self.target}.in{data['target_port']}\n"
            f"路径长度：{float(data['length']):g}"
        )

    def _apply_pen(self, hovered: bool = False) -> None:
        if hovered:
            color, width = QColor("#F2A900"), 4.0
        elif self._on_path:
            color, width = QColor("#E5484D"), 4.2
        else:
            color, width = QColor("#68737D"), 1.35
        pen = QPen(color, width)
        pen.setCapStyle(Qt.RoundCap)
        self.setPen(pen)

    def hoverEnterEvent(self, event):  # noqa: N802
        self.setZValue(5)
        self._apply_pen(hovered=True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):  # noqa: N802
        self.setZValue(-10)
        self._apply_pen()
        super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event):  # noqa: N802
        self.owner.edit_edge(self.source, self.target)
        event.accept()


class BenesGraphView(QGraphicsView):
    """Render the reference 8x8 Benes network with explicit switch ports."""

    weight_changed = Signal(str, str, float)

    SWITCH_WIDTH = 72.0
    SWITCH_HEIGHT = 76.0
    PORT_OFFSET = 30.0
    WIRE_TOP = 84.0
    WIRE_GAP = 64.0
    INPUT_X = 48.0
    OUTPUT_X = 1250.0
    STAGE_X = {1: 165.0, 2: 425.0, 3: 685.0, 4: 945.0, 5: 1130.0}

    def __init__(self, graph: nx.DiGraph, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.path_edges: set[tuple[str, str]] = set()
        self.switch_states: dict[str, str] = {}
        self.edge_items: dict[tuple[str, str], EdgeGraphicsItem] = {}
        self.edge_weight_labels: dict[
            tuple[str, str], QGraphicsSimpleTextItem
        ] = {}
        self.switch_state_items: dict[str, list[QGraphicsLineItem]] = {}
        self._path_nodes: set[str] = set()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QColor("#FBFCFD"))
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setMinimumSize(820, 520)
        self._render_scene()

    def _wire_y(self, index: int) -> float:
        return self.WIRE_TOP + index * self.WIRE_GAP

    def _node_center(self, node: str) -> QPointF:
        data = self.graph.nodes[node]
        if data["kind"] == "input":
            return QPointF(self.INPUT_X, self._wire_y(data["index"]))
        if data["kind"] == "output":
            return QPointF(self.OUTPUT_X, self._wire_y(data["index"]))
        upper_wire = self._wire_y(data["index"] * 2)
        lower_wire = self._wire_y(data["index"] * 2 + 1)
        return QPointF(self.STAGE_X[data["stage"]], (upper_wire + lower_wire) / 2)

    def port_position(self, node: str, direction: str, port: int) -> QPointF:
        """Return the exact scene position of a node's fixed input/output port."""
        data = self.graph.nodes[node]
        center = self._node_center(node)
        if data["kind"] == "input":
            return center
        if data["kind"] == "output":
            return center
        x_offset = -self.SWITCH_WIDTH / 2 if direction == "input" else self.SWITCH_WIDTH / 2
        y_offset = -self.PORT_OFFSET if port == 0 else self.PORT_OFFSET
        return QPointF(center.x() + x_offset, center.y() + y_offset)

    def set_route(self, path: list[str], states: dict[str, str]) -> None:
        self.path_edges = set(zip(path, path[1:]))
        self._path_nodes = set(path)
        self.switch_states = dict(states)
        self._render_scene()

    def clear_route(self) -> None:
        self.path_edges.clear()
        self._path_nodes.clear()
        self.switch_states.clear()
        self._render_scene()

    def refresh_edge_weights(self) -> None:
        for edge, item in self.edge_items.items():
            item.refresh_tooltip()
            if edge in self.edge_weight_labels:
                self._refresh_weight_label(edge)

    def edit_edge(self, source: str, target: str) -> None:
        current = float(self.graph.edges[source, target]["length"])
        value, accepted = QInputDialog.getDouble(
            self,
            "修改路径长度",
            f"{source} → {target}\n路径长度：",
            current,
            0.0,
            1_000_000.0,
            2,
        )
        if not accepted:
            return
        self.graph.edges[source, target]["length"] = float(value)
        self.edge_items[source, target].refresh_tooltip()
        if (source, target) in self.edge_weight_labels:
            self._refresh_weight_label((source, target))
        self.weight_changed.emit(source, target, float(value))

    def _render_scene(self) -> None:
        self._scene.clear()
        self.edge_items.clear()
        self.edge_weight_labels.clear()
        self.switch_state_items.clear()
        self._draw_stage_labels()
        self._draw_edges()
        self._draw_nodes()
        self._scene.setSceneRect(0, 0, 1310, 610)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def _draw_stage_labels(self) -> None:
        font = QFont("Microsoft YaHei UI", 9)
        font.setBold(True)
        for stage, x_position in self.STAGE_X.items():
            label = self._scene.addText(f"第 {stage} 级", font)
            label.setDefaultTextColor(QColor("#44515C"))
            bounds = label.boundingRect()
            label.setPos(x_position - bounds.width() / 2, 12)

    def _draw_edges(self) -> None:
        weight_font = QFont("Microsoft YaHei UI", 8)
        weight_font.setBold(True)
        for source, target, data in self.graph.edges(data=True):
            start = self.port_position(source, "output", data["source_port"])
            end = self.port_position(target, "input", data["target_port"])
            path = QPainterPath(start)
            path.lineTo(end)
            item = EdgeGraphicsItem(source, target, path, self)
            item.set_path_highlighted((source, target) in self.path_edges)
            self._scene.addItem(item)
            self.edge_items[source, target] = item
            if self.graph.nodes[source]["kind"] == "switch":
                label = self._scene.addSimpleText("", weight_font)
                label.setBrush(QBrush(QColor("#26343E")))
                label.setZValue(4)
                self.edge_weight_labels[source, target] = label
                self._refresh_weight_label((source, target))

    def _refresh_weight_label(self, edge: tuple[str, str]) -> None:
        source, target = edge
        data = self.graph.edges[source, target]
        label = self.edge_weight_labels[edge]
        label.setText(f"{float(data['length']):g}")
        port = self.port_position(source, "output", data["source_port"])
        bounds = label.boundingRect()
        y_position = (
            port.y() - bounds.height() - 3
            if data["source_port"] == 0
            else port.y() + 2
        )
        label.setPos(port.x() + 6, y_position)

    def _draw_nodes(self) -> None:
        label_font = QFont("Microsoft YaHei UI", 8)
        state_pen = QPen(QColor("#00E5FF"), 3.2)
        state_pen.setCapStyle(Qt.RoundCap)
        for node, data in self.graph.nodes(data=True):
            center = self._node_center(node)
            selected = node in self._path_nodes
            if data["kind"] != "switch":
                radius = 4.0
                fill = QColor("#F2B134") if selected else QColor("#2C3640")
                self._scene.addEllipse(
                    QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                    QPen(fill),
                    QBrush(fill),
                )
                label = self._scene.addText(node, label_font)
                label.setDefaultTextColor(QColor("#1F2A32"))
                bounds = label.boundingRect()
                if data["kind"] == "input":
                    label.setPos(center.x() - bounds.width() - 12, center.y() - bounds.height() / 2)
                else:
                    label.setPos(center.x() + 10, center.y() - bounds.height() / 2)
                continue

            rect = QRectF(
                center.x() - self.SWITCH_WIDTH / 2,
                center.y() - self.SWITCH_HEIGHT / 2,
                self.SWITCH_WIDTH,
                self.SWITCH_HEIGHT,
            )
            border = QPen(QColor("#E5484D") if selected else QColor("#136F63"))
            border.setWidthF(3.0 if selected else 1.4)
            self._scene.addRect(rect, border, QBrush(QColor("#08CFA5")))
            label = self._scene.addText(node, label_font)
            label.setDefaultTextColor(QColor("#24313A"))
            bounds = label.boundingRect()
            label.setPos(center.x() - bounds.width() / 2, rect.top() - bounds.height() - 2)

            for direction in ("input", "output"):
                for port in (0, 1):
                    point = self.port_position(node, direction, port)
                    self._scene.addEllipse(
                        QRectF(point.x() - 2.5, point.y() - 2.5, 5, 5),
                        QPen(QColor("#173A36")),
                        QBrush(QColor("#173A36")),
                    )

            if node in self.switch_states:
                lines: list[QGraphicsLineItem] = []
                for segment in state_segments(
                    self.switch_states[node], self.SWITCH_WIDTH, self.SWITCH_HEIGHT
                ):
                    translated = QLineF(
                        center.x() + segment.x1(),
                        center.y() + segment.y1(),
                        center.x() + segment.x2(),
                        center.y() + segment.y2(),
                    )
                    lines.append(self._scene.addLine(translated, state_pen))
                self.switch_state_items[node] = lines

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
