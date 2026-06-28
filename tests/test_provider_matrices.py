import json
from pathlib import Path

from identity_mapper.matrix import ReductionMatrix

PROVIDER_DIR = Path("src/identity_mapper/providers")


def test_provider_matrices_are_valid_matrix_rows() -> None:
    templates = sorted(PROVIDER_DIR.glob("*/matrix.json"))

    assert templates

    for template_path in templates:
        template = json.loads(template_path.read_text(encoding="utf-8"))
        matrix = ReductionMatrix.from_mapping(template)

        assert matrix.provider
        assert matrix.invariant == "Identity"
        assert matrix.rows

        for row in matrix.rows:
            assert row.section
            assert row.domain
