---
name: epc-settlement
description: Handle EPC construction settlement cost overruns — read the contract, compare BOQ lines, classify root causes, and produce a plan (variation / supplementary agreement / negotiation) plus a formal settlement book in Word. EPC 结算超支处理。
---

# EPC Settlement & Cost Overrun Handling (结算超支处理)

Use this skill when construction is finished but the settlement amount exceeds the contract: analyze the contract vs actual settlement difference, and produce a handling plan (variation sign-off / supplementary agreement / negotiation) and a formal settlement book.

## When to Use

- 用户发来EPC施工合同+结算清单,说明施工结束了但结算额超了
- 需要分析原合同vs实际结算的差异
- 需要出办理方案(签证/补充协议/谈判策略)
- EPC项目合同管理、结算对账、变更签证

## Prerequisites

- 合同文件(.docx/.doc/PDF)、结算清单(.xlsx)、收支流水(如有)
- Python 3 + python-docx + openpyxl
- 用户上传的文件可能先落在临时上传目录,先复制到桌面再读取

## Core Principles

1. **先读合同,再读清单** — 合同是法律依据,清单是事实依据,缺一不可
2. **分三层分析** — 原合同金额 → 实际成本(材料+劳务)→ 已收/未付资金流
3. **超支找根因** — 新增工程内容?单价变化?工程量偏差?范围外追加?
4. **方案分三条路** — 正规变更签证(最好)→ 补充协议(次好)→ 谈判让利(最后一招)
5. **已付款流水必须拉通** — 甲方付了多少、供应商付了多少、资金缺口多少

## Procedure

### Step 1: 读取合同

```bash
pip3 install python-docx openpyxl
python3 << 'PYEOF'
from docx import Document
import sys
doc = Document(sys.argv[1])
for para in doc.paragraphs:
    print(para.text)
for i, table in enumerate(doc.tables):
    print(f"\n--- 表格 {i+1} ---")
    for row in table.rows:
        print(" | ".join(cell.text.strip() for cell in row.cells))
PYEOF '合同文件.docx'
```

关键提取项:
- 合同总价(大小写两种)
- 各分项单价/总价
- 付款节点和比例
- 工程内容范围
- 变更/签证条款(有没有明确约定)
- 争议解决条款

### Step 2: 读取结算清单

```bash
python3 << 'PYEOF'
import openpyxl, sys
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)  # data_only=True 必须!
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f"\n=== Sheet: {sheet_name} ===")
    for row in ws.iter_rows(values_only=True):
        vals = [str(v) if v is not None else '' for v in row]
        if any(v.strip() for v in vals):
            print('\t'.join(vals))
PYEOF '结算清单.xlsx'
```

⚠️ 必须用 `data_only=True`,否则读到的是公式字符串("=F26+F47")而不是计算值。

### Step 3: 收支汇总分析

- **资金流入**:甲方预付款 + 中间付款
- **资金流出**:材料供应商 + 劳务分包 + 临时设施等
- **资金缺口** = 总成本 - 已收甲方款
- **甲方尾款** = 结算总价 - 已付甲方预付款

### Step 4: 超支分析(三栏对比表)

| 分项 | 原合同金额 | 实际清单金额 | 差额 |
|------|-----------|------------|------|
| ① 主体工程 | xx | xx | +xx |
| ② 新增项目 | - | xx | +xx |
| ③ 临时设施 | xx | xx | +xx |
| **合计** | **签约价** | **结算价** | **超支额** |

超支根因分类:
- **设计变更** — 施工中甲方要求增加了内容
- **新增项目** — 原合同范围之外的附加工作
- **工程量偏差** — 实际量大于估算量
- **单价变化** — 材料涨价/人工上涨
- **范围外追加** — 甲方口头承诺未写入合同

### Step 5: 出办理方案

**方案A:补工程变更签证单(推荐)**
- 变更事由说明、新增工程量明细(附计算式)、甲乙双方签字确认
- 适用:合同有变更条款或现场有甲方确认记录

**方案B:补签补充协议**
- 补充协议编号、签署日期、变更范围详细描述、变更金额及支付方式、原合同其他条款继续有效
- 适用:没有正式签证但双方认可新增事实

**方案C:谈判让利**
- 临时设施等弹性项目适当让步(如5,000-10,000元)
- 总价凑整给甲方"谈下来"的成就感
- 提出折中方案

### Step 6: 编制《工程结算书》(Word)

```
结算书结构:
├── 封面(项目信息+日期)
├── 一、结算说明(项目概况/原合同金额/变更增加金额/结算总价)
├── 二、结算明细表(分四部分:合同内已完成量/新增项目/场地工程/临时设施)
├── 三、结算汇总(含增减对比)
├── 四、付款情况(已付/应收尾款)
└── 五、附件(现场施工照片、材料采购凭证)
```

附件处理:如果用户说"含现场照片和采购凭证"但文件找不到——先全局搜索(Pictures/Documents/微信缓存),找不到就直接出正文+占位页("现场照片待补充"),不要卡住。

### Step 7(可选):《建设工程竣工报告》

结算书出完后甲方可能要求竣工报告(侧重质量评价和验收结论):
- 工程概况、工程内容及完成情况、工程验收情况、工程结算(引用结算书数据)、工程质量评定、附件清单
- 签字栏:建设+施工各一栏,无边框表格并排
- 质量评定结论不能空 — 甲方没签验收单时写"经建设单位现场查验,确认工程质量合格"

## 关键话术(与甲方谈判)

- 谈"新增内容按实结算": "合同包干价XX万,但新增的XX等都是合同范围外的内容,按实结算天经地义"
- 谈"甲方现场确认"依据: 合同条款如有"视施工情况现场确定""内容由甲方现场监督确认",就是法律武器
- 弹性让步: "临时设施部分弹性较大,如果甲方压价可以适当让步,其他新增项目据理力争"

## Pitfalls

1. **不要只看总价差额** — 分开看"合同内超支"和"合同外新增",谈判策略完全不同
2. **已收款≠已入账利润** — 甲方预付款可能已经全部花在材料上,资金链要算清
3. **合同没有变更条款时** — 找"甲方口头/现场确认"作为事实依据,微信记录/会议纪要都可以用
4. **欠供应商的钱是独立风险** — 即使甲方尾款没到,欠供应商的钱也要按时付
5. **结算书格式要专业** — 用 Word 出,不是 Excel 传过去
6. **读取上传文件先复制到桌面** — 临时上传目录用户找不到,必须用绝对路径输出到桌面
7. **xlsx 必须 data_only=True** — 否则读到公式字符串
8. **.doc 旧格式** — python-docx 报 PackageNotFoundError 时,用 olefile 二进制提取或让用户转成 .docx/PDF
9. **结算书可能有多个修订版本** — 确认用最新版,PDF 金额优先于旧的 docx

## Verification

- [ ] 合同已读(总价/分项/付款条件/变更条款)
- [ ] 结算清单已读(分项明细)
- [ ] 已收款/已付款流水已拉通
- [ ] 超支分析表已出
- [ ] 方案路径已明确(签证/补充协议/谈判)
- [ ] 甲方尾款金额已算清
- [ ] 结算书已输出(可选)
- [ ] 竣工报告已输出(如甲方要求)
