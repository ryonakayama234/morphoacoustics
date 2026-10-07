from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
from pathlib import Path
from types import ModuleType

import numpy as np

from morphoacoustics.domain.creature import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
)
from morphoacoustics.domain.result import (
    FeasibilityIssue,
    FeasibilityReport,
    FeasibilityStatus,
)
from morphoacoustics.physical import Tract1DGeometry
from morphoacoustics.preparation import (
    PreparationProvenance,
    PreparedMorphology,
    prepare_tract1d,
)
from morphoacoustics.preparation.tract1d import TRACT1D_BACKEND_ID

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "v3c_oracle.json"
ORACLE_GIT_BLOB_SHA = "91e8041568bf61c8f828a32176b72f720e4bd646"

OUTLET_LOCATION = 1.0
ORAL_SHAPER_KIND = "oral-shaper"
LIP_KIND = "lip"
ORAL_REACH_START = 0.0
LIP_REACH_START = 0.95
LIP_REACH_END = 1.0
MARGIN_ABS_TOLERANCE = 1.0e-15
EXPECTED_UNREACHABLE_ISSUE_CODE = "LOCATION_UNREACHABLE"
EXPECTED_UNREACHABLE_TASK_INDEX = 1

CONDITIONS = (
    ("M_plus", 0.75, FeasibilityStatus.FEASIBLE),
    ("M_boundary", 0.7167402543883221, FeasibilityStatus.FEASIBLE),
    ("M_minus", 0.70, FeasibilityStatus.INFEASIBLE),
)

SUPPORT_DECISION = "SUPPORT_PHONETIC_EMBODIED_INFEASIBILITY"


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP28 = load_experiment_module(
    "morpho_exp028_for_029",
    EXPERIMENTS / "028_task_field_morphology_transfer" / "run.py",
)
EXP27 = EXP28.EXP27
EXP26 = EXP28.EXP26


@dataclass(slots=True)
class ConditionResult:
    feasibility: FeasibilityReport
    endpoint: Tract1DGeometry | None
    waveform: np.ndarray | None
    acoustic_call_count: int


class CountingTransfer:
    """Instrument actual transfer evaluations on the V3a acoustic path."""

    def __init__(self) -> None:
        self.call_count = 0

    def evaluate(
        self,
        geometry: Tract1DGeometry,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        self.call_count += 1
        return EXP26.EXP9.far_field_pressure_transfer(
            geometry,
            frequencies_hz,
        )


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    payload = f"blob {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(payload).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def task_plan_payload() -> list[dict[str, object]]:
    return EXP27.task_plan_payload()


def policy_payload() -> dict[str, object]:
    return {
        "outlet_location": OUTLET_LOCATION,
        "outlet_articulator_kind": LIP_KIND,
        "interior_articulator_kind": ORAL_SHAPER_KIND,
        "supported_task_kinds": ["OPEN", "CONSTRICT"],
        "reach_interval_semantics": "inclusive",
    }


def fixture_payload() -> dict[str, object]:
    return {
        "total_length_m": 0.16,
        "section_count": 16,
        "section_length_m": 0.01,
        "oral_shaper_reachable_start": ORAL_REACH_START,
        "lip_reachable_start": LIP_REACH_START,
        "lip_reachable_end": LIP_REACH_END,
    }


def frozen_gate_payload() -> dict[str, object]:
    return {
        "margin_abs_tolerance": MARGIN_ABS_TOLERANCE,
        "expected_unreachable_issue_code": EXPECTED_UNREACHABLE_ISSUE_CODE,
        "expected_unreachable_task_index": EXPECTED_UNREACHABLE_TASK_INDEX,
        "infeasible_acoustic_call_count": 0,
        "require_feasible_endpoint_exact_equality": True,
        "require_feasible_waveform_exact_equality": True,
    }


def condition_payloads() -> list[dict[str, object]]:
    target = EXP27.TASKS[EXPECTED_UNREACHABLE_TASK_INDEX]
    total_length = fixture_payload()["total_length_m"]
    rows: list[dict[str, object]] = []
    for name, reachable_end, expected in CONDITIONS:
        margin = reachable_end - target.location
        rows.append(
            {
                "condition": name,
                "oral_shaper_reachable_end": reachable_end,
                "target_task_index": EXPECTED_UNREACHABLE_TASK_INDEX,
                "target_location": target.location,
                "normalized_margin": margin,
                "metric_margin_m": margin * float(total_length),
                "expected_status": expected.value,
            }
        )
    return rows


def local_oracle_preflight(oracle: dict[str, object]) -> dict[str, object]:
    current_task_plan = task_plan_payload()
    checks = {
        "oracle_blob_is_frozen": git_blob_sha1(ORACLE_PATH) == ORACLE_GIT_BLOB_SHA,
        "task_plan_matches_oracle": current_task_plan == oracle.get("task_plan"),
        "task_plan_representation_clean": EXP27.representation_is_clean(
            current_task_plan
        ),
        "fixture_matches_oracle": fixture_payload() == oracle.get("fixture"),
        "policy_matches_oracle": policy_payload()
        == oracle.get("capability_policy"),
        "frozen_gate_matches_oracle": frozen_gate_payload()
        == oracle.get("frozen_gate"),
    }
    return {
        "checks": checks,
        "pass": all(checks.values()),
        "task_plan_sha256": sha256_json(current_task_plan),
        "oracle_git_blob_sha": git_blob_sha1(ORACLE_PATH),
    }


def creature_for(
    *,
    cavity_id: str,
    oral_reachable_end: float,
) -> CreatureSpec:
    return CreatureSpec(
        name="v3c-calibrated-reach-body",
        cavities=(CavitySpec(id=cavity_id, kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="oral-shaper",
                cavity_id=cavity_id,
                kind=ORAL_SHAPER_KIND,
                reachable_start=ORAL_REACH_START,
                reachable_end=oral_reachable_end,
            ),
            ArticulatorSpec(
                id="lip",
                cavity_id=cavity_id,
                kind=LIP_KIND,
                reachable_start=LIP_REACH_START,
                reachable_end=LIP_REACH_END,
            ),
        ),
    )


def prepared_for(
    *,
    creature: CreatureSpec,
    geometry: Tract1DGeometry,
    condition: str,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        geometry,
        provenance=PreparationProvenance(
            source="experiment-029",
            model="v3c-reachability-boundary",
            notes=(
                f"condition={condition}",
                "same-calibrated-a-rest-geometry",
                "only-oral-shaper-reachable-end-varies",
            ),
        ),
    )


def required_articulator_kind(task: object) -> str:
    location = float(getattr(task, "location"))
    return LIP_KIND if location == OUTLET_LOCATION else ORAL_SHAPER_KIND


def validate_prepared(
    morphology: PreparedMorphology[Tract1DGeometry],
) -> tuple[FeasibilityIssue, ...]:
    issues: list[FeasibilityIssue] = []
    if morphology.backend_id != TRACT1D_BACKEND_ID:
        issues.append(
            FeasibilityIssue(
                code="PREPARED_BACKEND_MISMATCH",
                message=(
                    f"expected {TRACT1D_BACKEND_ID!r}, "
                    f"got {morphology.backend_id!r}"
                ),
            )
        )
    cavity_ids = {cavity.id for cavity in morphology.creature.cavities}
    if morphology.rest_state.cavity_id not in cavity_ids:
        issues.append(
            FeasibilityIssue(
                code="PREPARED_GEOMETRY_CAVITY_UNKNOWN",
                message="prepared rest geometry cavity is absent from CreatureSpec",
            )
        )
    return tuple(issues)


def capability_report(
    morphology: PreparedMorphology[Tract1DGeometry],
) -> FeasibilityReport:
    invalid = validate_prepared(morphology)
    if invalid:
        return FeasibilityReport(
            status=FeasibilityStatus.INVALID,
            issues=invalid,
        )

    cavity_id = morphology.rest_state.cavity_id
    supported_task_kinds = set(
        str(value) for value in policy_payload()["supported_task_kinds"]
    )
    unsupported: list[FeasibilityIssue] = []
    required_by_task: list[tuple[int, object, str, tuple[ArticulatorSpec, ...]]] = []

    for index, task in enumerate(EXP27.TASKS):
        if task.task not in supported_task_kinds:
            unsupported.append(
                FeasibilityIssue(
                    code="TASK_UNSUPPORTED",
                    message=f"unsupported task kind {task.task!r}",
                    gesture_index=index,
                )
            )
            continue

        required_kind = required_articulator_kind(task)
        articulators = tuple(
            articulator
            for articulator in morphology.creature.articulators
            if articulator.cavity_id == cavity_id
            and articulator.kind == required_kind
        )
        if not articulators:
            unsupported.append(
                FeasibilityIssue(
                    code="ACTUATOR_KIND_UNSUPPORTED",
                    message=(
                        f"no {required_kind!r} articulator is available "
                        f"for task {index}"
                    ),
                    gesture_index=index,
                )
            )
            continue
        required_by_task.append((index, task, required_kind, articulators))

    if unsupported:
        return FeasibilityReport(
            status=FeasibilityStatus.UNSUPPORTED,
            issues=tuple(unsupported),
        )

    infeasible: list[FeasibilityIssue] = []
    for index, task, required_kind, articulators in required_by_task:
        location = float(task.location)
        reachable = any(
            articulator.reachable_start
            <= location
            <= articulator.reachable_end
            for articulator in articulators
        )
        if not reachable:
            infeasible.append(
                FeasibilityIssue(
                    code=EXPECTED_UNREACHABLE_ISSUE_CODE,
                    message=(
                        f"{required_kind} cannot reach normalized location "
                        f"{location:.16g}"
                    ),
                    gesture_index=index,
                )
            )

    if infeasible:
        return FeasibilityReport(
            status=FeasibilityStatus.INFEASIBLE,
            issues=tuple(infeasible),
        )

    return FeasibilityReport(status=FeasibilityStatus.FEASIBLE)


def task_reach_rows(
    condition: str,
    morphology: PreparedMorphology[Tract1DGeometry],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cavity_id = morphology.rest_state.cavity_id
    total_length = morphology.rest_state.total_length_m

    for index, task in enumerate(EXP27.TASKS):
        required_kind = required_articulator_kind(task)
        articulator = next(
            articulator
            for articulator in morphology.creature.articulators
            if articulator.cavity_id == cavity_id
            and articulator.kind == required_kind
        )
        location = float(task.location)
        lower_margin = location - articulator.reachable_start
        upper_margin = articulator.reachable_end - location
        rows.append(
            {
                "condition": condition,
                "task_index": index,
                "task": task.task,
                "location": location,
                "required_articulator_kind": required_kind,
                "reachable_start": articulator.reachable_start,
                "reachable_end": articulator.reachable_end,
                "lower_margin": lower_margin,
                "upper_margin": upper_margin,
                "upper_metric_margin_m": upper_margin * total_length,
                "reachable": (
                    articulator.reachable_start
                    <= location
                    <= articulator.reachable_end
                ),
            }
        )
    return rows


def morphology_intervention_isolated(
    prepared: dict[str, PreparedMorphology[Tract1DGeometry]],
) -> bool:
    baseline = prepared["M_plus"]
    base_creature = baseline.creature
    base_oral = next(
        a for a in base_creature.articulators if a.kind == ORAL_SHAPER_KIND
    )
    base_lip = next(a for a in base_creature.articulators if a.kind == LIP_KIND)

    expected_ends = {
        name: reachable_end for name, reachable_end, _ in CONDITIONS
    }

    for name, morphology in prepared.items():
        creature = morphology.creature
        if (
            morphology.backend_id != baseline.backend_id
            or morphology.rest_state != baseline.rest_state
            or creature.name != base_creature.name
            or creature.cavities != base_creature.cavities
            or creature.connections != base_creature.connections
            or creature.source_organs != base_creature.source_organs
            or len(creature.articulators) != 2
        ):
            return False

        oral = next(
            (a for a in creature.articulators if a.kind == ORAL_SHAPER_KIND),
            None,
        )
        lip = next(
            (a for a in creature.articulators if a.kind == LIP_KIND),
            None,
        )
        if oral is None or lip is None:
            return False
        if (
            oral.id != base_oral.id
            or oral.cavity_id != base_oral.cavity_id
            or oral.kind != base_oral.kind
            or oral.reachable_start != base_oral.reachable_start
            or oral.reachable_end != expected_ends[name]
            or lip != base_lip
        ):
            return False

    return True


def render_with_counter(
    source: np.ndarray,
    start: Tract1DGeometry,
    *,
    label: str,
) -> tuple[np.ndarray, int]:
    counter = CountingTransfer()

    def transfer_for_time(
        center_s: float,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        geometry = EXP27.task_geometry_for_time(
            start,
            center_s,
            control_step_s=EXP27.PRIMARY_CONTROL_STEP_S,
            cavity_id=f"{start.cavity_id}-v3c-{label}",
        )
        return counter.evaluate(geometry, frequencies_hz)

    waveform = EXP26.EXP12.frame_render(
        np.asarray(source, dtype=np.float64),
        transfer_for_time,
        hop_size=EXP27.PRIMARY_HOP_SIZE,
        edge_mode="preroll_edge",
    )
    return np.asarray(waveform, dtype=np.float64), counter.call_count


def evaluate_condition(
    morphology: PreparedMorphology[Tract1DGeometry],
    source: np.ndarray,
    *,
    label: str,
) -> ConditionResult:
    feasibility = capability_report(morphology)
    if feasibility.status is not FeasibilityStatus.FEASIBLE:
        return ConditionResult(
            feasibility=feasibility,
            endpoint=None,
            waveform=None,
            acoustic_call_count=0,
        )

    endpoint = EXP27.realize_task_geometry(
        morphology.rest_state,
        1.0,
        cavity_id=morphology.rest_state.cavity_id,
    )
    waveform, call_count = render_with_counter(
        source,
        morphology.rest_state,
        label=label,
    )
    return ConditionResult(
        feasibility=feasibility,
        endpoint=endpoint,
        waveform=waveform,
        acoustic_call_count=call_count,
    )


def geometry_payload(geometry: Tract1DGeometry) -> dict[str, object]:
    return {
        "cavity_id": geometry.cavity_id,
        "lengths_m": [section.length_m for section in geometry.sections],
        "areas_m2": [section.area_m2 for section in geometry.sections],
    }


def geometry_physics_equal(
    left: Tract1DGeometry,
    right: Tract1DGeometry,
) -> bool:
    return (
        [section.length_m for section in left.sections]
        == [section.length_m for section in right.sections]
        and [section.area_m2 for section in left.sections]
        == [section.area_m2 for section in right.sections]
    )


def oracle_condition_checks(
    oracle: dict[str, object],
    prepared: dict[str, PreparedMorphology[Tract1DGeometry]],
    results: dict[str, ConditionResult],
) -> tuple[list[dict[str, object]], bool]:
    expected_by_name = {
        str(row["condition"]): row for row in oracle["conditions"]
    }
    rows: list[dict[str, object]] = []
    all_pass = True
    target_location = float(
        EXP27.TASKS[EXPECTED_UNREACHABLE_TASK_INDEX].location
    )

    for name, reachable_end, _ in CONDITIONS:
        expected = expected_by_name[name]
        observed_margin = reachable_end - target_location
        observed_metric_margin = (
            observed_margin * prepared[name].rest_state.total_length_m
        )
        observed_status = results[name].feasibility.status.value
        passed = (
            math.isclose(
                observed_margin,
                float(expected["normalized_margin"]),
                rel_tol=0.0,
                abs_tol=MARGIN_ABS_TOLERANCE,
            )
            and math.isclose(
                observed_metric_margin,
                float(expected["metric_margin_m"]),
                rel_tol=0.0,
                abs_tol=MARGIN_ABS_TOLERANCE,
            )
            and observed_status == str(expected["expected_status"])
            and reachable_end
            == float(expected["oral_shaper_reachable_end"])
        )
        all_pass = all_pass and passed
        rows.append(
            {
                "condition": name,
                "reachable_end": reachable_end,
                "normalized_margin": observed_margin,
                "expected_normalized_margin": expected["normalized_margin"],
                "metric_margin_m": observed_metric_margin,
                "expected_metric_margin_m": expected["metric_margin_m"],
                "observed_status": observed_status,
                "expected_status": expected["expected_status"],
                "pass": passed,
            }
        )

    return rows, all_pass


def reject_preflight(
    output_dir: Path,
    decision_name: str,
    *,
    upstream: dict[str, object],
    local: dict[str, object],
) -> dict[str, object]:
    decision = {
        "decision": decision_name,
        "gates": {
            "upstream_frozen_preflight": bool(upstream.get("pass")),
            "local_frozen_preflight": bool(local.get("pass")),
        },
        "upstream_preflight": upstream,
        "local_preflight": local,
        "claim_boundary": "No V3c claim: frozen upstream or local input changed.",
    }
    for filename in ("decision.json", "provenance.json"):
        (output_dir / filename).write_text(
            json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return decision


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    exp28_oracle = json.loads(EXP28.ORACLE_PATH.read_text(encoding="utf-8"))
    exp28_frozen = json.loads(
        EXP28.FROZEN_REFERENCE_PATH.read_text(encoding="utf-8")
    )

    m0_a = EXP26.EXP23.primary_geometry("a")
    m0_i = EXP26.EXP23.primary_geometry("i")
    upstream = EXP28.frozen_preflight(
        exp28_oracle,
        exp28_frozen,
        m0_a,
        m0_i,
    )
    local = local_oracle_preflight(oracle)

    if not upstream["pass"]:
        return reject_preflight(
            output_dir,
            "IMPLEMENTATION_MISMATCH",
            upstream=upstream,
            local=local,
        )
    if not local["pass"]:
        representation_clean = bool(
            local["checks"].get("task_plan_representation_clean")
        )
        return reject_preflight(
            output_dir,
            (
                "REPRESENTATION_LEAK"
                if not representation_clean
                else "IMPLEMENTATION_MISMATCH"
            ),
            upstream=upstream,
            local=local,
        )

    task_payload = task_plan_payload()
    task_hash = sha256_json(task_payload)
    (output_dir / "task_plan.json").write_text(
        json.dumps(task_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    creatures = {
        name: creature_for(
            cavity_id=m0_a.cavity_id,
            oral_reachable_end=reachable_end,
        )
        for name, reachable_end, _ in CONDITIONS
    }
    prepared = {
        name: prepared_for(
            creature=creatures[name],
            geometry=m0_a,
            condition=name,
        )
        for name, _, _ in CONDITIONS
    }

    intervention_isolated = morphology_intervention_isolated(prepared)
    morphology_payload = {
        name: {
            "creature_name": morphology.creature.name,
            "backend_id": morphology.backend_id,
            "rest_geometry_sha256": sha256_json(
                geometry_payload(morphology.rest_state)
            ),
            "articulators": [
                {
                    "id": a.id,
                    "cavity_id": a.cavity_id,
                    "kind": a.kind,
                    "reachable_start": a.reachable_start,
                    "reachable_end": a.reachable_end,
                }
                for a in morphology.creature.articulators
            ],
        }
        for name, morphology in prepared.items()
    }
    (output_dir / "morphologies.json").write_text(
        json.dumps(morphology_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    reach_rows: list[dict[str, object]] = []
    for name in prepared:
        reach_rows.extend(task_reach_rows(name, prepared[name]))
    write_csv(output_dir / "task_reach_trace.csv", reach_rows)

    sources, _ = EXP26.EXP13.build_sources()
    source_result = sources["lf_fixed"]
    source = np.asarray(source_result.source, dtype=np.float64)
    source_hash = EXP26.sha256_float64(source)

    results = {
        name: evaluate_condition(
            prepared[name],
            source,
            label=name.lower(),
        )
        for name, _, _ in CONDITIONS
    }

    oracle_rows, oracle_pass = oracle_condition_checks(
        oracle,
        prepared,
        results,
    )
    write_csv(output_dir / "oracle_condition_checks.csv", oracle_rows)

    for name in ("M_plus", "M_boundary"):
        result = results[name]
        if result.waveform is not None:
            np.save(
                output_dir / f"{name}_raw_pressure_pa.npy",
                result.waveform,
            )

    expected_statuses = {
        name: expected for name, _, expected in CONDITIONS
    }
    status_pattern_pass = all(
        results[name].feasibility.status is expected_statuses[name]
        for name in expected_statuses
    )
    no_invalid_or_unsupported = all(
        result.feasibility.status
        not in {FeasibilityStatus.INVALID, FeasibilityStatus.UNSUPPORTED}
        for result in results.values()
    )

    minus = results["M_minus"]
    failure_attribution_pass = bool(
        minus.feasibility.status is FeasibilityStatus.INFEASIBLE
        and len(minus.feasibility.issues) == 1
        and minus.feasibility.issues[0].code
        == EXPECTED_UNREACHABLE_ISSUE_CODE
        and minus.feasibility.issues[0].gesture_index
        == EXPECTED_UNREACHABLE_TASK_INDEX
    )
    no_fallback_pass = bool(
        minus.endpoint is None
        and minus.waveform is None
        and minus.acoustic_call_count == 0
    )

    plus = results["M_plus"]
    boundary = results["M_boundary"]
    feasible_outputs_present = bool(
        plus.endpoint is not None
        and boundary.endpoint is not None
        and plus.waveform is not None
        and boundary.waveform is not None
    )

    endpoint_equal = bool(
        feasible_outputs_present
        and geometry_physics_equal(plus.endpoint, boundary.endpoint)
    )
    waveform_equal = bool(
        feasible_outputs_present
        and np.array_equal(plus.waveform, boundary.waveform)
    )
    acoustic_calls_equal = bool(
        plus.acoustic_call_count == boundary.acoustic_call_count
        and plus.acoustic_call_count > 0
    )
    capability_null_control_pass = bool(
        endpoint_equal and waveform_equal and acoustic_calls_equal
    )

    if feasible_outputs_present:
        audited_reference_wave = EXP27.render_task_continuous(
            source,
            m0_a,
            control_step_s=EXP27.PRIMARY_CONTROL_STEP_S,
            hop_size=EXP27.PRIMARY_HOP_SIZE,
            label="v3c-instrumentation-reference",
        )
        instrumentation_matches_audited_renderer = bool(
            np.array_equal(plus.waveform, audited_reference_wave)
            and np.array_equal(boundary.waveform, audited_reference_wave)
        )
    else:
        instrumentation_matches_audited_renderer = False

    representation_invariant = bool(
        task_payload == oracle["task_plan"]
        and task_payload == exp28_oracle["task_plan"]
        and EXP27.representation_is_clean(task_payload)
    )
    implementation_match = bool(
        upstream["pass"]
        and local["pass"]
        and oracle_pass
        and instrumentation_matches_audited_renderer
    )

    if not representation_invariant:
        decision_name = "REPRESENTATION_LEAK"
    elif not intervention_isolated:
        decision_name = "MORPHOLOGY_INTERVENTION_INVALID"
    elif not implementation_match:
        decision_name = "IMPLEMENTATION_MISMATCH"
    elif not no_invalid_or_unsupported:
        decision_name = (
            "BACKEND_UNSUPPORTED"
            if any(
                result.feasibility.status is FeasibilityStatus.UNSUPPORTED
                for result in results.values()
            )
            else "FEASIBILITY_BOUNDARY_FAILED"
        )
    elif not status_pattern_pass:
        decision_name = "FEASIBILITY_BOUNDARY_FAILED"
    elif not failure_attribution_pass:
        decision_name = "FAILURE_ATTRIBUTION_INCONSISTENT"
    elif not no_fallback_pass:
        decision_name = "ACOUSTIC_FALLBACK_LEAK"
    elif not capability_null_control_pass:
        decision_name = "CAPABILITY_NULL_CONTROL_FAILED"
    else:
        decision_name = SUPPORT_DECISION

    condition_summary = {}
    for name, result in results.items():
        condition_summary[name] = {
            "status": result.feasibility.status.value,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "gesture_index": issue.gesture_index,
                }
                for issue in result.feasibility.issues
            ],
            "physical_endpoint_present": result.endpoint is not None,
            "physical_endpoint_sha256": (
                sha256_json(geometry_payload(result.endpoint))
                if result.endpoint is not None
                else None
            ),
            "waveform_present": result.waveform is not None,
            "waveform_sha256_float64": (
                EXP26.sha256_float64(result.waveform)
                if result.waveform is not None
                else None
            ),
            "acoustic_transfer_call_count": result.acoustic_call_count,
        }

    provenance = {
        "experiment": "029_task_field_embodied_infeasibility",
        "issue": 67,
        "parent_issue": 33,
        "upstream": {
            "v3a": "Experiment 027 / PR #63",
            "v3b": "Experiment 028 / PR #65",
            "frozen_preflight_reference_commit": upstream["reference_commit"],
            "frozen_preflight_implementation_sha256": (
                upstream["implementation_sha256"]
            ),
        },
        "task_plan_sha256": task_hash,
        "capability_policy": policy_payload(),
        "fixture": fixture_payload(),
        "oracle": {
            "path": "wolfram/v3c_oracle.json",
            "git_blob_sha": ORACLE_GIT_BLOB_SHA,
            "evaluated_before_python_experiment": True,
        },
        "source": {
            "name": source_result.name,
            "sha256_float64": source_hash,
        },
        "utterance_level_preflight": (
            "all frozen tasks must be supported and reachable before any "
            "physical/acoustic performance output is generated"
        ),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    decision = {
        "decision": decision_name,
        "gates": {
            "upstream_frozen_preflight": bool(upstream["pass"]),
            "local_frozen_preflight": bool(local["pass"]),
            "representation_invariant": representation_invariant,
            "morphology_intervention_isolated": intervention_isolated,
            "wolfram_oracle_reproduction": oracle_pass,
            "feasibility_boundary": bool(
                status_pattern_pass and no_invalid_or_unsupported
            ),
            "failure_attribution": failure_attribution_pass,
            "no_physical_or_acoustic_fallback": no_fallback_pass,
            "capability_null_control": capability_null_control_pass,
            "instrumented_renderer_matches_audited_renderer": (
                instrumentation_matches_audited_renderer
            ),
        },
        "task_plan_sha256": task_hash,
        "oracle_condition_checks": oracle_rows,
        "conditions": condition_summary,
        "null_control": {
            "physical_endpoints_exactly_equal": endpoint_equal,
            "raw_waveforms_exactly_equal": waveform_equal,
            "acoustic_call_counts_equal_and_positive": acoustic_calls_equal,
            "M_plus_calls": plus.acoustic_call_count,
            "M_boundary_calls": boundary.acoustic_call_count,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "frozen calibrated three-task plan under one experiment-local "
            "reachability fixture only; not biological reachability, "
            "force/contact mechanics, or arbitrary morphology infeasibility"
        ),
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-029-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
