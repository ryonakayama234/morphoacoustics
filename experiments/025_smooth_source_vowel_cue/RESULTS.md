# Experiment 025 results — objective gate

Issue: #55

Current decision: **SMOOTH_SOURCE_DIAGNOSTIC_READY_FOR_LISTENING**.

The objective Gate passed. Human vowel identification remains unknown until blinded responses are frozen.

Key measurements:
- tract oracle: PASS, 0.0 Hz error on checked peaks;
- S2 source magnitude oracle: PASS to numerical precision;
- S2 cycle-boundary jump/RMS: 0.004749, required <0.01;
- /i/ rendered P2/P1: S0 -28.7989 dB -> S2 -14.9687 dB;
- /i/ improvement: +13.8302 dB, required >=+10 dB;
- differential source-to-rendered oracle error:
  - /a/ 0.00595 dB;
  - /i/ 0.00023 dB;
  - /u/ 0.00434 dB;
  all required <=0.5 dB;
- startup metric: PASS for all vowels;
- finite outputs: PASS;
- level matching/no clipping: PASS.

Canonical objective run:
- GitHub Actions run 37550290788;
- head 84ce5567270b137d644fa218e7f12ac76d81799c;
- full output artifact 11452686043;
- public S2 listening artifact 11452263906;
- public artifact digest sha256:46481e48859c44f21c4dc06a7c2fc4699ad2e1cefe99a903aadb100f80683173.

The public listening artifact contains only T01..T30 WAV files, manifest.csv, response_template.csv and README.txt. It excludes the blind key.

Human Gate remains frozen at every vowel >=8/10 and overall >=24/30. Identity and perceived quality are recorded separately.
