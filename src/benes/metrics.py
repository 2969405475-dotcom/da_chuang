"""Metrics for a selected network path."""

from __future__ import annotations

import networkx as nx


def compute_path_metrics(G: nx.DiGraph, path: list[str]) -> dict:
    """Compute hop count and summed edge length for a path."""
    if not path:
        raise ValueError("路径不能为空")

    total_length = 0.0
    for source, target in zip(path, path[1:]):
        if not G.has_edge(source, target):
            raise ValueError(f"{source} → {target} 不是有效连线")
        total_length += float(G.edges[source, target]["length"])

    return {"hop_count": len(path) - 1, "length": total_length}

