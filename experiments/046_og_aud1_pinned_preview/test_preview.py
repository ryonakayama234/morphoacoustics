"""Experiment046: isolated preview acceptance tests, not formal Gate B."""
from __future__ import annotations
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
import og_aud1_preview as p


class PreviewTest(unittest.TestCase):
    def test_prepared_body_identity(self):
        a,b=p.prepare_body(.00015),p.prepare_body(.0006)
        self.assertNotEqual(a["preparation_digest"],b["preparation_digest"])
        self.assertEqual(a["blueprint"]["junctions"][0]["ports"],["A.out","B.in","C.in"])
        self.assertEqual([v["kind"] for v in a["blueprint"]["loads"]],["matched","matched"])
        self.assertEqual(a["blueprint"]["source"]["port"],"A.in")
        with self.assertRaises(ValueError):
            p.prepare_body(.00025)

    def test_six_ports_source_wav_and_repeated_bytes(self):
        receipt,files=p.compute_pair()
        repeat,files2=p.compute_pair()
        self.assertEqual(receipt,repeat)
        self.assertEqual(files,files2)
        self.assertEqual(receipt["schema"],p.SCHEMA)
        self.assertGreater(receipt["relative_raw_pressure_rms_difference"],.7)
        u=np.load(io.BytesIO(files[receipt["source_path"]]),allow_pickle=False)
        self.assertEqual((u.shape,u.dtype.str),((48000,),"<f8"))
        self.assertEqual(receipt["source_sha256"],p.digest(files[receipt["source_path"]]))
        for record in receipt["records"]:
            ports=np.load(io.BytesIO(files[record["six_port_path"]]),allow_pickle=False)
            pressure=np.load(io.BytesIO(files[record["raw_pressure_path"]]),allow_pickle=False)
            self.assertEqual(ports.shape,(6,2,48000))
            np.testing.assert_array_equal(ports[0,0],pressure)
            np.testing.assert_array_equal(ports[0,1],u)
            np.testing.assert_array_equal(ports[1,0],ports[2,0])
            np.testing.assert_array_equal(ports[1,0],ports[4,0])
            self.assertLess(np.max(np.abs(ports[1,1]-ports[2,1]-ports[4,1])),1e-15)
            with wave.open(io.BytesIO(files[record["wave_path"]]),"rb") as wav:
                self.assertEqual((wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),wav.getnframes()),(1,2,48000,48000))
                pcm=np.frombuffer(wav.readframes(48000),"<i2")
            np.testing.assert_array_equal(pcm,np.rint(pressure*receipt["shared_playback_gain_inverse_pa"]*32767).astype("<i2"))
            for name in (record["wave_path"],record["raw_pressure_path"],record["six_port_path"]):
                self.assertEqual(receipt["artifact_sha256"][name],p.digest(files[name]))

    def test_atomic_immutable_directory_and_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"new"
            r=p.run(out)
            original=hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest()
            self.assertEqual(r["core_commit"],subprocess.check_output(["git","rev-parse","HEAD"],cwd=p.ROOT,text=True).strip())
            with self.assertRaises(FileExistsError): p.run(out)
            self.assertEqual(hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest(),original)


if __name__=="__main__":
    unittest.main()
