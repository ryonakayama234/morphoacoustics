"""Append-only take-metrology-pack/0 logical Core research sidecar; no product Take."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from ..prereg_binding import Refusal, require, LAW, PREREG_CONTENT_SHA256

FEATURES=("level.v0","f0_observed.v0","harmonic_tilt.v0",
          "transfer_peak_candidates.v0","output_spectral_peaks.v0",
          "noise_proxy.v0","time_features.v0")

def canonical(obj: object)->bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False).encode()

def new_pack(*,evidence_id:str,utc:str,case_id:str,run_head:str,
             verification_head:str|None,geometry:dict,source:dict,
             raw_sha256:str|None,coefficient_ref:str,
             coefficient_sha256:str,loss:float,
             status:str,refusal_code:str|None=None)->dict:
    require(evidence_id and case_id and len(run_head)==40,
            "ARTIFACT_MISMATCH","real evidence ID and exact run HEAD required")
    coverage=[{"field_path":field,"origin_evidence_id":evidence_id,
               "status":"UNKNOWN","reason_code":reason,
               "evidence_level":"NOT_CAPTURED","method_id":None}
              for field,reason in (
                  ("origin.origin_record_sha256","NOT_CAPTURED"),
                  ("origin.take_id","ORIGIN_NOT_PRODUCT_TAKE"),
                  ("motion.task_plan_sha256","NOT_APPLICABLE"),
                  ("preview.wav_ref","NO_PREVIEW_IN_PROTOCOL"),
                  ("source_evidence.actual_run_samples_sha256","SOURCE_NOT_ATTESTED"))]
    coverage.extend({"field_path":"derived_features."+f+".value",
                     "origin_evidence_id":evidence_id,
                     "status":"UNKNOWN","reason_code":"METHOD_UNFROZEN",
                     "evidence_level":"NOT_CAPTURED","method_id":f}
                    for f in FEATURES)
    return {
      "pack_schema_version":"take-metrology-pack/0","pack_id":"b2-"+evidence_id,
      "origin":{"origin_class":"NEW_RUN","origin_record_ref":"research:"+evidence_id,
                "origin_record_sha256":None,"take_id":None,"evidence_id":evidence_id,
                "issuer":"Core-B2-research","issued_at_utc":utc,
                "measurement_time_utc":utc,"derivation_time_utc":utc,
                "claim_scope":"BOUNDED_MODEL_ONLY","parent_pack_id":None,
                "backfill":False},
      "request_body":{"fixture_id":case_id,"run_core_sha":run_head,
                      "verification_core_sha":verification_head,
                      "research_solver":LAW,"prereg_sha256":PREREG_CONTENT_SHA256,
                      "revision_id":geometry["revision_id"],
                      "preparation_digest":geometry["preparation_digest"],
                      "radii_m":list(geometry["radii_m"]),
                      "lengths_m":list(geometry["lengths_m"])},
      "source_evidence":{"source_id":"lf_fixed","prescribed_f0_hz":100.0,
                         "sample_count":24000,"sample_rate_hz":48000,
                         "dtype":"<f8","actual_run_samples_sha256":source.get("actual_run_samples_sha256"),
                         "recomputed_samples_sha256":source.get("recomputed_samples_sha256"),
                         "evidence_class":source.get("evidence_class","UNKNOWN"),
                         "full_verified_source_state":"UNKNOWN"},
      "motion":{"mode":"rest_only","script_id":None,"task_plan_sha256":None,
                "effort_model_status":"UNMODELED"},
      "medium_boundary_observer":{"loss_model":LAW,"lambda":loss,
                  "coefficient_manifest_ref":coefficient_ref,
                  "coefficient_manifest_sha256":coefficient_sha256,
                  "rho_kg_m3":1.21,"c_m_s":343.0,
                  "wall_model":"rigid_no_slip_isothermal",
                  "attenuation_np_m":0.0,"load_formula":"0.05*rho*c/S_last",
                  "phasor":"exp(+jwt)","source_port":"inlet_positive_U_m3_s",
                  "observer_kind":"MODEL_PRESSURE_PROXY","distance_m":0.2,
                  "observation_plane_ref":"uncalibrated_monopole_0.20m",
                  "pressure_generation_method":"351bin_100to800Hz_1overN",
                  "calibration_status":"UNCALIBRATED"},
      "raw_signal":{"artifact_sha256":raw_sha256,
                    "sha_scope":"le_f64_array_bytes","dtype":"<f8",
                    "frame_count":24000,"channels":1,"sample_rate_hz":48000,
                    "duration_s":0.5,
                    "missing_reason":"REFUSAL_NO_AUDIO" if raw_sha256 is None else None},
      "preview":{"wav_ref":None,"status":"NOT_APPLICABLE",
                 "reason_code":"NO_PREVIEW_IN_PROTOCOL"},
      "outcome":{"job_status":status,"refusal_code":refusal_code,
                 "implementation_conformance":"UNRESOLVED",
                 "effect":"UNKNOWN","full_verified_source_state":"UNKNOWN",
                 "unmodeled_effects":["wall_compliance","tissue_loss"]},
      "derived_features":[{"feature_name":f,"method_id":f,
                           "method_status":"DEFINED_NOT_VALIDATED",
                           "value":None,"reason_code":"METHOD_UNFROZEN"} for f in FEATURES],
      "coverage":coverage,"method_manifest_ref":None,
      "complex_transfer":[],"physical_observables":[]}

def write_once(path:Path,obj:dict)->str:
    raw=canonical(obj)+b"\n"
    require(path.parent.is_dir() and not path.parent.is_symlink(),
            "ARTIFACT_MISMATCH","invalid directory")
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600)
    except FileExistsError as exc:
        raise Refusal("OUTPUT_EXISTS","pack is append-only") from exc
    with os.fdopen(fd,"wb") as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(raw).hexdigest()

def old_reader(path:Path,external_digest:str)->dict:
    require(path.is_file() and not path.is_symlink()
            and hashlib.sha256(path.read_bytes()).hexdigest()==external_digest,
            "ARTIFACT_MISMATCH","copy-SHA or pack byte alteration")
    obj=json.loads(path.read_bytes())
    require(obj.get("pack_schema_version")=="take-metrology-pack/0"
            and obj.get("origin",{}).get("take_id") is None
            and len(obj.get("derived_features",[]))==7
            and all(f["value"] is None and
                    f["method_status"]=="DEFINED_NOT_VALIDATED"
                    for f in obj["derived_features"]),
            "ARTIFACT_MISMATCH","old logical reader mismatch")
    return obj
