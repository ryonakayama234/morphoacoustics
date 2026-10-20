"""Regression tests of experiment-local OG-AUD1 prototype (not production)."""
import io
import tempfile
import unittest
from pathlib import Path
import wave
import numpy as np
import monitor as m

# Independently assembled 12-state Wolfram global p/q oracle, not OG-4's API.
# Frequencies are FFT bin indices at 48k / 131072 Hz resolution.
ORACLE = {
    0.00015: {
        0: (914666.6666666669, 0.0),
        912: (1042702.4731353689, 360547.4138831005),
        2000: (1602004.4678172613, 559841.9119938943),
        3000: (2054054.0465644242, -67051.99136610457),
        6000: (917796.3177135957, 59736.41810470243),
        10000: (1406691.1454631877, -566091.7767368061),
    },
    0.00060: {
        0: (457333.33333333343, 0.0),
        912: (569153.5948545557, 629769.2375775203),
        2000: (1458695.155810588, 1631233.7728404065),
        3000: (4066009.389491543, -424735.11648391385),
        6000: (459842.2048290929, 95774.89272405088),
        10000: (1038541.7626076017, -1337402.2088780897),
    },
}

class MonitorTests(unittest.TestCase):
    def test_wolfram_global_grid_oracle(self):
        for area, bins in ORACLE.items():
            for k, (real, imag) in bins.items():
                f = k*m.SAMPLE_RATE/m.NFFT
                actual, reflect = m.transfer(area, np.array([f]))
                want = complex(real, imag)
                self.assertLess(abs(actual[0]-want)/abs(want), 1e-10)
                self.assertTrue(-1 < reflect < 1)
                self.assertGreater(actual[0].real, 0)

    def test_two_runs_byte_stable_and_wav(self):
        a, files = m.compute_pair()
        b, again = m.compute_pair()
        self.assertEqual(a, b)
        self.assertEqual(files, again)
        self.assertEqual(len(files), 5)
        self.assertGreater(a['relative_raw_pressure_rms_difference'], 1e-3)
        gain = a['pair_playback_gain_inverse_pa']
        self.assertGreater(gain, 0)
        for record in a['records']:
            x = np.load(io.BytesIO(files[record['pressure_path']]), allow_pickle=False)
            self.assertEqual(x.shape, (48000,))
            with wave.open(io.BytesIO(files[record['wav_path']]), 'rb') as wav:
                self.assertEqual((wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),wav.getnframes()),(1,2,48000,48000))
                pcm = np.frombuffer(wav.readframes(48000), '<i2')
                np.testing.assert_array_equal(pcm, np.rint(x * gain * 32767).astype('<i2'))
            self.assertLess(record['diagnostic']['prestart_peak_fraction'], 1e-5)
            self.assertLess(record['diagnostic']['tail_peak_fraction'], 1e-5)
            self.assertGreater(record['diagnostic']['source_pressure_work_J'], 0)

    def test_refuse_invalid_source_and_unsupported_body(self):
        with self.assertRaisesRegex(ValueError, 'INVALID:SOURCE_SAMPLES'):
            m.render_pressure(np.full(m.N_SAMPLES, float('nan')), 0.00015)
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED:C_AREA'):
            m.render_pressure(m.source(), 0.0003)
        with self.assertRaisesRegex(ValueError, 'INVALID:FREQUENCY_GRID'):
            m.transfer(0.00015, np.array([-1.0]))

    def test_refuse_existing_output_without_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'run'
            first = m.run(root)
            sha = m.sha256((root/'manifest.json').read_bytes())
            with self.assertRaises(FileExistsError):
                m.run(root)
            self.assertEqual(m.sha256((root/'manifest.json').read_bytes()), sha)
            self.assertEqual(first['status'], m.STATUS)

    def test_wrong_particle_velocity_law_is_falsified(self):
        # Two matched branches would (incorrectly) treat q-volume flow
        # with a different relative C coefficient under particle law.
        for area in m.C_AREAS_M2:
            f = 997.0
            true, _ = m.transfer(area, np.array([f]))
            z0 = m.RHO*m.SOUND_SPEED/m.AREA_A
            # wrong: u_A = (u_B+u_C), treating u as particle velocity;
            # equivalent bogus volumetric junction Y = (S_A/S_B)/Z_B+(S_A/S_C)/Z_C
            zb = m.RHO*m.SOUND_SPEED/m.AREA_B
            zc = m.RHO*m.SOUND_SPEED/area
            bogus_load = 1.0 / ((m.AREA_A/m.AREA_B)/zb + (m.AREA_A/area)/zc)
            r_bad = (bogus_load-z0)/(bogus_load+z0)
            delay = np.exp(-4j*np.pi*f*m.L_A/m.SOUND_SPEED)
            bad = z0*(1+r_bad*delay)/(1-r_bad*delay)
            self.assertGreater(abs(bad-true[0])/abs(true[0]), 0.01)

if __name__ == '__main__':
    unittest.main()
