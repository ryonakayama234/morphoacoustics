# VF-1A DATA — research-only physical representation
These are **experiment-local typed state concepts**, NOT universal schemas, new UI controls, public OrganNode types or persistent character data.

| quantity | meaning / SI unit | storage authority |
|---|---|---|
| model family + parameters | `m[kg], K[N/m], d[N s/m], g[m²], A0[m²], w[m], Amin[m²], Ig[Pa s²/m³], Rg[Pa s/m³], rho,Cd` | Core experiment fixture, declared revision |
| frozen prepared acoustic body | `Tract1DGeometry` section `length_m,area_m2`, SFI-2 `Geometry` | pinned Core SFI-3 Draft source, research only |
| respiratory command | `Psub(t)` [Pa], steady 0/800 in pilot | research stimulus, future Motion effort semantics *not adopted* |
| dynamic tissue | `x_i[m],v_i[m/s]`, elastic+kinetic energy [J] | ephemeral solver session only |
| fluid source | glottal `q[m³/s]`, `A(x)[m²]`, Bernoulli loss [W] | physical state, **NOT** waveform preset |
| chamber acoustic port | `p_mid[Pa], Uin=q-g·v[m³/s]`, `pU[W]` | coupled physical solver |
| outlet | matched resistance, outlet flow `[m³/s]`, loss [J] | pinned tract solver, **NOT** a receiver microphone |
| receipt | raw time traces, identity SHA, independent tests, error and unsupported boundaries, verdict | Core experimental archive |
| Studio Character, Motion, Scene, Take | **not modified or emitted** | existing Studio contract only |

The model's aperture law is a research constitutive hypothesis, not an edited Studio OrganGraph. If no sustained self-oscillation arises, preserve that negative result; do not infer a human-like F0. Failure: `INVALID` parameters, `UNSUPPORTED_CONTACT` for area floor, `NUMERICALLY_UNRESOLVED` integration/proof failure, `INDETERMINATE_PHYSIOLOGY` absent independent calibration.
