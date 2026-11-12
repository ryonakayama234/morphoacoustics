"""FZ-N1 candidate-side internal fault probes; not independent oracle adjudication."""
from __future__ import annotations
import hashlib
import numpy as np
from ..prereg_binding import Refusal, require, validate_lambda
from .identity import geometry_claim, model_claim, raw_claim, source_claim
from .physics import inspect

EXPECTED={
    "NEG-LAMBDA":"INVALID_LOSS_PARAMETER",
    "ACTIVE-ZY":"NONPASSIVE_MODEL",
    "SWAP-COEFF":"MODEL_IDENTITY_MISMATCH",
    "SWAP-LOAD":"LOAD_MISMATCH",
    "SWAP-GEOM-PORT":"PHYSICAL_IDENTITY_MISMATCH",
    "RAW-FORGE":"WAVEFORM_ORACLE_MISMATCH",
    "LOSS-IGNORED":"ORACLE_MISMATCH",
    "OLD-ATTENUATION":"UNREGISTERED_ATTENUATION",
    "SHA-SOURCE":"ARTIFACT_MISMATCH",
}

def run_one(name: str, *, case: dict, null: dict, full: dict,
            pressure_null: np.ndarray, pressure_full: np.ndarray,
            source: dict) -> dict:
    require(name in EXPECTED,"INVALID_FIXTURE","unknown FZ-N1 class")
    changed={}
    try:
        if name=="NEG-LAMBDA":
            changed={"lambda":-1.0}
            validate_lambda(-1)
        elif name=="ACTIVE-ZY":
            broken=dict(full)
            broken["z"]=full["z"].copy()
            old=complex(broken["z"][0,0])
            broken["z"][0,0]=complex(-abs(old.real),old.imag)
            changed={"bin":0,"section":0,"before":str(old),"after":str(broken["z"][0,0])}
            inspect(broken)
        elif name=="SWAP-COEFF":
            old=complex(full["z"][0,0])
            swapped=2*old
            changed={"original":str(old),"modified":str(swapped)}
            require(abs(swapped-old)<=1e-10+1e-8*abs(old),
                    "MODEL_IDENTITY_MISMATCH","internal z differs from frozen law")
        elif name=="SWAP-LOAD":
            changed={"original_load":full["load_R"],"mutated_load":2*full["load_R"]}
            meta={"law":"b2.lrf.circular-rigid-isothermal/1",
                  "phasor":"exp(+jwt)","volume_velocity":"m3/s_inlet_to_outlet",
                  "attenuation_np_m":0,"band_hz":[100,800,2],"proxy_m":0.2,
                  "rho":1.21,"c":343.0,"load_R":2*full["load_R"]}
            model_claim(meta,case)
        elif name=="SWAP-GEOM-PORT":
            reversed_radii=tuple(reversed(case["radii_m"]))
            changed={"reversed_radii_m":reversed_radii}
            geometry_claim(case["case"],reversed_radii,case["lengths_m"],case["preparation_digest"])
        elif name=="RAW-FORGE":
            fake=np.ascontiguousarray(2*pressure_null-pressure_full,dtype="<f8")
            digest=hashlib.sha256(fake.tobytes()).hexdigest()
            changed={"forged_raw_sha256":digest,"manifest_rehashed":True}
            raw_claim(fake,digest,pressure_full)
        elif name=="LOSS-IGNORED":
            changed={"declared_lambda":1.0,"actual_lambda":0.0}
            require(np.all(np.abs(null["z"]-full["z"])<=1e-10+1e-8*np.abs(full["z"])),
                    "ORACLE_MISMATCH","null output falsely labeled full-loss")
        elif name=="OLD-ATTENUATION":
            changed={"historical_attenuation_np_m":.4}
            require(False,"UNREGISTERED_ATTENUATION","historical attenuation is not B2")
        elif name=="SHA-SOURCE":
            fake=source["buffer"].copy()
            fake[100]=np.nextafter(fake[100],np.inf)
            sha=hashlib.sha256(np.ascontiguousarray(fake,dtype="<f8").tobytes()).hexdigest()
            changed={"mutated_source_index":100,"rehashed_sha256":sha}
            source_claim(fake,sha,source)
    except Refusal as exc:
        return {"fixture":name,"stage":"CANDIDATE_DIAGNOSTIC_ONLY","mutation":changed,
                "expected":EXPECTED[name],"actual":exc.code,
                "verdict":"CANDIDATE_REFUSAL_OBSERVED" if exc.code==EXPECTED[name] else "UNRESOLVED",
                "accepted_run":False,"audio_issued":False}
    return {"fixture":name,"stage":"CANDIDATE_DIAGNOSTIC_ONLY","mutation":changed,
            "expected":EXPECTED[name],"actual":None,"verdict":"FAILED_TO_REFUSE",
            "accepted_run":False,"audio_issued":False}
