from __future__ import annotations

from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.physical import Tract1DGeometry

from .protocol import PreparationProvenance, PreparedMorphology

TRACT1D_BACKEND_ID = "fidelity0.tract1d"


def prepare_tract1d(
    creature: CreatureSpec,
    geometry: Tract1DGeometry,
    *,
    provenance: PreparationProvenance | None = None,
) -> PreparedMorphology[Tract1DGeometry]:
    """Bind a prepared serial 1D rest geometry to a creature.

    This function validates only facts required to make the binding coherent.
    It deliberately does not reject morphology features that Fidelity 0 cannot
    solve.  Such capability limitations remain realization outcomes and must be
    reported as ``UNSUPPORTED`` rather than disappearing during preparation.
    """

    known_cavities = {cavity.id for cavity in creature.cavities}
    if geometry.cavity_id not in known_cavities:
        raise ValueError(
            f"prepared 1D geometry cavity {geometry.cavity_id!r} is not in creature"
        )

    if provenance is None:
        provenance = PreparationProvenance(
            source="manual",
            model="prepared-tract1d-geometry",
        )

    return PreparedMorphology(
        creature=creature,
        rest_state=geometry,
        backend_id=TRACT1D_BACKEND_ID,
        provenance=provenance,
    )
