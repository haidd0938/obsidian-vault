# Complex DOCX Conversion Notes (formerly in print-layout-kit)

## Header indentation scaling
After horizontal→vertical, header `w:ind w:left` doesn't auto-scale.
Fix: `new_left = int(old_left * 16783 / 23758)`, remove `w:spacing` negative tracking.

## 98-section DOCX edge case
Sections over 50000 twips (~55cm) should stay landscape. Only convert body sections.

## Ultra-large pages
A2/A1 folding drawings: mark as "keep landscape", convert only body sections.

## Verification
After conversion, randomly sample 5-10 sections and compare:
- Header indentation
- Column count
- Page dimensions
