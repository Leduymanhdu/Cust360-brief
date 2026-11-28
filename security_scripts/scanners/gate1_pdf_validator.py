"""
Gate 1: PDF Validation & Malware Scanner
=========================================
RFP Requirements:
  - SEC 04: Scan/sandbox uploads, block active content
  - ACC 06: Max 10MB, max 20 pages
  - Mục 4 (Tiêu chí): Only accept readable files, scan for malware

Pipeline position: FIRST gate - runs BEFORE opening file for text extraction.
Rationale: If a PDF contains malware/exploit, parsing it for injection
           patterns (Gate 2) could trigger the exploit.

Checks performed:
  1. File exists & readable
  2. Magic bytes = PDF (%PDF-)
  3. File size ≤ MAX_FILE_SIZE_MB
  4. Page count ≤ MAX_PAGES
  5. Not encrypted/password-protected
  6. No embedded JavaScript (active content)
  7. No auto-actions (OpenAction, AA entries)
  8. No embedded files/attachments (potential payload carriers)

Usage:
  python -I gate1_pdf_validator.py <file_or_directory> [--config CONFIG_PATH]

Output:
  - Console summary (PASS/FAIL per file)
  - JSON log in logs/ directory
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Thử import pymupdf - nếu không có thì báo lỗi rõ ràng
# ---------------------------------------------------------------------------
try:
    import pymupdf  # pymupdf >= 1.24 recommended import
except ImportError:
    try:
        import fitz as pymupdf  # fallback for older versions
    except ImportError:
        print("ERROR: pymupdf (PyMuPDF) chưa cài. Chạy: pip install pymupdf")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Default config - có thể override bằng file JSON
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "max_file_size_mb": 10,       # ACC 06
    "max_pages": 20,               # ACC 06
    "block_javascript": True,      # SEC 04: block active content
    "block_auto_actions": True,    # SEC 04: block auto-execute
    "block_encrypted": True,       # Can't scan encrypted content
    "block_embedded_files": True,  # Potential malware carriers
}


def load_config(config_path: str | None = None) -> dict:
    """Load config từ file JSON, merge với defaults."""
    config = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        config.update(user_config)
    return config


# ---------------------------------------------------------------------------
# Individual check functions - mỗi function trả về (pass: bool, detail: str)
# ---------------------------------------------------------------------------

def check_file_exists(filepath: str) -> tuple[bool, str]:
    """Check 1: File tồn tại và đọc được."""
    if not os.path.exists(filepath):
        return False, f"File không tồn tại: {filepath}"
    if not os.path.isfile(filepath):
        return False, f"Không phải file: {filepath}"
    if not os.access(filepath, os.R_OK):
        return False, f"Không có quyền đọc: {filepath}"
    return True, "File tồn tại và đọc được"


def check_magic_bytes(filepath: str) -> tuple[bool, str]:
    """Check 2: PDF magic bytes (%PDF-) ở đầu file."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(5)
        if header == b"%PDF-":
            return True, "Magic bytes hợp lệ (%PDF-)"
        else:
            return False, f"Không phải PDF. Header: {header!r}"
    except Exception as e:
        return False, f"Lỗi đọc header: {e}"


def check_file_size(filepath: str, max_mb: float) -> tuple[bool, str]:
    """Check 3: Kích thước file ≤ giới hạn."""
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb <= max_mb:
        return True, f"Kích thước: {size_mb:.2f} MB (giới hạn: {max_mb} MB)"
    else:
        return False, f"Vượt giới hạn: {size_mb:.2f} MB > {max_mb} MB"


def check_page_count(doc: pymupdf.Document, max_pages: int) -> tuple[bool, str]:
    """Check 4: Số trang ≤ giới hạn."""
    count = doc.page_count
    if count <= max_pages:
        return True, f"Số trang: {count} (giới hạn: {max_pages})"
    else:
        return False, f"Vượt giới hạn trang: {count} > {max_pages}"


def check_not_encrypted(doc: pymupdf.Document) -> tuple[bool, str]:
    """Check 5: PDF không bị mã hóa/password-protect."""
    if doc.is_encrypted:
        return False, "PDF bị mã hóa - không thể scan nội dung"
    return True, "Không mã hóa"


def check_no_javascript(doc: pymupdf.Document) -> tuple[bool, str]:
    """
    Check 6: Không có JavaScript embedded.
    SEC 04 yêu cầu block active content.

    Cách kiểm tra:
    - PDF-level JavaScript (document actions)
    - Page-level JavaScript
    - Annotation actions chứa JS
    """
    findings = []

    # Check document-level JS
    # PyMuPDF: xform_dict chứa JS catalog
    try:
        # Scan raw PDF content for /JavaScript entries
        # This is more reliable than API-level checks
        for i in range(len(doc)):
            page = doc[i]
            # Check page annotations for JavaScript actions
            annots = page.annots()
            if annots:
                for annot in annots:
                    annot_info = annot.info
                    # Some annotations can carry JS
                    if "/JS" in str(annot_info) or "JavaScript" in str(annot_info):
                        findings.append(f"Page {i+1}: Annotation chứa JavaScript")
    except Exception:
        pass  # Some pages may not have annotations

    # Scan raw xref table for JavaScript references
    try:
        for xref in range(1, doc.xref_length()):
            try:
                xref_str = doc.xref_object(xref)
                if "/JavaScript" in xref_str or "/JS " in xref_str or "/JS(" in xref_str:
                    findings.append(f"xref {xref}: Chứa JavaScript reference")
            except Exception:
                continue
    except Exception:
        pass

    if findings:
        return False, f"Phát hiện JavaScript: {'; '.join(findings[:3])}"
    return True, "Không có JavaScript"


def check_no_auto_actions(doc: pymupdf.Document) -> tuple[bool, str]:
    """
    Check 7: Không có MALICIOUS auto-execute actions.

    Phân biệt:
    - Benign OpenAction: /FitH, /Fit, /FitV, /XYZ (chỉ set zoom/view) → OK
    - Dangerous OpenAction: chứa /JavaScript, /URI, /Launch, /GoToR → BLOCK
    - /AA (Additional Actions): luôn suspicious trên Page/Catalog
    """
    findings = []

    # Benign OpenAction destinations - chỉ thay đổi cách hiển thị
    BENIGN_ACTIONS = ["/Fit", "/FitH", "/FitV", "/FitB", "/FitBH",
                      "/FitBV", "/FitR", "/XYZ"]

    try:
        for xref in range(1, doc.xref_length()):
            try:
                xref_str = doc.xref_object(xref)

                if "/OpenAction" in xref_str:
                    # Check if it's just a view destination (benign)
                    is_benign = any(ba in xref_str for ba in BENIGN_ACTIONS)
                    has_dangerous = any(
                        d in xref_str
                        for d in ["/JavaScript", "/JS", "/URI", "/Launch",
                                  "/GoToR", "/SubmitForm", "/ImportData"]
                    )
                    if has_dangerous:
                        findings.append(
                            f"xref {xref}: OpenAction nguy hiểm (có thể chạy code)")
                    elif not is_benign:
                        findings.append(
                            f"xref {xref}: OpenAction không xác định được loại")
                    # else: benign view action → skip

                if "/AA" in xref_str:
                    if "/Page" in xref_str or "/Catalog" in xref_str:
                        findings.append(f"xref {xref}: Additional Actions (AA)")
            except Exception:
                continue
    except Exception:
        pass

    if findings:
        return False, f"Phát hiện auto-actions: {'; '.join(findings[:3])}"
    return True, "Không có auto-actions nguy hiểm"


def check_no_embedded_files(doc: pymupdf.Document) -> tuple[bool, str]:
    """
    Check 8: Không có embedded files/attachments.
    Embedded files có thể chứa malware (exe, macro-enabled docs, etc.)
    """
    try:
        count = doc.embfile_count()
        if count > 0:
            names = [doc.embfile_info(i).get("name", "unknown") for i in range(count)]
            return False, f"Có {count} file đính kèm: {', '.join(names[:5])}"
    except Exception:
        pass

    return True, "Không có embedded files"


# ---------------------------------------------------------------------------
# Main scan function
# ---------------------------------------------------------------------------

def scan_pdf(filepath: str, config: dict) -> dict:
    """
    Chạy tất cả checks cho 1 file PDF.

    Returns:
        dict với keys: file, timestamp, overall_result, checks[]
        Mỗi check: {name, passed, detail}
    """
    result = {
        "file": os.path.basename(filepath),
        "filepath": os.path.abspath(filepath),
        "timestamp": datetime.now().isoformat(),
        "overall_result": "PASS",  # default, sẽ đổi nếu có FAIL
        "checks": [],
        "fail_reasons": [],
    }

    def add_check(name: str, passed: bool, detail: str):
        result["checks"].append({
            "name": name,
            "passed": passed,
            "detail": detail,
        })
        if not passed:
            result["overall_result"] = "FAIL"
            result["fail_reasons"].append(f"{name}: {detail}")

    # --- Checks không cần mở PDF ---
    passed, detail = check_file_exists(filepath)
    add_check("file_exists", passed, detail)
    if not passed:
        return result  # Không thể tiếp tục

    passed, detail = check_magic_bytes(filepath)
    add_check("magic_bytes", passed, detail)
    if not passed:
        return result  # Không phải PDF

    passed, detail = check_file_size(filepath, config["max_file_size_mb"])
    add_check("file_size", passed, detail)
    # Vẫn tiếp tục check (để report đầy đủ)

    # --- Checks cần mở PDF ---
    try:
        doc = pymupdf.open(filepath)
    except Exception as e:
        add_check("pdf_open", False, f"Không mở được PDF: {e}")
        return result

    add_check("pdf_open", True, "Mở file thành công")

    passed, detail = check_page_count(doc, config["max_pages"])
    add_check("page_count", passed, detail)

    if config["block_encrypted"]:
        passed, detail = check_not_encrypted(doc)
        add_check("not_encrypted", passed, detail)

    if config["block_javascript"]:
        passed, detail = check_no_javascript(doc)
        add_check("no_javascript", passed, detail)

    if config["block_auto_actions"]:
        passed, detail = check_no_auto_actions(doc)
        add_check("no_auto_actions", passed, detail)

    if config["block_embedded_files"]:
        passed, detail = check_no_embedded_files(doc)
        add_check("no_embedded_files", passed, detail)

    doc.close()
    return result


def scan_directory(dirpath: str, config: dict) -> list[dict]:
    """Scan tất cả .pdf files trong directory."""
    results = []
    pdf_files = sorted(Path(dirpath).rglob("*.pdf"))
    if not pdf_files:
        print(f"  ⚠ Không tìm thấy file PDF nào trong: {dirpath}")
        return results

    for pdf_path in pdf_files:
        result = scan_pdf(str(pdf_path), config)
        results.append(result)
    return results


def print_summary(results: list[dict]):
    """In tóm tắt kết quả ra console."""
    print("\n" + "=" * 65)
    print("GATE 1: PDF VALIDATION & MALWARE SCAN - KẾT QUẢ")
    print("=" * 65)

    pass_count = sum(1 for r in results if r["overall_result"] == "PASS")
    fail_count = len(results) - pass_count

    for r in results:
        status = "✅ PASS" if r["overall_result"] == "PASS" else "❌ FAIL"
        print(f"\n  {status}  {r['file']}")
        if r["fail_reasons"]:
            for reason in r["fail_reasons"]:
                print(f"         → {reason}")

    print(f"\n{'─' * 65}")
    print(f"  Tổng: {len(results)} file | ✅ PASS: {pass_count} | ❌ FAIL: {fail_count}")
    print("=" * 65)


def save_log(results: list[dict], log_dir: str):
    """Lưu kết quả scan ra file JSON."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gate1_scan_{timestamp}.json")

    log_data = {
        "scan_type": "gate1_pdf_validation",
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "passed": sum(1 for r in results if r["overall_result"] == "PASS"),
        "failed": sum(1 for r in results if r["overall_result"] == "FAIL"),
        "results": results,
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Log saved: {log_file}")
    return log_file


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python -I gate1_pdf_validator.py <file_or_directory> [--config CONFIG]")
        print("\nExamples:")
        print("  python -I gate1_pdf_validator.py test_data/clean/")
        print("  python -I gate1_pdf_validator.py test_data/dirty/dirty_oversized_25pages.pdf")
        print("  python -I gate1_pdf_validator.py test_data/ --config configs/gate1_config.json")
        sys.exit(1)

    target = sys.argv[1]

    # Parse --config
    config_path = None
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        if idx + 1 < len(sys.argv):
            config_path = sys.argv[idx + 1]

    config = load_config(config_path)

    print(f"\n🔍 Gate 1: PDF Validation & Malware Scan")
    print(f"   Config: max {config['max_file_size_mb']}MB, max {config['max_pages']} pages")
    print(f"   Target: {target}")

    # Scan
    if os.path.isfile(target):
        results = [scan_pdf(target, config)]
    elif os.path.isdir(target):
        results = scan_directory(target, config)
    else:
        print(f"ERROR: Không tìm thấy: {target}")
        sys.exit(1)

    if not results:
        print("Không có file nào để scan.")
        sys.exit(0)

    # Output
    print_summary(results)

    # Save log - tìm logs/ directory relative to script hoặc project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # security_scripts/
    log_dir = os.path.join(project_dir, "logs")
    save_log(results, log_dir)


if __name__ == "__main__":
    main()
