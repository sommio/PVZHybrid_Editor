from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_workflow_runs_free_hosted_python_test_gate():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "runs-on: ubuntu-latest" in workflow
    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "cache: pip" in workflow
    assert "cache-dependency-path: requirements-dev.txt" in workflow
    assert "python -m ruff check i18n.py i18n_audit.py tests" in workflow
    assert "python -m pytest -q" in workflow
