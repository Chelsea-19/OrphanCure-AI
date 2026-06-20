"""Tests for graph benchmark utilities using synthetic graph fixtures only."""

from pathlib import Path

import pandas as pd

from app.evaluation.graph_benchmark import (
    GRAPH_EDGE_COLUMNS,
    GRAPH_FEATURE_COLUMNS,
    GRAPH_MAPPING_COLUMNS,
    GRAPH_NODE_COLUMNS,
    GRAPH_PATH_COLUMNS,
    MissingGraphFilesError,
    calculate_graph_features,
    load_graph_files,
    map_entity_to_node,
    prepare_graph_outputs,
    shortest_path,
    top_k_simple_paths,
)
from app.evaluation.repodb_benchmark import validate_benchmark_files


def write_toy_primekg(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "relation": "drug_targets_gene",
                "x_id": "drug_aspirin",
                "x_type": "drug",
                "x_name": "Aspirin",
                "y_id": "gene_ptgs1",
                "y_type": "gene/protein",
                "y_name": "PTGS1",
            },
            {
                "relation": "gene_associated_with_disease",
                "x_id": "gene_ptgs1",
                "x_type": "gene/protein",
                "x_name": "PTGS1",
                "y_id": "disease_pain",
                "y_type": "disease",
                "y_name": "Pain",
            },
            {
                "relation": "drug_related_gene",
                "x_id": "drug_metformin",
                "x_type": "drug",
                "x_name": "Metformin",
                "y_id": "gene_ampk",
                "y_type": "gene/protein",
                "y_name": "AMPK",
            },
        ]
    ).to_csv(root / "kg.csv", index=False)


def toy_pairs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Aspirin",
                "disease_name": "Pain",
                "raw_status": "Approved",
                "expected_label": "positive",
                "source": "fixture",
                "source_id": "row:1",
                "notes": "",
            },
            {
                "pair_id": "p2",
                "drug_name": "Missing Drug",
                "disease_name": "Pain",
                "raw_status": "Terminated",
                "expected_label": "negative_or_failed",
                "source": "fixture",
                "source_id": "row:2",
                "notes": "",
            },
        ]
    )


def test_graph_node_and_edge_loading_and_normalization(tmp_path):
    write_toy_primekg(tmp_path)
    graph = load_graph_files("primekg", tmp_path)
    assert set(graph.nodes.columns) == set(GRAPH_NODE_COLUMNS)
    assert set(graph.edges.columns) == set(GRAPH_EDGE_COLUMNS)
    assert "drug_aspirin" in set(graph.nodes["node_id"])
    assert "disease_pain" in set(graph.nodes["node_id"])


def test_drug_and_disease_name_mapping(tmp_path):
    write_toy_primekg(tmp_path)
    graph = load_graph_files("primekg", tmp_path)
    drug = map_entity_to_node(graph.nodes, "aspirin", "drug")
    disease = map_entity_to_node(graph.nodes, "Pain", "disease")
    assert drug.mapped
    assert disease.mapped
    assert drug.node_id == "drug_aspirin"


def test_shortest_and_top_k_paths(tmp_path):
    write_toy_primekg(tmp_path)
    graph = load_graph_files("primekg", tmp_path)
    path = shortest_path(graph, "drug_aspirin", "disease_pain", max_length=4)
    paths = top_k_simple_paths(graph, "drug_aspirin", "disease_pain", max_length=4, top_k=10)
    assert path == ["drug_aspirin", "gene_ptgs1", "disease_pain"]
    assert paths[0] == path


def test_graph_feature_calculation():
    feature = calculate_graph_features(
        {"pair_id": "p1", "drug_name": "Aspirin", "disease_name": "Pain"},
        "primekg",
        True,
        True,
        [
            {
                "path_length": 2,
                "path_node_types": '["drug", "gene/protein", "disease"]',
            }
        ],
        ["drug_aspirin", "gene_ptgs1", "disease_pain"],
        max_path_length=4,
    )
    assert feature["has_path"]
    assert feature["n_drug_target_disease_paths"] == 1
    assert feature["n_gene_mediated_paths"] == 1
    assert feature["graph_connectivity_score"] > 0


def test_missing_graph_file_behavior(tmp_path):
    missing = tmp_path / "missing"
    try:
        load_graph_files("primekg", missing)
    except MissingGraphFilesError as exc:
        assert "Missing local primekg graph files" in str(exc)
    else:
        raise AssertionError("Expected MissingGraphFilesError")


def test_unmapped_drug_and_normalized_output_schema(tmp_path):
    write_toy_primekg(tmp_path)
    graph = load_graph_files("primekg", tmp_path)
    nodes, edges, mappings, paths, features = prepare_graph_outputs(toy_pairs(), graph, max_pairs=2, max_path_length=4, top_k_paths=10)
    assert list(nodes.columns) == list(GRAPH_NODE_COLUMNS)
    assert list(edges.columns) == list(GRAPH_EDGE_COLUMNS)
    assert list(mappings.columns) == list(GRAPH_MAPPING_COLUMNS)
    assert list(paths.columns) == list(GRAPH_PATH_COLUMNS)
    assert list(features.columns) == list(GRAPH_FEATURE_COLUMNS)
    missing = features[features["pair_id"] == "p2"].iloc[0]
    assert not missing["drug_mapped"]
    assert missing["status"] == "partial_success"
    assert "no drug graph node match" in missing["error_message"]


def test_graph_validation_failure_when_required_columns_missing(tmp_path):
    pairs = tmp_path / "pairs.csv"
    split = tmp_path / "split.csv"
    nodes = tmp_path / "nodes.csv"
    edges = tmp_path / "edges.csv"
    mappings = tmp_path / "mappings.csv"
    paths = tmp_path / "paths.csv"
    features = tmp_path / "features.csv"
    toy_pairs().head(1).to_csv(pairs, index=False)
    pd.DataFrame([{"pair_id": "p1", "split": "test"}]).to_csv(split, index=False)
    pd.DataFrame([{"node_id": "n1"}]).to_csv(nodes, index=False)
    pd.DataFrame([{"source_node_id": "n1"}]).to_csv(edges, index=False)
    pd.DataFrame([{"pair_id": "p1"}]).to_csv(mappings, index=False)
    pd.DataFrame([{"pair_id": "p1"}]).to_csv(paths, index=False)
    pd.DataFrame([{"pair_id": "p1"}]).to_csv(features, index=False)
    errors = validate_benchmark_files(
        pairs,
        split,
        graph_nodes_path=nodes,
        graph_edges_path=edges,
        graph_mappings_path=mappings,
        graph_paths_path=paths,
        graph_features_path=features,
    )
    assert any("graph nodes file is missing required columns" in error for error in errors)
    assert any("graph edges file is missing required columns" in error for error in errors)
    assert any("graph mappings file is missing required columns" in error for error in errors)
    assert any("graph paths file is missing required columns" in error for error in errors)
    assert any("graph features file is missing required columns" in error for error in errors)

