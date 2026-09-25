import io
import unittest
import zipfile

from scanner import scan_directory, scan_zip


class ScannerTests(unittest.TestCase):
    def test_demo_detects_redacted_secret_and_legacy_rules(self):
        findings = scan_directory("demo_repo")["findings"]
        self.assertTrue(any(item["type"] == "hardcoded_secret" and item["detail"] == "Potential secret detected; value redacted" for item in findings))
        self.assertGreaterEqual(sum(item["type"] == "hardcoded_secret" for item in findings), 2)
        self.assertTrue(any(item["type"] == "legacy_boto_v2" for item in findings))
        self.assertTrue(any(item["type"] == "outdated_dependency" for item in findings))

    def test_zip_path_traversal_is_rejected(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("../escape.py", "print('no')")
        with self.assertRaises(ValueError):
            scan_zip(payload.getvalue())


if __name__ == "__main__":
    unittest.main()
