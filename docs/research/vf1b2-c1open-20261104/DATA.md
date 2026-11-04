# C1-Open DATA — measured values, serialized states and provenance
This is **a research trace format**, not a production `BodyRevision` ABI, Studio `Take`, graph port or performance contract.
```mermaid
flowchart LR
 F["Fixture; geometry, material, reservoir"] --> P["Prepared exact cell volumes gji"]
 P --> R["Raw trace; start/end and 4 RK stages"]
 R --> O["Independent physics observer"]
 O --> D["Scientific decision + SHA receipts"]
 R --> D
```
`Fixture`: `n` cells; `upstream_delta_pa`, `outlet_pa` [Pa]; two tissue initial `x0` [m], `v0` [m/s]; `locked` fixed-wall control. Physical constants and EOS in frozen source; not user-editable Studio fields.
`y(t)`: cell masses [kg] then cell axial momenta [kg m/s] then cell total energies [J] then two tissue displacements [m] and velocities [m/s]. Each saved step includes 4 RK4 stage states, per-face fluxes (kg/s,N,W), independently recoverable cell pressures [Pa abs], face ghost thermodynamic states, wall volume-rate [m³/s], generalized forces [N] and signed flux/damping/work integrals [J].
`audit.py` does **not** import the solver; reconstructs cell geometry, EOS, characteristic identities, independently evaluates Rusanov face flux, per-stage forces, every RK increment, all-time cumulative balance and boundary total-enthalpy work; rejects forged pressure/force/initial conditions/truncated history.
`RESULTS.json`: signed SI residuals and separately stored raw trace SHA-256. The marker `STOP_NUMERICALLY_UNRESOLVED_REFINED_GRID` is a scientific verdict despite green software tests for *expected stop*. External measured reference, physiologic loss law, acoustic source, mouth port, ear receiver: **none**. Historic C1-R0 and Studio data are unmodified.
