"""Construction of the fixed 8x8 Benes switching network."""

from __future__ import annotations

import random

import networkx as nx


def randomize_edge_lengths(G: nx.DiGraph) -> None:
    """Randomize interstage lengths while restoring boundary lengths to one."""
    for source, target in G.edges:
        edge = G.edges[source, target]
        edge["length"] = (
            float(random.randint(1, 10))
            if edge["segment"] == "interstage"
            else 1.0
        )


def build_benes_network(N: int) -> nx.DiGraph:
    """Build the supported 8x8 Benes network as a directed graph."""
    if N != 8:
        raise ValueError("当前版本仅支持 8×8 Benes 网络")

    graph = nx.DiGraph(name="8x8 Benes")
    stage_count = 5
    switches_per_stage = N // 2

    for index in range(N):
        graph.add_node(f"I{index}", kind="input", stage=0, index=index)
        graph.add_node(f"O{index}", kind="output", stage=stage_count + 1, index=index)

    for stage in range(1, stage_count + 1):
        for index in range(switches_per_stage):
            graph.add_node(
                f"S{stage}_{index}", kind="switch", stage=stage, index=index
            )

    for wire in range(N):
        graph.add_edge(
            f"I{wire}",
            f"S1_{wire // 2}",
            length=1.0,
            source_port=wire % 2,
            target_port=wire % 2,
            segment="input",
        )

    for stage in range(1, stage_count):
        for source_index in range(switches_per_stage):
            for source_port in range(2):
                if stage == 1:
                    target_index = source_index // 2 + 2 * source_port
                    target_port = source_index % 2
                elif stage == 4:
                    target_index = 2 * (source_index % 2) + source_port
                    target_port = source_index // 2
                else:
                    target_index = (source_index // 2) * 2 + source_port
                    target_port = source_index % 2
                graph.add_edge(
                    f"S{stage}_{source_index}",
                    f"S{stage + 1}_{target_index}",
                    length=0.0,
                    source_port=source_port,
                    target_port=target_port,
                    segment="interstage",
                )

    for wire in range(N):
        graph.add_edge(
            f"S{stage_count}_{wire // 2}",
            f"O{wire}",
            length=1.0,
            source_port=wire % 2,
            target_port=wire % 2,
            segment="output",
        )

    randomize_edge_lengths(graph)
    return graph
