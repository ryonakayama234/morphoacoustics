"""OG-3 candidate: fixed passive physical organ graph data, not a general anatomy model.

Only explicit SI parameters, typed acoustic ports and immutable revisions belong here.
This module has no research-experiment imports and no eager package initializer changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SCHEMA = "og3.passive.fixed2.v1"
PORT_KIND = "acoustic.p_u"
SERIES_LAW = "ideal.series.p_u"
BRANCH_LAW = "ideal.branch3.p_u"


@dataclass(frozen=True, slots=True)
class AcousticPort:
    id: str
    direction: str
    kind: str = PORT_KIND


@dataclass(frozen=True, slots=True)
class PassiveTubeOrgan:
    id: str
    revision: str
    length_m: float
    area_m2: float
    inlet: AcousticPort
    outlet: AcousticPort
    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.21


@dataclass(frozen=True, slots=True)
class AcousticJunction:
    id: str
    law: str
    ports: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OrganGraphBlueprint:
    schema: str
    organs: tuple[PassiveTubeOrgan, ...]
    junctions: tuple[AcousticJunction, ...]
    source_port: str
    load_ports: tuple[str, ...]
    termination: str = "matched"


def graph_to_dict(graph: OrganGraphBlueprint) -> dict[str, Any]:
    """JSON-compatible exact-revision snapshot; physical digest uses binary64 hex."""
    return {
        "schema": graph.schema,
        "organs": [
            {"id": n.id, "revision": n.revision, "length_m": n.length_m,
             "area_m2": n.area_m2, "sound_speed_m_s": n.sound_speed_m_s,
             "air_density_kg_m3": n.air_density_kg_m3,
             "inlet": {"id": n.inlet.id, "direction": n.inlet.direction,
                       "kind": n.inlet.kind},
             "outlet": {"id": n.outlet.id, "direction": n.outlet.direction,
                        "kind": n.outlet.kind}}
            for n in graph.organs
        ],
        "junctions": [
            {"id": e.id, "law": e.law, "ports": list(e.ports)}
            for e in graph.junctions
        ],
        "source_port": graph.source_port,
        "load_ports": list(graph.load_ports),
        "termination": graph.termination,
    }


def graph_from_dict(snapshot: dict[str, Any]) -> OrganGraphBlueprint:
    """Lossless Python JSON roundtrip; validate_graph enforces physics separately."""
    if not isinstance(snapshot, dict):
        raise ValueError("graph snapshot must be an object")
    if set(snapshot) != {
        "schema", "organs", "junctions", "source_port", "load_ports", "termination"
    }:
        raise ValueError("graph snapshot keys must match v1 exactly")
    try:
        nodes = []
        if not isinstance(snapshot["organs"], list):
            raise ValueError("organs must be a list")
        for node in snapshot["organs"]:
            if not isinstance(node, dict) or set(node) != {
                "id", "revision", "length_m", "area_m2", "sound_speed_m_s",
                "air_density_kg_m3", "inlet", "outlet"
            }:
                raise ValueError("organ snapshot keys")
            ports = []
            for role in ("inlet", "outlet"):
                pd = node[role]
                if not isinstance(pd, dict) or set(pd) != {"id", "direction", "kind"}:
                    raise ValueError("port snapshot keys")
                ports.append(AcousticPort(pd["id"], pd["direction"], pd["kind"]))
            nodes.append(PassiveTubeOrgan(
                node["id"], node["revision"], node["length_m"], node["area_m2"],
                ports[0], ports[1], node["sound_speed_m_s"],
                node["air_density_kg_m3"]
            ))
        if not isinstance(snapshot["junctions"], list):
            raise ValueError("junctions must be a list")
        edges = []
        for ed in snapshot["junctions"]:
            if not isinstance(ed, dict) or set(ed) != {"id", "law", "ports"}:
                raise ValueError("junction snapshot keys")
            if not isinstance(ed["ports"], list):
                raise ValueError("junction ports must be a list")
            edges.append(AcousticJunction(ed["id"], ed["law"], tuple(ed["ports"])))
        if not isinstance(snapshot["load_ports"], list):
            raise ValueError("load_ports must be a list")
        return OrganGraphBlueprint(
            snapshot["schema"], tuple(nodes), tuple(edges),
            snapshot["source_port"], tuple(snapshot["load_ports"]),
            snapshot["termination"],
        )
    except (KeyError, TypeError) as error:
        raise ValueError("malformed graph snapshot") from error
