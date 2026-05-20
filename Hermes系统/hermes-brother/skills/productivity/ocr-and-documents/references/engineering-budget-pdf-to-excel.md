# 广联达工程预算PDF → Excel 转换方案

来源：成县栖月云居民宿装修项目（2026-05-08 session）

## 背景

老板有2个广联达软件导出的PDF预算文件，需要转成可编辑的Excel。
- 室外附属预算（20页PDF → 4个工作表）
- 预算书（77页PDF，含6个分部 → 4个工作表）

## 核心问题

第一次转换用 `page.get_text()` 纯文本提取，结果与PDF金额差别大。
**原因**：纯文本提取无法保留表格行列对齐关系，数字串行。

## 解决方案

用 `pymupdf.find_tables()` 从PDF中提取表格结构，然后按单元格位置对应提取。

### 关键代码模式

```python
import pymupdf

doc = pymupdf.open(pdf_path)
for page in doc:
    tables = page.find_tables()
    for tab in tables.tables:
        rows = tab.extract()
        # rows[0] = table title
        # rows[1] = engineering name + page info
        # rows[2-4] = multi-level merged headers  
        # rows[5+] = data rows
```

### 处理广联达计价表的核心逻辑

```python
for row in rows[5:]:  # 跳过表头
    code = str(row[0]).strip() if row[0] else ''
    name = str(row[1]).strip() if len(row)>1 and row[1] else ''
    unit = str(row[2]).strip() if len(row)>2 and row[2] else ''
    qty = str(row[3]).strip() if len(row)>3 and row[3] else ''
    price = str(row[4]).strip() if len(row)>4 and row[4] else ''
    total = str(row[5]).strip() if len(row)>5 and row[5] else ''
    
    if not code and not name:
        continue
    
    name_clean = name.replace('\n',' ').strip()
    
    # 分类标题行：无定额编号但有施工量单位的行
    # 如"塑木围墙130米"、"碎石停车位"等
    if code == '' and any(k in name_clean for k in ['米','㎡','平方米','座','台','个','项']):
        # 这是段落标题，不是明细行
        current_section = name_clean
        continue
    
    # 定额条目行
    items.append({
        'code': code,
        'name': name_clean,
        'unit': unit,
        'qty': qty,
        'price': price,
        'total': total,
        'section': current_section
    })
```

### 费用计算表提取

费用计算表的表格结构不同（8列 vs 15列），需要单独处理：

```python
for row in rows[2:]:
    seq = str(row[0]).strip() if row[0] else ''
    name = str(row[1]).strip() if len(row)>1 and row[1] else ''
    code = str(row[3]).strip() if len(row)>3 and row[3] else ''
    rate = str(row[4]).strip() if len(row)>4 and row[4] else ''
    formula = str(row[5]).strip() if len(row)>5 and row[5] else ''
    amt = str(row[7]).strip() if len(row)>7 and row[7] else ''
```

### 识别各分部工程

预算书可能包含多个分部（如户型1、户型2、标准间，每个含建筑与装饰+拆除）。
分部名称在表格的第1行或第2行，格式为 `工程名称:XXX`：

```python
for row in rows[:3]:
    for cell in row:
        if cell and '工程名称:' in str(cell):
            part_name = str(cell).replace('工程名称:','').replace('工程名称：','').strip()
```

## 分部费用数据（成县项目）

从PDF的费用计算表中逐一提取：

| 分部 | 工程造价 | 分部分项 | 人工费 | 材料费 |
|------|---------|---------|-------|-------|
| 户型1--建筑与装饰 | 226,130.83 | 174,742.50 | 28,106.73 | 146,202.31 |
| 户型1--拆除 | 2,137.59 | 1,048.94 | 946.77 | 0 |
| 户型2--建筑与装饰 | 193,359.21 | 145,580.19 | 27,025.28 | 118,115.11 |
| 户型2--拆除 | 2,311.61 | 1,109.71 | 1,049.40 | 0 |
| 标准间--建筑与装饰 | 562,086.01 | 439,266.42 | 65,489.80 | 372,727.88 |
| 标准间--拆除 | 909.18 | 462.55 | 385.66 | 0 |
| **室内合计** | **986,934.43** | — | — | — |
| 室外附属工程 | 1,681,937.59 | — | — | — |
| **两个项目总计** | **2,668,872.02** | — | — | — |

## 输出Excel结构

### 室外附属预算（4个工作表）
1. **工程计价表** — 77行明细，含分类段落标题
2. **造价汇总** — 总造价 ¥1,681,937.59 仪表板
3. **费用计算表** — 分部分项→措施→管理→利润→价差→规费→税金→工程造价
4. **措施费明细** — 环保/安全/临时设施等10项

### 预算书（4个工作表）
1. **总说明及汇总** — 6个分部汇总 + 编制说明
2. **分部分项计价表** — 234项详细清单，分部标题隔开（黄色底色）
3. **费用计算汇总** — 各分部费用构成横向对比表
4. **费用计算明细** — 6个分部各自的费用计算表

## 注意事项（从用户反馈中学到的）

1. ❌ **第一次用纯文本提取导致金额错误** → 必须用 `find_tables()`
2. ✅ 所有金额直接从PDF提取，不做任何四舍五入或重新计算
3. ✅ 合计行从PDF原文提取，不是自己加总
4. ✅ Excel金额列设置 `#,##0.00` 格式，便于肉眼核对
