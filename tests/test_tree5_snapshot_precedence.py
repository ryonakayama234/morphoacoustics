"""Frozen A1.3 Snapshot phase ordering, independent of production selectors.

Use only unittest so the R5 failure can also be reproduced without pytest.
The full repository's pytest runner collects this same TestCase.
"""
from __future__ import annotations

import copy
from itertools import combinations
import json
from pathlib import Path
import unittest

from morphoacoustics_graph.tree5 import Tree5Error, prepare_tree5, restore_tree5


FIX = json.loads((Path(__file__).resolve().parents[1] /
                  "docs/research/og5-contract-goldens.json").read_text())
MARKERS = ("schema", "digest_version", "backend_id", "blueprint.schema")
COMBINATIONS = tuple(group for size in range(1, 5)
                     for group in combinations(MARKERS, size))


def snapshot_with(markers: tuple[str, ...]) -> dict:
    value = copy.deepcopy(FIX["blueprint_snapshot_variants"]["baseline"]["snapshot"])
    for marker in markers:
        if marker == "blueprint.schema":
            value["blueprint"]["schema"] = "future"
        else:
            value[marker] = "future"
    return value


def expected_capability(markers: tuple[str, ...]) -> tuple[str, str]:
    # Literal reference to A1.3's groups and ASCII ordering, not a shared helper.
    if "digest_version" in markers:
        return "VERSION_NOT_SUPPORTED", "/digest_version"
    if "schema" in markers:
        return "VERSION_NOT_SUPPORTED", "/schema"
    if "backend_id" in markers:
        return "BACKEND_NOT_SUPPORTED", "/backend_id"
    return "VERSION_NOT_SUPPORTED", "/blueprint/schema"


class TestSnapshotPrecedence(unittest.TestCase):
    def assert_restore_refusal(self, value, status, code, path):
        with self.assertRaises(Tree5Error) as failure:
            restore_tree5(value)
        self.assertEqual(failure.exception.receipt(),
                         {"status": status, "code": code, "path": path})

    def test_all_outer_and_nested_marker_combinations(self):
        for markers in COMBINATIONS:
            with self.subTest(markers=markers):
                self.assert_restore_refusal(snapshot_with(markers), "UNSUPPORTED",
                                            *expected_capability(markers))

    def test_nested_shape_errors_precede_outer_capability(self):
        for markers in COMBINATIONS:
            with self.subTest(markers=markers):
                value = snapshot_with(markers)
                value["blueprint"]["organs"][0]["length_m"] = True
                self.assert_restore_refusal(value, "INVALID", "INVALID_NUMBER",
                                            "/blueprint/organs/0/length_m")

    def test_nested_relationship_errors_precede_outer_capability(self):
        for markers in COMBINATIONS:
            with self.subTest(markers=markers):
                value = snapshot_with(markers)
                value["blueprint"]["junctions"][0]["ports"][0] = "missing"
                self.assert_restore_refusal(value, "INVALID", "UNKNOWN_PORT",
                                            "/blueprint/junctions/0/ports/0")

    def test_outer_digest_syntax_precedes_capability(self):
        for markers in COMBINATIONS:
            with self.subTest(markers=markers):
                value = snapshot_with(markers)
                value["blueprint_digest"] = "not-a-digest"
                self.assert_restore_refusal(value, "INVALID", "INVALID_STRING",
                                            "/blueprint_digest")

    def test_capability_precedes_identity_then_blueprint_hash_precedes_preparation(self):
        for markers in COMBINATIONS:
            with self.subTest(markers=markers):
                value = snapshot_with(markers)
                value["blueprint_digest"] = value["preparation_digest"] = "sha256:" + "0" * 64
                self.assert_restore_refusal(value, "UNSUPPORTED", *expected_capability(markers))
        value = snapshot_with(())
        value["blueprint_digest"] = value["preparation_digest"] = "sha256:" + "0" * 64
        self.assert_restore_refusal(value, "INVALID", "IDENTITY_MISMATCH", "/blueprint_digest")
        value = snapshot_with(())
        value["preparation_digest"] = "sha256:" + "0" * 64
        self.assert_restore_refusal(value, "INVALID", "IDENTITY_MISMATCH", "/preparation_digest")

    def test_receiver_binding_precedes_invalid_request(self):
        prepared = prepare_tree5(copy.deepcopy(FIX["blueprint_snapshot_variants"]["baseline"]["input"]))
        object.__setattr__(prepared, "_snapshot_json", json.dumps(snapshot_with(MARKERS)))
        with self.assertRaises(Tree5Error) as failure:
            prepared.response([True])
        self.assertEqual(failure.exception.receipt(), {
            "status": "INVALID", "code": "PREPARED_BINDING_INVALID", "path": "/prepared"})


if __name__ == "__main__":
    unittest.main()
