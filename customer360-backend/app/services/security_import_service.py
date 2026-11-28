import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
SECURITY_DIR = PROJECT_DIR / "security_scripts"
SCANNERS_DIR = SECURITY_DIR / "scanners"

if str(SCANNERS_DIR) not in sys.path:
    sys.path.insert(0, str(SCANNERS_DIR))

from gate1_pdf_validator import load_config as load_gate1_config, scan_pdf as gate1_scan
from gate2_injection_scanner import compile_patterns, load_patterns, scan_file as gate2_scan
from gate3_pii_masker import (
    compile_rules,
    load_pii_rules,
    scan_and_mask_csv,
    scan_pdf as gate3_scan_pdf,
)


class SecurityImportService:
    def __init__(self, report_dir: Path | None = None):
        self.config_dir = SECURITY_DIR / "configs"
        self.report_dir = report_dir or (SECURITY_DIR / "logs")
        self.output_dir = SECURITY_DIR / "test_data" / "masked_output"

        self.gate1_config = load_gate1_config(
            str(self.config_dir / "gate1_config.json")
        )
        self.gate2_patterns = compile_patterns(
            load_patterns(str(self.config_dir / "injection_patterns.json"))
        )
        pii_config = load_pii_rules(str(self.config_dir / "pii_rules.json"))
        self.gate3_mask_rules, self.gate3_whitelist_rules = compile_rules(pii_config)

    def _run_gate(self, name: str, gate: Callable[[], dict]) -> dict:
        try:
            return gate()
        except Exception as exc:
            return {
                "overall_result": "ERROR",
                "error": f"{name} unavailable: {type(exc).__name__}: {exc}",
            }

    def import_file(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            result = self._base_result(str(path))
            result["decision"] = "REJECT"
            result["import_status"] = "REJECTED"
            result["rejection_reason"] = "File does not exist or is not a readable file"
            result["gates"]["gate1"] = {"overall_result": "ERROR", "error": "File unavailable"}
            result["gates"]["gate2"] = {"overall_result": "NOT_RUN"}
            result["gates"]["gate3"] = {"overall_result": "NOT_RUN"}
            return self._save_result(result)

        ext = path.suffix.lower()
        result = self._base_result(str(path))

        if ext == ".pdf":
            gate1 = self._run_gate("Gate 1", lambda: gate1_scan(str(path), self.gate1_config))
        else:
            gate1 = {"overall_result": "SKIP", "detail": "Gate 1 applies only to PDF files"}
        result["gates"]["gate1"] = gate1

        gate2 = self._run_gate(
            "Gate 2",
            lambda: gate2_scan(str(path), self.gate2_patterns),
        )
        result["gates"]["gate2"] = gate2

        if ext == ".pdf":
            gate3 = self._run_gate(
                "Gate 3",
                lambda: gate3_scan_pdf(
                    str(path),
                    self.gate3_mask_rules,
                    self.gate3_whitelist_rules,
                ),
            )
        elif ext == ".csv":
            gate3 = self._run_gate(
                "Gate 3",
                lambda: scan_and_mask_csv(
                    str(path),
                    self.gate3_mask_rules,
                    self.gate3_whitelist_rules,
                    str(self.output_dir),
                ),
            )
        else:
            gate3 = {"overall_result": "SKIP", "detail": "Unsupported for PII gate"}
        result["gates"]["gate3"] = gate3

        decision = self._aggregate_decision(result)
        result.update(decision)
        if gate3.get("masked_output"):
            result["masked_output"] = gate3["masked_output"]

        return self._save_result(result)

    def _base_result(self, filepath: str) -> dict:
        return {
            "file": Path(filepath).name,
            "filepath": str(Path(filepath).resolve()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gates": {},
            "decision": "REJECT",
            "import_status": "REJECTED",
            "rejection_reason": None,
        }

    def _aggregate_decision(self, result: dict) -> dict:
        gate1 = result["gates"]["gate1"]
        gate2 = result["gates"]["gate2"]
        gate3 = result["gates"]["gate3"]
        reasons = []

        if gate1["overall_result"] in ("FAIL", "ERROR"):
            reasons.extend(gate1.get("fail_reasons", [gate1.get("error", "Gate 1 failed")]))

        if gate2["overall_result"] in ("REJECT", "ERROR", "FLAG"):
            if gate2["overall_result"] == "ERROR":
                reasons.append(gate2.get("error", "Gate 2 failed"))
            elif gate2["overall_result"] == "FLAG":
                reasons.append("Prompt injection requires human review")
            else:
                reasons.append("Prompt injection detected")

        if gate3["overall_result"] in ("ERROR", "SKIP"):
            if gate3["overall_result"] == "ERROR":
                reasons.append(gate3.get("error", "Gate 3 failed"))
            elif gate3.get("detail"):
                reasons.append(gate3["detail"])
        elif gate3["overall_result"] == "PII_FOUND":
            summary = gate3.get("summary", {})
            if result["filepath"].lower().endswith(".pdf"):
                reasons.append("PII detected in PDF; a masked PDF is not available")
            elif summary.get("masked", 0) == 0:
                reasons.append("PII detected but no safe masked copy was produced")

        if reasons:
            return {
                "decision": "REJECT",
                "import_status": "REJECTED",
                "rejection_reason": "; ".join(reasons),
            }

        if gate3["overall_result"] == "PII_FOUND":
            return {
                "decision": "ACCEPT",
                "import_status": "ACCEPTED_WITH_PII_MASKED",
                "rejection_reason": None,
            }

        return {
            "decision": "ACCEPT",
            "import_status": "ACCEPTED",
            "rejection_reason": None,
        }

    def _save_result(self, result: dict) -> dict:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        report_path = self.report_dir / f"import_validation_{timestamp}.json"
        with report_path.open("w", encoding="utf-8") as report_file:
            json.dump(result, report_file, ensure_ascii=False, indent=2)
        result["validation_report"] = str(report_path)
        with report_path.open("w", encoding="utf-8") as report_file:
            json.dump(result, report_file, ensure_ascii=False, indent=2)
        return result
