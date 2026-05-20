# Offline Task Farm: Migrating Cron Jobs Off the MacBook

> This user's MacBook is the single point of failure — close the lid and all 10 cron jobs stop.
> Solution: migrate pure-computation tasks to a local PC cluster (6x i5/8G/500G Win10).
> Hermes+AI tasks stay on the MacBook (or migrate to another Hermes instance later).

## Hardware Profile (2026-05-08)

- 6x desktop PCs at 单位 (office)
- CPU: Intel i5 (generation unspecified)
- RAM: ~8GB each
- Storage: ~500GB HDD each
- OS: Windows 10
- Network: office LAN (same subnet)

## Task Classification Matrix

| Category | Requires AI? | CPU bound? | RAM needed | Migrate? |
|----------|-------------|-----------|------------|----------|
| Stock analysis (Python scripts) | No | Low-Medium | 1-2GB | ✅ Yes |
| Web scraping (crawlers) | No | Low | 512MB-1GB | ✅ Yes |
| FFmpeg video rendering | No | High (multi-core) | 2-4GB | ✅ Yes |
| GitHub trending monitoring | No | Low | <512MB | ✅ Yes |
| API health/balance checks | No | Low | <256MB | ✅ Yes |
| Weekly project summaries | Yes | — | — | ❌ No (needs LLM) |
| EPC daily video (content gen) | Yes | — | — | ❌ No (needs LLM) |
| Xinqiuhui daily video (content gen) | Yes | — | — | ❌ No (needs LLM) |

## Migration Priority

**Tier 1 (5 min each, big impact):**
1. Stock daily review → dedicated Windows PC (Python + pip only)
2. Gansu project crawler → another PC
3. GitHub trending monitor → any PC
4. DeepSeek balance check → any PC

**Tier 2 (30 min each, medium effort):**
5. Stock morning report + alerts → same PC as stock daily review
6. Video rendering (FFmpeg batch) → 2 dedicated PCs, run overnight

**Tier 3 (blocked):**
7. EPC daily short video → needs Hermes/AI skills
8. Xinqiuhui daily video → needs Hermes/AI skills

## Architecture

```
Office LAN (192.168.x.x)
│
├─ PC#1 [NAS主控] → Shared folder (SMB) for all outputs
│                   Runs: nothing automated, just storage
│
├─ PC#2 [爬虫工]  → Gansu crawler (11:00) + GitHub trending (22:00)
│
├─ PC#3 [股票工]  → Stock morning report (7:30) + daily review (15:30)
│                   Python scripts from stock-robot/
│
├─ PC#4 [视频工1] → FFmpeg rendering (overnight batch)
│
├─ PC#5 [视频工2] → FFmpeg rendering (overnight batch)
│
└─ PC#6 [备用]    → Falls on any failed task
```

## Communication Back to User

Since these PCs don't have Hermes/Telegram:
1. Tasks write results to the shared folder (PC#1)
2. The MacBook's Hermes cron jobs read from the shared folder via SMB mount
3. Or: write results to a file, and the existing Telegram integration on MacBook picks them up

## Cost

- **Zero upfront** — all hardware exists
- **Electricity**: ~100-150W per PC × 6 × 8h/day ≈ 5-7 kWh/day ≈ ¥3-4/day at residential rates
