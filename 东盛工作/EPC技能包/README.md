# EPC Construction Skills (建筑工程 EPC 技能包)

> Field-tested Agent Skills for EPC (Engineering-Procurement-Construction) building projects in China. These skills encode the hard-won procedures of a 16-year construction veteran: how to package bid qualification documents, settle cost overruns, fight back against audit deductions, run weekly cost-profit cockpits, and write government approval documents.

一套经过真实项目验证的 EPC 建筑工程 Agent 技能包。把老师傅的实战流程结构化:投标报名资料、结算超支处理、审计核减应对、成本利润驾驶舱、报建公文写作。

## Skills (5)

| Skill | What it does |
|-------|--------------|
| [epc-bid-packaging](epc-bid-packaging/) | Read recruitment announcements, position company strengths, design tiered pricing, produce a complete qualification-packaging Word doc with commitment letters. 公建/棚改/装修报名资料编制 |
| [epc-settlement](epc-settlement/) | Read contracts & BOQs, compare overruns, classify root causes, produce variation/supplementary-agreement/negotiation plans and a formal settlement book. EPC 结算超支处理 |
| [epc-audit-defense](epc-audit-defense/) | Build a claim-vs-audit comparison table, recognize deduction tactics, write an objection letter, and run a negotiation decision tree with evidence checklists. 审计核减应对 |
| [epc-cost-control](epc-cost-control/) | Decompose budget → target cost → target profit, track the four cost levers (materials/labor/measures/overhead), and run a weekly Excel cockpit with early warnings. EPC 成本利润管控 |
| [epc-approval-docs](epc-approval-docs/) | Draft formal Chinese government approval documents (planning permits, filing applications) with the correct 红头文件 conventions. 报建审批公文 |

## Requirements

- Works with any skills-compatible AI agent (Claude Code, Codex, Cursor, Hermes, ...)
- SKILL.md files are written in Chinese (with English keywords) — the target users are Chinese construction professionals; agents read Chinese fine
- Python 3 + python-docx + openpyxl for document/Excel generation (optional, only for document output steps)

## Install

Copy any skill folder into your agent's skills directory, e.g.:

```bash
# Claude Code
cp -r epc-bid-packaging ~/.claude/skills/

# Hermes
cp -r epc-bid-packaging ~/.hermes/skills/
```

Or reference the SKILL.md in a project with:

```bash
mkdir -p .claude/skills && cp -r epc-settlement .claude/skills/
```

## License

MIT — free to use, adapt, and resell. No warranty; verify all figures against local regulations and contracts.

## Provenance

These procedures were distilled from real projects in Gansu province, China (2024–2026): government renovation recruitment with innovative settlement modes, EPC factory construction with target-profit control, and settlement-audit disputes. All company names, project names, people, and exact amounts have been removed; the methodology is generic and transferable.

---

*Agent Skills standard: https://agentskills.io · Marketplace index: https://skillsmp.com*
