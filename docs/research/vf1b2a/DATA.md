# VF-1B2a DATA — experiment-local metric contract
**Frozen before code**; not Core/public API or adopted organ model.

## Independent inputs (SI)
`A_entry_m2, A_exit_m2 > 0`, `length_m > 0`, `density_kg_m3 > 0`, `p_up_pa >= p_down_pa`, `0 < discharge_coefficient <=1`, dimensionless constant `separation_area_ratio = 1.2`, sampling count `samples>=3`.
- `case_id` exact fixture. No dynamic tissue displacement/velocity, no material, no oscillatory source.
- All parameter values and shape names included in every case receipt; fixed source Git head, document hashes, and test-result hash in aggregate report; refuse NaN/inf and boolean numeric impersonation.
- The attempted reversed-drive input is **UNSUPPORTED_REVERSE_FLOW**, not a negative result for an unknown backward separation closure.

## Outputs (SI)
`volume_flow_m3_s`, `separation_z_m`, `separation_area_m2`, `separation_active: boolean`, `upstream_power_w`, `declared_farfield_loss_w`, `fixed_wall_power_w=0`, `bookkeeping_residual_w`, and sampled `z_m,area_m2,pressure_pa,attached`. `separation_active` is false for `Pup=Pout` even if a geometric candidate still exists.
Measurements are written as CSV plus `vf1b2a_receipt.json` with SHA256 of exact files. `pressure_pa` is model predicted **static pressure**, not validated pressure tap data or tract acoustic pressure. No acoustic waveform output.

## Provenance and verdict
Full commit SHA and tracked-clean Git state, source/tests/docs/workflow SHA256, independently run unittest result receipt with schema `vf1b2a.unittest.v1`, bool `passed=true`, exact integer `exit_code=0` are required for model numeric PASS; missing/failing status => `NUMERICALLY_UNRESOLVED` regardless of good traces.

`G0`: trace completeness and refusal, `G1`: analytic and model consistency, **`G2=INDETERMINATE_NO_INDEPENDENT_NUMERIC_PRESSURE_DATA`** (published qualitative mechanisms are NOT a quantified error fit), `G3=NOT_APPLICABLE_RIGID_GEOMETRY`, `G4=NO_GO`. Output `NUMERICALLY_CONSISTENT_RIGID_FLOW_PROXY` is not a biological phonation claim.


## Actual recorded v1 evidence (2026-10-27)
Source head `ee7f5224596dd2cf47dc6996b2b4365801e49867`; exact [successful CI #40425929420](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40425929420), artifact `vf1b2a-rigid-flow-evidence` ID `12699682538` (8,166 bytes, expires 2027-01-25). Contains 7 CSV numerical traces, status, unittest log, runner log and JSON receipt/source file hashes. All 16 independent stdlib tests passed in this source checkpoint; 7/7 analytic case audits and 7/7 scalar controls true. Units in CSV/JSON are physical SI, though the predictions are **not experimentally calibrated**. The source code has no current public output ABI.

The first RED run [#40425826631](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40425826631) is intentionally kept and archived (artifact `12699513144`). It generated all seven physical-model trajectories but a *test only* falsely expected the valid `Pup=0` case to raise ValueError. The science receipt correctly returned `NUMERICALLY_UNRESOLVED` and the workflow failed. Latest test source commit `ee7f522` restores the valid zero-drive control; it does **not change** physical equations or post-hoc thresholds.
