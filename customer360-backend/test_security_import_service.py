import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.security_import_service import SecurityImportService


ROOT = Path(__file__).resolve().parents[1]
SECURITY_DIR = ROOT / "security_scripts"


class SecurityImportServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = SecurityImportService(report_dir=Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_invalid_pdf_reaches_all_gates_and_is_rejected(self):
        pdf_file = SECURITY_DIR / "test_data" / "dirty" / "dirty_oversized_25pages.pdf"

        result = self.service.import_file(str(pdf_file))

        self.assertEqual(set(result["gates"]), {"gate1", "gate2", "gate3"})
        self.assertEqual(result["gates"]["gate1"]["overall_result"], "FAIL")
        self.assertEqual(result["gates"]["gate2"]["overall_result"], "PASS")
        self.assertEqual(result["gates"]["gate3"]["overall_result"], "PASS")
        self.assertEqual(result["decision"], "REJECT")
        self.assertEqual(result["import_status"], "REJECTED")
        self.assertIn("25", result["rejection_reason"])
        self.assertTrue(Path(result["validation_report"]).exists())

    def test_csv_pii_is_masked_and_status_is_accepted(self):
        csv_file = SECURITY_DIR / "test_data" / "csv_samples" / "contacts_with_pii.csv"

        result = self.service.import_file(str(csv_file))

        self.assertEqual(result["gates"]["gate1"]["overall_result"], "SKIP")
        self.assertEqual(result["gates"]["gate2"]["overall_result"], "PASS")
        self.assertEqual(result["gates"]["gate3"]["overall_result"], "PII_FOUND")
        self.assertEqual(result["decision"], "ACCEPT")
        self.assertEqual(result["import_status"], "ACCEPTED_WITH_PII_MASKED")
        self.assertTrue(Path(result["masked_output"]).exists())

    def test_gate_error_fails_closed_and_saves_reason(self):
        csv_file = SECURITY_DIR / "test_data" / "csv_samples" / "contacts_with_pii.csv"

        with patch(
            "app.services.security_import_service.scan_and_mask_csv",
            side_effect=RuntimeError("gate unavailable"),
        ):
            result = self.service.import_file(str(csv_file))

        self.assertEqual(result["gates"]["gate3"]["overall_result"], "ERROR")
        self.assertEqual(result["decision"], "REJECT")
        self.assertEqual(result["import_status"], "REJECTED")
        self.assertIn("Gate 3 unavailable", result["rejection_reason"])
        self.assertTrue(Path(result["validation_report"]).exists())


if __name__ == "__main__":
    unittest.main()
