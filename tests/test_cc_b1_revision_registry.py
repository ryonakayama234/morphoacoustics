"""Gate C receipt registry negatives plus actual physical archive/restart tests."""
from __future__ import annotations

from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
import json
import os
import shutil
from pathlib import Path
import runpy
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "cc_b1_revision_registry.py"
PHYSICAL_CLI = ROOT / "tools" / "cc_b1_candidate_cli.py"
REG = runpy.run_path(str(CLI))
VERSION = REG["VERSION"]
REG_ID = REG["IDENTITY_PATTERN"]
canonical = REG["canonical"]
derive = REG["_expected_record"]
put = REG["_install_record"]
resolve = REG["resolve_revision"]
RegistryError = REG["RegistryError"]


def private_dir(tmp_path: Path) -> Path:
    path = tmp_path / "private-registry"
    path.mkdir(mode=0o700)
    path.chmod(0o700)
    return path


def command(script: Path, *args: str) -> tuple[int, dict[str, object]]:
    proc = subprocess.run(
        [sys.executable, str(script), *args], cwd=ROOT,
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert proc.stdout.count("\n") == 1, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    return proc.returncode, json.loads(proc.stdout)


def test_both_derived_physical_identities_are_distinct() -> None:
    small = derive("0.90")
    large = derive("1.10")
    assert small["revision_id"] != large["revision_id"]
    assert REG_ID.fullmatch(small["revision_id"])
    assert REG_ID.fullmatch(large["revision_id"])
    assert small["body_revision"]["edit"]["section_index"] == 8
    assert small["body_revision"]["parent"] == large["body_revision"]["parent"]
    assert small["body_revision_sha256"] == (
        "sha256:" + sha256(canonical(small["body_revision"])).hexdigest()
    )


def test_registry_exclusive_bytes_idempotence_and_restart(tmp_path: Path) -> None:
    directory = private_dir(tmp_path)
    original = derive("0.90")
    assert put(directory, original) == "REGISTERED"
    entry = directory / "revisions" / (original["revision_id"] + ".json")
    first = entry.read_bytes()
    assert first == canonical(original)
    assert put(directory, original) == "ALREADY_REGISTERED"
    assert entry.read_bytes() == first
    # New interpreter (not just reused module scope) must resolve the identical body.
    code, persisted = command(CLI, "--resolve", "--registry-dir", str(directory),
                              "--revision-id", original["revision_id"])
    assert code == 0
    assert persisted["status"] == "RESOLVED"
    assert persisted["body_revision"] == original["body_revision"]
    assert first == entry.read_bytes()


@pytest.mark.parametrize("change", [
    lambda q: q.update(revision_id="cc-b1-" + "0" * 64),
    lambda q: q["body_revision"].update(revision_id="cc-b1-forged"),
    lambda q: q["body_revision"]["parent"].update(revision=999),
    lambda q: q["body_revision"]["edit"].update(section_index=7),
    lambda q: q["body_revision"]["edit"].update(new_area_m2=1e-3),
    lambda q: q["body_revision"].update(backend_id="false-solver"),
    lambda q: q.update(rest_area_ratio="1.10"),
    lambda q: q.update(phantom_source="external-audio"),
])
def test_forged_registry_record_refused_without_trusting_sha(
    tmp_path: Path, change
) -> None:
    directory = private_dir(tmp_path)
    expected = derive("0.90")
    assert put(directory, expected) == "REGISTERED"
    entry = directory / "revisions" / (expected["revision_id"] + ".json")
    forged = json.loads(entry.read_text("utf-8"))
    change(forged)
    forged["body_revision_sha256"] = (
        "sha256:" + sha256(canonical(forged["body_revision"])).hexdigest()
    )
    entry.write_bytes(canonical(forged))
    with pytest.raises(RegistryError, match="REGISTRY_COLLISION_OR_TAMPER"):
        resolve(directory, expected["revision_id"])
    with pytest.raises(RegistryError, match="REGISTRY_COLLISION_OR_TAMPER"):
        put(directory, expected)
    assert entry.read_bytes() == canonical(forged)


@pytest.mark.parametrize("bytes_data", [
    b'{"x":1,"x":1}',
    b'{"x":NaN}',
    b"not-json",
    b"x" * 8193,
])
def test_corrupt_canonical_entry_fail_closed(tmp_path: Path, bytes_data: bytes) -> None:
    directory = private_dir(tmp_path)
    original = derive("0.90")
    put(directory, original)
    entry = directory / "revisions" / (original["revision_id"] + ".json")
    entry.write_bytes(bytes_data)
    with pytest.raises(RegistryError):
        resolve(directory, original["revision_id"])


def test_unknown_missing_id_and_symlink_refuse(tmp_path: Path) -> None:
    directory = private_dir(tmp_path)
    expected = derive("0.90")
    assert REG["execute"](["--resolve", "--registry-dir", str(directory),
                           "--revision-id", "cc-b1-" + "f"*64])["status"] == "REFUSED"
    assert REG["execute"](["--resolve", "--registry-dir", str(directory),
                           "--revision-id", "../file"])["status"] == "REFUSED"
    with pytest.raises(RegistryError):
        resolve(directory, expected["revision_id"])
    put(directory, expected)
    actual = directory / "revisions" / (expected["revision_id"] + ".json")
    link = directory / "link-to-private"
    try:
        link.symlink_to(directory, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Platform lacks symlinks")
    assert REG["execute"](["--resolve", "--registry-dir", str(link),
                           "--revision-id", expected["revision_id"]])["status"] == "REFUSED"
    actual.unlink()
    actual.symlink_to("/etc/hosts")
    with pytest.raises(RegistryError):
        resolve(directory, expected["revision_id"])


def test_refuse_world_writable_store_and_invalid_cli(tmp_path: Path) -> None:
    directory = private_dir(tmp_path)
    directory.chmod(0o777)
    with pytest.raises(RegistryError, match="REGISTRY_DIR_UNSAFE"):
        put(directory, derive("0.90"))
    code, value = command(CLI, "--register", "--registry-dir", str(directory))
    assert code != 0 and value["status"] == "REFUSED"
    code, value = command(CLI, "--register", "--resolve",
                          "--registry-dir", str(directory))
    assert code != 0 and value["status"] == "REFUSED"



def test_staging_fault_never_publishes_partially_written_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = private_dir(tmp_path)
    expected = derive("0.90")
    original_link = os.link

    def interrupted_before_publication(*args, **kwargs):
        raise OSError("FAULT_INJECTION_LINK_FAILED")

    monkeypatch.setattr(os, "link", interrupted_before_publication)
    with pytest.raises(RegistryError, match="REGISTRY_PUBLISH_FAILED"):
        put(directory, expected)
    monkeypatch.setattr(os, "link", original_link)
    entries = directory / "revisions"
    assert list(entries.iterdir()) == []  # no final record or staging leftovers
    with pytest.raises(RegistryError, match="REVISION_NOT_FOUND"):
        resolve(directory, expected["revision_id"])
    assert put(directory, expected) == "REGISTERED"


def test_failed_staging_fsync_no_false_registered_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = private_dir(tmp_path)
    record = derive("1.10")
    original_fsync = os.fsync

    def failed_sync(fd: int) -> None:
        raise OSError("FAULT_INJECTION_SYNC_FAILED")

    monkeypatch.setattr(os, "fsync", failed_sync)
    with pytest.raises(RegistryError, match="REGISTRY_PUBLISH_FAILED"):
        put(directory, record)
    monkeypatch.setattr(os, "fsync", original_fsync)
    assert list((directory / "revisions").iterdir()) == []
    assert put(directory, record) == "REGISTERED"
    assert resolve(directory, record["revision_id"])["status"] == "RESOLVED"


def test_concurrent_same_revision_never_generates_two_identities(tmp_path: Path) -> None:
    directory = private_dir(tmp_path)
    record = derive("0.90")
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(put, directory, record) for _ in range(2)]
        results: list[str] = []
        for future in futures:
            try:
                results.append(future.result(timeout=15))
            except RegistryError as exc:
                # An in-progress hard link may temporarily have nlink=2;
                # refusing during publication is safer than false success.
                assert exc.code == "REGISTRY_ENTRY_UNSAFE"
                results.append("REFUSED_DURING_PUBLICATION")
    assert results.count("REGISTERED") == 1
    assert all(x in ("REGISTERED", "ALREADY_REGISTERED",
                     "REFUSED_DURING_PUBLICATION") for x in results)
    assert resolve(directory, record["revision_id"])["body_revision"] == record["body_revision"]
    assert sorted(p.name for p in (directory / "revisions").iterdir()) == [
        record["revision_id"] + ".json"
    ]


@pytest.mark.skipif(os.environ.get("CC_B1_GATE_C_PHYSICAL") != "1",
                    reason="CI runs two actual physical waveforms and fresh-process registry")
def test_two_true_1d_archives_registry_pair_and_restart(tmp_path: Path) -> None:
    directory = private_dir(tmp_path)
    code, base = command(
        PHYSICAL_CLI, "--protocol-version", "cc-b1-core-limited-performer/v1",
        "--inspect",
    )
    assert code == 0
    ids = []
    for ratio in ("0.90", "1.10"):
        request = tmp_path / ("physical-" + ratio + ".json")
        request.write_text(json.dumps({
            "schema_version": "cc-b1-core-limited-performer/v1",
            "parent": base["parent"],
            "edit": {"cavity_id": base["editable"]["cavity_id"],
                     "section_index": 8, "rest_area_ratio": ratio},
        }), "utf-8")
        archive = tmp_path / ("archive-" + ratio)
        code, performed = command(
            PHYSICAL_CLI, "--protocol-version", "cc-b1-core-limited-performer/v1",
            "--perform", "--request", str(request),
            "--output-dir", str(archive),
        )
        assert code == 0 and performed["status"] == "SUCCEEDED"
        assert performed["acoustic_calls_per_body"] == 102
        code, registered = command(
            CLI, "--register", "--registry-dir", str(directory),
            "--archive-dir", str(archive),
        )
        assert code == 0 and registered["status"] == "REGISTERED"
        ids.append(registered["revision_id"])
        code, again = command(
            CLI, "--register", "--registry-dir", str(directory),
            "--archive-dir", str(archive),
        )
        assert code == 0 and again["status"] == "ALREADY_REGISTERED"
        code, reread = command(
            CLI, "--resolve", "--registry-dir", str(directory),
            "--revision-id", registered["revision_id"],
        )
        assert code == 0 and reread["status"] == "RESOLVED"
        assert reread["body_revision"] == performed["body_revision"]
        assert reread["body_revision_sha256"] == registered["body_revision_sha256"]

        # Remove the completion marker. No unverified physical Take may
        # introduce a new body identity in a different store.
        incomplete = tmp_path / ("incomplete-" + ratio)
        incomplete.mkdir()
        (incomplete / "edited.wav").write_bytes((archive / "edited.wav").read_bytes())
        other = tmp_path / ("empty-" + ratio)
        other.mkdir(mode=0o700)
        code, rejected = command(
            CLI, "--register", "--registry-dir", str(other),
            "--archive-dir", str(incomplete),
        )
        assert code != 0 and rejected["status"] == "REFUSED"
        assert not (other / "revisions").exists()
    assert len(set(ids)) == 2
    archival = os.environ.get("CC_B1_REGISTRY_ARTIFACT_DIR")
    if archival:
        evidence = Path(archival)
        evidence.mkdir(parents=True, exist_ok=True)
        shutil.copytree(directory, evidence / "registry")
        for ratio in ("0.90", "1.10"):
            shutil.copytree(tmp_path / ("archive-" + ratio),
                            evidence / ("physical-" + ratio))
        (evidence / "evidence.json").write_text(json.dumps({
            "registry_schema_version": VERSION,
            "revision_ids": ids,
            "physics": "genuine two freshly executed source-pinned Core 1D pairs",
            "scope": "research only; never a Studio Take, origin signature or ABX",
        }, sort_keys=True, indent=2), "utf-8")
