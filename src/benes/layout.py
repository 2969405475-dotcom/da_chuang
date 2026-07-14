"""Shared deterministic coordinates for Benes renderers."""

from __future__ import annotations

import networkx as nx


def benes_positions(G: nx.DiGraph) -> dict[str, tuple[float, float]]:
    """Return stable left-to-right positions for every network node."""
    positions: dict[str, tuple[float, float]] = {}
    for node, data in G.nodes(data=True):
        stage = int(data["stage"])
        index = int(data["index"])
        if data["kind"] == "switch":
            y = 1.0 + index * 2.0
        else:
            y = float(index)
        positions[node] = (float(stage), -y)
    return positions

