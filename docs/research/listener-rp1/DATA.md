# DATA — evidence and qualified operations (proposed research schema)

D0, no production schema / package contract. Future code must not substitute unknown values, relabel normalized impedance as absolute impedance, or interpret data playback permission as physical counterfactual permission.

## Evidence discriminated union
1. \`MEASURED_PRESSURE_TRANSFER\` — fixed-condition sampled HRIR/HRTF or measured complex pressure ratio. It can support **only** declared observation or qualified, rights-permitted reproduction; *never* a changed-load prediction from pressure-only data.
2. \`SYNTHETIC_REFERENCE_PORT\` — explicitly declared ps (complex Pa), Zs (absolute Pa·s/m³), Zt (absolute Pa·s/m³), rigid tube geometry, medium properties, f>0, named source/entrance/terminal planes and phasor. Allows synthetic 1D computations in Gate B only.
3. \`CALIBRATED_ACOUSTIC_PORT\` — physically measured equivalent-port variables with calibration chains, uncertainty, multiple independent loads/conditions as needed and exact plane. Type reservable; Gate A/B may validate metadata but **must refuse physical prediction** pending measured Gate C.
4. \`UNQUALIFIED_OBSERVATION\` — insufficient or contradictory provenance/boundaries. May be retained as traceable raw evidence; no prediction.

No untagged free-form union/cast. \`measurement_source_sha256\`, processing version, measurement definition and rights declarations are recorded independent of numerical fields.

## Required metadata when applicable
- \`source_reference_plane\`, \`receiver_input_plane\`, \`receiver_output_plane\`; no inferred coincidence of \`KU100_STORED_CHANNEL\` and \`CANAL_ENTRANCE\`.
- \`pressure_kind\`: TOTAL / INCIDENT / SOURCE_EQUIVALENT / STORED_CHANNEL_RATIO — different physics, not aliases.
- \`phasor_convention\`: PEAK_EXP_PLUS_IWT (synthetic default only because explicitly declared, never guessed from file).
- \`flow_direction\`: ENTRANCE_TO_TERMINAL for source/load coupling.
- \`terminal_load_condition\`: absolute Zt in SI or measured open/blocked state; a bare HRTF does not supply Zt.
- \`time_origin\`, sample rate, channel identity and calibration; no inference of absolute flight time from short postprocessed HRIR.
- \`validity_range\`, uncertainty/measurement class, selected operations; \`rights_status\`: NOT_ASSESSED / RESEARCH_REVIEW / REUSE_CLEARED / BLOCKED. No automated legal conclusion.

## Operations
\`INSPECT_METADATA\`: parse/validate evidence provenance and tags; unknown rights can be recorded but not independently cleared.
\`PREDICT_CHANGED_LOAD\`: needs synthetic fully specified port in Gate B; measured or calibrated records blocked until Gate C; bare HRTF always UNIDENTIFIABLE for this operation.
\`REPRODUCE_MEASURED_CHANNEL\`: out of Gate A/B runtime scope; rights review and precise measurement semantics required.
\`EXPORT_OR_DISTRIBUTE\`: separate rights gate; numerical physics validity alone does not imply rights.

## Refusal vs verdict
\`INVALID\`: malformed, nonfinite, contradictory or wrong units.
\`UNSUPPORTED\`: valid evidence but physical model/operation outside gate scope.
\`UNIDENTIFIABLE\`: observationally insufficient for requested counterfactual; do not fill missing ps/Zs.
\`NUMERICALLY_UNRESOLVED\`: adequately specified but numerically ill-conditioned/out of safe compute range.
\`RIGHTS_REVIEW_REQUIRED\`: publication/reuse requires separate legal qualification.
These are **input/operation outcomes**, not claims that a research hypothesis has failed or that a dataset is scientifically worthless.
