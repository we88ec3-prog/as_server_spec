#!/usr/bin/env python3
"""A032 roy3 full-corpus regression; original assets optional in clean Git checkout."""
import os, unittest
from pathlib import Path
from a032_roy3_full_c35_atlas import (build_atlas, PendingMap, accept_c35_for_pending,
    EXPECTED_PAIR_ATLAS_SHA256)
from a032_c35_probe import FormatError

class FullC35AtlasTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.exe=Path(os.getenv("ASGARD_EXE","/mnt/data/Asgard.exe"))
  cls.map_dir=Path(os.getenv("ASGARD_MAP_DIR","/mnt/data"))
  cls.available=cls.exe.is_file() and all((cls.map_dir/f"Map{i}.dat").is_file() for i in (0,1,2))
  if cls.available:cls.atlas=build_atlas(cls.exe,cls.map_dir)
 def require_source(self):
  if not self.available:self.skipTest("Original EXE/MAP archives absent (not checked into Git)")
 def test_01_all_494(self):
  self.require_source()
  self.assertEqual(self.atlas["summary"]["map_count"],494)
  self.assertEqual(self.atlas["summary"]["map_count_by_archive"],{"Map0.dat":288,"Map1.dat":184,"Map2.dat":22})
 def test_02_pair_digest(self):
  self.require_source()
  self.assertEqual(self.atlas["summary"]["map_ref_to_c35_digest_sha256"],EXPECTED_PAIR_ATLAS_SHA256)
 def test_03_unique_values_and_clusters(self):
  self.require_source()
  s=self.atlas["summary"]
  self.assertEqual((s["distinct_payload_sha256"],s["distinct_c35_pair"],s["duplicate_c35_clusters"]),(330,330,33))
  self.assertEqual(s["excess_repeated_refs"],164)
  self.assertEqual(s["distinct_content_sharing_same_c35"],0)
 def test_04_fixed_real_samples(self):
  self.require_source()
  rows={r["map_ref"]:r for r in self.atlas["entries"]}
  for ref,pair in ((0,"000063A9"),(6,"00040F90"),(10000,"00040F90"),
                   (18001,"0012F892"),(20001,"0016E9B9")):
   self.assertEqual(rows[ref]["c35_body_hex"],pair)
 def test_05_duplicate_different_map_identity(self):
  self.require_source()
  rows={r["map_ref"]:r for r in self.atlas["entries"]}
  self.assertEqual(rows[6]["payload_sha256"],rows[10000]["payload_sha256"])
  pending=PendingMap(6,rows[6]["payload_sha256"],rows[6]["c35_body_hex"],4)
  body=bytes.fromhex(rows[10000]["c35_body_hex"])
  self.assertFalse(accept_c35_for_pending(pending,active_map_ref=10000,
        active_generation=4,active_payload_sha256=rows[10000]["payload_sha256"],received_body=body))
 def test_06_match_pending(self):
  p=PendingMap(6,"sample_sha","00040F90",4)
  self.assertTrue(accept_c35_for_pending(p,active_map_ref=6,active_generation=4,
        active_payload_sha256="sample_sha",received_body=bytes.fromhex("00040f90")))
 def test_07_stale_generation_rejected(self):
  p=PendingMap(6,"s","00040F90",4)
  self.assertFalse(accept_c35_for_pending(p,active_map_ref=6,active_generation=3,
        active_payload_sha256="s",received_body=bytes.fromhex("00040f90")))
 def test_08_wrong_content_rejected(self):
  p=PendingMap(6,"s","00040F90",4)
  self.assertFalse(accept_c35_for_pending(p,active_map_ref=6,active_generation=4,
        active_payload_sha256="different",received_body=bytes.fromhex("00040f90")))
 def test_09_wrong_pair_rejected(self):
  p=PendingMap(6,"s","00040F90",4)
  self.assertFalse(accept_c35_for_pending(p,active_map_ref=6,active_generation=4,
        active_payload_sha256="s",received_body=bytes.fromhex("00040f91")))
 def test_10_bad_body_rejected(self):
  p=PendingMap(6,"s","00040F90",4)
  for bad in (None,b"",b"\0",b"\0"*5,"00040F90"):
   self.assertFalse(accept_c35_for_pending(p,active_map_ref=6,active_generation=4,
      active_payload_sha256="s",received_body=bad))
 def test_11_original_versions_pinned(self):
  self.require_source()
  self.assertTrue(self.atlas["summary"]["original_exe_and_archives_sha_pinned"])
 def test_12_native_gui_not_falsely_passed(self):
  self.require_source()
  self.assertEqual(self.atlas["summary"]["native_GUI_spawn_walk"],"not-run")
if __name__=="__main__":unittest.main(verbosity=2)
