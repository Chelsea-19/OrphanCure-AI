"""Graph-based mechanism/path benchmark utilities for PrimeKG and PharmKG."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


GRAPH_NODE_COLUMNS = (
    "node_id",
    "node_name",
    "node_type",
    "graph_source",
    "synonyms",
    "external_ids",
    "status",
    "notes",
)
GRAPH_EDGE_COLUMNS = (
    "source_node_id",
    "source_node_name",
    "source_node_type",
    "relation",
    "target_node_id",
    "target_node_name",
    "target_node_type",
    "graph_source",
    "evidence",
    "status",
    "notes",
)
GRAPH_MAPPING_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "mapped_drug_node_id",
    "mapped_drug_node_name",
    "mapped_disease_node_id",
    "mapped_disease_node_name",
    "drug_mapped",
    "disease_mapped",
    "mapping_confidence",
    "mapping_method",
    "status",
    "error_message",
    "notes",
)
GRAPH_PATH_COLUMNS = (
    "pair_id",
    "path_id",
    "path_length",
    "path_nodes",
    "path_relations",
    "path_node_types",
    "graph_source",
    "path_score",
    "status",
    "notes",
)
GRAPH_FEATURE_COLUMNS = (
    "pair_id",
    "graph_source",
    "drug_name",
    "disease_name",
    "drug_mapped",
    "disease_mapped",
    "has_path",
    "shortest_path_length",
    "n_paths_len_2",
    "n_paths_len_3",
    "n_paths_len_4",
    "n_drug_target_disease_paths",
    "n_gene_mediated_paths",
    "graph_connectivity_score",
    "status",
    "error_message",
    "notes",
)
VALID_GRAPH_STATUSES = {"success", "partial_success", "failed", "skipped"}
GENE_LIKE_TYPES = {"gene", "protein", "gene/protein", "target"}


@dataclass(frozen=True)
class GraphData:
    """Normalized graph tables plus adjacency for path extraction."""

    graph_source: str
    nodes: pd.DataFrame
    edges: pd.DataFrame
    adjacency: dict[str, list[tuple[str, str]]]


@dataclass(frozen=True)
class NodeMapping:
    """Best-effort graph node mapping."""

    query_name: str
    node_type: str
    mapped: bool
    node_id: str = ""
    node_name: str = ""
    confidence: float = 0.0
    method: str = "unmapped"
    error_message: str = ""


class MissingGraphFilesError(FileNotFoundError):
    """Raised when no local graph files are available."""


def normalize_key(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip().casefold()
    return " ".join("".join(char if char.isalnum() else " " for char in text).split())


def normalize_type(value: object) -> str:
    text = normalize_key(value).replace(" ", "/")
    if text in {"drug", "compound", "chemical"}:
        return "drug"
    if text in {"disease", "condition", "indication", "phenotype/disease"}:
        return "disease"
    if text in {"gene", "protein", "gene/protein", "gene/protein"}:
        return "gene/protein"
    return text or "unknown"


def manual_graph_download_instructions(graph_source: str, graph_dir: str | Path) -> str:
    if graph_source == "primekg":
        source = (
            "Download PrimeKG from the official PrimeKG resources. The preferred local file is "
            "`kg.csv` with columns like relation, x_id, x_type, x_name, y_id, y_type, y_name. "
            "PrimeKG is described in Chandak et al., Scientific Data 10, 67 (2023), "
            "doi:10.1038/s41597-023-01960-3."
        )
    else:
        source = (
            "Place PharmKG node/edge CSV exports in the graph directory. Expected files are "
            "`nodes.csv` and `edges.csv`, or an edge list with source/target node fields."
        )
    return (
        f"Missing local {graph_source} graph files.\n"
        f"{source}\n"
        f"Place files under: {Path(graph_dir)}\n"
        "Do not use toy fixtures as real benchmark data."
    )


def load_graph_files(graph_source: str, graph_dir: str | Path) -> GraphData:
    """Load and normalize a local PrimeKG/PharmKG graph."""
    graph_root = Path(graph_dir)
    if not graph_root.exists():
        raise MissingGraphFilesError(manual_graph_download_instructions(graph_source, graph_root))

    nodes_file = _first_existing(graph_root, ("nodes.csv", "node.csv", "nodes.tsv", "nodes.tab"))
    edges_file = _first_existing(graph_root, ("kg.csv", "edges.csv", "edge.csv", "kg.tsv", "edges.tsv", "edges.tab", "kg.csv.gz"))
    if edges_file is None:
        csvs = sorted(list(graph_root.glob("*.csv")) + list(graph_root.glob("*.tsv")) + list(graph_root.glob("*.tab")) + list(graph_root.glob("*.csv.gz")))
        edges_file = csvs[0] if csvs else None
    if edges_file is None:
        raise MissingGraphFilesError(manual_graph_download_instructions(graph_source, graph_root))

    raw_edges = read_table(edges_file)
    if nodes_file:
        raw_nodes = read_table(nodes_file)
        nodes = normalize_nodes(raw_nodes, graph_source)
        edges = normalize_edges(raw_edges, graph_source, nodes)
    else:
        edges = normalize_edges(raw_edges, graph_source)
        nodes = nodes_from_edges(edges, graph_source)
    return GraphData(graph_source, nodes, edges, build_adjacency(edges))


def read_table(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    sep = "\t" if source.suffix.lower() in {".tsv", ".tab"} else ","
    return pd.read_csv(source, sep=sep, compression="infer", low_memory=False)


def _first_existing(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def normalize_nodes(raw_nodes: pd.DataFrame, graph_source: str) -> pd.DataFrame:
    node_id_col = find_column(raw_nodes, ("node_id", "id", "node_index", "index"))
    node_name_col = find_column(raw_nodes, ("node_name", "name", "label"))
    node_type_col = find_column(raw_nodes, ("node_type", "type", "category", "label_type"))
    synonyms_col = find_column(raw_nodes, ("synonyms", "synonym"), required=False)
    external_ids_col = find_column(raw_nodes, ("external_ids", "external_id", "xrefs"), required=False)
    rows = []
    for _, row in raw_nodes.iterrows():
        rows.append(
            {
                "node_id": str(row[node_id_col]),
                "node_name": str(row[node_name_col]),
                "node_type": normalize_type(row[node_type_col]),
                "graph_source": graph_source,
                "synonyms": str(row[synonyms_col]) if synonyms_col else "",
                "external_ids": str(row[external_ids_col]) if external_ids_col else "",
                "status": "success",
                "notes": "",
            }
        )
    return pd.DataFrame(rows, columns=GRAPH_NODE_COLUMNS).drop_duplicates("node_id").reset_index(drop=True)


def normalize_edges(raw_edges: pd.DataFrame, graph_source: str, nodes: pd.DataFrame | None = None) -> pd.DataFrame:
    if {"x_id", "x_type", "x_name", "y_id", "y_type", "y_name"}.issubset(raw_edges.columns):
        relation_col = "display_relation" if "display_relation" in raw_edges.columns else "relation" if "relation" in raw_edges.columns else None
        evidence_col = "relation" if "relation" in raw_edges.columns else None
        edges = pd.DataFrame(
            {
                "source_node_id": raw_edges["x_id"].fillna("").astype(str),
                "source_node_name": raw_edges["x_name"].fillna("").astype(str),
                "source_node_type": raw_edges["x_type"].map(normalize_type),
                "relation": raw_edges[relation_col].fillna("related_to").astype(str) if relation_col else "related_to",
                "target_node_id": raw_edges["y_id"].fillna("").astype(str),
                "target_node_name": raw_edges["y_name"].fillna("").astype(str),
                "target_node_type": raw_edges["y_type"].map(normalize_type),
                "graph_source": graph_source,
                "evidence": raw_edges[evidence_col].fillna("").astype(str) if evidence_col else "",
                "status": "success",
                "notes": "",
            }
        )
        return edges[list(GRAPH_EDGE_COLUMNS)].drop_duplicates().reset_index(drop=True)
    else:
        source_id_col = find_column(raw_edges, ("source_node_id", "source_id", "source", "head_id", "subject_id", "x_id"))
        target_id_col = find_column(raw_edges, ("target_node_id", "target_id", "target", "tail_id", "object_id", "y_id"))
        source_name_col = find_column(raw_edges, ("source_node_name", "source_name", "head_name", "subject_name", "x_name"), required=False)
        target_name_col = find_column(raw_edges, ("target_node_name", "target_name", "tail_name", "object_name", "y_name"), required=False)
        source_type_col = find_column(raw_edges, ("source_node_type", "source_type", "head_type", "subject_type", "x_type"), required=False)
        target_type_col = find_column(raw_edges, ("target_node_type", "target_type", "tail_type", "object_type", "y_type"), required=False)
    relation_col = find_column(raw_edges, ("relation", "display_relation", "predicate", "edge_type", "type"), required=False)
    evidence_col = find_column(raw_edges, ("evidence", "source", "sources", "reference"), required=False)
    node_lookup = nodes.set_index("node_id").to_dict("index") if nodes is not None and not nodes.empty else {}
    rows = []
    for _, row in raw_edges.iterrows():
        source_id = str(row[source_id_col])
        target_id = str(row[target_id_col])
        source_node = node_lookup.get(source_id, {})
        target_node = node_lookup.get(target_id, {})
        rows.append(
            {
                "source_node_id": source_id,
                "source_node_name": _row_value(row, source_name_col, source_node.get("node_name", source_id)),
                "source_node_type": normalize_type(_row_value(row, source_type_col, source_node.get("node_type", "unknown"))),
                "relation": str(row[relation_col]) if relation_col else "related_to",
                "target_node_id": target_id,
                "target_node_name": _row_value(row, target_name_col, target_node.get("node_name", target_id)),
                "target_node_type": normalize_type(_row_value(row, target_type_col, target_node.get("node_type", "unknown"))),
                "graph_source": graph_source,
                "evidence": str(row[evidence_col]) if evidence_col else "",
                "status": "success",
                "notes": "",
            }
        )
    return pd.DataFrame(rows, columns=GRAPH_EDGE_COLUMNS).drop_duplicates().reset_index(drop=True)


def _row_value(row: pd.Series, column: str | None, fallback: object) -> str:
    if column and column in row and not pd.isna(row[column]):
        return str(row[column])
    return str(fallback)


def nodes_from_edges(edges: pd.DataFrame, graph_source: str) -> pd.DataFrame:
    rows = []
    for prefix in ("source", "target"):
        rows.append(
            edges[[f"{prefix}_node_id", f"{prefix}_node_name", f"{prefix}_node_type"]].rename(
                columns={
                    f"{prefix}_node_id": "node_id",
                    f"{prefix}_node_name": "node_name",
                    f"{prefix}_node_type": "node_type",
                }
            )
        )
    nodes = pd.concat(rows, ignore_index=True).drop_duplicates("node_id")
    nodes["graph_source"] = graph_source
    nodes["synonyms"] = ""
    nodes["external_ids"] = ""
    nodes["status"] = "success"
    nodes["notes"] = ""
    return nodes[list(GRAPH_NODE_COLUMNS)].reset_index(drop=True)


def find_column(df: pd.DataFrame, candidates: Iterable[str], required: bool = True) -> str | None:
    normalized = {normalize_key(column): column for column in df.columns}
    for candidate in candidates:
        found = normalized.get(normalize_key(candidate))
        if found:
            return found
    if required:
        raise ValueError(f"Missing required graph column from candidates {list(candidates)}")
    return None


def build_adjacency(edges: pd.DataFrame) -> dict[str, list[tuple[str, str]]]:
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for _, edge in edges.iterrows():
        source = str(edge["source_node_id"])
        target = str(edge["target_node_id"])
        relation = str(edge["relation"])
        adjacency.setdefault(source, []).append((target, relation))
        adjacency.setdefault(target, []).append((source, relation))
    return adjacency


def map_entity_to_node(nodes: pd.DataFrame, name: str, expected_type: str) -> NodeMapping:
    expected = normalize_type(expected_type)
    candidates = nodes[nodes["node_type"] == expected].copy()
    query = normalize_key(name)
    if not query:
        return NodeMapping(name, expected, False, error_message="empty entity name")
    candidates["name_key"] = candidates["node_name"].map(normalize_key)
    exact = candidates[candidates["name_key"] == query]
    if not exact.empty:
        row = exact.iloc[0]
        return NodeMapping(name, expected, True, str(row["node_id"]), str(row["node_name"]), 1.0, "exact_name")
    synonym_match = find_synonym_match(candidates, query)
    if synonym_match is not None:
        row = synonym_match
        return NodeMapping(name, expected, True, str(row["node_id"]), str(row["node_name"]), 0.9, "synonym")
    return NodeMapping(name, expected, False, error_message=f"no {expected} graph node match")


def find_synonym_match(candidates: pd.DataFrame, query: str) -> pd.Series | None:
    for _, row in candidates.iterrows():
        synonyms = str(row.get("synonyms", ""))
        if not synonyms:
            continue
        values = [item.strip() for item in synonyms.replace("|", ";").split(";") if item.strip()]
        if query in {normalize_key(value) for value in values}:
            return row
    return None


def shortest_path(graph: GraphData, source_id: str, target_id: str, max_length: int) -> list[str]:
    if source_id == target_id:
        return [source_id]
    queue = deque([(source_id, [source_id])])
    visited = {source_id}
    while queue:
        current, path = queue.popleft()
        if len(path) - 1 >= max_length:
            continue
        for neighbor, _ in graph.adjacency.get(current, []):
            if neighbor in visited:
                continue
            new_path = path + [neighbor]
            if neighbor == target_id:
                return new_path
            visited.add(neighbor)
            queue.append((neighbor, new_path))
    return []


def top_k_simple_paths(graph: GraphData, source_id: str, target_id: str, max_length: int, top_k: int) -> list[list[str]]:
    paths: list[list[str]] = []
    queue = deque([[source_id]])
    expansions = 0
    max_expansions = 50000
    while queue and len(paths) < top_k and expansions < max_expansions:
        path = queue.popleft()
        current = path[-1]
        if len(path) - 1 >= max_length:
            continue
        for neighbor, _ in graph.adjacency.get(current, []):
            if neighbor in path:
                continue
            new_path = path + [neighbor]
            expansions += 1
            if neighbor == target_id:
                paths.append(new_path)
                if len(paths) >= top_k:
                    break
            else:
                queue.append(new_path)
            if expansions >= max_expansions:
                break
    return sorted(paths, key=lambda item: (len(item), item))[:top_k]


def path_relations(graph: GraphData, path: list[str]) -> list[str]:
    relations = []
    for left, right in zip(path, path[1:]):
        relation = next((rel for node, rel in graph.adjacency.get(left, []) if node == right), "related_to")
        relations.append(relation)
    return relations


def node_lookup(nodes: pd.DataFrame) -> dict[str, dict[str, Any]]:
    return {str(row["node_id"]): row.to_dict() for _, row in nodes.iterrows()}


def is_gene_mediated_path(path_types: list[str]) -> bool:
    return any(normalize_type(node_type) in GENE_LIKE_TYPES for node_type in path_types[1:-1])


def is_drug_target_disease_path(path_types: list[str]) -> bool:
    return len(path_types) == 3 and normalize_type(path_types[1]) in GENE_LIKE_TYPES


def path_score(path_length: int, max_path_length: int) -> float:
    if path_length <= 0:
        return 0.0
    return max(0.0, (max_path_length - path_length + 1) / max_path_length)


def process_graph_pair(
    pair: dict[str, Any],
    graph: GraphData,
    max_path_length: int,
    top_k_paths: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    pair_id = str(pair["pair_id"])
    drug_name = str(pair["drug_name"])
    disease_name = str(pair["disease_name"])
    drug = map_entity_to_node(graph.nodes, drug_name, "drug")
    disease = map_entity_to_node(graph.nodes, disease_name, "disease")
    errors = [msg for msg in (drug.error_message, disease.error_message) if msg]
    mapping_status = "success" if drug.mapped and disease.mapped else "partial_success" if drug.mapped or disease.mapped else "failed"
    confidence_values = [value for value in (drug.confidence, disease.confidence) if value > 0]
    mapping_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    mapping = {
        "pair_id": pair_id,
        "drug_name": drug_name,
        "disease_name": disease_name,
        "mapped_drug_node_id": drug.node_id,
        "mapped_drug_node_name": drug.node_name,
        "mapped_disease_node_id": disease.node_id,
        "mapped_disease_node_name": disease.node_name,
        "drug_mapped": drug.mapped,
        "disease_mapped": disease.mapped,
        "mapping_confidence": mapping_confidence,
        "mapping_method": "+".join(sorted({drug.method, disease.method} - {"unmapped"})) or "unmapped",
        "status": mapping_status,
        "error_message": " | ".join(errors),
        "notes": "Graph mapping only; not clinical evidence.",
    }
    paths: list[dict[str, Any]] = []
    shortest: list[str] = []
    if drug.mapped and disease.mapped:
        shortest = shortest_path(graph, drug.node_id, disease.node_id, max_path_length)
        raw_paths = top_k_simple_paths(graph, drug.node_id, disease.node_id, max_path_length, top_k_paths)
        lookup = node_lookup(graph.nodes)
        for index, path in enumerate(raw_paths, start=1):
            path_types = [str(lookup.get(node, {}).get("node_type", "unknown")) for node in path]
            path_names = [str(lookup.get(node, {}).get("node_name", node)) for node in path]
            length = len(path) - 1
            paths.append(
                {
                    "pair_id": pair_id,
                    "path_id": f"{pair_id}_path_{index}",
                    "path_length": length,
                    "path_nodes": json.dumps(path_names),
                    "path_relations": json.dumps(path_relations(graph, path)),
                    "path_node_types": json.dumps(path_types),
                    "graph_source": graph.graph_source,
                    "path_score": path_score(length, max_path_length),
                    "status": "success",
                    "notes": "Graph path only; not proof of drug efficacy.",
                }
            )
    feature = calculate_graph_features(pair, graph.graph_source, drug.mapped, disease.mapped, paths, shortest, max_path_length, errors)
    return mapping, paths, feature


def calculate_graph_features(
    pair: dict[str, Any],
    graph_source: str,
    drug_mapped: bool,
    disease_mapped: bool,
    paths: list[dict[str, Any]],
    shortest: list[str],
    max_path_length: int,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    path_lengths = [int(path["path_length"]) for path in paths]
    shortest_length = len(shortest) - 1 if shortest else 0
    gene_paths = 0
    dtd_paths = 0
    for path in paths:
        types = json.loads(path["path_node_types"])
        if is_gene_mediated_path(types):
            gene_paths += 1
        if is_drug_target_disease_path(types):
            dtd_paths += 1
    has_path = bool(paths)
    score = path_score(shortest_length, max_path_length) if has_path else 0.0
    if dtd_paths:
        score = min(1.0, score + 0.15)
    elif gene_paths:
        score = min(1.0, score + 0.05)
    if has_path and drug_mapped and disease_mapped:
        status = "success"
    elif drug_mapped or disease_mapped:
        status = "partial_success"
    else:
        status = "failed"
    return {
        "pair_id": str(pair["pair_id"]),
        "graph_source": graph_source,
        "drug_name": str(pair["drug_name"]),
        "disease_name": str(pair["disease_name"]),
        "drug_mapped": drug_mapped,
        "disease_mapped": disease_mapped,
        "has_path": has_path,
        "shortest_path_length": shortest_length,
        "n_paths_len_2": path_lengths.count(2),
        "n_paths_len_3": path_lengths.count(3),
        "n_paths_len_4": path_lengths.count(4),
        "n_drug_target_disease_paths": dtd_paths,
        "n_gene_mediated_paths": gene_paths,
        "graph_connectivity_score": score,
        "status": status,
        "error_message": " | ".join(errors or []),
        "notes": "Graph connectivity is mechanism support, not clinical efficacy.",
    }


def prepare_graph_outputs(
    pairs: pd.DataFrame,
    graph: GraphData,
    max_pairs: int | None,
    max_path_length: int,
    top_k_paths: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = pairs.head(max_pairs).copy() if max_pairs else pairs.copy()
    mappings: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    for _, pair in selected.iterrows():
        mapping, pair_paths, feature = process_graph_pair(pair.to_dict(), graph, max_path_length, top_k_paths)
        mappings.append(mapping)
        paths.extend(pair_paths)
        features.append(feature)
    return (
        graph.nodes[list(GRAPH_NODE_COLUMNS)],
        graph.edges[list(GRAPH_EDGE_COLUMNS)],
        pd.DataFrame(mappings, columns=GRAPH_MAPPING_COLUMNS),
        pd.DataFrame(paths, columns=GRAPH_PATH_COLUMNS),
        pd.DataFrame(features, columns=GRAPH_FEATURE_COLUMNS),
    )


def write_graph_outputs(
    output_dir: str | Path,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    mappings: pd.DataFrame,
    paths: pd.DataFrame,
    features: pd.DataFrame,
) -> None:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(root / "graph_nodes_normalized.csv", index=False)
    edges.to_csv(root / "graph_edges_normalized.csv", index=False)
    mappings.to_csv(root / "graph_pair_mappings.csv", index=False)
    paths.to_csv(root / "graph_pair_paths.csv", index=False)
    features.to_csv(root / "graph_pair_features.csv", index=False)
