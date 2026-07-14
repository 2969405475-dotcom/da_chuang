"""Deterministic layout and optional static rendering for Benes networks."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from benes.layout import benes_positions

__all__ = ["benes_positions", "draw_benes_network"]


def draw_benes_network(
    G: nx.DiGraph,
    path: list[str] | None = None,
    save_path: str | None = None,
) -> None:
    """Draw a static network image and optionally highlight a route."""
    import matplotlib.pyplot as plt

    positions = benes_positions(G)
    path_edges = set(zip(path or [], (path or [])[1:]))
    node_colors = ["#159A9C" if node in (path or []) else "#E8ECEF" for node in G]
    edge_colors = ["#E45756" if edge in path_edges else "#AEB8C2" for edge in G.edges]
    widths = [2.8 if edge in path_edges else 1.0 for edge in G.edges]

    figure, axis = plt.subplots(figsize=(14, 7))
    nx.draw_networkx(
        G,
        positions,
        ax=axis,
        node_color=node_colors,
        edge_color=edge_colors,
        width=widths,
        node_size=900,
        font_size=8,
        arrows=True,
        arrowsize=10,
    )
    axis.set_axis_off()
    figure.tight_layout()
    if save_path:
        output = Path(save_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output, dpi=160, bbox_inches="tight")
        plt.close(figure)
    else:
        plt.show()
