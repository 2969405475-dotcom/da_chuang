from unittest.mock import patch

import networkx as nx
from PySide6.QtCore import Qt

from benes.topology import build_benes_network
from benes.ui.graph_view import BenesGraphView, state_segments
from benes.ui.main_window import MainWindow


def test_graph_uses_distinct_fixed_ports_for_every_switch(qtbot):
    graph = build_benes_network(8)
    view = BenesGraphView(graph)
    qtbot.addWidget(view)

    assert len(view.edge_items) == 48
    for node, data in graph.nodes(data=True):
        if data["kind"] != "switch":
            continue
        assert view.port_position(node, "input", 0) != view.port_position(
            node, "input", 1
        )
        assert view.port_position(node, "output", 0) != view.port_position(
            node, "output", 1
        )
        for source, _, edge_data in graph.in_edges(node, data=True):
            item = view.edge_items[source, node]
            assert item.path().pointAtPercent(1) == view.port_position(
                node, "input", edge_data["target_port"]
            )
        for _, target, edge_data in graph.out_edges(node, data=True):
            item = view.edge_items[node, target]
            assert item.path().pointAtPercent(0) == view.port_position(
                node, "output", edge_data["source_port"]
            )


def test_every_switch_output_shows_its_edge_weight_near_the_port(qtbot):
    graph = build_benes_network(8)
    view = BenesGraphView(graph)
    qtbot.addWidget(view)

    assert len(view.edge_weight_labels) == 40
    for source, target, data in graph.edges(data=True):
        if graph.nodes[source]["kind"] != "switch":
            assert (source, target) not in view.edge_weight_labels
            continue
        label = view.edge_weight_labels[source, target]
        port = view.port_position(source, "output", data["source_port"])
        assert label.text() == f"{float(data['length']):g}"
        assert label.font().pointSize() >= 8
        assert label.pos().x() > port.x()
        if data["source_port"] == 0:
            assert label.pos().y() < port.y()
        else:
            assert label.pos().y() >= port.y()


def test_bar_and_cross_are_drawn_as_parallel_and_crossed_segments():
    bar = state_segments("bar", width=64, height=72)
    cross = state_segments("cross", width=64, height=72)

    assert len(bar) == len(cross) == 2
    assert all(line.y1() == line.y2() for line in bar)
    assert all(line.y1() != line.y2() for line in cross)
    assert cross[0].y1() == cross[1].y2()
    assert cross[0].y2() == cross[1].y1()


def test_graph_double_click_editor_updates_edge_weight(qtbot):
    graph = build_benes_network(8)
    view = BenesGraphView(graph)
    qtbot.addWidget(view)
    view.show()
    edge = ("S1_0", "S2_0")
    item = view.edge_items[edge]
    click_position = view.mapFromScene(item.path().pointAtPercent(0.5))

    with patch(
        "benes.ui.graph_view.QInputDialog.getDouble", return_value=(7.5, True)
    ), qtbot.waitSignal(view.weight_changed, timeout=1000) as signal:
        qtbot.mouseDClick(view.viewport(), Qt.LeftButton, pos=click_position)

    assert signal.args == ["S1_0", "S2_0", 7.5]
    assert graph.edges[edge]["length"] == 7.5
    assert "7.5" in item.toolTip()
    assert view.edge_weight_labels[edge].text() == "7.5"


def test_graph_view_records_and_clears_visual_switch_states(qtbot):
    graph = build_benes_network(8)
    view = BenesGraphView(graph)
    qtbot.addWidget(view)
    path = ["I0", "S1_0", "S2_0"]
    states = {"S1_0": "bar"}

    view.set_route(path, states)

    assert view.path_edges == {("I0", "S1_0"), ("S1_0", "S2_0")}
    assert view.switch_states == states
    assert len(view.switch_state_items["S1_0"]) == 2
    view.clear_route()
    assert view.path_edges == set()
    assert view.switch_states == {}
    assert view.switch_state_items == {}


def test_main_window_has_no_weight_table_and_plans_route(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert not hasattr(window, "weight_table")
    assert all(
        1.0 <= data["length"] <= 10.0
        for _, _, data in window.graph.edges(data=True)
    )
    window.source_combo.setCurrentText("I3")
    window.target_combo.setCurrentText("O6")

    qtbot.mouseClick(window.plan_button, Qt.LeftButton)

    path = window.path_value.text().split(" → ")
    expected_length = nx.path_weight(window.graph, path, "length")
    assert window.graph_view.path_edges
    assert path[0] == "I3"
    assert path[-1] == "O6"
    assert f"总长度：{expected_length:g}" in window.metrics_value.text()
    assert window.states_list.count() == 5
    assert hasattr(window, "all_paths_list")
    assert window.all_paths_list.count() == 4
    for row in range(4):
        text = window.all_paths_list.item(row).text()
        assert f"路径 {row + 1}" in text
        assert "总长度：" in text
        assert "I3" in text
        assert "O6" in text


def test_edge_edit_marks_existing_result_as_stale(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    qtbot.mouseClick(window.plan_button, Qt.LeftButton)

    window.graph_view.weight_changed.emit("I0", "S1_0", 4.0)

    assert window.statusBar().currentMessage() == "权重已变化，请重新规划"
    assert window.all_paths_list.count() == 0


def test_randomize_button_replaces_weights_and_clears_result(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    qtbot.mouseClick(window.plan_button, Qt.LeftButton)

    with patch("benes.topology.random.randint", return_value=4):
        qtbot.mouseClick(window.randomize_button, Qt.LeftButton)

    for _, _, data in window.graph.edges(data=True):
        expected = 4.0 if data["segment"] == "interstage" else 1.0
        assert data["length"] == expected
    assert {
        label.text() for label in window.graph_view.edge_weight_labels.values()
    } == {"1", "4"}
    assert not window.graph_view.path_edges
    assert window.path_value.text() == "尚未规划"
    assert window.all_paths_list.count() == 0
