from __future__ import annotations

import unittest
import geo_meta


class ExplicitCveMetadataTests(unittest.TestCase):
    def test_empty_cve_does_not_inherit_cve_from_related_link(self):
        article = """---
answer: Cloud security authorization has a defined scope.
cve: ''
sources:
  - title: AWS NATO announcement
    url: https://www.aboutamazon.com/news/aws/aws-first-cloud-provider-nato-restricted-workloads
    publisher: Amazon
---
# AWS NATO
[A separate CVE story](https://www.cybernote.click/2026/08/25/example-CVE-2026-77811/)
"""
        metadata = geo_meta.build_geo_meta(article, cve_hint="AWS", slug="aws-nato")
        self.assertNotIn("_cng_cve", metadata)

    def test_legacy_article_without_declared_cve_still_extracts(self):
        md = """# Vulnerability
Affected: CVE-2026-77811
"""
        metadata = geo_meta.build_geo_meta(md)
        self.assertEqual("CVE-2026-77811", metadata.get("_cng_cve"))

    def test_official_aws_nato_announcement_is_a_primary_source(self):
        self.assertTrue(geo_meta.is_primary_source(
            "https://www.aboutamazon.com/news/aws/aws-first-cloud-provider-nato-restricted-workloads"
        ))


if __name__ == "__main__":
    unittest.main()
