from unittest.mock import patch

import networkx as nx
import pytest

from benes.topology import build_benes_network, randomize_edge_lengths


def test_builds_expected_8x8_benes_structure():
    graph = build_benes_network(8)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 36
    assert graph.number_of_edges() == 48
    assert {n for n, d in graph.nodes(data=True) if d["kind"] == "input"} == {
        f"I{i}" for i in range(8)
    }
    assert {n for n, d in graph.nodes(data=True) if d["kind"] == "output"} == {
        f"O{i}" for i in range(8)
    }
    assert sum(d["kind"] == "switch" for _, d in graph.nodes(data=True)) == 20
    for stage in range(1, 6):
        assert {f"S{stage}_{index}" for index in range(4)} <= set(graph)


def test_boundary_edges_default_to_one_and_interstage_edges_are_random():
    values = [float((index % 10) + 1) for index in range(32)]
    with patch("benes.topology.random.randint", side_effect=values) as randint:
        graph = build_benes_network(8)

    assert randint.call_count == 32
    for _, _, data in graph.edges(data=True):
        if data["segment"] in {"input", "output"}:
            assert data["length"] == 1.0
        else:
            assert 1.0 <= data["length"] <= 10.0
        assert data["source_port"] in {0, 1}
        assert data["target_port"] in {0, 1}
        assert data["segment"] in {"input", "interstage", "output"}


def test_reference_topology_has_fixed_port_to_port_connections():
    graph = build_benes_network(8)

    expected_stage_1 = {
        ("S1_0", "S2_0", 0, 0),
        ("S1_0", "S2_2", 1, 0),
        ("S1_1", "S2_0", 0, 1),
        ("S1_1", "S2_2", 1, 1),
        ("S1_2", "S2_1", 0, 0),
        ("S1_2", "S2_3", 1, 0),
        ("S1_3", "S2_1", 0, 1),
        ("S1_3", "S2_3", 1, 1),
    }
    expected_stage_2 = {
        ("S2_0", "S3_0", 0, 0),
        ("S2_0", "S3_1", 1, 0),
        ("S2_1", "S3_0", 0, 1),
        ("S2_1", "S3_1", 1, 1),
        ("S2_2", "S3_2", 0, 0),
        ("S2_2", "S3_3", 1, 0),
        ("S2_3", "S3_2", 0, 1),
        ("S2_3", "S3_3", 1, 1),
    }

    def connections(stage):
        return {
            (source, target, data["source_port"], data["target_port"])
            for source, target, data in graph.edges(data=True)
            if source.startswith(f"S{stage}_")
            and target.startswith(f"S{stage + 1}_")
        }

    assert connections(1) == expected_stage_1
    assert connections(2) == expected_stage_2
    assert connections(3) == {
        (source.replace("S2", "S3"), target.replace("S3", "S4"), out_port, in_port)
        for source, target, out_port, in_port in expected_stage_2
    }
    assert connections(4) == {
        (target.replace("S2", "S4"), source.replace("S1", "S5"), in_port, out_port)
        for source, target, out_port, in_port in expected_stage_1
    }


def test_output_banyan_connects_each_last_stage_switch_across_both_halves():
    graph = build_benes_network(8)

    expected_predecessors = {
        "S5_0": {"S4_0", "S4_2"},
        "S5_1": {"S4_0", "S4_2"},
        "S5_2": {"S4_1", "S4_3"},
        "S5_3": {"S4_1", "S4_3"},
    }

    for switch, predecessors in expected_predecessors.items():
        assert set(graph.predecessors(switch)) == predecessors


def test_every_switch_has_exactly_two_fixed_inputs_and_outputs():
    graph = build_benes_network(8)

    for node, data in graph.nodes(data=True):
        if data["kind"] != "switch":
            continue
        incoming_ports = {edge[2]["target_port"] for edge in graph.in_edges(node, data=True)}
        outgoing_ports = {edge[2]["source_port"] for edge in graph.out_edges(node, data=True)}
        assert graph.in_degree(node) == 2
        assert graph.out_degree(node) == 2
        assert incoming_ports == {0, 1}
        assert outgoing_ports == {0, 1}


def test_randomize_edge_lengths_keeps_boundary_weights_at_one():
    graph = build_benes_network(8)
    for source, target, data in graph.edges(data=True):
        if data["segment"] in {"input", "output"}:
            graph.edges[source, target]["length"] = 9.0

    with patch("benes.topology.random.randint", return_value=7) as randint:
        randomize_edge_lengths(graph)

    assert randint.call_count == 32
    for _, _, data in graph.edges(data=True):
        expected = 7.0 if data["segment"] == "interstage" else 1.0
        assert data["length"] == expected


def test_every_input_can_reach_every_output():
    graph = build_benes_network(8)

    for source in (f"I{i}" for i in range(8)):
        for target in (f"O{i}" for i in range(8)):
            assert nx.has_path(graph, source, target)


@pytest.mark.parametrize("size", [2, 4, 16])
def test_rejects_unsupported_sizes(size):
    with pytest.raises(ValueError, match="仅支持 8×8"):
        build_benes_network(size)
