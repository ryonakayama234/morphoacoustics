"""SMC-7 L1-R: bounded evidence wrapper for *unverified* Japanese reading paths.

No G2P model, semantic motor mapping, temporal scheduling, body or audio.
Stage-specific research-only receipts; the caller's evidence metadata is not
a signature or proof of linguistic correctness.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any

from .reading_paths import ReadingPath, ReadingProposal, make_proposal

_MAX_CONTEXT_CHARS = 512
_MAX_CONTEXT_BYTES = 2048
_MAX_SOURCE_CHARS = 256
_MAX_SOURCE_BYTES = 2048
_MAX_PATHS = 3
_MAX_METRIC_SAMPLES = 10000
_VERSION = "smc7-l1r-evidence/v0"


@dataclass(frozen=True, slots=True)
class EvidenceManifest:
    provider_id: str
    provider_version: str
    dictionary_digest: str
    policy_revision: str
    license_id: str
    context_digest: str


@dataclass(frozen=True, slots=True)
class L1Envelope:
    status: str
    code: str
    context_digest: str | None
    manifest_identity: str | None
    envelope_id: str | None
    proposal: ReadingProposal | None


@dataclass(frozen=True, slots=True)
class L1Selection:
    status: str
    code: str
    selected_path_id: str | None
    selection_id: str | None


@dataclass(frozen=True, slots=True)
class ReadingMetrics:
    n: int
    hits_at_1: int
    hits_at_2: int
    hits_at_3: int
    candidate_total: int
    recall_at_1: Fraction
    recall_at_2: Fraction
    recall_at_3: Fraction
    burden: Fraction


def _ascii(value: object) -> bool:
    return (type(value) is str and 0 < len(value) <= 80
            and value.isascii() and all(33 <= ord(ch) <= 126 for ch in value))


def _scalar(value: str) -> bool:
    return all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in value)


def _hash(tag: str, value: object) -> str:
    # Canonical data are built exclusively from validated plain built-in fields.
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(tag.encode("ascii") + b"\x00" + raw).hexdigest()


def _hex_digest(value: object) -> bool:
    return (type(value) is str and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value))


def _context_error(context: object, revision: object, profile: object) -> str | None:
    if type(context) is not str:
        return "INVALID_CONTEXT"
    if len(context) > _MAX_CONTEXT_CHARS:
        return "CONTEXT_LIMIT"
    if not _scalar(context):
        return "INVALID_CONTEXT"
    if len(context.encode("utf-8")) > _MAX_CONTEXT_BYTES:
        return "CONTEXT_LIMIT"
    if not _ascii(revision) or type(profile) is not str or profile != "ja-JP":
        return "INVALID_PROFILE_OR_REVISION"
    return None


def context_hash(context: object, revision: object, profile: object = "ja-JP") -> str:
    """Context is raw, not NFKC- or NFC-normalized; no inferred semantics."""
    err = _context_error(context, revision, profile)
    if err:
        raise ValueError(err)
    return _hash("SMC7-L1R-CONTEXT/v0", [revision, profile, context])


def _manifest_error(value: object) -> str | None:
    if type(value) is not EvidenceManifest:
        return "INVALID_MANIFEST"
    assert isinstance(value, EvidenceManifest)
    for field in (value.provider_id, value.provider_version,
                  value.policy_revision, value.license_id):
        if not _ascii(field):
            return "INVALID_MANIFEST"
    if not _hex_digest(value.dictionary_digest) or not _hex_digest(value.context_digest):
        return "INVALID_MANIFEST"
    return None


def manifest_id(value: EvidenceManifest) -> str:
    """Content identity only. A self-claimed provider is NOT authenticated."""
    err = _manifest_error(value)
    if err:
        raise ValueError(err)
    return _hash("SMC7-L1R-MANIFEST/v0", [
        value.provider_id, value.provider_version, value.dictionary_digest,
        value.policy_revision, value.license_id, value.context_digest,
    ])


def _envelope_refusal(code: str, status: str = "REJECTED") -> L1Envelope:
    return L1Envelope(status, code, None, None, None, None)


def _source_error(value: object, revision: object) -> str | None:
    if type(value) is not str or not value:
        return "INVALID_SOURCE"
    if len(value) > _MAX_SOURCE_CHARS:
        return "SOURCE_LIMIT"
    if not _scalar(value):
        return "INVALID_SOURCE"
    if len(value.encode("utf-8")) > _MAX_SOURCE_BYTES:
        return "SOURCE_LIMIT"
    if not _ascii(revision):
        return "INVALID_REVISION"
    # Restricted L1 source repertoire, independent of L0 span correctness.
    # A complete caller-provided reading is not authority for unsupported text.
    if not all(
        ch in " \n\t、。！？…"
        or 0x3041 <= ord(ch) <= 0x3096
        or 0x30A1 <= ord(ch) <= 0x30FA
        or 0x4E00 <= ord(ch) <= 0x9FFF
        for ch in value
    ):
        return "UNSUPPORTED_SOURCE"
    return None


def make_l1_envelope(
    source_text: object,
    source_revision: object,
    context_text: object,
    manifest: object,
    paths: object,
) -> L1Envelope:
    """Only register bounded whole-utterance hypotheses. NEVER run G2P or SMC."""
    source_error = _source_error(source_text, source_revision)
    if source_error:
        return _envelope_refusal(source_error)
    context_error = _context_error(context_text, source_revision, "ja-JP")
    if context_error:
        return _envelope_refusal(context_error)
    manifest_error = _manifest_error(manifest)
    if manifest_error:
        return _envelope_refusal(manifest_error)
    assert isinstance(manifest, EvidenceManifest)
    cd = context_hash(context_text, source_revision)
    if cd != manifest.context_digest:
        return _envelope_refusal("CONTEXT_MISMATCH")
    if type(paths) is not tuple:
        return _envelope_refusal("INVALID_PATHS")
    if len(paths) > _MAX_PATHS:
        return _envelope_refusal("CANDIDATE_LIMIT")
    if not paths:
        return _envelope_refusal("NO_CANDIDATES", status="ABSTAIN")
    mid = manifest_id(manifest)
    for path in paths:
        if type(path) is not ReadingPath:
            return _envelope_refusal("INVALID_PATHS")
        if type(path.evidence_id) is not str or path.evidence_id != mid:
            return _envelope_refusal("EVIDENCE_MISMATCH")
    proposal = make_proposal(source_text, source_revision, paths)
    if proposal.status != "PROPOSED" or type(proposal.proposal_digest) is not str:
        return _envelope_refusal("INVALID_PROPOSAL")
    identity = _hash("SMC7-L1R-ENVELOPE/v0", [
        _VERSION, proposal.proposal_digest, cd, mid,
    ])
    return L1Envelope("PROPOSED", "OK", cd, mid, identity, proposal)


def _selection_refusal(code: str) -> L1Selection:
    return L1Selection("REJECTED", code, None, None)


def select_l1_path(
    envelope: object,
    source_text: object,
    source_revision: object,
    context_text: object,
    manifest: object,
    paths: object,
    selected_path_id: object,
    actor: object,
) -> L1Selection:
    """Revalidate *all* caller-controlled material; no implicit top1 selection."""
    if type(envelope) is not L1Envelope:
        return _selection_refusal("STALE_ENVELOPE")
    assert isinstance(envelope, L1Envelope)
    if (type(envelope.status) is not str or type(envelope.code) is not str
            or type(envelope.context_digest) is not str
            or type(envelope.manifest_identity) is not str
            or type(envelope.envelope_id) is not str
            or type(envelope.proposal) is not ReadingProposal):
        return _selection_refusal("STALE_ENVELOPE")
    inherited = envelope.proposal
    # A frozen dataclass is publicly constructible. Check built-in types before
    # an equality call: mock.ANY and custom __eq__ must never authenticate.
    if (type(inherited.source_text) is not str
            or type(inherited.source_revision) is not str
            or type(inherited.source_digest) is not str
            or type(inherited.proposal_digest) is not str
            or type(inherited.status) is not str
            or type(inherited.code) is not str
            or type(inherited.paths) is not tuple):
        return _selection_refusal("STALE_ENVELOPE")
    verified_proposal = make_proposal(inherited.source_text,
                                      inherited.source_revision, inherited.paths)
    if verified_proposal.status != "PROPOSED" or inherited != verified_proposal:
        return _selection_refusal("STALE_ENVELOPE")
    rebuilt = make_l1_envelope(source_text, source_revision,
                               context_text, manifest, paths)
    if rebuilt.status != "PROPOSED" or envelope != rebuilt:
        return _selection_refusal("STALE_ENVELOPE")
    if not _ascii(selected_path_id):
        return _selection_refusal("SELECTION_REQUIRED")
    if not _ascii(actor):
        return _selection_refusal("INVALID_ACTOR")
    assert rebuilt.proposal is not None
    if selected_path_id not in {p.path_id for p in rebuilt.proposal.paths}:
        return _selection_refusal("UNKNOWN_SELECTED_PATH")
    sid = _hash("SMC7-L1R-SELECTION/v0",
                [rebuilt.envelope_id, selected_path_id, actor])
    return L1Selection("SELECTED", "OK", selected_path_id, sid)


def _reading_text(value: object) -> bool:
    # A string is a complete utterance reading here, NOT a word fragment.
    return (type(value) is str and 1 <= len(value) <= _MAX_SOURCE_CHARS
            and _scalar(value) and all(0x30A1 <= ord(x) <= 0x30FA
                                        or ord(x) == 0x30FC for x in value))


def evaluate_paths(gold: object, candidates: object) -> ReadingMetrics:
    """Exact sample-level set recall and burden, no model/gold coupling.

    Caller must separately establish dataset permission, held-out provenance,
    corpus policy and multiple-gold adjudication before linguistic claims.
    """
    if (type(gold) is not tuple or type(candidates) is not tuple
            or not 1 <= len(gold) <= _MAX_METRIC_SAMPLES
            or len(candidates) != len(gold)):
        raise ValueError("INVALID_SAMPLE_COUNT")
    hits = [0, 0, 0]
    total = 0
    for refs, outputs in zip(gold, candidates):
        if (type(refs) is not tuple or not 1 <= len(refs) <= 8
                or type(outputs) is not tuple or len(outputs) > _MAX_PATHS):
            raise ValueError("INVALID_PATH_SET")
        if (not all(_reading_text(x) for x in refs)
                or not all(_reading_text(x) for x in outputs)):
            raise ValueError("INVALID_READING")
        if len(set(refs)) != len(refs) or len(set(outputs)) != len(outputs):
            raise ValueError("DUPLICATE_READING")
        total += len(outputs)
        reference = set(refs)
        for i in range(3):
            if reference.intersection(outputs[:i + 1]):
                hits[i] += 1
    n = len(gold)
    return ReadingMetrics(n, hits[0], hits[1], hits[2], total,
                          Fraction(hits[0], n), Fraction(hits[1], n),
                          Fraction(hits[2], n), Fraction(total, n))
