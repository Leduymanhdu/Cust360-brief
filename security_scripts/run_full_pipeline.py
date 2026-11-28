"""
Full Pipeline Runner
====================
Chạy tuần tự: Gate 1 → Gate 2 → Gate 3
File FAIL ở gate nào thì dừng ở gate đó (không chạy gate tiếp).
Tạo report tổng hợp pass/fail counts + detected issues.

Usage:
  python -I run_full_pipeline.py <directory>
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add scanners directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scanners"))

from gate1_pdf_validator import scan_pdf as gate1_scan, load_config as gate1_config
from gate2_injection_scanner import (
    scan_file as gate2_scan,
    load_patterns,
    compile_patterns,
)
from gate3_pii_masker import (
    scan_pdf as gate3_scan_pdf,
    scan_and_mask_csv as gate3_scan_csv,
    load_pii_rules,
    compile_rules,
)


def run_pipeline(target_dir: str):
    """Run full 4-gate pipeline on a directory."""
    target_path = Path(target_dir)
    if not target_path.exists():
        raise FileNotFoundError(f"Không tìm thấy đường dẫn đầu vào: {target_dir}")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(project_dir, "configs")
    log_dir = os.path.join(project_dir, "logs")
    output_dir = os.path.join(project_dir, "test_data", "masked_output")

    # Load all configs
    g1_config = gate1_config(os.path.join(config_dir, "gate1_config.json"))
    g2_patterns = compile_patterns(
        load_patterns(os.path.join(config_dir, "injection_patterns.json"))
    )
    g3_config = load_pii_rules(os.path.join(config_dir, "pii_rules.json"))
    g3_mask_rules, g3_wl_rules = compile_rules(g3_config)

    # Find all files
    if target_path.is_file():
        files = [target_path] if target_path.suffix.lower() in (".pdf", ".csv") else []
    else:
        files = sorted(
            p for p in target_path.rglob("*")
            if p.suffix.lower() in (".pdf", ".csv")
            and "masked_output" not in str(p)
        )

    print("\n" + "=" * 70)
    print("  FULL PIPELINE RUN - Customer 360 Security Gates")
    print("  Gate 1: PDF Validation → Gate 2: Injection → Gate 3: PII Mask")
    print("=" * 70)
    print(f"  Target: {target_dir}")
    print(f"  Files found: {len(files)}")
    print("=" * 70)

    pipeline_results = []

    for fpath in files:
        filepath = str(fpath)
        filename = fpath.name
        ext = fpath.suffix.lower()

        file_result = {
            "file": filename,
            "filepath": filepath,
            "gates": {},
            "final_status": "UNKNOWN",
            "decision": "REJECT",
            "rejection_reason": None,
            "stopped_at": None,
            "issues": [],
        }

        print(f"\n  📄 {filename}")
        gate1_result = None
        gate2_result = None
        gate3_result = None
        gate1_failed = False
        gate2_failed = False
        gate3_failed = False

        # ─── Gate 1: PDF Validation (PDF only) ───
        if ext == ".pdf":
            try:
                g1 = gate1_scan(filepath, g1_config)
                gate1_result = g1
            except Exception as exc:
                g1 = {
                    "overall_result": "ERROR",
                    "fail_reasons": [f"Gate 1 không hoạt động: {type(exc).__name__}: {exc}"],
                }
                gate1_result = g1
            file_result["gates"]["gate1"] = g1["overall_result"]
            print(f"     Gate 1 (Validation): {g1['overall_result']}", end="")

            if g1["overall_result"] in ("FAIL", "ERROR"):
                print(f" ← {', '.join(g1['fail_reasons'][:2])}")
                gate1_failed = True
                file_result["issues"].extend(g1["fail_reasons"])
            else:
                print()
        else:
            file_result["gates"]["gate1"] = "SKIP"
            print(f"     Gate 1 (Validation): SKIP (not PDF)")

        # A failed/errored PDF validation must stop before the file is parsed by
        # the injection or PII scanners.
        if gate1_failed:
            file_result["gates"].update({"gate2": "SKIP", "gate3": "SKIP"})
            file_result["final_status"] = "REJECTED"
            file_result["decision"] = "REJECT"
            file_result["stopped_at"] = "gate1"
            file_result["rejection_reason"] = "; ".join(file_result["issues"])
            file_result["gate_results"] = {
                "gate1": gate1_result,
                "gate2": None,
                "gate3": None,
            }
            pipeline_results.append(file_result)
            continue

        # ─── Gate 2: Injection Scan ───
        try:
            g2 = gate2_scan(filepath, g2_patterns)
            gate2_result = g2
        except Exception as exc:
            g2 = {
                "overall_result": "ERROR",
                "summary": {"by_category": {}},
                "error": f"{type(exc).__name__}: {exc}",
            }
            gate2_result = g2
        file_result["gates"]["gate2"] = g2["overall_result"]
        print(f"     Gate 2 (Injection):  {g2['overall_result']}", end="")

        if g2["overall_result"] in ("REJECT", "ERROR"):
            cats = g2["summary"]["by_category"]
            cat_str = ", ".join(f"{c}: {n}" for c, n in cats.items())
            reason = g2.get("error") if g2["overall_result"] == "ERROR" else f"Injection detected: {cat_str}"
            print(f" ← {reason}")
            gate2_failed = True
            file_result["issues"].append(reason if g2["overall_result"] == "ERROR" else f"Injection detected: {cat_str}")
        elif g2["overall_result"] == "FLAG":
            print(" ← Cần review")
            gate2_failed = True
            file_result["issues"].append("Injection: flagged for review")
        else:
            print()

        # Rejected or flagged injection results do not proceed to PII parsing.
        if gate2_failed:
            file_result["gates"]["gate3"] = "SKIP"
            is_flagged = g2["overall_result"] == "FLAG"
            file_result["final_status"] = "FLAGGED" if is_flagged else "REJECTED"
            file_result["decision"] = "REJECT"
            file_result["stopped_at"] = "gate2"
            file_result["rejection_reason"] = "; ".join(file_result["issues"])
            file_result["gate_results"] = {
                "gate1": gate1_result,
                "gate2": gate2_result,
                "gate3": None,
            }
            pipeline_results.append(file_result)
            continue

        # ─── Gate 3: PII Mask ───
        try:
            if ext == ".pdf":
                g3 = gate3_scan_pdf(filepath, g3_mask_rules, g3_wl_rules)
                gate3_result = g3
            elif ext == ".csv":
                g3 = gate3_scan_csv(filepath, g3_mask_rules, g3_wl_rules, output_dir)
                gate3_result = g3
            else:
                g3 = {"overall_result": "SKIP", "summary": {"total_pii": 0, "masked": 0, "kept": 0}}
                gate3_result = g3
        except Exception as exc:
            g3 = {
                "overall_result": "ERROR",
                "summary": {"total_pii": 0, "masked": 0, "kept": 0},
                "error": f"{type(exc).__name__}: {exc}",
            }
            gate3_result = g3

        file_result["gates"]["gate3"] = g3["overall_result"]
        s = g3["summary"]
        print(f"     Gate 3 (PII Mask):   {g3['overall_result']}", end="")

        if g3["overall_result"] == "PII_FOUND":
            print(f" ← PII: {s['total_pii']} (masked: {s['masked']}, kept: {s['kept']})")
            file_result["issues"].append(
                f"PII found: {s['total_pii']} (masked: {s['masked']}, kept: {s['kept']})"
            )
            if g3.get("masked_output"):
                file_result["masked_output"] = g3["masked_output"]
            if ext == ".pdf" or s["masked"] == 0:
                gate3_failed = True
        elif g3["overall_result"] == "ERROR":
            print(f" ← {g3['error']}")
            gate3_failed = True
            file_result["issues"].append(f"Gate 3 không hoạt động: {g3['error']}")
        else:
            print()

        # ─── Final Status ───
        if gate1_failed:
            file_result["final_status"] = "REJECTED"
            file_result["stopped_at"] = "gate1"
        elif gate2_failed:
            file_result["final_status"] = "REJECTED"
            file_result["stopped_at"] = "gate2"
        elif gate3_failed:
            file_result["final_status"] = "REJECTED"
            file_result["stopped_at"] = "gate3"
        elif g2["overall_result"] == "FLAG":
            file_result["final_status"] = "FLAGGED"
        elif g3["overall_result"] == "PII_FOUND":
            file_result["final_status"] = "PASSED_WITH_PII"
        else:
            file_result["final_status"] = "CLEAN"

        if file_result["final_status"] in ("CLEAN", "PASSED_WITH_PII"):
            file_result["decision"] = "ACCEPT"
            file_result["rejection_reason"] = None
        else:
            file_result["decision"] = "REJECT"
            file_result["rejection_reason"] = "; ".join(file_result["issues"])

        file_result["gate_results"] = {
            "gate1": gate1_result,
            "gate2": gate2_result,
            "gate3": gate3_result,
        }

        pipeline_results.append(file_result)

    # ─── Summary ───
    print("\n" + "=" * 70)
    print("  TỔNG KẾT PIPELINE")
    print("=" * 70)

    status_counts = {}
    for r in pipeline_results:
        st = r["final_status"]
        status_counts[st] = status_counts.get(st, 0) + 1

    for status, count in sorted(status_counts.items()):
        icon = {
            "CLEAN": "✅",
            "PASSED_WITH_PII": "🔒",
            "FLAGGED": "⚠️",
            "REJECTED": "❌",
        }.get(status, "❓")
        print(f"  {icon} {status}: {count}")

    print(f"\n  Tổng file: {len(pipeline_results)}")

    # Show rejected files
    rejected = [r for r in pipeline_results if r["final_status"] == "REJECTED"]
    if rejected:
        print(f"\n  ❌ Files bị reject:")
        for r in rejected:
            print(f"     {r['file']} (stopped at {r['stopped_at']})")
            for issue in r["issues"][:2]:
                print(f"       → {issue}")

    # Show PII files
    pii_files = [r for r in pipeline_results if r["final_status"] == "PASSED_WITH_PII"]
    if pii_files:
        print(f"\n  🔒 Files có PII (đã mask):")
        for r in pii_files:
            for issue in r["issues"]:
                print(f"     {r['file']}: {issue}")

    print("=" * 70)

    # ─── Save report ───
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(log_dir, f"pipeline_report_{timestamp}.json")

    report = {
        "report_type": "full_pipeline_test",
        "timestamp": datetime.now().isoformat(),
        "target_directory": target_dir,
        "total_files": len(pipeline_results),
        "summary": status_counts,
        "results": pipeline_results,
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 JSON log: {report_path}")

    # ─── Markdown report cho người đọc ───
    report_dir = os.path.join(project_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)
    md_path = os.path.join(report_dir, f"test_report_{timestamp}.md")

    md_lines = [
        "# BÁO CÁO KIỂM TRA AN NINH DỮ LIỆU",
        "## Customer 360 Briefing Assistant - SongNhat Vietnam",
        "",
        f"**Ngày chạy:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"**Thư mục test:** `{target_dir}`",
        f"**Tổng file:** {len(pipeline_results)}",
        "",
        "---",
        "",
        "## 1. Tổng kết",
        "",
        "| Kết quả | Số file | Ý nghĩa |",
        "|---------|---------|---------|",
    ]

    status_info = {
        "CLEAN": ("✅", "File sạch, đủ điều kiện vào pipeline"),
        "PASSED_WITH_PII": ("🔒", "Có PII đã được mask, cho vào pipeline"),
        "FLAGGED": ("⚠️", "Cần human review trước khi cho vào"),
        "REJECTED": ("❌", "Bị từ chối, không đưa vào pipeline"),
    }
    for st, count in sorted(status_counts.items()):
        icon, desc = status_info.get(st, ("❓", st))
        md_lines.append(f"| {icon} {st} | {count} | {desc} |")

    md_lines += [
        "",
        "---",
        "",
        "## 2. Chi tiết từng file",
        "",
        "| # | File | Gate 1 | Gate 2 | Gate 3 | Quyết định | Kết quả | Ghi chú |",
        "|---|------|--------|--------|--------|------------|---------|---------|",
    ]

    for i, r in enumerate(pipeline_results, 1):
        g1 = r["gates"].get("gate1", "-")
        g2 = r["gates"].get("gate2", "-")
        g3 = r["gates"].get("gate3", "-")
        final = r["final_status"]
        icon = status_info.get(final, ("❓",))[0]
        issues_str = "; ".join(r["issues"][:2]) if r["issues"] else "-"
        # Truncate long issues
        if len(issues_str) > 80:
            issues_str = issues_str[:77] + "..."
        md_lines.append(
            f"| {i} | {r['file']} | {g1} | {g2} | {g3} | {r['decision']} | {icon} {final} | {issues_str} |"
        )

    # Section 3: Rejected files detail
    rejected = [r for r in pipeline_results if r["final_status"] == "REJECTED"]
    if rejected:
        md_lines += [
            "",
            "---",
            "",
            "## 3. Files bị từ chối (chi tiết)",
            "",
        ]
        for r in rejected:
            md_lines.append(f"### ❌ {r['file']}")
            md_lines.append(f"- **Dừng tại:** Gate {r['stopped_at'][-1]}")
            for issue in r["issues"]:
                md_lines.append(f"- **Lý do:** {issue}")
            md_lines.append("")

    # Section 4: PII files
    pii_files = [r for r in pipeline_results if r["final_status"] == "PASSED_WITH_PII"]
    if pii_files:
        section_num = 4 if rejected else 3
        md_lines += [
            "---",
            "",
            f"## {section_num}. Files có PII (đã xử lý)",
            "",
        ]
        for r in pii_files:
            md_lines.append(f"### 🔒 {r['file']}")
            for issue in r["issues"]:
                md_lines.append(f"- {issue}")
            if r.get("masked_output"):
                md_lines.append(f"- **Bản đã mask:** `{r['masked_output']}`")
            md_lines.append("")

    # Section: Pipeline config
    md_lines += [
        "---",
        "",
        f"## {'5' if rejected and pii_files else '4' if rejected or pii_files else '3'}. Cấu hình pipeline",
        "",
        "| Gate | Script | Config |",
        "|------|--------|--------|",
        "| Gate 1 - PDF Validation | `scanners/gate1_pdf_validator.py` | Max 10MB, max 20 trang |",
        "| Gate 2 - Injection Scan | `scanners/gate2_injection_scanner.py` | `configs/injection_patterns.json` (49 patterns) |",
        "| Gate 3 - PII Mask | `scanners/gate3_pii_masker.py` | `configs/pii_rules.json` (5 rules + 3 whitelist) |",
        "",
        "---",
        "",
        f"*Report generated by `run_full_pipeline.py` - {datetime.now().isoformat()}*",
    ]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"  📊 Markdown report: {md_path}")
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -I run_full_pipeline.py <directory>")
        sys.exit(1)
    run_pipeline(sys.argv[1])
