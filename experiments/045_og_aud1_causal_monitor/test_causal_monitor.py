"""Exploratory scientific/regression controls for OG-AUD1 Experiment 045."""
import io
import tempfile
import unittest
from pathlib import Path
import wave

import numpy as np
import causal_monitor as m

# Independently returned Wolfram evaluator numbers at 733 Hz, 2026-10-20.
WOLFRAM_ZIN_733 = {
    .00015: complex(1603112.2733702508, 559611.8806294522),
    .0006: complex(1461638.155840067, 1632724.2267963341),
}


class CausalMonitorTest(unittest.TestCase):
    def test_wolfram_frequency_oracle(self):
        for area, expected in WOLFRAM_ZIN_733.items():
            z0, r, tau = m.physical_parameters(area)
            actual = z0 * (1 + 2 * sum(
                r**k * np.exp(-2j * np.pi * 733 * k * tau)
                for k in range(1, m.ECHO_COUNT + 1)
            ))
            self.assertLess(abs(actual - expected) / abs(expected), 1e-12)

    def test_all_ports_signed_flow_and_passivity(self):
        t = np.arange(m.FRAMES) / m.FS
        for area in m.AREAS_C:
            states, diag = m.ports(t, area)
            self.assertEqual(set(states), {"A.in", "A.out", "B.in",
                                           "B.out", "C.in", "C.out"})
            self.assertLess(diag["relative_energy_imbalance"], 1e-6)
            self.assertLess(diag["max_junction_flow_residual_m3s"], 1e-15)
            self.assertTrue(np.array_equal(states["A.out"][0], states["B.in"][0]))
            self.assertTrue(np.array_equal(states["A.out"][0], states["C.in"][0]))

    def test_exact_source_prestart_and_echo_tail(self):
        t = np.arange(m.FRAMES) / m.FS
        for area in m.AREAS_C:
            states, diag = m.ports(t, area)
            self.assertTrue(np.all(states["A.in"][0][t < .10] == 0))
            self.assertTrue(np.all(states["A.in"][0][t > .50] == 0))
            self.assertLess(diag["omitted_echo_pressure_upper_bound_pa"], 1e-10)

    def test_wrong_no_reflection_mutant_is_rejected(self):
        t = np.arange(m.FRAMES) / m.FS
        u = m.source(t)
        for area in m.AREAS_C:
            p, _ = m.ports(t, area)
            correct = p["A.in"][0]
            z0, _, _ = m.physical_parameters(area)
            wrong = z0 * u  # invalidly drops the A<->J reflection
            self.assertGreater(np.sqrt(np.mean((wrong-correct)**2)) /
                               np.sqrt(np.mean(correct**2)), .1)

    def test_deterministic_fresh_wav_pair_and_source_identity(self):
        receipt, files = m.compute()
        repeat, files2 = m.compute()
        self.assertEqual(receipt, repeat)
        self.assertEqual(files, files2)
        self.assertGreater(receipt["relative_raw_pressure_rms_difference"], .7)
        self.assertEqual(receipt["source_sha256"], m.sha256(files["raw_U_m3_s.npy"]))
        gain = receipt["shared_playback_gain_inverse_pa"]
        for record in receipt["records"]:
            pressure = np.load(io.BytesIO(files[record["raw_pressure_path"]]))
            with wave.open(io.BytesIO(files[record["wave_path"]]), "rb") as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth(),
                                  wav.getframerate(), wav.getnframes()),
                                 (1, 2, 48000, 48000))
                pcm = np.frombuffer(wav.readframes(48000), "<i2")
                np.testing.assert_array_equal(
                    pcm, np.rint(pressure*gain*32767).astype("<i2"))

    def test_refusal_and_atomic_directory_immutability(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED"):
            m.ports(np.arange(10, dtype=float), .00025)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            m.ports(np.array([float("nan")]), .00015)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "fresh"
            m.run(output)
            digest = m.sha256((output/"manifest.json").read_bytes())
            with self.assertRaisesRegex(FileExistsError, "IMMUTABLE"):
                m.run(output)
            self.assertEqual(m.sha256((output/"manifest.json").read_bytes()), digest)


if __name__ == "__main__":
    unittest.main()
