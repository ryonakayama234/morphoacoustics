"""Exact printed M5 reference assertions and adversarial fail-closed tests."""
import csv
import io
import json
import unittest
from evaluate import (SOURCE, evaluate, git_blob_sha, kex_im, parse_rows,
                      read_source, reconstructed_p16_minus_p11_pa)

# Independent literal paper table review, separate from the production-like evaluator.
EXPECTED = {
 "0.005":[(3,"1.0","-0.723"),(5,"1.9","-1.103"),(10,"4.2","-0.567"),(15,"6.3","-0.346"),(25,"10.5","-0.077")],
 "0.0075":[(3,"2.3","-1.313"),(5,"4.3","-0.397"),(10,"9.2","0.114"),(15,"13.8","0.194"),(25,"22.1","0.228")],
 "0.01":[(3,"6.1","0.211"),(5,"10.2","0.279"),(10,"19.6","0.268"),(15,"27.3","0.257"),(25,"40.2","0.218")],
 "0.02":[(3,"29.7","0.275"),(5,"41.6","0.219"),(10,"64.7","0.167"),(15,"82.8","0.146"),(25,"113","0.111")],
 "0.04":[(3,"80.7","0.140"),(5,"106","0.108"),(10,"161","0.101"),(15,"204","0.071")],
 "0.08":[(3,"180","0.079"),(5,"231","0.078"),(10,"336","0.066"),(15,"416","0.057")],
 "0.16":[(3,"420","0.064"),(5,"552","0.055"),(10,"826","0.035"),(15,"1055","0.028")],
 "0.32":[(1,"563","0.079"),(3,"1060","0.061"),(5,"1460","0.043")],
}


class M5Reference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.rows = read_source()

    def changed(self, old: bytes, new: bytes) -> bytes:
        self.assertIn(old, self.raw)
        return self.raw.replace(old, new, 1)

    def test_pinned_audited_transcription_hash(self):
        self.assertEqual("026f91bb98380254d111bf8e84e24a23818eed6e",git_blob_sha(self.raw))
        with self.assertRaises(ValueError):
            read_source(self.changed(b"0.02,5,41.6,0.219",b"0.02,5,41.6,0.220"))

    def test_independent_literal_match_all_35(self):
        expected = [(d,int(p),q,k) for d, seq in EXPECTED.items() for p,q,k in seq]
        actual = [(r["d_cm"],int(r["pressure_cmH2O"]),r["flow_cm3_s"],r["kex_experimental"])
                  for r in csv.DictReader(io.StringIO(self.raw.decode()))]
        self.assertEqual(35,len(expected))
        self.assertEqual(expected,actual)

    def test_publication_blanks_remain_omitted(self):
        self.assertEqual(13,8*6-len(self.rows))
        self.assertNotIn((.005,1), {(r["d_cm"],r["pressure_cmH2O"]) for r in self.rows})

    def test_hypothesis_status_and_no_go_labels(self):
        result = evaluate(self.rows)
        self.assertTrue(all(result["hypotheses"].values()))
        self.assertEqual(35,result["case_count"])
        self.assertIn("INDETERMINATE",result["g2"])
        self.assertEqual("VOICE_NO_GO",result["g4"])

    def test_seven_negative_coefficients_are_missed_by_positive_only_im(self):
        result = evaluate(self.rows)
        self.assertEqual(7,result["negative_k_count"])
        self.assertEqual(7,result["im_wrong_sign_cases_all_35"])
        self.assertGreater(result["im_MAE_all_35"],.05)

    def test_theory_equation_source_anchors(self):
        self.assertAlmostEqual(.0198,kex_im(.02),places=12)
        self.assertAlmostEqual(.1472,kex_im(.16),places=12)

    def test_derived_pressure_is_not_a_measured_tap(self):
        r=next(r for r in self.rows if r["d_cm"]==.02 and r["pressure_cmH2O"]==5)
        self.assertAlmostEqual(39.79,reconstructed_p16_minus_p11_pa(r),delta=.1)
        self.assertNotIn("measured_pressure_tap",r)

    def test_negative_derived_pressure_recovery(self):
        r=next(r for r in self.rows if r["d_cm"]==.005)
        self.assertLess(reconstructed_p16_minus_p11_pa(r),0)

    def test_flow_and_pressure_units_si(self):
        result=evaluate(self.rows)
        r=next(r for r in result["rows"] if r["diameter_cm"]==.02 and r["pressure_cmH2O"]==5)
        self.assertAlmostEqual(41.6e-6,r["Q_m3_s"])
        self.assertAlmostEqual(490.3325,r["Delta_p_T_Pa"])

    def test_missing_published_row(self):
        with self.assertRaises(ValueError):
            parse_rows("\n".join(self.raw.decode().splitlines()[:-1]))

    def test_duplicate_row(self):
        lines=self.raw.decode().splitlines()
        with self.assertRaises(ValueError):
            parse_rows("\n".join(lines+[lines[1]]))

    def test_nonpublished_pressure_condition(self):
        with self.assertRaises(ValueError):
            parse_rows(self.changed(b"0.02,5,41.6,0.219",b"0.02,1,41.6,0.219").decode())

    def test_bad_flow_or_nonfinite(self):
        for v in (b"nan",b"-41.6",b"0"):
            with self.subTest(v=v),self.assertRaises(ValueError):
                parse_rows(self.changed(b"0.02,5,41.6,0.219",b"0.02,5,"+v+b",0.219").decode())

    def test_nonfinite_coefficient(self):
        with self.assertRaises(ValueError):
            parse_rows(self.changed(b"0.02,5,41.6,0.219",b"0.02,5,41.6,inf").decode())

    def test_unit_header_swap(self):
        with self.assertRaises(ValueError):
            parse_rows(self.raw.decode().replace("flow_cm3_s","flow_m3_s",1))

    def test_unphysical_area_ratio(self):
        for d in (-.02,0,5,float("nan")):
            with self.subTest(d=d),self.assertRaises(ValueError):
                kex_im(d)

    def test_corrupt_sign_refutes_locked_hypothesis(self):
        rows=[dict(r) for r in self.rows]
        rows[0]["k_experimental"] *= -1
        self.assertFalse(evaluate(rows)["hypotheses"]["H_SIGN"])

    def test_never_elevate_algebra_to_pressure_or_voice_claim(self):
        r=evaluate(self.rows)
        self.assertTrue(all("p16_minus_p11_Pa_ALGEBRAIC_NOT_MEASURED_TAP" in x for x in r["rows"]))
        self.assertNotIn("PHYSICS_VALIDATED",json.dumps(r))
        self.assertIn("HOLD",r["g3"])


if __name__ == "__main__":
    unittest.main()
