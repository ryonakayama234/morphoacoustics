# DATA — limited registry record and CLI contract

Namespace: `cc-b1-body-revision-registry/v0` (research-only); **not** Performance Contract v0/v1 and not an extension of the committed CLI performer v1 schema.

Operations:
- `python tools/cc_b1_revision_registry.py --register --registry-dir DIR --archive-dir PHYSICAL_ARCHIVE` validates the existing physical archive through the strict CLI v1 verifier before accepting a receipt. Registry DIR must already exist as a trusted non-symlink local directory.
- `python tools/cc_b1_revision_registry.py --resolve --registry-dir DIR --revision-id cc-b1-<64 lower-case hex>` returns the exact trusted receipt reconstructed from the Core baseline and stored canonical record. Does **not** replay synthesis.
- Only one operation, no request overrides of source, motor, F0, geometry, physical law, or arbitrary ratio.

Record **canonical UTF-8 JSON** (sorted compact keys, `allow_nan=False`, no LF) at `DIR/revisions/<revision_id>.json`:
```json
{
  "schema_version": "cc-b1-body-revision-registry/v0",
  "revision_id": "<derived Core identity>",
  "rest_area_ratio": "0.90 or 1.10",
  "body_revision": {"...": "exact Core-generated BodyRevision receipt"},
  "body_revision_sha256": "sha256:<SHA256 canonical body_revision bytes>"
}
```

Payload bytes and the outer record are recomputed from *trusted installed Core code plus trusted M0/r1*, not accepted from caller-provided JSON. The 64-byte digest is an integrity checksum **not** a signature. IDs are content-derived from Core's immutable edit. Registry files have maximum bounded size, exclusive creation (mode 0600), no overwrites, and verified canonical rereads. Only `0.90`/`1.10` are legitimate for this capability; absent/mutated/unknown revision returns typed non-success. A pair of archive runs of the same body must not create multiple different BodyRevisions.

No auto migration of older creator contract, no implicit selection of `latest`; future version upgrades must use a new version and explicit migration with provenance. Currently limited CLI and local file store do not provide authorized multi-user identity or hostile-race guarantees.

### Publication guarantees and limits

Registration is two-phase within the **same filesystem directory**: fsynced `.stage-<random>` data precedes `os.link` with `FileExistsError` idempotency check against exact canonical bytes. The stable revision name is never opened for a non-exclusive write and is never replaced. The file read requires regular inode, one link, maximum 8192 bytes, non-group/other permissions; exact canonical equality to a freshly rederived trusted Core record. On re-read failure, return non-success and do not invent a body. A concurrent resolver can refuse during the link-count-2 staging window; a subsequent read succeeds after staging name removal. On crash a staging file may remain; a privileged/manual review is required before cleanup. This candidate requires a POSIX/Linux filesystem (including normal WSL2 Linux-side filesystem); network mounts and Windows filesystem semantics are **not** validated. No durable signed chain-of-custody, no multiwriter hostile race proof, no remote service exposure.
