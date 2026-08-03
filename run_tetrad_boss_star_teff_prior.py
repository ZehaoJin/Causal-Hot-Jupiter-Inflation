"""Run Tetrad BOSS with configurable restrictions on parents of star_teff."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import pydot


os.environ.setdefault("JAVA_HOME", "/home/zhengyujia/.local/tetrad-jdk")
os.environ["PATH"] = f"{os.environ['JAVA_HOME']}/bin:{os.environ['PATH']}"

from pytetrad.tools.TetradSearch import TetradSearch  # noqa: E402


INPUT_CSV = Path(os.environ.get("TETRAD_BOSS_INPUT_CSV", "hot_jupiters_20260403.csv"))
OUTPUT_DIR = Path(os.environ.get("TETRAD_BOSS_OUTPUT_DIR", "results/tetrad_boss_star_teff_not_child"))
VARIABLES = tuple(
    os.environ.get("TETRAD_BOSS_VARIABLES", "mass,radius,star_teff,orbital_period").split(",")
)
SCORE = os.environ.get("TETRAD_BOSS_SCORE", "sem_bic")
TARGET_WITH_NO_PARENTS = "star_teff"
ALLOWED_TARGET_PARENTS = frozenset(
    filter(None, os.environ.get("TETRAD_BOSS_ALLOWED_TARGET_PARENTS", "star_age").split(","))
)
ROOT_CAUSES = frozenset(
    filter(None, os.environ.get("TETRAD_BOSS_ROOT_CAUSES", "star_age").split(","))
)
PUBLICATION_LABELS = {
    "orbital_period": "<I>P</I><SUB>orb</SUB>",
    "mass": "<I>M</I><SUB><I>p</I></SUB>",
    "radius": "<I>R</I><SUB><I>p</I></SUB>",
    "star_teff": "<I>T</I><SUB>eff</SUB>",
}


def apply_publication_labels(graph: pydot.Dot, variables: tuple[str, ...]) -> None:
    """Apply manuscript labels to the Tetrad-generated Graphviz graph."""
    existing_nodes = {node.get_name().strip('"') for node in graph.get_nodes()}
    for variable in variables:
        if variable not in existing_nodes:
            graph.add_node(pydot.Node(variable))

    for node in graph.get_nodes():
        name = node.get_name().strip('"')
        label = PUBLICATION_LABELS.get(name)
        if label is not None:
            node.set("label", f"<{label}>")


def main() -> None:
    """Run constrained Tetrad BOSS and save graph artifacts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV, index_col=0)
    if "mean_density" in VARIABLES:
        df["mean_density"] = df["mass"] / (df["radius"] ** 3)
    if "F_inc" in VARIABLES:
        df["F_inc"] = (df["star_teff"] ** 4) * (df["star_mass"] ** 0.93) * (
            df["orbital_period"] ** (-4 / 3)
        )

    selected = df.loc[:, VARIABLES].apply(pd.to_numeric, errors="coerce").dropna()
    standardized = (selected - selected.mean()) / selected.std(ddof=0)
    selected.to_csv(OUTPUT_DIR / "selected_complete_cases.csv")
    standardized.to_csv(OUTPUT_DIR / "selected_complete_cases_standardized.csv")

    search = TetradSearch(standardized)
    if SCORE == "sem_bic":
        search.use_sem_bic(penalty_discount=2)
        score_summary = {"name": "SEM-BIC", "penalty_discount": 2}
    elif SCORE == "basis_function_bic":
        search.use_basis_function_bic(
            truncation_limit=3,
            penalty_discount=2,
            singularity_lambda=0.0,
            do_one_equation_only=False,
        )
        score_summary = {
            "name": "Basis Function BIC",
            "truncation_limit": 3,
            "penalty_discount": 2,
            "singularity_lambda": 0.0,
            "do_one_equation_only": False,
        }
    elif SCORE == "basis_function_bic_fs":
        search.use_basis_function_bic_fs(
            truncation_limit=3,
            penalty_discount=2,
            singularity_lambda=0.0,
            do_one_equation_only=False,
        )
        score_summary = {
            "name": "Basis Function BIC Full Sample",
            "truncation_limit": 3,
            "penalty_discount": 2,
            "singularity_lambda": 0.0,
            "do_one_equation_only": False,
        }
    elif SCORE == "trff_bic":
        search.use_trff_bic(
            trff_ridge=0.001,
            ffml_ff_features=100,
            penalty_discount=1,
            trff_nu=5.0,
        )
        score_summary = {
            "name": "TRFF-BIC",
            "trff_ridge": 0.001,
            "ffml_ff_features": 100,
            "penalty_discount": 1,
            "trff_nu": 5.0,
        }
    elif SCORE == "ffml":
        search.use_ffml(
            ffml_ridge=1.0,
            bw_max_rows=100,
            ffml_ff_features=50,
            cat_rho=0.5,
            effective_sample_size=-1,
        )
        score_summary = {
            "name": "FFML",
            "ffml_ridge": 1.0,
            "bw_max_rows": 100,
            "ffml_ff_features": 50,
            "cat_rho": 0.5,
            "effective_sample_size": -1,
        }
    else:
        raise ValueError(f"Unsupported TETRAD_BOSS_SCORE: {SCORE}")

    forbidden_edges: list[dict[str, str]] = []
    forbidden_pairs: set[tuple[str, str]] = set()
    prior_rules: list[str] = []

    def forbid_edge(parent: str, child: str) -> None:
        """Forbid one directed edge without recording duplicates."""
        pair = (parent, child)
        if pair in forbidden_pairs:
            return
        search.set_forbidden(parent, child)
        forbidden_pairs.add(pair)
        forbidden_edges.append({"source": parent, "target": child})

    if TARGET_WITH_NO_PARENTS in VARIABLES:
        allowed_parents = sorted(ALLOWED_TARGET_PARENTS.intersection(VARIABLES))
        prior_rules.append(
            f"{TARGET_WITH_NO_PARENTS} cannot be a child of selected variables "
            f"except {allowed_parents}"
        )
        for parent in VARIABLES:
            if parent == TARGET_WITH_NO_PARENTS or parent in ALLOWED_TARGET_PARENTS:
                continue
            forbid_edge(parent, TARGET_WITH_NO_PARENTS)

    for root_cause in sorted(ROOT_CAUSES.intersection(VARIABLES)):
        prior_rules.append(f"{root_cause} cannot be a child of any other selected variable")
        for parent in VARIABLES:
            if parent != root_cause:
                forbid_edge(parent, root_cause)

    prior = "; ".join(prior_rules) or None

    search.run_boss(num_starts=1, use_bes=False, use_data_order=True, output_cpdag=True)

    graph_text = str(search.get_string())
    graph_dot = search.get_dot()
    graph_matrix = search.get_graph_to_matrix()
    graph_matrix.index = VARIABLES
    graph_matrix.columns = VARIABLES

    graphs = pydot.graph_from_dot_data(graph_dot)
    if not graphs:
        raise RuntimeError("Tetrad returned DOT text that pydot could not parse.")
    graph = graphs[0]
    apply_publication_labels(graph, VARIABLES)

    edges = []
    for edge in graph.get_edges():
        arrowtail = edge.get("arrowtail")
        arrowhead = edge.get("arrowhead")
        edge_type = "directed" if arrowtail == "none" and arrowhead == "normal" else "undirected"
        edges.append(
            {
                "source": edge.get_source().strip('"'),
                "target": edge.get_destination().strip('"'),
                "edge_type": edge_type,
            }
        )

    (OUTPUT_DIR / "knowledge.txt").write_text(str(search.get_knowledge()), encoding="utf-8")
    (OUTPUT_DIR / "graph.txt").write_text(graph_text, encoding="utf-8")
    (OUTPUT_DIR / "graph.dot").write_text(graph.to_string(), encoding="utf-8")
    graph.write_png(OUTPUT_DIR / "graph.png")
    graph.write_pdf(OUTPUT_DIR / "graph.pdf")
    graph_matrix.to_csv(OUTPUT_DIR / "adjacency_matrix.csv")
    pd.DataFrame(edges).to_csv(OUTPUT_DIR / "edges.csv", index=False)
    pd.DataFrame(forbidden_edges).to_csv(OUTPUT_DIR / "forbidden_edges.csv", index=False)

    summary = {
        "algorithm": "Tetrad BOSS",
        "input_path": str(INPUT_CSV),
        "score": score_summary,
        "variables": list(VARIABLES),
        "n_rows_original": int(df.shape[0]),
        "n_rows_complete": int(selected.shape[0]),
        "n_rows_dropped": int(df.shape[0] - selected.shape[0]),
        "prior": prior,
        "forbidden_edges": forbidden_edges,
        "edges": edges,
        "outputs": {
            "graph_png": str(OUTPUT_DIR / "graph.png"),
            "graph_pdf": str(OUTPUT_DIR / "graph.pdf"),
            "graph_dot": str(OUTPUT_DIR / "graph.dot"),
            "graph_text": str(OUTPUT_DIR / "graph.txt"),
            "adjacency_matrix": str(OUTPUT_DIR / "adjacency_matrix.csv"),
            "edges": str(OUTPUT_DIR / "edges.csv"),
        },
    }
    (OUTPUT_DIR / "tetrad_boss_results_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
