"""Data lineage graph utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

import networkx as nx

from .models import StorageAsset


@dataclass
class LineageGraph:
    """Helper for constructing and exporting lineage graphs."""

    graph: nx.DiGraph = field(default_factory=nx.DiGraph)

    def add_provider_assets(self, provider: str, assets: Iterable[StorageAsset]) -> None:
        """Add nodes for assets and connect them using simple ordering."""

        for asset in assets:
            node_id = f"{provider}:{asset.name}"
            self.graph.add_node(node_id, provider=provider, region=asset.region)
        self._connect_lineage(provider)

    def _connect_lineage(self, provider: str) -> None:
        """Create simple provider-specific lineage edges for demo purposes."""

        provider_nodes = sorted(
            [node for node in self.graph.nodes if str(node).startswith(provider)]
        )
        if len(provider_nodes) < 2:
            return
        for upstream, downstream in self._pairwise(provider_nodes):
            self.graph.add_edge(upstream, downstream, risk="replication")

    def to_mermaid(self) -> str:
        lines = ["flowchart LR"]
        for source, target in self.graph.edges:
            lines.append(f"    {self._sanitize(source)} --> {self._sanitize(target)}")
        if len(lines) == 1:
            lines.append("    No_Lineage[/No lineage detected/]")
        return "\n".join(lines)

    def to_json(self) -> Dict[str, List[Tuple[str, str]]]:
        """Export nodes and edges in JSON-serializable format."""

        return {
            "nodes": list(self.graph.nodes),
            "edges": [(u, v) for u, v in self.graph.edges],
        }

    @staticmethod
    def _sanitize(node: str) -> str:
        """Make node IDs safe for Mermaid output."""

        return node.replace(":", "_")

    @staticmethod
    def _pairwise(nodes: List[str]) -> Iterable[Tuple[str, str]]:
        """Yield ordered pairs for adjacent nodes."""

        for index in range(len(nodes) - 1):
            yield nodes[index], nodes[index + 1]
