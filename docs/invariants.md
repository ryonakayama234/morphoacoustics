# Invariants

These rules are architectural constraints, not implementation suggestions.

## I1. Motor programs do not specify sound directly

A gesture or motor program must not directly set waveform samples, spectra, formants, or other downstream acoustic observations.

## I2. Gesture semantics are morphology-independent

Changing morphology must not require changing the gesture schema. Each morphology may realize the same task differently, or fail to realize it.

## I3. Physical infeasibility is a valid result

The system must be able to return an explicit infeasibility result. It must not silently coerce an unreachable task into a plausible-looking acoustic output.

## I4. Neural components do not bypass the physical causal path

Neural components may propose latent physical parameters, estimate inverse solutions, or improve a downstream residual. They must not replace the central causal path with direct motor-to-audio generation while claiming to be the physical simulator.

## I5. Observations are not latent state

Waveform, spectrogram, F0, formants, and perceptual features are downstream observations or analyses. They must remain distinguishable from physical state and task representation.

## I6. Backend capability is separate from domain expressivity

A backend may reject a morphology or phenomenon that it cannot solve. Solver limitations must not be encoded as universal restrictions on the domain schema.
