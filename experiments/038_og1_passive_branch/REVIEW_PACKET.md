# OG-1 independent review packet

## Physics/numerics reviewer

- Confirm zero-volume, common-medium, linear plane-wave, fixed rigid lossless limits.
- Audit exp(+i wt), tube flow signs, outward junction flow mapping and peak phasor power.
- Derive three-port scattering independently; pressure-wave power requires admittance
  weighting. Check all incident directions and complex mixed waves, not just A incidence.
- Audit 12x12 normalization, independent tangent oracle and all six p/U endpoint pairs.
- Check matched-varying versus fixed-terminal-impedance interventions are distinguished.
- Check pressure release/closed zero terminal power, nonzero internal standing fields,
  conditioning, singular lossless mode and absence of artificial damping/regularization.
- Assess frozen tolerances as engineering gates, not physiological validation.
- Record review against exact commit SHA and any limitations or disagreements.

## Code/API reviewer

- Verify immutable explicit tubes, junction, typed ports, edges and boundaries.
- Validate malformed data before unsupported topology, including mixed-invalid larger graphs.
- Verify tuple/edge reversal canonical identity, source/boundary/frequency/source-hash identity.
- Check both diagnostic mutations are rejected by oracle evidence that is not derived
  from the candidate solver's own equations or inverse-roundtrip.
- Confirm full runner recomputation, exclusive fresh output directories, completion marker,
  same-runtime repeat, CSV/graph/source digests and independent Wolfram archive.
- Check latest generic and dedicated scientific CI, all Python matrix jobs, artifacts.
- Confirm changes remain experimental; no source/public-contract/Studio drift.

## Adoption

User authorized an isolated research trial, not an automatic production promotion.
Keep Draft until independent reviews and a recorded limited decision. Resolve OG-0
#90/#93 separately. Research merge does not by itself authorize a public graph API.
