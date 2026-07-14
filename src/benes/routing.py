"""Shortest-path routing and switch state derivation."""

from __future__ import annotations

import math
from numbers import Real

import networkx as nx


def _validate_endpoint(graph: nx.DiGraph, node: str, kind: str) -> None:
    if node not in graph or graph.nodes[node].get("kind") != kind:
        label = "输入" if kind == "input" else "输出"
        raise ValueError(f"{label}端口无效：{node}")


def _validate_weights(graph: nx.DiGraph, weight: str) -> None:
    for source, target, data in graph.edges(data=True):
        value = data.get(weight)
        if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not math.isfinite(float(value))
            or float(value) < 0
        ):
            raise ValueError(f"路径长度无效：{source} → {target}")


def find_path(
    G: nx.DiGraph,
    src: str,
    dst: str,
    method: str = "bfs",
    weight: str | None = None,
) -> list[str]:
    """Find a valid path from an input port to an output port."""
    _validate_endpoint(G, src, "input")
    _validate_endpoint(G, dst, "output")

    try:
        if method == "bfs":
            return nx.shortest_path(G, src, dst)
        if method == "dijkstra":
            weight_name = weight or "length"
            _validate_weights(G, weight_name)
            return nx.dijkstra_path(G, src, dst, weight=weight_name)
    except nx.NetworkXNoPath as exc:
        raise nx.NetworkXNoPath(f"{src} 到 {dst} 不存在可达路径") from exc

    raise ValueError(f"不支持的路径算法：{method}")


def enumerate_paths(
    G: nx.DiGraph,
    src: str,
    dst: str,
    weight: str = "length",
) -> list[tuple[list[str], float]]:
    """Return all valid paths sorted by their total weight."""
    _validate_endpoint(G, src, "input")
    _validate_endpoint(G, dst, "output")
    _validate_weights(G, weight)

    ranked_paths = [
        (list(path), float(nx.path_weight(G, path, weight)))
        for path in nx.all_simple_paths(G, src, dst)
    ]
    if not ranked_paths:
        raise nx.NetworkXNoPath(f"{src} 到 {dst} 不存在可达路径")
    ranked_paths.sort(key=lambda item: (item[1], item[0]))
    return ranked_paths


def compute_switch_states(G: nx.DiGraph, path: list[str]) -> dict[str, str]:
    """Return bar/cross states for switches traversed by a path."""
    states: dict[str, str] = {}
    for index in range(1, len(path) - 1):
        node = path[index]
        if not node.startswith("S"):
            continue
        incoming_port = G.edges[path[index - 1], node]["target_port"]
        outgoing_port = G.edges[node, path[index + 1]]["source_port"]
        states[node] = "bar" if incoming_port == outgoing_port else "cross"
    return states
