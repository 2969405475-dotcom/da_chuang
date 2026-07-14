import networkx as nx
import pytest

from benes.metrics import compute_path_metrics


def test_computes_hop_count_and_total_length():
    graph = nx.DiGraph()
    graph.add_edge("I0", "S1_0", length=1.25)
    graph.add_edge("S1_0", "O0", length=2.75)

    metrics = compute_path_metrics(graph, ["I0", "S1_0", "O0"])

    assert metrics == {"hop_count": 2, "length": 4.0}


def test_rejects_empty_or_invalid_paths():
    graph = nx.DiGraph()
    graph.add_edge("I0", "O0", length=1.0)

    with pytest.raises(ValueError, match="不能为空"):
        compute_path_metrics(graph, [])
    with pytest.raises(ValueError, match="不是有效连线"):
        compute_path_metrics(graph, ["I0", "X", "O0"])

