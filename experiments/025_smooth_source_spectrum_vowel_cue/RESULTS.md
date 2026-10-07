# Experiment 025 results — smooth source-spectrum vowel cue

Issue: #55

## Current decision

**CLOSED_SET_CUE_SUPPORTED; HUMAN_GATE_INCOMPLETE; VOICE_LIKENESS_FAILED_QUALITATIVELY**

The preregistered objective Gate passed. The human session was deliberately stopped with one missing response after the listener reported that the stimuli remained buzzer-like and were not experienced as meaningful voice. Therefore the preregistered 30/30 human Gate is not declared PASS or FAIL.

After the responses were frozen, the key was opened for descriptive analysis only. All 29 answered trials were correct.

## Provenance

- GitHub Actions run: 37553098145
- branch: `v1b-smooth-source-spectrum`
- source commit: `25a9046773015946fc21fe4f8240b820ed1f614b`
- full output artifact ID: `11453931273`
- full output digest: `sha256:fd3644cd60d67764272982f7ca924a19a136df8cf8f3746d91de2dea585648e5`
- public blind-listening artifact ID: `11454125625`
- public blind-listening digest: `sha256:b2ec2d19d149fd37a18a8ec5ff12f987ce48e192c91e36696930d83821b8be0e`

## Objective Gate

### Tract oracle

PASS.

All 15 checked Arai /a i u/ tract peaks remain exactly equal to the checked-in Experiment-023 oracle on the 0.25 Hz scan grid.

### Source oracle

PASS.

Maximum source harmonic-ratio error against the independent Wolfram oracle is below `6e-14 dB`.

### Cycle-boundary artifact

PASS.

- S0 LF baseline: `4.4062e-05`
- S2 cos/n² diagnostic: **`0.0047490`**
- frozen requirement: **< 0.01**

Independent Wolfram pre-implementation prediction for S2 was `0.0047014`.

### Rendered vowel cue

S0 P2/P1:

- /a/: -10.5463 dB
- /i/: -28.7989 dB
- /u/: -23.5550 dB

S2 P2/P1:

- /a/: -6.0487 dB
- /i/: **-14.9687 dB**
- /u/: -14.8911 dB

For /i/:

- improvement: **+13.8302 dB**
- frozen requirement: **>= +10 dB**
- result: PASS

The pre-implementation Wolfram prediction was approximately +14.9241 dB.

### Other objective checks

- rendered oracle tolerance: PASS under the preregistered 2.5 dB engineering tolerance;
- startup artifact: PASS;
- all outputs finite: PASS;
- listening level match: PASS;
- steady-RMS spread: `5.55e-17`;
- no clipping.

## Human Gate

A fresh blind set uses seed 25025:

- 10 /a/
- 10 /i/
- 10 /u/
- choices: a / i / u / UNIDENTIFIABLE

Response semantics are explicit:

> If two vowels seem mixed and neither is clearly primary, choose UNIDENTIFIABLE.

Frozen Gate:

- each vowel >=8/10;
- total >=24/30;
- no previously passing vowel may fall below 8/10.

Voice quality is evaluated separately from categorical identity.

## Human session result

Frozen responses contained 29 categorical answers and one missing response (T12). The missing item was not silently converted to UNIDENTIFIABLE.

After freezing and ending the session, the blind key was opened descriptively:

- answered /a/: 10/10 correct;
- answered /i/: 9/9 correct;
- answered /u/: 10/10 correct;
- answered total: **29/29 correct**;
- T12 was true /i/ and remained **MISSING**.

The preregistered 30-item Gate is therefore formally incomplete. Even so, the answered trials show essentially complete three-way closed-set separability.

Independent Wolfram summaries for the 29 answered trials:
- empirical information carried by the three-class responses: 1.5832 bits out of log2(3)=1.5850 bits;
- 29/29 under an independent unbiased three-choice reference: ~1.46e-14.

These are engineering descriptors, not population-level statistics.

### Qualitative result

The listener reported:

- buzzer-like quality: u > i > a;
- the stimuli were perceived more as tones/sounds than as voice;
- /a/ was the only category that felt clearly speech-like without strong prompting;
- /i/ versus /u/ could usually be selected once the candidate set was supplied, but without that prior set the signal carried little obvious phonetic or linguistic meaning.

This dissociates **closed-set categorical discriminability** from **voice-likeness / open-set phonetic meaning**.

## Research interpretation

This dissociation is consistent with prior speech-perception results:

- Remez et al. (1981) showed that highly artificial sine-wave replicas can preserve linguistic information despite obviously unnatural speech quality: https://pubmed.ncbi.nlm.nih.gov/7233191/
- open-response synthetic-speech tests degrade much more than closed-response tests as intelligibility worsens, showing reliance on response-set constraints: https://pmc.ncbi.nlm.nih.gov/articles/PMC3512093/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC3917555/
- Bunton & Story (2010) found that time-varying area functions and natural durations improve synthetic-vowel identification over static area functions: https://pmc.ncbi.nlm.nih.gov/articles/PMC2855717/
- Klatt & Klatt (1990) show that voice quality depends on source properties such as harmonic structure, aspiration, formant bandwidths, and source-related coupling effects, not formant placement alone: https://pubmed.ncbi.nlm.nih.gov/2137837/
- Titze (2008) shows that the voice source and vocal tract are physically coupled and that the glottal source spectrum is affected by tract loading: https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/

The Experiment-025 source was intentionally diagnostic:
sum cos(2*pi*n*F0*t)/n^2.

Wolfram gives the infinite-series limit on one period as a periodic quadratic function, not a physiological glottal flow pulse. Its harmonic amplitude envelope is -12.04 dB/octave before the downstream observer. Therefore success of this source should be interpreted as evidence about spectral cue availability, not as progress toward a natural voice source.

## Claim boundary and next action

Supported:

> Increasing high-frequency excitation while preserving the artifact Gate can restore near-perfect closed-set /a i u/ discriminability in the current tract fixtures.

Not supported:

- biological vocal-fold realism;
- open-set phonetic identity;
- voice-likeness or naturalness;
- arbitrary Japanese speech;
- readiness to keep repeating the same forced-choice listening protocol.

Next work should move to #37's already-defined evaluation design: free kana transcription first, constrained identification second, voice-likeness/artifact as a separate axis, using natural Japanese references. In parallel, source work should compare the current LF-family source against a physically interpretable aperiodicity/aspiration candidate (#30) and a reduced self-oscillating vocal-fold source rather than further tuning diagnostic harmonic series.
