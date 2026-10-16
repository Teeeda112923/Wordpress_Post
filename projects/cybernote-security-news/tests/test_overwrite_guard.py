from __future__ import annotations

import unittest

from wp_auto_post import cve_ids_in, existing_post_cve_conflict


def post(slug, title, cve=""):
    return {"slug": slug, "title": {"raw": title}, "meta": {"_cng_cve": cve}}


class OverwriteGuardTests(unittest.TestCase):
    def test_same_title_but_different_cve_is_a_conflict(self):
        existing = post("cisco-esa-cve-2026-76461-rce", "【緊急】Cisco ESA", "CVE-2026-76461")
        self.assertEqual({"CVE-2026-76461"}, existing_post_cve_conflict(existing, {"CVE-2026-76519"}))

    def test_same_cve_is_not_a_conflict(self):
        existing = post("cisco-esa-cve-2026-76461-rce", "x", "CVE-2026-76461")
        self.assertEqual(set(), existing_post_cve_conflict(existing, {"CVE-2026-76461", "CVE-2026-1"}))

    def test_no_cve_on_either_side_is_not_a_conflict(self):
        self.assertEqual(set(), existing_post_cve_conflict(post("what-is-api", "APIとは"), set()))
        self.assertEqual(set(), existing_post_cve_conflict(post("a", "b"), {"CVE-2026-76519"}))

    def test_cve_ids_in_is_case_insensitive(self):
        self.assertEqual({"CVE-2026-76519"}, cve_ids_in("x-cve-2026-76519-y"))


if __name__ == "__main__":
    unittest.main()
