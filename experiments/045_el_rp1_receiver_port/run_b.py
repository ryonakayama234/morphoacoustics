"""Run frozen 16-case Gate B Core-matrix / independent JS-wave comparison."""
from __future__ import annotations
import json
from audit_b import compare_row, load_oracle
from coupler import solve_port
from qualifier import SyntheticReferencePort

def main():
    source = load_oracle()
    params = source["fixed"]
    maxima = {"max_pressure_error_pa":0., "max_zc_scaled_flow_error_pa":0.,
              "max_power_error_w":0.}
    records = []
    for row in source["rows"]:
        a,l,f = row[:3]
        spec = SyntheticReferencePort(
            params["source_pressure_pa"], params["source_impedance_pa_s_m3"],
            params["terminal_impedance_pa_s_m3"], a,l,f,
            params["air_density_kg_m3"], params["sound_speed_m_s"])
        full = solve_port(spec)
        parts = solve_port(spec, segment_lengths_m=(.4*l,.6*l))
        errors = compare_row(row,full)
        compare_row(row,parts)
        for k,v in errors.items():
            maxima[k] = max(maxima[k],v)
        records.append({"area_m2":a,"length_m":l,"frequency_hz":f,
                        "pL_real_pa":full.pL_pa.real,"pL_imag_pa":full.pL_pa.imag,
                        "p0_real_pa":full.p0_pa.real,"p0_imag_pa":full.p0_pa.imag,
                        "max_source_boundary_residual_pa":abs(full.residual_source_boundary_pa),
                        "max_tube_power_residual_w":abs(full.residual_tube_energy_w)})
    print(json.dumps({
        "schema":"el-rp1.gateb.synthetic-receipt.v1",
        "d0_sha":"a33c8c68879f732cd830b2caab6b8024b5322297",
        "b0_sha":"624ce156a4c377ec742794ea6a3278e61a6651e4",
        "oracle_git_blob_sha":"81286d0a2b7ea26cf33ce65d0eb98be6df47b607",
        "comparison_method":"Core UniformTube matrix vs frozen independent JS wave",
        "scope":"SYNTHETIC_1D_NOT_HUMAN_EAR",
        "count":len(records),"max_errors":maxima,"rows":records,
        "independent_physical_review":"PENDING","public_api":"NOT_ADOPTED",
    }, indent=2, sort_keys=True, allow_nan=False))

if __name__=="__main__":
    main()
