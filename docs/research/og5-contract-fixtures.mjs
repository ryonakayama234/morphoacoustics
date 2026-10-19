// Independent design-byte verifier. No production graph validator or solver.
import fs from 'node:fs';
import crypto from 'node:crypto';
const root = new URL('.', import.meta.url);
const g = JSON.parse(fs.readFileSync(new URL('og5-contract-goldens.json', root), 'utf8'));
const legacy = JSON.parse(fs.readFileSync(new URL('og5-blueprint-goldens.json', root), 'utf8'));
function assert(ok, label) { if (!ok) throw new Error(label); }
function size(n) { const b = Buffer.alloc(4); b.writeUInt32BE(n); return b; }
function encode(v) {
  if (typeof v === 'number') {
    assert(Number.isFinite(v), 'finite number');
    const b = Buffer.alloc(9); b[0] = 100; b.writeDoubleBE(v === 0 ? 0 : v, 1); return b;
  }
  if (typeof v === 'string') {
    assert([...v].every(c => c.charCodeAt(0) < 128), 'ASCII');
    const b = Buffer.from(v, 'ascii'); return Buffer.concat([Buffer.from('s'), size(b.length), b]);
  }
  if (Array.isArray(v)) return Buffer.concat([Buffer.from('l'), size(v.length), ...v.map(encode)]);
  assert(v !== null && typeof v === 'object', 'map');
  const keys = Object.keys(v).sort();
  return Buffer.concat([Buffer.from('m'), size(keys.length), ...keys.flatMap(k => [encode(k), encode(v[k])])]);
}
function vector(kind, payload) {
  const bytes = encode(payload);
  const prefixed = Buffer.concat([Buffer.from(g.domains[kind] + '\0', 'ascii'), bytes]);
  return {domain: g.domains[kind], canonical_hex: bytes.toString('hex'),
    domain_prefixed_hex: prefixed.toString('hex'),
    digest: 'sha256:' + crypto.createHash('sha256').update(prefixed).digest('hex')};
}
function equalVector(actual, expected, label) {
  for (const k of ['domain', 'canonical_hex', 'domain_prefixed_hex', 'digest']) assert(actual[k] === expected[k], label + '.' + k);
}
function canonical(bp) {
  const b = structuredClone(bp);
  for (const [collection, key] of [['organs','id'], ['junctions','id'], ['loads','port']]) {
    b[collection].sort((a,b) => a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0);
  }
  return b;
}
function prepPayload(s) { return Object.fromEntries(['schema','digest_version','backend_id','blueprint_digest'].map(k => [k,s[k]])); }
for (const [name, row] of Object.entries(g.blueprint_snapshot_variants)) {
  const s = row.snapshot;
  assert(vector('blueprint', canonical(row.input)).digest === s.blueprint_digest, name + ' input digest');
  assert(vector('blueprint', s.blueprint).digest === s.blueprint_digest, name + ' snapshot digest');
  assert(vector('preparation', prepPayload(s)).digest === s.preparation_digest, name + ' preparation');
  if (name in legacy.expected) assert(s.blueprint_digest === legacy.expected[name], name + ' inherited');
}
const base = g.blueprint_snapshot_variants.baseline.snapshot;
equalVector(vector('blueprint', base.blueprint), g.byte_vectors.baseline_blueprint, 'blueprint bytes');
equalVector(vector('preparation', prepPayload(base)), g.byte_vectors.baseline_preparation, 'preparation bytes');
for (const name of ['baseline_observation', 'ordered_duplicate_observation']) {
  const observation = g[name]; const {observation_digest, ...payload} = observation;
  const v = vector('observation', payload); assert(v.digest === observation_digest, name + ' digest');
  equalVector(v, g.byte_vectors[name], name + ' bytes');
  const n = observation.frequencies_hz.length;
  assert(observation.port_ids.length === 10, '10 ports');
  for (const field of ['pressure_pa','volume_flow_m3_s','mean_power_w']) {
    assert(observation[field].length === n && observation[field].every(row => row.length === 10), name + ' ' + field + ' shape');
  }
  assert(observation.diagnostics.length === n, 'diagnostic shape');
}
equalVector(vector('blueprint', {number: -0}), g.byte_vectors.negative_zero, '-zero');
equalVector(vector('blueprint', {number: 0}), g.byte_vectors.positive_zero, '+zero');
assert(g.byte_vectors.positive_zero.digest === g.byte_vectors.negative_zero.digest, 'zero normalization');
// Error fixtures are normative expectations for future Gate B, not exercised
// through a nonexistent production validator by this byte-only design tool.
for (const row of g.error_contract_fixtures) {
  const e = row.expected_error;
  assert(row.expected_message === `${e.status}:${e.code}:${e.path}`, row.name + ' error message');
}
console.log(JSON.stringify({status:'PASS', snapshot_variants:Object.keys(g.blueprint_snapshot_variants).length,
  byte_vectors:Object.keys(g.byte_vectors).length,
  error_contract_fixtures:g.error_contract_fixtures.length,
  scope:'independent JavaScript bytes/hashes/shapes; no production validation or solver execution'}));
