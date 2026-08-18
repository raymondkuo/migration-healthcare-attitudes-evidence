# -*- coding: utf-8 -*-
"""Tests that drive the shipped auditor against the real site HTML and named VERIFIED xlsx."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SITE = SCRIPT_DIR.parent
# The reference workbook is the one this archive publishes. Resolved from the repository
# so that no local path - and no author's name - is baked into a published file.
TRUTH = SITE / "data" / "FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx"
sys.path.insert(0, str(SCRIPT_DIR))

import audit_site_against_verified as audit  # noqa: E402


class TestShippedAuditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verified = audit.load_verified(TRUTH)
        cls.twn_html = audit.read_html(SITE / "countries" / "TWN.html")
        cls.aus_html = audit.read_html(SITE / "countries" / "AUS.html")

    def test_truth_has_40_iso3_and_required_sheets(self):
        self.assertEqual(len(self.verified["iso3_list"]), 40)
        for name in (
            "README", "Panel_final", "Data_quality", "Corrections_applied",
            "Known_issues", "Verification_log", "Source_register",
            "Irregular_estimates_all", "Codebook",
        ):
            self.assertIn(name, self.verified["sheets"])

    def test_parse_and_compare_TWN_and_AUS_panel_against_xlsx(self):
        for iso, html in (("TWN", self.twn_html), ("AUS", self.aus_html)):
            parsed = audit.parse_panel_table(html)
            self.assertGreater(len(parsed["cells"]), 10, iso)
            self.assertIn("population", parsed["vars"])
            for cell in parsed["cells"]:
                xv, xg = audit.panel_lookup(
                    self.verified["Panel_final"], iso, cell["year"], cell["variable"]
                )
                got = audit.match_label(cell["value"], xv)
                independent_ok = audit.numbers_equal(cell["value"], xv)
                self.assertEqual(
                    got == "MATCH",
                    independent_ok,
                    msg="%s %s %s site=%r xlsx=%r got=%s"
                    % (iso, cell["variable"], cell["year"], cell["value"], xv, got),
                )
                if cell["grade"] is not None and xg is not None:
                    self.assertEqual(
                        audit.match_label(cell["grade"], xg) == "MATCH",
                        str(cell["grade"]) == str(xg),
                    )

    def test_evidence_pages_match_country_page_and_xlsx(self):
        for iso, html in (("TWN", self.twn_html), ("AUS", self.aus_html)):
            parsed = audit.parse_panel_table(html)
            for cell in parsed["cells"]:
                if cell["value"] is None:
                    continue
                evp = SITE / "evidence-pages" / ("%s__%s.html" % (iso, cell["variable"]))
                self.assertTrue(evp.is_file(), msg=str(evp))
                ev = audit.parse_evidence_values(audit.read_html(evp))
                evc = next((e for e in ev if e["year"] == cell["year"]), None)
                self.assertIsNotNone(evc, msg="%s %s %s" % (iso, cell["variable"], cell["year"]))
                self.assertTrue(
                    audit.numbers_equal(evc["value"], cell["value"]),
                    msg="evidence≠country page %s %s %s" % (iso, cell["variable"], cell["year"]),
                )
                xv, _ = audit.panel_lookup(
                    self.verified["Panel_final"], iso, cell["year"], cell["variable"]
                )
                self.assertEqual(
                    audit.match_label(evc["value"], xv) == "MATCH",
                    audit.numbers_equal(evc["value"], xv),
                )

    def test_every_nonnull_panel_cell_is_on_the_country_page_or_flagged(self):
        rows = audit.build_audit_rows(SITE, self.verified)
        for iso in ("TWN", "AUS"):
            panel = self.verified["Panel_final"]
            g = panel[panel["iso3"] == iso]
            compared = {
                (r["variable"], str(r["year"]))
                for r in rows
                if r["iso3"] == iso
                and r["verified_sheet"] == "Panel_final"
                and r["item"] == "panel cell"
                and r["page"].endswith("%s.html" % iso)
            }
            for _, rec in g.iterrows():
                year = int(rec["year"])
                for var in audit.PANEL_VARS:
                    if var not in g.columns or audit.is_blank(rec.get(var)):
                        continue
                    self.assertIn(
                        (var, str(year)),
                        compared,
                        msg="%s %s %s displayed-or-should-be cell missing from audit rows" % (iso, var, year),
                    )

    def test_stat_links_from_TWN_include_live_url_and_existing_archive(self):
        page = SITE / "countries" / "TWN.html"
        pairs = audit.extract_stat_links_from_html(page, self.twn_html, SITE)
        urls = {p["url"] for p in pairs if p.get("url")}
        self.assertTrue(any("ws.moi.gov.tw" in u for u in urls), urls)
        archives = [Path(p["archive_path"]) for p in pairs if p.get("archive_path")]
        self.assertTrue(any(a.is_file() for a in archives), "no existing TWN archive paired")

    def test_numbers_equal_readme_percent_string(self):
        self.assertTrue(audit.numbers_equal("2415 (98.4%)", "2415 (98.4%)"))
        self.assertTrue(audit.numbers_equal(98.4, "2415 (98.4%)"))
        self.assertFalse(audit.numbers_equal(1699, 1692))

    def test_hash_compare_local_archive_to_itself(self):
        sample = SITE / "evidence" / "countries" / "TWN" / "value_check.csv"
        self.assertTrue(sample.is_file())
        digest = audit.sha256_file(sample)
        fake_fetch = {
            "downloadable": True,
            "sha256": digest,
            "bytes": sample.stat().st_size,
            "content_type": "text/csv",
        }
        cc, exists, ash, _note = audit.compare_live_to_archive(fake_fetch, sample)
        self.assertEqual(cc, "exact_match")
        self.assertEqual(exists, "yes")
        self.assertEqual(ash, digest)
        fake_fetch["sha256"] = "0" * 64
        cc2, _, _, _ = audit.compare_live_to_archive(fake_fetch, sample)
        self.assertEqual(cc2, "mismatch")

    def test_write_checklist_has_40_iso_sheets_and_required_groups(self):
        """Drive write_checklist on real TWN/AUS rows, then audit the shipped workbook."""
        rows = []
        panel = self.verified["Panel_final"]
        for iso, html in (("TWN", self.twn_html), ("AUS", self.aus_html)):
            parsed = audit.parse_panel_table(html)
            for cell in parsed["cells"]:
                xv, _ = audit.panel_lookup(panel, iso, cell["year"], cell["variable"])
                rows.append(audit.new_row(
                    iso3=iso, verified_sheet="Panel_final",
                    page="countries/%s.html" % iso,
                    variable=cell["variable"], year=cell["year"],
                    item="panel cell",
                    site_value=cell["value"], xlsx_value=xv,
                    number_match=audit.match_label(cell["value"], xv),
                ))
        required = (
            "README", "Panel_final", "Data_quality", "Corrections_applied",
            "Known_issues", "Verification_log", "Source_register",
            "Irregular_estimates_all",
        )
        for iso in self.verified["iso3_list"]:
            for sh in required:
                rows.append(audit.new_row(
                    iso3=iso, verified_sheet=sh,
                    item="sheet coverage", number_match="N/A",
                ))
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "checklist.xlsx"
            audit.write_checklist(rows, out, self.verified["iso3_list"], str(TRUTH))
            self.assertTrue(out.is_file())
            self.assertNotEqual(out.resolve(), TRUTH.resolve())
            report = audit.checklist_structure_report(out, self.verified["iso3_list"])
            self.assertIn("country_sheets=40 expected=40", report)

        shipped = SITE / "AUDIT_checklist_site_vs_VERIFIED.xlsx"
        self.assertTrue(shipped.is_file(), "shipped checklist missing")
        self.assertNotEqual(shipped.resolve(), TRUTH.resolve())
        shipped_report = audit.checklist_structure_report(shipped, self.verified["iso3_list"])
        self.assertIn("country_sheets=40 expected=40", shipped_report)
        for iso in self.verified["iso3_list"]:
            line = next(x for x in shipped_report.splitlines() if x.startswith(iso + " "))
            self.assertIn("missing_groups=[]", line, msg=line)
            n = int(line.split("rows=")[1].split()[0])
            self.assertGreater(n, 0, msg=line)

    def test_captured_live_bodies_hash_against_local_archives(self):
        """Compare saved live bodies (when present) via the shipped compare function."""
        pairs = [
            (
                Path(r"C:\Users\Raymond\AppData\Local\Temp\grok-goal-ff878ac0dd8e\implementer\downloads\wb_SP_POP_TOTL.live.json"),
                SITE / "evidence" / "api" / "wb_SP_POP_TOTL.json",
            ),
            (
                Path(r"C:\Users\Raymond\AppData\Local\Temp\grok-goal-ff878ac0dd8e\implementer\downloads\wb_SM_POP_TOTL.live.json"),
                SITE / "evidence" / "api" / "wb_SM_POP_TOTL.json",
            ),
            (
                Path(r"C:\Users\Raymond\AppData\Local\Temp\grok-goal-ff878ac0dd8e\implementer\downloads\mol_c12020.live.pdf"),
                SITE / "evidence" / "countries" / "TWN" / "foreign_workers__d0a0269c40__statdb.mol.gov.tw.pdf",
            ),
            (
                Path(r"C:\Users\Raymond\AppData\Local\Temp\grok-goal-ff878ac0dd8e\implementer\downloads\moj_001344148.live.pdf"),
                SITE / "evidence" / "countries" / "JPN" / "irregular_proxy_overstayers__3c80fc7397__www.moj.go.jp.pdf",
            ),
        ]
        compared = 0
        for live, arch in pairs:
            if not live.is_file() or not arch.is_file():
                continue
            rec = {
                "downloadable": True,
                "sha256": audit.sha256_file(live),
                "bytes": live.stat().st_size,
                "content_type": "application/octet-stream",
            }
            cc, exists, ash, _ = audit.compare_live_to_archive(rec, arch)
            self.assertEqual(exists, "yes", msg=str(arch))
            self.assertEqual(cc, "exact_match", msg="%s vs %s" % (live, arch))
            self.assertEqual(ash, rec["sha256"])
            compared += 1
        self.assertGreaterEqual(compared, 1, "no captured live bodies found to hash-compare")


if __name__ == "__main__":
    unittest.main(verbosity=2)
