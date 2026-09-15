#!/usr/bin/env python3
"""Stdlib regression tests for the collection-only history inventory generator.

The CLI parses required arguments at module import, so these tests inspect its literals
with AST rather than importing it. They do not invoke Git or inspect repository history.
All candidate values below are synthetic fixtures, never credentials.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("audit-history-publication.py")


def assignment(tree: ast.Module, name: str) -> ast.Assign:
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return node
    raise AssertionError(f"assignment {name!r} not found")


class AuditInventoryRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
        pattern_rows = ast.literal_eval(assignment(cls.tree, "patterns").value)
        cls.generic_assignment = re.compile(dict(pattern_rows)["generic_secret_assignment"])

    def test_generic_assignments_cover_common_quoted_and_unquoted_forms(self) -> None:
        fixtures = {
            "quoted JSON key": b'"api_key": "FixtureJsonValue123"',
            "quoted Python mapping key": b"'client_secret' : 'FixturePythonMap123'",
            "unquoted Python assignment": b'access_token = "FixturePythonValue123"',
            "case-insensitive spaced YAML": b"PASSWORD   :   FixtureYamlValue123",
        }
        for label, fixture in fixtures.items():
            with self.subTest(label=label):
                self.assertIsNotNone(self.generic_assignment.search(fixture))

    def test_generic_assignments_exclude_nonsecret_keys_and_short_values(self) -> None:
        fixtures = {
            "nonsecret key": b'display_name: "FixturePublicValue123"',
            "secret substring only": b'monkey = "FixturePublicValue123"',
            "value shorter than eight bytes": b'"api_key": "short7"',
        }
        for label, fixture in fixtures.items():
            with self.subTest(label=label):
                self.assertIsNone(self.generic_assignment.search(fixture))

    def test_stdout_machine_status_is_collection_only_and_not_assessed(self) -> None:
        status = ast.literal_eval(assignment(self.tree, "MACHINE_STATUS").value)
        self.assertEqual(
            status,
            {
                "collection_status": "COMPLETE",
                "assessment_status": "NOT_ASSESSED",
            },
        )

        summary_node = assignment(self.tree, "summary").value
        self.assertIsInstance(summary_node, ast.Dict)
        self.assertTrue(
            any(
                key is None and isinstance(value, ast.Name) and value.id == "MACHINE_STATUS"
                for key, value in zip(summary_node.keys, summary_node.values)
            ),
            "stdout summary must include MACHINE_STATUS",
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            print(json.dumps(status, sort_keys=True))
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["collection_status"], "COMPLETE")
        self.assertEqual(payload["assessment_status"], "NOT_ASSESSED")
        self.assertNotIn("PASS", payload.values())


if __name__ == "__main__":
    unittest.main()
