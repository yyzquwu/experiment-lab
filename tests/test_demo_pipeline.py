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

    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    hillstrom_processed = raw_dir / "hillstrom_experiment.csv"
    hillstrom_processed.write_text(
        "\n".join(
            [
                "user_id,variant,timestamp,pre_metric,segment,channel,history,recency,mens,womens,newbie,outcome_conversion,outcome_spend",
                "1,control,2008-03-20 00:00:00,120.0,1) $0 - $100,Web,120.0,5,1,0,0,0,0.0",
                "2,treatment,2008-03-20 00:01:00,210.0,3) $200 - $350,Phone,210.0,7,0,1,1,1,35.0",
                "3,control,2008-03-20 00:02:00,150.0,2) $100 - $200,Web,150.0,6,1,1,0,0,0.0",
                "4,treatment,2008-03-20 00:03:00,260.0,4) $350 - $500,Phone,260.0,3,0,1,1,1,48.0",
                "5,control,2008-03-20 00:04:00,130.0,1) $0 - $100,Web,130.0,8,1,0,0,0,0.0",
                "6,treatment,2008-03-20 00:05:00,280.0,4) $350 - $500,Phone,280.0,2,0,1,1,1,52.0",
            ]
        ),
        encoding="utf-8",
    )

    generate.main()
    run_demo.main()

    expected_files = [
        tmp_path / "reports" / "case_1_hillstrom_conversion.md",
        tmp_path / "reports" / "case_2_hillstrom_spend.md",
        tmp_path / "reports" / "case_3_sequential_peeking.md",
        tmp_path / "reports" / "case_4_search_ctr.md",
        tmp_path / "reports" / "decision_memo.md",
        tmp_path / "reports" / "methods_appendix.md",
        tmp_path / "reports" / "figures" / "hillstrom_conversion_interim_path.png",
        tmp_path / "reports" / "figures" / "sequential_interim_path.png",
        tmp_path / "reports" / "figures" / "search_ratio_guardrails.png",
        tmp_path / "case_studies" / "README.md",
    ]
    for path in expected_files:
        assert path.exists(), f"Expected artifact was not written: {path}"
