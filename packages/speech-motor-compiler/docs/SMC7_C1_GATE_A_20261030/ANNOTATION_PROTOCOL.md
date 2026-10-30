# Gate A / independent Japanese-reading gold annotation manual
2026-10-30 JST | DRAFT FOR 120-PILOT ONLY | #244. This is **not** frozen gold or evidence annotators have been hired.

## Target and roles
Annotate contemporary standard ja-JP complete-utterance pronunciation in fullwidth katakana; a reading is not IPA, pitch accent, devoicing, acoustic output, articulatory action or body feasibility.
Roles: two **different actual human Japanese-competent** annotators A and B, and a third independent human adjudicator C. A and B receive the SAME exact original script/context, independently, **without B0/B1/C predictions, candidate sets, benchmark expected answers, each other's answers or hints about preferred target reading**. C receives raw A+B only after both submissions lock; C must not see provider guesses. Preserve original annotations, disagreements, timestamps and role separation; no LLM-impersonated plurality.

## Case record
case_id, content_sha256, immutable source UTF-8/revision, context identity, family_id, document_id, stratum, original target [start,end) Unicode **codepoint** interval (not bytes or rendered graphemes), source legal-rights reference; exact original spelling never silently normalized. Authoritative target interval comes from independent source annotation, not target kana marker positions.

## Reviewer output
Independent reviewer_id alias, manual_revision, completion timestamp, status SINGLE / MULTI_ACCEPTABLE / UNKNOWN / CONTEXT_INSUFFICIENT / UNSUPPORTED with explanation; one or more **complete** acceptable katakana utterance paths, original-span target readings, acceptable alternate readings and rationale, confidence as subjective narrative (NOT a calibrated number). If a legitimate reading is unresolved, mark UNKNOWN; do not invent a singleton truth.
For C 400, demand 100 **exact orthographic word families** each with four meaningfully contrasting contexts and >=2 verified readings across those four contexts. A word family is NOT just the same individual kanji under different compound words.

## Transcription policy draft v0.1 (pilot to refine, no heldout outcome access)
- Preserve original source byte digest and codepoints. Derived phonological kana is separate, never source-mutate NFC/NFKC silently.
- Fullwidth katakana for spoken reading, particle reading rather than visually copied script where divergent. Do not encode F0/accent, timing, speaking style or physical organs as reference text.
- Record long vowel notation alternatives (e.g. vowel series versus long mark) and explicit canonical-equivalence proposals rather than silently substituting. Freeze exact normalization and acceptable variants only after independent 120 pilot.
- Explicit punctuation/pauses: keep original characters in a separate source-boundary layer; a pilot-proposed exact comparison canonicalization must document whether standard punctuation is copied or dropped. Different policies cannot be compared as if same truth.
- Numerals, proper names, loanwords, rare surnames, dialectal readings and OOV: ask for context and label UNKNOWN if necessary, do not fabricate. Annotate genuine ambiguity and retain multi-gold. Distinguish unknown language from unsupported L0 source repertoire.
- Complete spoken-path reading coverage is obligatory; no only-target-kanji gold. Alignment to original non-silent characters must be independently checked before any L0 motor admission; text-only G2P is not authoritative alignment.

## Partition and quality gates
Pilot 120 independent families/docs (used only for manual/provider selection and normalization). Heldout 880 with C400 (100 families×4), O240 varied ordinary, U160 names/OOV (separate resolvable/unknown), A80 genuinely underdetermined. Partition at document + orthographic family + exact/near-duplicate text levels; no text/family/doc from pilot may appear in heldout; never use heldout reference keys to generate candidates.
A and B annotate all eligible original cases independently, C adjudicates any conflict; raw confusion matrices, agreement, multiple acceptable labels and unresolved C proportion preserved. If C unresolved >5%, existing protocol demands MORE_DATA_INVALID_GOLD. Do NOT unilaterally exclude difficult sentences to rescue accuracy.

## Access control and freeze
Raw licensed text and gold kept in access-controlled research storage with allowed permissions, not public Git by default. Publish only lawful hashes, source DOI/URL/revisions, counts and reviewed aggregate findings. Corpus freeze requires actual immutable originals + rights/NOTICE, 120/880 partition hashes, blind annotations from A+B, independent C decisions, valid multi-gold, annotation manual and normalization version, exact provider/model/lexicon/prompt/dependencies, predeclared bootstrap groupings, evaluator version and leakage check before ANY heldout prediction inspection.
C1 code implementation and score evaluation do not proceed from a draft manual or unverified source alone.

## Disagreement adjudication taxonomy
HETERONYM_CONTEXT / PARTICLE_PRONUNCIATION / LONG_VOWEL_CONVENTION / PUNCTUATION_AND_BOUNDARY / NAME_OOV / MULTIPLE_NATURAL / UNKNOWN / SOURCE_INTERVAL_ERROR / ANNOTATOR_TRANSCRIPTION_ERROR / OTHER. Preserve A and B raw strings and edits separately; C may accept multiple readings or explicitly abstain without forcing majority vote.

## Safety falsifiers
Any generator-predicted reading shown to A or B; one person acting as both independent annotations; hidden forced unique for legitimate ambiguity; absent rights; original source offsets projected from kana string matching; pilot and heldout family overlap; source text silently modified; or heldout labels used in a prompt: FAIL / NO FREEZE.
