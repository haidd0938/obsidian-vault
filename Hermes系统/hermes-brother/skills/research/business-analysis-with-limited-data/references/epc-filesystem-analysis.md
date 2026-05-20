# EPC Business Analysis from Filesystem

A concrete implementation of business analysis for EPC companies, using filesystem scans of project directories to generate business intelligence.

## When to Use
- Analyzing an EPC/construction company's business profile
- Need to understand company capabilities based on actual project portfolio
- Preparing strategic recommendations for EPC project management optimization
- Creating data-driven business analysis with limited structured data

## Core Script

The `epc_project_scanner.py` script (see `templates/epc_project_scanner.py`) scans project directories:

```bash
python epc_project_scanner.py
# Or specify path
python epc_project_scanner.py --path "/path/to/projects"
```

Outputs: `epc_projects_analysis.json`, `epc_projects_list.csv`, `epc_analysis_summary.txt`

## Project Categorization

Projects categorized by name keywords:
- 资质相关: 资质, 资格, certif
- 设计项目: 设计, 规划, design
- 施工项目: 施工, 建设, construct, 工程
- 安全鉴定: 安全, 鉴定, 检测, safety
- 政府项目: 住建局, 政府, 军队, 采购
- 新能源, 农业, 文旅, 民生, 商业

## Competency Assessment (6 Dimensions)
1. **全产业链覆盖** — design + construction projects presence
2. **跨行业能力** — diversity across categories
3. **政府项目经验** — government project count
4. **专业技术服务** — safety/certification projects
5. **风险管理能力** — safety assessment projects
6. **区域深耕优势** — regional distribution

## Strategic Recommendation Generation
- Digital transformation (BIM, document management)
- EPC process optimization (integration enhancement)
- Market development (emerging sectors focus)
- Supply chain optimization (10% cost reduction target)
- Risk management improvement

## Pitfalls
- Binary files (.doc/.dwg) can't be content-scanned — use metadata
- Incomplete categorization for projects without matching keywords
- Large directory trees can be slow — use parallel processing
- Permission issues require graceful error handling

## Case Study: 甘肃东盛建筑设计有限公司
**47 projects** across 12 categories, 666 PDFs, 85 DWG, 124 DOC, 88 DOCX, 33 XLSX.
Core competencies: 全产业链覆盖✅, 跨行业能力✅, 区域深耕优势✅
