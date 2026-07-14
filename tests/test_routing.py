import math

import networkx as nx
import pytest

import benes.routing as routing
from benes.routing import compute_switch_states, find_path
from benes.topology import build_benes_network


def assert_valid_path(graph, path, source, target):
    assert path[0] == source
    assert path[-1] == target
    assert all(graph.has_edge(a, b) for a, b in zip(path, path[1:]))


def test_dijkstra_finds_a_valid_shortest_path_for_all_port_pairs():
    graph = build_benes_network(8)

    for source in (f"I{i}" for i in range(8)):
        for target in (f"O{i}" for i in range(8)):
            path = find_path(graph, source, target, method="dijkstra", weight="length")
            assert_valid_path(graph, path, source, target)
            assert nx.path_weight(graph, path, "length") == nx.dijkstra_path_length(
                graph, source, target, weight="length"
            )


def test_dijkstra_avoids_an_expensive_edge_when_an_alternative_exists():
    graph = build_benes_network(8)
    nx.set_edge_attributes(graph, 1.0, "length")
    original = find_path(graph, "I0", "O0", method="dijkstra", weight="length")
    expensive_edge = (original[2], original[3])
    graph.edges[expensive_edge]["length"] = 100.0

    replacement = find_path(graph, "I0", "O0", method="dijkstra", weight="length")

    assert expensive_edge not in set(zip(replacement, replacement[1:]))
    assert nx.path_weight(graph, replacement, "length") < 100.0


def test_enumerates_four_paths_sorted_by_total_length():
    graph = build_benes_network(8)

    assert hasattr(routing, "enumerate_paths")
    ranked_paths = routing.enumerate_paths(graph, "I3", "O6", weight="length")

    assert len(ranked_paths) == 4
    lengths = [length for _, length in ranked_paths]
    assert lengths == sorted(lengths)
    for path, length in ranked_paths:
        assert_valid_path(graph, path, "I3", "O6")
        assert length == nx.path_weight(graph, path, "length")

    shortest = find_path(graph, "I3", "O6", method="dijkstra", weight="length")
    assert lengths[0] == nx.path_weight(graph, shortest, "length")


@pytest.mark.parametrize("source,target", [("X", "O0"), ("I0", "X"), ("S1_0", "O0")])
def test_rejects_invalid_endpoints(source, target):
    with pytest.raises(ValueError, match="端口"):
        find_path(build_benes_network(8), source, target, method="dijkstra", weight="length")


@pytest.mark.parametrize("bad_weight", [-1.0, math.inf, math.nan, "abc"])
def test_rejects_invalid_edge_lengths(bad_weight):
    graph = build_benes_network(8)
    first_edge = next(iter(graph.edges))
    graph.edges[first_edge]["length"] = bad_weight

    with pytest.raises(ValueError, match="路径长度"):
        find_path(graph, "I0", "O0", method="dijkstra", weight="length")


def test_reports_when_no_path_exists():
    graph = build_benes_network(8)
    graph.remove_edges_from(list(graph.in_edges("O0")))

    with pytest.raises(nx.NetworkXNoPath, match="不存在可达路径"):
        find_path(graph, "I0", "O0", method="dijkstra", weight="length")


def test_computes_bar_and_cross_from_edge_ports():
    graph = nx.DiGraph()
    graph.add_edge("I0", "S1_0", target_port=0, source_port=0, length=1.0)
    graph.add_edge("S1_0", "S2_0", target_port=1, source_port=0, length=1.0)
    graph.add_edge("S2_0", "O0", target_port=0, source_port=0, length=1.0)

    states = compute_switch_states(graph, ["I0", "S1_0", "S2_0", "O0"])

    assert states == {"S1_0": "bar", "S2_0": "cross"}
