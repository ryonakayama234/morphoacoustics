"""Reproduce bounded SMC/Core Gate A receipt; writes JSON to stdout, no WAV."""
from __future__ import annotations
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "speech-motor-compiler" / "tests"))

from test_smc5_preregistered import encoded, valid
from binding_preflight import audit_smc_core_binding


def rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def main() -> int:
    receipt = audit_smc_core_binding(encoded(valid()))
    data = {
        "schema": "cvi1-smc-core-preflight-receipt/v0",
        "evidence_class": "synthetic_formal_compatibility_only",
        "smc6_ancestry_commit": "0caa70f6bb8333f60fbcc2f29ea57578c998033c",
        "stage_a": receipt.stage_a,
        "stage_b": receipt.stage_b,
        "reason": receipt.reason,
        "canonical_request_sha256": receipt.canonical_request_sha256,
        "candidate_digest": receipt.candidate_digest,
        "source_timing_digest": receipt.source_timing_digest,
        "task_count": len(receipt.tasks),
        "exact_event_count": len(receipt.exact_events),
        "physical_coverage": {"supported": receipt.physical_coverage[0],
                              "required": receipt.physical_coverage[1]},
        "tasks": [
            {
                "task_id": t.task_id,
                "definition_id": t.definition_id,
                "semantic_revision": t.semantic_revision,
                "goal_kind": t.goal_kind,
                "variable": t.variable,
                "value_domain": t.value_domain,
                "applicability_domain": t.applicability_domain,
                "capabilities": list(t.capabilities),
                "goal_interval": [rational(t.lower), rational(t.upper)],
                "members": [list(m) for m in t.members],
                "physical_binding_verified": False,
            }
            for t in receipt.tasks
        ],
        "exact_smc_events": [
            {
                "task_id": tid,
                "event": ev.value,
                "earliest_s": rational(lo),
                "latest_s": rational(hi),
                "selected_s": rational(selected),
                "NOT_a_measured_articulator_event": True,
            }
            for tid, ev, lo, hi, selected in receipt.exact_events
        ],
        "physical_trace": None,
        "acoustic_trace": None,
        "take": None,
        "physical_or_perceptual_conclusion": "NOT_TESTED",
    }
    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if (receipt.stage_a == "FORMAL_AUTHENTICATED"
                 and receipt.stage_b == "UNMAPPED_SEMANTICS"
                 and receipt.physical_coverage == (0, 3)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
