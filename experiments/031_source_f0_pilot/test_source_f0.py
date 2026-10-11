"""Non-physics policy tests for the preregistered F0-only source experiment."""
from __future__ import annotations

import unittest

import numpy as np

from morphoacoustics.integration import limited_live as live
from run import F0_S0, F0_F1, source_for_f0, rms, pcm_wav


class SourceF0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exp = live._load_audited_experiment()
        cls.exp13 = cls.exp.EXP26.EXP13

    def test_baseline_reconstructs_exact_adopted_source(self) -> None:
        adopted = np.asarray(
            self.exp13.build_sources()[0][live.SOURCE_ID].source, dtype=np.float64
        )
        s0, params = source_for_f0(self.exp13, F0_S0)
        self.assertTrue(np.array_equal(adopted, s0))
        self.assertEqual(params["f0_hz"], 100.0)
        self.assertEqual(params["nominal_cycles_in_clip"], 50.0)
        self.assertEqual(params["rd"], 1.0)

    def test_f0_is_the_only_changed_source_parameter(self) -> None:
        a, pa = source_for_f0(self.exp13, F0_S0)
        b, pb = source_for_f0(self.exp13, F0_F1)
        self.assertEqual(pa["nominal_period_samples"], 480.0)
        self.assertEqual(pb["nominal_period_samples"], 400.0)
        self.assertEqual(pb["nominal_cycles_in_clip"], 60.0)
        for key in ("rd", "ra", "rk", "rg", "tp", "te", "ta", "alpha", "balance"):
            self.assertEqual(pa[key], pb[key])
        self.assertEqual(a.shape, (24000,))
        self.assertEqual(b.shape, (24000,))
        self.assertTrue(np.isfinite(a).all())
        self.assertTrue(np.isfinite(b).all())
        self.assertFalse(np.array_equal(a, b))
        self.assertAlmostEqual(float(np.max(a)), float(np.max(b)), places=12)

    def test_unregistered_f0_is_rejected(self) -> None:
        for value in (0, 99, 121, 240, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                source_for_f0(self.exp13, value)

    def test_pcm_encoder_requires_finite_safe_playback_amplitude(self) -> None:
        values = np.zeros(live.SAMPLES, dtype=np.float64)
        values[1024] = 0.2
        audio, metadata = pcm_wav(values)
        self.assertTrue(audio.startswith(b"RIFF"))
        self.assertGreater(metadata["rms_normalized"], 0)
        with self.assertRaises(RuntimeError):
            pcm_wav(np.ones(live.SAMPLES, dtype=np.float64))
        with self.assertRaises(RuntimeError):
            pcm_wav(np.full(live.SAMPLES, np.nan))


if __name__ == "__main__":
    unittest.main()
