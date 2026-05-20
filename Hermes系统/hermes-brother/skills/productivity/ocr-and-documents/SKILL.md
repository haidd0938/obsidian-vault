---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Engineering Budget / 广联达 PDF Table Extraction

Special case: **工程预算PDF（广联达/造价软件导出）**。这类PDF的表格特点是：

- 多层合并表头（例如：单价|合价→人工费|材料费|主材费|机械费等子列）
- 分类标题行穿插在数据行之间（如"塑木围墙130米"作为段落标题，下一行为具体定额条目）
- 金额数字需要**原样保留**，不能重新计算（用户会核对原始PDF）

### Method: pymupdf.find_tables() + Manual Header Parsing

**DO NOT** use `page.get_text()` for budget PDFs — it flattens the table layout and loses column-position context, producing wrong totals. Always use table extraction:

```python
import pymupdf

doc = pymupdf.open("budget.pdf")
for page in doc:
    tables = page.find_tables()           # ← key method
    for tab in tables.tables:
        rows = tab.extract()              # ← list of lists, None for empty cells
        # rows[0]: title row ("工程计价表")
        # rows[1]: engineering name + page info
        # rows[2-4]: multi-level merged headers
        # rows[5+]: actual data rows
```

### Critical Steps for Budget PDFs

1. **Identify table type** — check `rows[0]` for "工程计价表" vs "费用计算表" vs "人材机汇总表"
2. **Parse section title rows** — rows where `code==""` and `name` has 米/平方米/座/台/个 are **category headers**, not data rows. Skip them or use as section markers.
3. **Multi-level headers** — rows[2-4] contain merged header cells. Column indices shift. Always reference by position relative to `rows[2]` (which usually has: 定额编号, 分项工程名称, 单位, 数量, 单价, 合价).
4. **Verify totals** — after extraction, cross-check the 合价 column on the last data page against the cover page's 工程造价.

### Budget PDF Page Map (typical structure)

| Pages | Content |
|-------|---------|
| 1 | Cover (工程造价) |
| 2-3 | 编制说明 |
| 4 | 单项工程汇总表 |
| 5 | 费用计算表 |
| 6-10 | 工程计价表 (detail line items, 5 pages total) |
| 11 | 费率措施费汇总表 |
| 12+ | 人材机价差表, 人材机汇总表 |

### Exporting to Excel

```python
import openpyxl
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill

wb = openpyxl.Workbook()
ws = wb.active

# Write headers
headers = ['序号', '定额编号', '分项工程名称', '单位', '数量', '单价(元)', '合价(元)']
for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    # style it...

# Write data rows
for i, item in enumerate(items, 1):
    ws.cell(row=i+1, column=1, value=i)
    ws.cell(row=i+1, column=2, value=item['code'])
    ws.cell(row=i+1, column=3, value=item['name'])
    # ...

# Use number_format for financial columns:
cell.number_format = '#,##0.00'
```

### Pitfalls

- **Never re-calculate totals** — the user will compare against the PDF. Extract the 合价 column as-is.
- **Merged header cells** produce `None` in adjacent positions — check with `cell is not None`, not truthiness.
- **分类标题行** look like data but have no 定额编号 — they're section markers. Handle separately.
- **合计行** appears on the last page of each section — it's part of the table, extract it as a bold row.
- Different 分部 (e.g. 户型1 vs 标准间, 建筑与装饰 vs 拆除) have separate 费用计算表 pages — scan the entire PDF for multiple "费用计算表" occurrences.

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
