import json
from pathlib import Path


TEMPLATE_DIR = Path("docs/reduction-templates")


def test_reduction_templates_are_valid_matrix_rows() -> None:
    templates = sorted(TEMPLATE_DIR.glob("*.json"))

    assert templates

    for template_path in templates:
        template = json.loads(template_path.read_text(encoding="utf-8"))

        assert template["invariant"] == "Identity"
        assert template["rows"]

        for row in template["rows"]:
            assert row["section"]
            assert row["domain"]
            assert ("source" in row) ^ ("literal" in row)
