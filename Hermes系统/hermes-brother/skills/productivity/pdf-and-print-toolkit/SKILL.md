---
name: pdf-and-print-toolkit
description: UMBRELLA — PDF editing (文字替换/水印/合并/加密/提取) + print layout conversion (横→竖A4, PDF→Word screenshot render). Covers pdf-tool (PyMuPDF), plk (横→竖PDF/DOCX), and plk-pro (PDF→竖版Word via screenshot).
category: productivity
tags: [pdf, print, layout, conversion, editing, watermark, merge, split]
related_skills: []
---

# PDF and Print Toolkit

Three complementary CLI tools for PDF processing and print layout conversion on macOS.

## Tool Overview

| Tool | Command | Purpose | Technology |
|------|---------|---------|------------|
| **pdf-tool** | `pdf-tool` | General PDF editing (17 subcommands) | PyMuPDF (fitz) |
| **plk** | `plk` | PDF/DOCX横→竖版排版 | PyMuPDF + python-docx |
| **plk-pro** | `plk-pro` | PDF→A4竖版Word via screenshot | PyMuPDF + python-docx + Pillow |

---

## Section A: pdf-tool — General PDF Editing

Installed at `~/.local/bin/pdf-tool`. Based on PyMuPDF (fitz), 17 subcommands, full Chinese support.

### Installation
```bash
pip3 install PyMuPDF
```

### All Commands

| Command | Function | Example |
|---------|----------|---------|
| **info** | View metadata + per-page details | `pdf-tool info 报告.pdf` |
| **edit** | Natural language text replacement | `pdf-tool edit 合同.pdf 1 "把'甲方'改成'乙方'"` |
| **replace-text** | Precise batch text replacement | `pdf-tool replace-text 报告.pdf 1 旧字 新字` |
| **replace-img** | Replace images | `pdf-tool replace-img 报告.pdf 2 新图.jpg` |
| **watermark** | Batch add watermark (45° diagonal) | `pdf-tool watermark 合同.pdf "机密" -o 合同_水印.pdf` |
| **merge** | Merge multiple PDFs | `pdf-tool merge a.pdf b.pdf -o 合并.pdf` |
| **split** | Split by page range | `pdf-tool split 报告.pdf 1-3,5,7-9` |
| **rotate** | Rotate pages (90/180/270°) | `pdf-tool rotate 报告.pdf 2 90` |
| **compress** | Compress (garbage+deflate) | `pdf-tool compress 报告.pdf` |
| **encrypt / decrypt** | AES-256 | `pdf-tool encrypt 报告.pdf 123456` |
| **extract-text** | Extract text to txt | `pdf-tool extract-text 报告.pdf` |
| **extract-img** | Extract images to directory | `pdf-tool extract-img 报告.pdf` |
| **add-page / delete-page** | Add/delete pages | `pdf-tool add-page 主.pdf 插入页.pdf 3` |
| **crop** | Crop pages | `pdf-tool crop 报告.pdf 1 "50,50,400,500"` |
| **scale** | Scale PDF by percentage | `pdf-tool scale 报告.pdf 80` |

### Limitations
- `edit` (natural language) is limited — PyMuPDF uses mask+reinsert, suitable only for simple replacements
- `replace-img` inserts at top-left, not exact position
- `compress` uses garbage=4+deflate, limited on already-compressed PDFs

---

## Section B: plk — Print Layout Kit

One-click convert horizontal PDF/DOCX to vertical A4 layout. Solves "engineering drawings/wide tables/slides in vertical print" pain point.

### Installation
```bash
pip3 install pymupdf python-docx reportlab
# plk is at /usr/local/bin/
```

### Usage
```bash
# Check page orientation
plk --check 施工方案.pdf
# → 15页中有 3 页横版

# Convert PDF (horizontal→vertical)
plk 施工方案.pdf
# → 施工方案_竖版.pdf

# Convert Word document
plk 项目建议书.docx
# → 项目建议书_竖版.docx

# Batch convert
plk ~/Desktop/图纸/*.pdf --outdir ~/Desktop/竖版图纸/

# Specify output
plk 横版设计图.pdf 最终打印版.pdf -f
```

### Technical Approach
**PDF:** PyMuPDF renders each page onto a new A4 vertical page, scaled proportionally, centered with 5mm margins.
**DOCX:** Changes section orientation, scales wide images to 15.5cm, converts multi-column to 1-column.

### Known Issues
- Header indentation doesn't auto-scale after orientation change — must proportionally scale `w:ind w:left`
- Ultra-large drawing pages (55.9×39.5cm) should keep landscape — only convert body sections
- 98-section DOCX documents: sections with width > 50000 twips (~55cm) should stay landscape
- Images in large drawings may overflow after conversion

---

## Section C: plk-pro — Print Layout Pro (Screenshot Strategy)

Converts horizontal PDF to A4 vertical Word document using full-page screenshot rendering. Preserves all content (text, images, tables) in-place.

### Installation
```bash
pip install PyMuPDF python-docx Pillow
# plk-pro is at /usr/local/bin/plk-pro
```

### Usage
```bash
plk-pro input.pdf -o output.docx
plk-pro input.pdf -o output.docx --dpi 200
plk-pro --help
```

### Strategy per Page Type
| Page Type | Strategy |
|-----------|----------|
| Vertical | Scale to A4 width |
| Normal landscape (width < 1500pt) | Scale to A4 width |
| Ultra-wide (width >= 1500pt) | **Slice** into A4-width segments for readability |

### Limitations
- Ultra-wide pages (e.g., 3370pt folded drawings) → many segments (68 → ~258 A4 pages)
- Text is non-selectable (embedded as images)
- File size large (50-80MB at 200dpi for 68-page PDF)
- PDF input only

### Evolution
| Ver | Approach | Problem |
|-----|----------|---------|
| v1 | Extract text+images | Garbled, format lost |
| v2 | Full-page render + center-crop | Content cut in half |
| v3 | Full-page no-crop | Ultra-wide text too small |
| v4 | **Stratified + ultra-wide slicing** | ✅ Usable |

---

## Section D: Workflow Selection Guide

| Your Need | Use | Why |
|-----------|-----|-----|
| Edit PDF text/watermark/merge/split | `pdf-tool` | 17 subcommands for all editing needs |
| Print a horizontal PDF vertically | `plk` | One-click, preserves vector content |
| Print to editable Word with layout | `plk-pro` | Screenshot strategy, everything in-place |
| Batch process many PDFs | `plk` or `plk-pro` | Both support glob patterns |
| Super-wide engineering drawings | `plk-pro` auto-slice | Handles folding drawing segments |

## Pitfalls
1. **Mac security**: `python3 -c` can't execute directly. Use `python3 /path/to/script.py` instead.
2. **Font paths**: plk uses macOS PingFang font path — works on macOS only.
3. **Security alerts**: tirith may flag write operations — approve when prompted.
4. **Huge output file size**: plk-pro at 200dpi can produce 50-80MB files. Lower DPI if size is a concern.
5. **Large drawings in DOCX**: Keep A2/A1+ pages landscape, don't auto-convert them.
