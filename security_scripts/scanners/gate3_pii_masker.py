"""
Gate 3: PII Masker
==================
RFP Requirements:
  - SEC 02: Protect personal data
  - Mục 6 (Tiêu chí): Mask personal phone/email, add access_level column

Pipeline position: THIRD gate - after injection scan (Gate 2).
Rationale: File đã qua malware check (Gate 1) và injection check (Gate 2).
           Giờ mask PII trước khi data đi vào pipeline chính.

Approach:
  - PDF: Scan → report PII found (PDF text thường không sửa trực tiếp)
  - CSV: Scan → tạo bản copy đã mask (không sửa file gốc!)
  - Dùng whitelist để tránh mask business data (email @company.vn, hotline, MST DN)

Key design decision:
  Tạo COPY đã mask, KHÔNG sửa file gốc.
  Lý do: Nếu mask sai (false positive), có thể so sánh lại với bản gốc.

Usage:
  python -I gate3_pii_masker.py <file_or_dir> [--config CONFIG] [--output-dir DIR]

Output:
  - Console summary
  - Masked CSV copies in output directory
  - JSON log in logs/
"""

import os
import sys
import re
import json
import csv
from datetime import datetime
from pathlib import Path
from copy import deepcopy

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        print("ERROR: pymupdf chưa cài. Chạy: pip install pymupdf")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_pii_rules(config_path: str | None = None) -> dict:
    """Load PII rules from JSON config."""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Minimal defaults
    return {
        "rules": [
            {
                "id": "PII-DEFAULT-01",
                "type": "phone",
                "regex": r"(?:\+84|0)[3789]\d[\.\s-]?\d{3}[\.\s-]?\d{3,4}",
                "mask": "***-***-****",
                "action": "mask",
            },
            {
                "id": "PII-DEFAULT-02",
                "type": "email_personal",
                "regex": r"[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.[a-zA-Z]{2,}",
                "mask": "***@***.***",
                "action": "mask",
            },
        ],
        "whitelist": {"patterns": []},
    }


def compile_rules(config: dict) -> tuple[list[dict], list[dict]]:
    """
    Compile mask rules và whitelist patterns.
    Returns: (mask_rules, whitelist_rules)
    """
    mask_rules = []
    for rule in config.get("rules", []):
        try:
            mask_rules.append({
                **rule,
                "compiled": re.compile(rule["regex"], re.IGNORECASE),
            })
        except re.error as e:
            print(f"  ⚠ Regex lỗi [{rule.get('id', '?')}]: {e}")

    whitelist_rules = []
    for wl in config.get("whitelist", {}).get("patterns", []):
        try:
            whitelist_rules.append({
                **wl,
                "compiled": re.compile(wl["regex"], re.IGNORECASE),
            })
        except re.error as e:
            print(f"  ⚠ Whitelist regex lỗi: {e}")

    return mask_rules, whitelist_rules


# ---------------------------------------------------------------------------
# Core logic: detect & mask
# ---------------------------------------------------------------------------

def is_whitelisted(text: str, match_start: int, match_end: int,
                   whitelist_rules: list[dict]) -> bool:
    """
    Check if a PII match is actually whitelisted (business data).
    Ví dụ: email @company.vn, hotline 1900xxx
    """
    matched_text = text[match_start:match_end]
    for wl in whitelist_rules:
        if wl["compiled"].search(matched_text):
            return True
    return False


def detect_pii_in_text(text: str, mask_rules: list[dict],
                       whitelist_rules: list[dict]) -> list[dict]:
    """
    Tìm tất cả PII trong text.
    Returns list of findings (chưa mask, chỉ detect).
    """
    findings = []
    for rule in mask_rules:
        for match in rule["compiled"].finditer(text):
            # Check whitelist
            whitelisted = is_whitelisted(
                text, match.start(), match.end(), whitelist_rules
            )
            findings.append({
                "rule_id": rule["id"],
                "type": rule["type"],
                "matched_text": match.group(),
                "position": {"start": match.start(), "end": match.end()},
                "mask_value": rule["mask"],
                "action": "keep" if whitelisted else rule.get("action", "mask"),
                "whitelisted": whitelisted,
                "whitelist_reason": "Business data" if whitelisted else None,
            })
    return findings


def mask_text(text: str, findings: list[dict]) -> str:
    """
    Apply masking to text based on findings.
    Chỉ mask những findings có action='mask'.
    Process từ cuối lên đầu để không lệch position.
    """
    # Sort by position descending (mask from end to start)
    to_mask = sorted(
        [f for f in findings if f["action"] == "mask"],
        key=lambda f: f["position"]["start"],
        reverse=True,
    )

    masked = text
    for f in to_mask:
        start = f["position"]["start"]
        end = f["position"]["end"]
        masked = masked[:start] + f["mask_value"] + masked[end:]

    return masked


# ---------------------------------------------------------------------------
# PDF scanning (report only - can't easily modify PDF text)
# ---------------------------------------------------------------------------

def scan_pdf(filepath: str, mask_rules: list[dict],
             whitelist_rules: list[dict]) -> dict:
    """
    Scan PDF cho PII. Chỉ report, không mask (PDF text modification phức tạp).
    Trong production, sẽ extract text → mask → tạo file mới.
    """
    result = {
        "file": os.path.basename(filepath),
        "filepath": os.path.abspath(filepath),
        "file_type": ".pdf",
        "timestamp": datetime.now().isoformat(),
        "overall_result": "PASS",
        "findings": [],
        "summary": {
            "total_pii": 0,
            "masked": 0,
            "kept": 0,
            "flagged": 0,
            "by_type": {},
        },
        "masked_output": None,  # PDF: no auto-masking
    }

    try:
        doc = pymupdf.open(filepath)
        for i, page in enumerate(doc):
            text = page.get_text("text")
            page_findings = detect_pii_in_text(text, mask_rules, whitelist_rules)

            for f in page_findings:
                f["page"] = i + 1
                result["findings"].append(f)

        doc.close()
    except Exception as e:
        result["error"] = str(e)
        result["overall_result"] = "ERROR"
        return result

    # Summarize
    result["summary"]["total_pii"] = len(result["findings"])
    for f in result["findings"]:
        ptype = f["type"]
        result["summary"]["by_type"][ptype] = (
            result["summary"]["by_type"].get(ptype, 0) + 1
        )
        if f["action"] == "mask":
            result["summary"]["masked"] += 1
        elif f["action"] == "keep":
            result["summary"]["kept"] += 1
        elif f["action"] == "flag":
            result["summary"]["flagged"] += 1

    if result["summary"]["masked"] > 0 or result["summary"]["flagged"] > 0:
        result["overall_result"] = "PII_FOUND"

    return result


# ---------------------------------------------------------------------------
# CSV scanning & masking
# ---------------------------------------------------------------------------

def scan_and_mask_csv(filepath: str, mask_rules: list[dict],
                      whitelist_rules: list[dict],
                      output_dir: str) -> dict:
    """
    Scan CSV cho PII, tạo bản copy đã mask.
    File gốc KHÔNG bị sửa đổi.
    """
    result = {
        "file": os.path.basename(filepath),
        "filepath": os.path.abspath(filepath),
        "file_type": ".csv",
        "timestamp": datetime.now().isoformat(),
        "overall_result": "PASS",
        "findings": [],
        "summary": {
            "total_pii": 0,
            "masked": 0,
            "kept": 0,
            "flagged": 0,
            "by_type": {},
        },
        "masked_output": None,
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
    except Exception as e:
        result["error"] = str(e)
        result["overall_result"] = "ERROR"
        return result

    masked_rows = []

    for row_idx, row in enumerate(rows, 1):
        masked_row = dict(row)  # copy

        for col_name, cell_value in row.items():
            if not cell_value or not cell_value.strip():
                continue

            cell_findings = detect_pii_in_text(
                cell_value, mask_rules, whitelist_rules
            )

            for f in cell_findings:
                f["row"] = row_idx
                f["column"] = col_name
                result["findings"].append(f)

            # Apply masking to cell
            if cell_findings:
                masked_row[col_name] = mask_text(cell_value, cell_findings)

        masked_rows.append(masked_row)

    # Summarize
    result["summary"]["total_pii"] = len(result["findings"])
    for f in result["findings"]:
        ptype = f["type"]
        result["summary"]["by_type"][ptype] = (
            result["summary"]["by_type"].get(ptype, 0) + 1
        )
        if f["action"] == "mask":
            result["summary"]["masked"] += 1
        elif f["action"] == "keep":
            result["summary"]["kept"] += 1
        elif f["action"] == "flag":
            result["summary"]["flagged"] += 1

    if result["summary"]["masked"] > 0 or result["summary"]["flagged"] > 0:
        result["overall_result"] = "PII_FOUND"

    # Write masked copy
    if result["summary"]["masked"] > 0:
        os.makedirs(output_dir, exist_ok=True)
        stem = Path(filepath).stem
        output_path = os.path.join(output_dir, f"{stem}_masked.csv")

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(masked_rows)

        result["masked_output"] = output_path

    return result


# ---------------------------------------------------------------------------
# Directory scanning
# ---------------------------------------------------------------------------

def scan_directory(dirpath: str, mask_rules: list[dict],
                   whitelist_rules: list[dict],
                   output_dir: str) -> list[dict]:
    """Scan tất cả PDF và CSV."""
    results = []
    files = sorted(
        p for p in Path(dirpath).rglob("*")
        if p.suffix.lower() in (".pdf", ".csv")
    )

    if not files:
        print(f"  ⚠ Không tìm thấy file nào trong: {dirpath}")
        return results

    for fpath in files:
        ext = fpath.suffix.lower()
        if ext == ".pdf":
            r = scan_pdf(str(fpath), mask_rules, whitelist_rules)
        elif ext == ".csv":
            r = scan_and_mask_csv(str(fpath), mask_rules, whitelist_rules,
                                  output_dir)
        else:
            continue
        results.append(r)

    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_summary(results: list[dict]):
    print("\n" + "=" * 65)
    print("GATE 3: PII MASKER - KẾT QUẢ")
    print("=" * 65)

    for r in results:
        s = r["summary"]
        if r["overall_result"] == "PASS":
            status = "✅ CLEAN"
        elif r["overall_result"] == "PII_FOUND":
            status = "🔒 PII_FOUND"
        else:
            status = f"⚠  {r['overall_result']}"

        print(f"\n  {status}  {r['file']}")

        if s["total_pii"] > 0:
            print(f"         Tổng PII: {s['total_pii']}")
            print(f"         → Masked: {s['masked']} | Kept (business): {s['kept']} "
                  f"| Flagged: {s['flagged']}")

            if s["by_type"]:
                types_str = ", ".join(
                    f"{t}: {c}" for t, c in s["by_type"].items()
                )
                print(f"         → Loại: {types_str}")

            # Show examples
            masked_findings = [f for f in r["findings"] if f["action"] == "mask"]
            kept_findings = [f for f in r["findings"] if f["action"] == "keep"]

            if masked_findings:
                print(f"         Ví dụ masked:")
                for f in masked_findings[:3]:
                    loc = f"p.{f.get('page', '?')}" if "page" in f else f"row {f.get('row', '?')} [{f.get('column', '')}]"
                    print(f"           {loc}: \"{f['matched_text']}\" → \"{f['mask_value']}\"")

            if kept_findings:
                print(f"         Kept (whitelist):")
                for f in kept_findings[:2]:
                    print(f"           \"{f['matched_text']}\" - {f.get('whitelist_reason', 'business')}")

            if r.get("masked_output"):
                print(f"         📄 Masked copy: {r['masked_output']}")

    # Totals
    total_files = len(results)
    total_pii = sum(r["summary"]["total_pii"] for r in results)
    total_masked = sum(r["summary"]["masked"] for r in results)
    total_kept = sum(r["summary"]["kept"] for r in results)

    print(f"\n{'─' * 65}")
    print(f"  Tổng: {total_files} file | PII found: {total_pii} "
          f"| Masked: {total_masked} | Kept: {total_kept}")
    print("=" * 65)


def save_log(results: list[dict], log_dir: str) -> str:
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gate3_scan_{timestamp}.json")

    log_data = {
        "scan_type": "gate3_pii_mask",
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "total_pii_found": sum(r["summary"]["total_pii"] for r in results),
        "total_masked": sum(r["summary"]["masked"] for r in results),
        "total_kept": sum(r["summary"]["kept"] for r in results),
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
        print("Usage: python -I gate3_pii_masker.py <file_or_dir> [--config CONFIG] [--output-dir DIR]")
        sys.exit(1)

    target = sys.argv[1]

    config_path = None
    output_dir = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--config" and i + 1 < len(args):
            config_path = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            i += 1

    # Default output dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    if not output_dir:
        output_dir = os.path.join(project_dir, "test_data", "masked_output")

    # Load config
    config = load_pii_rules(config_path)
    mask_rules, whitelist_rules = compile_rules(config)

    print(f"\n🔍 Gate 3: PII Masker")
    print(f"   {len(mask_rules)} mask rules, {len(whitelist_rules)} whitelist rules")
    print(f"   Target: {target}")
    print(f"   Output: {output_dir}")

    # Scan
    if os.path.isfile(target):
        ext = Path(target).suffix.lower()
        if ext == ".pdf":
            results = [scan_pdf(target, mask_rules, whitelist_rules)]
        elif ext == ".csv":
            results = [scan_and_mask_csv(target, mask_rules, whitelist_rules,
                                         output_dir)]
        else:
            print(f"Unsupported: {ext}")
            sys.exit(1)
    elif os.path.isdir(target):
        results = scan_directory(target, mask_rules, whitelist_rules, output_dir)
    else:
        print(f"ERROR: {target}")
        sys.exit(1)

    if not results:
        sys.exit(0)

    print_summary(results)

    log_dir = os.path.join(project_dir, "logs")
    save_log(results, log_dir)


if __name__ == "__main__":
    main()
