---
name: epc-business-analysis-from-filesystem
description: Analyze EPC (Engineering, Procurement, Construction) company competitiveness and project management optimization based on filesystem project data. Scans project directories, categorizes projects, extracts key metrics, and generates strategic recommendations.
tags: [epc, construction, project-analysis, business-intelligence, filesystem-scan]
created: 2026-04-17
updated: 2026-04-17
version: 1.0
---

# EPC Business Analysis from Filesystem

This skill provides a comprehensive framework to analyze EPC (Engineering, Procurement, Construction) companies by scanning their project directories. It extracts business intelligence from file structures, categorizes projects, identifies core competencies, and generates strategic optimization recommendations.

## When to Use

Use this skill when:
- Analyzing an EPC/construction company's business profile without access to internal databases
- Need to understand company capabilities based on actual project portfolio
- Preparing strategic recommendations for EPC project management optimization
- Assessing core competitiveness from filesystem evidence
- Creating data-driven business analysis with limited structured data

## Prerequisites

- Python 3.7+
- Access to company project directories
- Basic file permissions to scan directories

## Core Components

### 1. Project Scanner (`epc_project_scanner.py`)
The main script that scans project directories, categorizes projects, and generates analysis reports.

### 2. Analysis Framework
- **Project Categorization**: Classifies projects into EPC-relevant categories (design, construction, safety, government, etc.)
- **Competency Assessment**: Evaluates 6 core EPC competencies from project evidence
- **File Analysis**: Extracts intelligence from file types and structures
- **Strategic Recommendations**: Generates optimization suggestions based on findings

## Usage

### Basic Usage

```bash
# Run the scanner on a project directory
python epc_project_scanner.py

# Or specify custom path
python epc_project_scanner.py --path "/path/to/projects"
```

### Output Files
The script generates three key outputs:
1. `epc_projects_analysis.json` - Complete JSON report with all data
2. `epc_projects_list.csv` - CSV listing of all projects with metadata
3. `epc_analysis_summary.txt` - Human-readable summary report

### Integration with Local LLM

```python
# Use the analysis data as context for LLM recommendations
import json

with open('epc_projects_analysis.json', 'r') as f:
    analysis = json.load(f)

prompt = f"""
Based on this EPC company analysis:
- Total projects: {analysis['total_projects']}
- Project categories: {analysis['projects_by_category']}
- File types: {analysis['file_types_distribution']}

Generate strategic recommendations for EPC project management optimization.
"""
```

## Analysis Logic

### Project Categorization
Projects are categorized based on name patterns into EPC-relevant categories:

```python
categories = {
    '资质相关': ['资质', '资格', 'certif'],
    '设计项目': ['设计', '规划', 'design'],
    '施工项目': ['施工', '建设', 'construct', '工程'],
    '安全鉴定': ['安全', '鉴定', '检测', 'safety'],
    '政府项目': ['住建局', '政府', '军队', '采购', '文旅局', '乡村局'],
    '产业项目': ['产业', '铝业', '面粉厂', '冷链', '物流'],
    '文旅项目': ['文旅', '旅游', '水上世界', '写意'],
    '新能源': ['风电', '能源', '新能源'],
    '农业项目': ['苹果', '粮油', '农业'],
    '民生项目': ['卫生院', '饮水', '水库', '住房'],
    '商业项目': ['台球', '俱乐部', '经营', '代运营', '改造'],
    '合作项目': ['合作', '合伙', 'cooperat']
}
```

### Core Competency Assessment
The script evaluates 6 key EPC competencies:

1. **全产业链覆盖** (Full Industry Chain Coverage): Checks for both design and construction projects
2. **跨行业能力** (Cross-Industry Capability): Assesses diversity across project categories
3. **政府项目经验** (Government Project Experience): Counts government-related projects
4. **专业技术服务** (Professional Technical Services): Evaluates safety/certification projects
5. **风险管理能力** (Risk Management Capability): Assesses safety assessment projects
6. **区域深耕优势** (Regional Deep Cultivation Advantage): Analyzes regional project distribution

### File Intelligence
- **PDF documents**: Technical specifications, reports, standards
- **DWG files**: Design drawings and CAD work
- **DOC/DOCX**: Contracts, agreements, project documentation
- **XLS/XLSX**: Cost estimates, schedules, budgets
- **JPG/PNG**: Project photos, site images, visual documentation

## Strategic Recommendation Framework

### 1. Digital Transformation Recommendations
Based on file type analysis:
- High PDF count → Digital document management system
- DWG files present → BIM adoption strategy
- Limited digital formats → Digitization roadmap

### 2. EPC Process Optimization
Based on project mix:
- Design+Construction projects → EPC integration enhancement
- Safety projects → Risk management process improvement
- Government projects → Public sector EPC strategy

### 3. Market Development
Based on project categories:
- Emerging sectors (新能源, 文旅) → Market expansion focus
- Traditional sectors → Efficiency improvement
- Regional projects → Local market deepening

## Case Study:甘肃东盛建筑设计有限公司

### Analysis Results
- **Total projects**: 47
- **Key categories**: 资质相关 (3), 设计项目 (2), 施工项目 (3), 安全鉴定 (3), 政府项目 (4)
- **File types**: 666 PDFs, 85 DWG, 124 DOC, 88 DOCX, 33 XLSX
- **Core competencies**: 全产业链覆盖✅, 跨行业能力✅, 区域深耕优势✅

### Generated Recommendations
1. **Digital upgrade strategy**: BIM platform implementation
2. **EPC standardization**: Based on 2886MB of资质办理 standards
3. **Talent development**: EPC复合型人才培养
4. **Supply chain optimization**: 10% cost reduction target
5. **Risk management enhancement**: Safety assessment process improvement
6. **Market expansion**: Government EPC projects focus

## Pitfalls and Solutions

### Pitfall 1: Binary File Access
**Issue**: Cannot read .doc/.dwg files directly
**Solution**: Use file metadata (type, size, count) rather than content

### Pitfall 2: Incomplete Categorization
**Issue**: Some projects don't match keyword patterns
**Solution**: Manual review of "其他项目" category, adjust keywords

### Pitfall 3: Large Directory Trees
**Issue**: Scanning 271+ directories can be slow
**Solution**: Implement progress tracking, parallel processing for large scans

### Pitfall 4: Permission Issues
**Issue**: Cannot access some directories
**Solution**: Graceful error handling, skip inaccessible paths

## Advanced Features

### Custom Categorization
Modify the `categorize_project()` method to add industry-specific keywords:

```python
def categorize_project(self, project_name):
    # Add custom industry keywords
    custom_keywords = {
        '工业项目': ['factory', 'plant', 'manufacturing'],
        '医疗项目': ['hospital', 'clinic', 'medical'],
        '教育项目': ['school', 'university', 'education']
    }
    # Merge with existing categories
```

### Integration with Local LLM
Use the analysis data to generate targeted recommendations:

```bash
# Feed analysis to local LLM
python epc_project_scanner.py --llm-prompt "Generate 2026 optimization plan"
```

### Export Formats
Support multiple output formats:
- JSON for programmatic use
- CSV for spreadsheet analysis
- Markdown for reports
- PDF for presentations

## Validation Checklist

After running the analysis, verify:

- [ ] All expected project directories were scanned
- [ ] Project categorization makes business sense
- [ ] File type distribution reflects actual work
- [ ] Competency assessment matches known capabilities
- [ ] Recommendations are actionable and specific

## Related Skills

- `business-analysis-with-limited-data`: General business analysis with sparse data
- `codebase-inspection`: Code analysis patterns that inspired this approach
- `wechat-official-account-matrix-strategy`: Business strategy development

## Maintenance Notes

- Update categorization keywords as company business evolves
- Add support for new file types as technology changes
- Refine competency assessment thresholds based on industry benchmarks
- Consider adding machine learning for smarter categorization

---

**Created from**: Analysis of甘肃东盛建筑设计有限公司 with 47 project directories
**Key insight**: Filesystem structure reveals business capabilities more accurately than self-reported data
**Value proposition**: Low-effort, high-insight business intelligence for EPC/construction companies