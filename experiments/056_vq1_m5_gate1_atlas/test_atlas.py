"""Independent adversarial test oracles. All numeric fixtures are SYNTHETIC."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import atlas

BYTES = b"FAKE_NON_PUBLISHED_FIGURE_FOR_SYNTHETIC_TESTS"
AX = {"unit": "z_cm_life", "tick1_pixel": 0, "tick1_value": 0,
      "tick2_pixel": 600, "tick2_value": .6, "tick_radius_pixel": .2}
AY = {"unit": "drop_cmH2O_life", "tick1_pixel": 0, "tick1_value": 0,
      "tick2_pixel": 100, "tick2_value": 10, "tick_radius_pixel": .2}


def mark(t, y, side="FW", *, x=None, status="VISIBLE"):
    if x is None:
        x = {6:211, 11:413, 13:511}.get(t, 211+40*(t-6))
    return {"tap":t,"side":side,"observation":status,
            "pixel_x":float(x) if status=="VISIBLE" else None,
            "pixel_y":float(y) if status=="VISIBLE" else None,
            "radius_px":1.0 if status=="VISIBLE" else None,
            "z_life_m":float(x)*.00001,"z_unc_m":.000025,
            "z_source":"SYNTHETIC_TEST_GEOMETRY_NOT_M5_OBSERVATION"}


def source(markers=None):
    if markers is None:
        markers = [mark(6,30),mark(11,70),mark(13,50)]
    case = {"id":atlas.CASE_ID,"doi":atlas.DOI,"figure":"2B",
            "d_life_m":.0002,"dp_life_cmH2O":10,"scale":7.5,
            "reference_tap":0,"drop_sign":"p0_minus_pi"}
    sessions = []
    for ix in range(2):
        m = copy.deepcopy(markers)
        if ix:
            for p in m:
                if p["observation"]=="VISIBLE":
                    p["pixel_y"] += .3
                    p["pixel_x"] += .3
        sessions.append({"read_id":str(ix), "analyst_id":"SYNTHETIC_READER_"+str(ix),
                         "independent":True,"x_axis":copy.deepcopy(AX),
                         "y_axis":copy.deepcopy(AY),"markers":m})
    return {"schema":"vq1-m5-gate1/v1","case":case,
            "figure_asset":{"uri":"https://example.invalid/SYNTHETIC",
                            "sha256":hashlib.sha256(BYTES).hexdigest(),
                            "source_kind":"original_measured_figure2b",
                            "acquisition_note":"SYNTHETIC_BYTE_FIXTURE_NOT_REAL_PAPER"},
            "reads":sessions}


class MetrologyTests(unittest.TestCase):
    def test_no_source_is_honest_hold(self):
        payload = {"schema":"vq1-m5-gate1/v1", "case":source()["case"],
                   "figure_asset":None, "reads":[]}
        r = atlas.audit(payload)
        self.assertEqual(r["source_metrology"],atlas.S0)
        self.assertEqual(r["reason"],"SOURCE_IMAGE_NOT_ACQUIRED")
        self.assertEqual(r["source_qualified_samples"],0)
        self.assertEqual(r["voice"],"NO_GO")

    def test_synthetic_partial_and_features_are_not_qualified(self):
        r=atlas.audit(source(),BYTES)
        self.assertEqual(r["source_metrology"],atlas.PARTIAL)
        self.assertEqual(r["accepted_fw_taps"],[6,11,13])
        self.assertEqual(r["source_qualified_samples"],0)
        self.assertEqual(r["feature_checks"]["H_AXIAL"],"INDETERMINATE_INSTRUMENT_UNQUALIFIED")
        self.assertEqual(r["digitization_only_checks"]["H_AXIAL"],"SUPPORT_CANDIDATE")
        self.assertEqual(r["feature_checks"]["H_RECOVERY"],"INDETERMINATE_INSTRUMENT_UNQUALIFIED")
        self.assertEqual(r["digitization_only_checks"]["H_RECOVERY"],"SUPPORT_CANDIDATE")
        self.assertEqual(r["external_source_audit"],"REQUIRED_NOT_PERFORMED")

    def test_synthetic_eight_tap_candidate_is_still_not_verified(self):
        markers = [mark(i,20+i*5) for i in range(6,14)]
        r=atlas.audit(source(markers),BYTES)
        self.assertEqual(r["source_metrology"],atlas.COMPLETE)
        self.assertEqual(r["source_qualified_samples"],0)

    def test_conversions_preserve_negative_plot_slopes(self):
        lo,hi=atlas.axis_interval(AY,30,1,"drop_cmH2O_life")
        self.assertLessEqual(lo,3)
        self.assertGreaterEqual(hi,3)
        invert=dict(AY,tick1_pixel=100,tick2_pixel=0)
        lo,hi=atlas.axis_interval(invert,70,1,"drop_cmH2O_life")
        self.assertLess(lo,hi)

    def test_corrupt_hash_or_no_bytes_refused(self):
        p=source()
        p["figure_asset"]["sha256"]="0"*64
        with self.assertRaisesRegex(atlas.SourceHold,"SHA256"):
            atlas.audit(p,BYTES)
        with self.assertRaisesRegex(atlas.SourceHold,"bytes unavailable"):
            atlas.audit(source(),None)

    def test_figure4_computed_curve_rejected(self):
        p=source()
        p["figure_asset"]["source_kind"]="model_reconstruction"
        with self.assertRaisesRegex(atlas.SourceHold,"computed/reconstructed"):
            atlas.audit(p,BYTES)

    def test_wrong_case_panel_sign_and_scale_rejected(self):
        for k,v in [("id","M6"),("doi","10.0000/invalid"),("figure","2C"),
                    ("d_life_m",.0016),("dp_life_cmH2O",15),
                    ("scale",1),("drop_sign","pi_minus_p0"),("reference_tap",16)]:
            p=source()
            p["case"][k]=v
            with self.subTest(k=k),self.assertRaises(atlas.SourceHold):
                atlas.audit(p,BYTES)

    def test_anonymous_or_duplicate_reading_refused(self):
        for mutation in ["duplicate_read","duplicate_analyst","flag","read_missing"]:
            p=source()
            if mutation=="duplicate_read":p["reads"][1]["read_id"]="0"
            if mutation=="duplicate_analyst":p["reads"][1]["analyst_id"]=p["reads"][0]["analyst_id"]
            if mutation=="flag":p["reads"][1]["independent"]=False
            if mutation=="read_missing":p["reads"].pop()
            with self.subTest(mutation=mutation),self.assertRaises(atlas.SourceHold):
                atlas.audit(p,BYTES)

    def test_invalid_ticks_and_axis_units(self):
        for kind in ["degenerate","uncertainty_overlap","unit","sign_reversal","bool"]:
            p=source()
            a=p["reads"][0]["y_axis"]
            if kind=="degenerate":a["tick2_pixel"]=0
            if kind=="uncertainty_overlap":a["tick_radius_pixel"]=100
            if kind=="unit":a["unit"]="rig_pascal"
            if kind=="sign_reversal":a["unit"]="pi_minus_p0"
            if kind=="bool":a["tick1_pixel"]=True
            with self.subTest(kind=kind),self.assertRaises(atlas.SourceHold):
                atlas.audit(p,BYTES)

    def test_nonfinite_and_duplicate_marker_refused(self):
        for kind in ["nan","bool","duplicate","tap15","wrong_side","wrong_z"]:
            p=source()
            m=p["reads"][0]["markers"][0]
            if kind=="nan":m["pixel_x"]=float("nan")
            if kind=="bool":m["pixel_x"]=True
            if kind=="duplicate":p["reads"][0]["markers"].append(copy.deepcopy(m))
            if kind=="tap15":m["tap"]=15
            if kind=="wrong_side":m["side"]="LEFT"
            if kind=="wrong_z":m["z_life_m"]=.3
            with self.subTest(kind=kind),self.assertRaises(atlas.SourceHold):
                atlas.audit(p,BYTES)

    def test_ambiguous_NFW_not_copied(self):
        p=source()
        for s in p["reads"]:
            s["markers"].append(mark(6,30,"NFW",status="OCCLUDED"))
        r=atlas.audit(p,BYTES)
        self.assertEqual(r["accepted_fw_taps"],[6,11,13])
        self.assertEqual(len(r["candidate_markers"]),3)
        self.assertTrue(any("NFW" in v["point"] for v in r["unresolved"]))

    def test_nonvisible_numeric_marker_refused(self):
        p=source()
        for s in p["reads"]:
            s["markers"][0]["observation"]="OCCLUDED"
        with self.assertRaisesRegex(atlas.SourceHold,"numeric pixels"):
            atlas.audit(p,BYTES)

    def test_disagreeing_readers_become_unresolved(self):
        p=source()
        p["reads"][1]["markers"][0]["pixel_y"]=95.
        r=atlas.audit(p,BYTES)
        self.assertEqual(r["accepted_fw_taps"],[11,13])
        self.assertTrue(any(v["reason"]=="INCOMPATIBLE_INDEPENDENT_READS" for v in r["unresolved"]))
        self.assertEqual(r["feature_checks"]["H_AXIAL"],"INDETERMINATE_MISSING_INDEPENDENT_POINTS")

    def test_absent_source_with_claimed_numeric_read_refused(self):
        p=source()
        p["figure_asset"]=None
        with self.assertRaisesRegex(atlas.SourceHold,"cannot digitize"):
            atlas.audit(p)

    def test_pressure_feature_interval_overlap_not_forced(self):
        p=source()
        for s in p["reads"]:
            s["markers"][1]["pixel_y"]=s["markers"][0]["pixel_y"]
        r=atlas.audit(p,BYTES)
        self.assertEqual(r["feature_checks"]["H_AXIAL"],"INDETERMINATE_INSTRUMENT_UNQUALIFIED")
        self.assertEqual(r["digitization_only_checks"]["H_AXIAL"],"INDETERMINATE_INTERVAL_OVERLAP")


    def test_ambiguous_attachment_category_preserved_without_number(self):
        p=source()
        for s in p["reads"]:
            s["markers"].append(mark(7,45,"AMBIGUOUS",status="AMBIGUOUS"))
        receipt=atlas.audit(p,BYTES)
        self.assertTrue(any(v["point"]=="tap7:AMBIGUOUS" for v in receipt["unresolved"]))
        self.assertTrue(all(v["attachment_class"]!="AMBIGUOUS" for v in receipt["candidate_markers"]))
        p["reads"][0]["markers"][-1]=mark(7,45,"AMBIGUOUS",status="VISIBLE")
        with self.assertRaisesRegex(atlas.SourceHold,"unknown attachment class"):
            atlas.audit(p,BYTES)

    def test_compatible_readers_do_not_shrink_uncertainty_to_intersection(self):
        p=source()
        first=atlas.axis_interval(AY,30,1,"drop_cmH2O_life")
        second=atlas.axis_interval(AY,30.3,1,"drop_cmH2O_life")
        receipt=atlas.audit(p,BYTES)
        joined=next(v["drop_pa_interval"] for v in receipt["candidate_markers"]
                    if v["tap"]==6 and v["attachment_class"]=="FW")
        self.assertAlmostEqual(joined[0],min(first[0],second[0])*atlas.CMH2O_TO_PA)
        self.assertAlmostEqual(joined[1],max(first[1],second[1])*atlas.CMH2O_TO_PA)

    def test_runner_pins_explicit_checked_source_head(self):
        import run
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"receipt.json"
            with patch.dict(os.environ,{"VQ1_M5_TEST_OUTCOME":"success",
                                        "SOURCE_HEAD":"source-head-not-merge-head",
                                        "GITHUB_SHA":"synthetic-merge-head"}),patch.object(sys,"argv",["run.py","--out",str(path)]):
                run.main()
            receipt=json.loads(path.read_text())
            self.assertEqual(receipt["code_head"],"source-head-not-merge-head")


    def test_physical_tap_uncertainty_not_narrowed_by_plot_resolution(self):
        r=atlas.audit(source(),BYTES)
        v=next(p for p in r["candidate_markers"] if p["tap"]==6 and
               p["attachment_class"]=="FW")
        self.assertAlmostEqual(v["z_m_interval"][0],.00211-.000025)
        self.assertAlmostEqual(v["z_m_interval"][1],.00211+.000025)

    def test_zero_resolution_plot_cannot_certify_instrument_precision(self):
        p=source()
        for s in p["reads"]:
            for marker in s["markers"]:
                marker["radius_px"]=1e-9
            s["x_axis"]["tick_radius_pixel"]=0
            s["y_axis"]["tick_radius_pixel"]=0
        r=atlas.audit(p,BYTES)
        self.assertEqual(r["instrument_uncertainty"],"UNQUALIFIED_NO_ABSOLUTE_BOUND")
        self.assertEqual(r["feature_checks"]["H_AXIAL"],"INDETERMINATE_INSTRUMENT_UNQUALIFIED")
        self.assertEqual(r["source_qualified_samples"],0)


class RunnerTests(unittest.TestCase):
    def test_normal_source_hold_json(self):
        import run
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"receipt.json"
            with patch.dict(os.environ,{"VQ1_M5_TEST_OUTCOME":"success"}),patch.object(sys,"argv",["run.py","--out",str(path)]):
                run.main()
            r=json.loads(path.read_text())
            self.assertEqual(r["source_metrology"],atlas.S0)
            self.assertEqual(r["source_qualified_samples"],0)

    def test_red_test_preserves_non_success_receipt(self):
        import run
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"receipt.json"
            with patch.dict(os.environ,{"VQ1_M5_TEST_OUTCOME":"failure"}),patch.object(sys,"argv",["run.py","--out",str(path)]):
                with self.assertRaises(SystemExit):
                    run.main()
            r=json.loads(path.read_text())
            self.assertEqual(r["source_metrology"],"NUMERICALLY_UNRESOLVED")
            self.assertEqual(r["voice"],"NO_GO")

    def test_corrupt_json_preserves_failure_receipt(self):
        import run
        with tempfile.TemporaryDirectory() as d:
            inp,out=Path(d)/"in.json",Path(d)/"out.json"
            inp.write_text("not-json")
            with patch.dict(os.environ,{"VQ1_M5_TEST_OUTCOME":"success"}),patch.object(sys,"argv",["run.py","--input",str(inp),"--out",str(out)]):
                with self.assertRaises(SystemExit):
                    run.main()
            r=json.loads(out.read_text())
            self.assertIn("error",r)
            self.assertEqual(r["source_metrology"],"NUMERICALLY_UNRESOLVED")


if __name__=="__main__":
    unittest.main()
