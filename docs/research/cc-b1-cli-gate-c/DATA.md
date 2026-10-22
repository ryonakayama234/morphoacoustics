# DATA — candidate command and data contract (freeze before code)

Command: `python tools/cc_b1_candidate_cli.py --protocol-version cc-b1-core-limited-performer/v1 --inspect`, or same version with `--perform --request PATH --output-dir PATH`, or `--verify --archive-dir PATH`. Exactly one operation. Version must be explicitly named; unknown version emits `UNSUPPORTED / SCHEMA_VERSION_UNSUPPORTED`.

All commands emit exactly one UTF-8 JSON object on stdout. No status message should be printed in prose on stdout. Exit `0` only for successful inspect/perform/verify; otherwise nonzero. For successful verification, the returned JSON is the original verified research manifest, not a synthetic Studio Take. Existing candidate schema `contracts/cc-b1/v1/core-limited-performer-request.schema.json` remains unchanged.

Strict `--request`: UTF-8 regular non-symlink file with at most 4096 bytes; reject duplicate object keys at **every depth**, NaN/Infinity, invalid UTF-8, and malformed JSON; typed `INVALID/REQUEST_JSON_INVALID`. Supported request must pass the existing candidate exact-key/schema/body/ratio validator. Do not reinterpret forbidden source or task controls as metadata.

Strict `--verify` preflight: archive path must exist as a non-symlink directory and `result.json` must be a non-symlink, at most 64 KiB strict JSON file without duplicate keys/nonfinite constants. Then call the inherited `verify_output_archive` to replay the Core-derived BodyRevision and original pressure/WAV SHA/quantized oracle checks. This parser is an additional outer safety boundary: it cannot make archived SHA a signature.

Conservative filesystem rule: any **existing** path component that is a symlink is refused; the `--perform` destination must not exist. Residual TOCTOU/permissions/race issues remain `NOT_TESTED` and block stable service adoption.

Failure transport: `{schema_version,status,error:{code,message},artifacts:[]}`; never return `SUCCEEDED` for invalid/unverified content. Do not leak host traceback/path details in machine response. Unknown CLI flags are parser errors, not silently ignored.
