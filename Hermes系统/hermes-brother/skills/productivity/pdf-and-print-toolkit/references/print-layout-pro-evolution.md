# plk-pro Evolution Notes

## Version History
| Ver | Approach | Problem |
|-----|----------|---------|
| v1 | Extract text+images re-layout | Garbled, format lost |
| v2 | Full-page render + center-crop | Content cut in half |
| v3 | Full-page no-crop | Ultra-wide text too small |
| v4 | Stratified strategy + ultra-wide segment slicing | ✅ Usable |

## Key Parameters
| Param | Default | Description |
|-------|---------|-------------|
| DPI | 150 | Higher = clearer but larger files |
| A4 width | 210mm | Standard |
| A4 height | 297mm | Standard |
| Margin | 10mm | Page padding |
| Ultra-wide threshold | 1500pt | Pages wider than this get sliced |
