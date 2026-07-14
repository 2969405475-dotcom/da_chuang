from pathlib import Path

from benes.topology import build_benes_network
from benes.visualize import benes_positions, draw_benes_network


def test_positions_follow_benes_stages():
    graph = build_benes_network(8)
    positions = benes_positions(graph)

    assert positions["I0"][0] < positions["S1_0"][0]
    assert positions["S1_0"][0] < positions["S5_0"][0]
    assert positions["S5_0"][0] < positions["O0"][0]
    assert len(positions) == graph.number_of_nodes()


def test_draws_static_network_to_file(tmp_path: Path):
    output = tmp_path / "benes.png"

    draw_benes_network(build_benes_network(8), save_path=str(output))

    assert output.exists()
    assert output.stat().st_size > 1_000

