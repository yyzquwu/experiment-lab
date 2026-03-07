from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_demo_writes_showcase_artifacts(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)

    generate = _load_script_module("generate_data_module", repo_root / "scripts" / "generate_synthetic_data.py")
    run_demo = _load_script_module("run_demo_module", repo_root / "scripts" / "run_demo.py")

    generate.main()
    run_demo.main()

    expected_files = [
        tmp_path / "reports" / "case_1_signup.md",
        tmp_path / "reports" / "case_2_checkout_value.md",
        tmp_path / "reports" / "case_3_sequential_peeking.md",
        tmp_path / "reports" / "case_4_search_ctr.md",
        tmp_path / "reports" / "decision_memo.md",
        tmp_path / "reports" / "methods_appendix.md",
        tmp_path / "reports" / "figures" / "signup_segment_lift.png",
        tmp_path / "reports" / "figures" / "sequential_interim_path.png",
        tmp_path / "reports" / "figures" / "search_ratio_guardrails.png",
        tmp_path / "case_studies" / "README.md",
    ]
    for path in expected_files:
        assert path.exists(), f"Expected artifact was not written: {path}"
