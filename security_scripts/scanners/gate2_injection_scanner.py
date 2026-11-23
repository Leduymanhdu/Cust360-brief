"""
Gate 2: Prompt Injection Scanner
=================================
RFP Requirements:
  - SEC 04: Scan for hidden instructions in uploaded content
  - ACC 06: Treat embedded instructions as DATA, not commands

Pipeline position: SECOND gate - after Gate 1 (malware/validation).
Rationale: File đã được xác nhận an toàn về mặt cấu trúc (Gate 1),
           giờ mới mở ra đọc text content để scan injection.

Approach:
  - Extract text from PDF using PyMuPDF
  - Match against regex patterns (loaded from config)
  - Report: file, page number, position, matched pattern, severity
  - Decision: REJECT file nếu tìm thấy HIGH/CRITICAL patterns
              FLAG file nếu tìm thấy MEDIUM patterns (cần review)

Usage:
  python -I gate2_injection_scanner.py <file_or_directory> [--config CONFIG]
  python -I gate2_injection_scanner.py test_data/dirty/ --config configs/injection_patterns.json

Output:
  - Console summary
  - JSON log in logs/ directory
"""

import os
import sys
import re
import json
import csv
from datetime import datetime
from pathlib import Path

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        print("ERROR: pymupdf chưa cài. Chạy: pip install pymupdf")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Default patterns - sẽ bị override nếu có config file
# ---------------------------------------------------------------------------
DEFAULT_PATTERNS = [
    {
        "id": "INJ-BASIC-01",
        "category": "direct_override",
        "patterns_en": ["ignore (all )?previous instructions"],
        "patterns_vi": ["bỏ qua (tất cả )?hướng dẫn trước"],
        "severity": "HIGH",
    },
]


def load_patterns(config_path: str | None = None) -> list[dict]:
    """
    Load injection patterns từ config JSON.
    Mỗi pattern group có: id, category, patterns_en, patterns_vi, severity.
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("patterns", DEFAULT_PATTERNS)
    return DEFAULT_PATTERNS


def compile_patterns(pattern_groups: list[dict]) -> list[dict]:
    """
    Compile tất cả regex patterns thành compiled objects.
    Gộp patterns_en + patterns_vi cho mỗi group.
    Returns list of {id, category, severity, regex, raw_pattern}
    """
    compiled = []
    for group in pattern_groups:
        all_patterns = group.get("patterns_en", []) + group.get("patterns_vi", [])
        for raw in all_patterns:
            try:
                compiled.append({
                    "id": group["id"],
                    "category": group["category"],
                    "severity": group.get("severity", "MEDIUM"),
                    "description": group.get("description", ""),
                    "regex": re.compile(raw, re.IGNORECASE),
                    "raw_pattern": raw,
                })
            except re.error as e:
                print(f"  ⚠ Regex lỗi [{group['id']}]: {raw} → {e}")
    return compiled


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_by_page(filepath: str) -> list[dict]:
    """
    Extract text từ mỗi page của PDF.
    Returns: [{page: int, text: str}, ...]
    """
    pages = []
    try:
        doc = pymupdf.open(filepath)
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append({"page": i + 1, "text": text})
        doc.close()
    except Exception as e:
        pages.append({"page": 0, "text": "", "error": str(e)})
    return pages


def extract_text_from_csv(filepath: str) -> list[dict]:
    """
    Extract text từ CSV - gộp tất cả cells thành 1 'page'.
    CSV không có concept page, nên dùng row number.
    """
    rows_text = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, 1):
                line = " | ".join(row)
                rows_text.append(f"[Row {row_num}] {line}")
    except Exception as e:
        rows_text.append(f"[Error] {e}")

    return [{"page": 1, "text": "\n".join(rows_text)}]


# ---------------------------------------------------------------------------
# Scanning logic
# ---------------------------------------------------------------------------

def scan_text(pages: list[dict], compiled_patterns: list[dict]) -> list[dict]:
    """
    Scan extracted text against compiled patterns.
    Returns list of findings: {page, line_num, matched_text, pattern_id,
                               category, severity, position}
    """
    findings = []

    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["text"]
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            for pat in compiled_patterns:
                match = pat["regex"].search(line)
                if match:
                    findings.append({
                        "page": page_num,
                        "line_num": line_num,
                        "matched_text": match.group()[:100],  # truncate
                        "context": line.strip()[:200],  # surrounding text
                        "pattern_id": pat["id"],
                        "category": pat["category"],
                        "severity": pat["severity"],
                        "position": {
                            "start": match.start(),
                            "end": match.end(),
                        },
                    })

    return findings


def scan_file(filepath: str, compiled_patterns: list[dict]) -> dict:
    """
    Scan 1 file (PDF hoặc CSV) cho injection patterns.
    """
    ext = Path(filepath).suffix.lower()

    result = {
        "file": os.path.basename(filepath),
        "filepath": os.path.abspath(filepath),
        "file_type": ext,
        "timestamp": datetime.now().isoformat(),
        "overall_result": "PASS",
        "findings": [],
        "summary": {
            "total_findings": 0,
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "by_category": {},
        },
    }

    # Extract text
    if ext == ".pdf":
        pages = extract_text_by_page(filepath)
    elif ext == ".csv":
        pages = extract_text_from_csv(filepath)
    else:
        result["overall_result"] = "SKIP"
        result["skip_reason"] = f"Unsupported file type: {ext}"
        return result

    # Scan
    findings = scan_text(pages, compiled_patterns)
    result["findings"] = findings
    result["summary"]["total_findings"] = len(findings)

    # Aggregate by severity & category
    for f in findings:
        sev = f["severity"]
        cat = f["category"]
        result["summary"]["by_severity"][sev] = (
            result["summary"]["by_severity"].get(sev, 0) + 1
        )
        result["summary"]["by_category"][cat] = (
            result["summary"]["by_category"].get(cat, 0) + 1
        )

    # Decision logic
    if result["summary"]["by_severity"].get("CRITICAL", 0) > 0:
        result["overall_result"] = "REJECT"
    elif result["summary"]["by_severity"].get("HIGH", 0) > 0:
        result["overall_result"] = "REJECT"
    elif result["summary"]["by_severity"].get("MEDIUM", 0) > 0:
        result["overall_result"] = "FLAG"  # cần human review
    else:
        result["overall_result"] = "PASS"

    return result


def scan_directory(dirpath: str, compiled_patterns: list[dict]) -> list[dict]:
    """Scan tất cả PDF và CSV trong directory."""
    results = []
    files = sorted(
        p for p in Path(dirpath).rglob("*")
        if p.suffix.lower() in (".pdf", ".csv")
    )

    if not files:
        print(f"  ⚠ Không tìm thấy file PDF/CSV nào trong: {dirpath}")
        return results

    for fpath in files:
        result = scan_file(str(fpath), compiled_patterns)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_summary(results: list[dict]):
    """In kết quả scan ra console."""
    print("\n" + "=" * 65)
    print("GATE 2: PROMPT INJECTION SCAN - KẾT QUẢ")
    print("=" * 65)

    pass_count = sum(1 for r in results if r["overall_result"] == "PASS")
    reject_count = sum(1 for r in results if r["overall_result"] == "REJECT")
    flag_count = sum(1 for r in results if r["overall_result"] == "FLAG")
    skip_count = sum(1 for r in results if r["overall_result"] == "SKIP")

    for r in results:
        status_map = {
            "PASS": "✅ PASS",
            "REJECT": "❌ REJECT",
            "FLAG": "⚠️  FLAG",
            "SKIP": "⏭  SKIP",
        }
        status = status_map.get(r["overall_result"], r["overall_result"])
        print(f"\n  {status}  {r['file']}")

        if r["overall_result"] == "SKIP":
            print(f"         → {r.get('skip_reason', 'N/A')}")
            continue

        if r["findings"]:
            # Group findings by category for cleaner output
            cats = r["summary"]["by_category"]
            for cat, count in cats.items():
                print(f"         → {cat}: {count} finding(s)")

            # Show first 3 findings as examples
            print(f"         Ví dụ:")
            for f in r["findings"][:3]:
                print(
                    f"           [{f['severity']}] p.{f['page']} "
                    f"L{f['line_num']}: \"{f['matched_text']}\" "
                    f"({f['pattern_id']})"
                )
            if len(r["findings"]) > 3:
                print(f"           ... và {len(r['findings']) - 3} finding(s) khác")

    print(f"\n{'─' * 65}")
    print(f"  Tổng: {len(results)} file")
    print(f"  ✅ PASS: {pass_count} | ❌ REJECT: {reject_count} "
          f"| ⚠️  FLAG: {flag_count} | ⏭ SKIP: {skip_count}")
    print("=" * 65)


def save_log(results: list[dict], log_dir: str) -> str:
    """Lưu kết quả ra JSON log."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gate2_scan_{timestamp}.json")

    log_data = {
        "scan_type": "gate2_injection_scan",
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "passed": sum(1 for r in results if r["overall_result"] == "PASS"),
        "rejected": sum(1 for r in results if r["overall_result"] == "REJECT"),
        "flagged": sum(1 for r in results if r["overall_result"] == "FLAG"),
        "results": results,
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Log saved: {log_file}")
    return log_file


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python -I gate2_injection_scanner.py <file_or_dir> [--config CONFIG]")
        print("\nExamples:")
        print("  python -I gate2_injection_scanner.py test_data/dirty/dirty_injection_test.pdf")
        print("  python -I gate2_injection_scanner.py test_data/ --config configs/injection_patterns.json")
        sys.exit(1)

    target = sys.argv[1]

    config_path = None
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        if idx + 1 < len(sys.argv):
            config_path = sys.argv[idx + 1]

    # Load & compile patterns
    pattern_groups = load_patterns(config_path)
    compiled = compile_patterns(pattern_groups)
    print(f"\n🔍 Gate 2: Prompt Injection Scanner")
    print(f"   Loaded {len(compiled)} regex patterns from {len(pattern_groups)} groups")
    print(f"   Target: {target}")

    # Scan
    if os.path.isfile(target):
        results = [scan_file(target, compiled)]
    elif os.path.isdir(target):
        results = scan_directory(target, compiled)
    else:
        print(f"ERROR: Không tìm thấy: {target}")
        sys.exit(1)

    if not results:
        print("Không có file nào để scan.")
        sys.exit(0)

    # Output
    print_summary(results)

    # Save log
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    log_dir = os.path.join(project_dir, "logs")
    save_log(results, log_dir)


if __name__ == "__main__":
    main()
