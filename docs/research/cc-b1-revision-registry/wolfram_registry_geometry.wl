(* Independent ideal static-geometry and canonical-byte consistency checks.
   This does NOT check Core's dynamic 1D solver or filesystem race resistance. *)
ClearAll[areas, ratios, site, len, actual, mask, delta, loc];
areas = Array[aa, 16]; ratios = {9/10, 11/10};
site = 9; (* Wolfram is 1-based; Core site_index = 8 zero-based *)
len = 1/100; (* m per section, 16 x 10 mm = 0.16 m *)
geometry = Table[
  delta = Simplify[ReplacePart[areas, site -> ratio areas[[site]]] - areas];
  loc = Flatten @ Position[Map[!TrueQ[PossibleZeroQ[#]] &, delta], True];
  <|"ratio" -> ratio, "changed_zero_based" -> (loc - 1),
    "remaining_15_unchanged" -> (Length[loc] == 1 && First[loc] == site),
    "volume_difference_m3" -> Simplify[len Total[delta]],
    "edited_site_positive_if_base_positive" ->
      FullSimplify[ratio areas[[site]] > 0, Assumptions -> areas[[site]] > 0],
    "total_rest_tube_length_m" -> 16 len|>,
  {ratio, ratios}];
(* Independently exercise identical canonical UTF-8 byte sequence used by
   Python json.dumps(... sort_keys=True, separators=(',', ':'), allow_nan=False)
   on a deliberately simple public fixture, NOT a privileged Core receipt. *)
json = "{\"body_revision\":{\"edit\":{\"section_index\":8},\"parent\":{\"revision\":1}},\"rest_area_ratio\":\"0.90\",\"schema_version\":\"cc-b1-body-revision-registry/v0\"}";
hashFixture = <|"byte_count" -> Length[ToCharacterCode[json, "UTF8"]],
                "sha256_hex" -> Hash[ByteArray[ToCharacterCode[json, "UTF8"]], "SHA256", "HexString"]|>;
<|"geometry" -> geometry, "hash_fixture" -> hashFixture|>
