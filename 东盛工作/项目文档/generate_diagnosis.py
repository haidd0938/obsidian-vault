#!/usr/bin/env python3
"""
成县栖月云居民宿 - 户型诊断信息图生成器
融合虎小象「禅院宅居断事师」风格 + 实际户型图标注
A4竖版可打印
"""

import base64
from PIL import Image
import io

def resize_and_encode(path, max_width=1600):
    """Resize image to max_width and return base64 string"""
    img = Image.open(path)
    w, h = img.size
    if w > max_width:
        ratio = max_width / w
        new_w = max_width
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

print("Encoding images...")
floor1_b64 = resize_and_encode("/Users/mac/Desktop/first_floor_layout.png", 1600)
floor2_b64 = resize_and_encode("/Users/mac/Desktop/second_floor_layout.png", 1600)
print(f"Floor 1: {len(floor1_b64)} chars")
print(f"Floor 2: {len(floor2_b64)} chars")

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>栖月云居 · 户型诊断报告</title>
<style>
@page {{
  size: A4 portrait;
  margin: 12mm 15mm;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  background: #f8f6f2;
  color: #2c2c2c;
  padding: 20px;
}}

.page {{
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto 30px auto;
  background: #faf8f4;
  padding: 12mm 15mm;
  box-shadow: 0 2px 20px rgba(0,0,0,0.06);
  border-radius: 4px;
}}

/* ===== 封面区 ===== */
.cover {{
  position: relative;
  margin-bottom: 20mm;
  padding-bottom: 8mm;
  border-bottom: 2px solid #d4c9b0;
}}
.cover-badge {{
  display: inline-block;
  background: #c8513a;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: 3px;
  letter-spacing: 2px;
  margin-bottom: 6px;
}}
.cover-title {{
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: 4px;
  margin-bottom: 4px;
}}
.cover-sub {{
  font-size: 14px;
  color: #8a7e6b;
  letter-spacing: 2px;
}}
.cover-meta {{
  display: flex;
  gap: 30px;
  margin-top: 8px;
  font-size: 12px;
  color: #6a5e4b;
}}
.cover-meta span {{
  display: flex;
  align-items: center;
  gap: 4px;
}}

/* ===== 诊断区块通用 ===== */
.section {{
  margin-bottom: 14mm;
}}
.section-title {{
  font-size: 16px;
  font-weight: 700;
  color: #3a3328;
  padding-bottom: 4px;
  border-bottom: 1px solid #d4c9b0;
  margin-bottom: 6mm;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 1px;
}}
.section-title .count {{
  font-size: 11px;
  font-weight: 400;
  color: #8a7e6b;
}}

/* ===== 户型图区 ===== */
.floorplan {{
  margin-bottom: 8mm;
}}
.floorplan-label {{
  font-size: 14px;
  font-weight: 600;
  color: #5a4e3b;
  margin-bottom: 3mm;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.floorplan-img {{
  width: 100%;
  border-radius: 4px;
  border: 1px solid #e0d9c8;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}}
.floorplan-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6mm;
}}

/* ===== 优先级标签 ===== */
.priority-red {{ color: #c8513a; font-weight: 700; }}
.priority-yellow {{ color: #c89a3a; font-weight: 700; }}
.priority-green {{ color: #5a8a5a; font-weight: 700; }}

.badge-red {{
  display: inline-block;
  background: #c8513a;
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 2px;
  margin-right: 4px;
}}
.badge-yellow {{
  display: inline-block;
  background: #d4a84b;
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 2px;
  margin-right: 4px;
}}
.badge-green {{
  display: inline-block;
  background: #7aa87a;
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 2px;
  margin-right: 4px;
}}

/* ===== 诊断卡片 ===== */
.cards {{
  display: flex;
  flex-direction: column;
  gap: 4mm;
}}
.card {{
  background: #f3efe8;
  border-left: 3px solid #d4c9b0;
  padding: 3mm 4mm;
  border-radius: 3px;
}}
.card.red {{ border-left-color: #c8513a; }}
.card.yellow {{ border-left-color: #d4a84b; }}
.card.green {{ border-left-color: #7aa87a; }}

.card-header {{
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 2px;
}}
.card-title {{
  font-size: 13px;
  font-weight: 700;
  color: #2c2c2c;
}}
.card-jue {{
  font-size: 11px;
  color: #8a7e6b;
  font-style: italic;
}}
.card-body {{
  font-size: 11px;
  line-height: 1.6;
  color: #4a4a4a;
}}
.card-body .chain {{
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 2px;
  font-size: 11px;
}}
.chain-item {{
  background: #e8e3d8;
  padding: 1px 6px;
  border-radius: 2px;
  font-size: 10px;
  color: #5a4e3b;
}}
.chain-arrow {{
  color: #b8aa90;
  font-size: 12px;
}}

/* ===== 金句区 ===== */
.jinjv {{
  background: #2c2c2c;
  color: #ece6d8;
  padding: 5mm 6mm;
  border-radius: 4px;
  margin-bottom: 6mm;
  text-align: center;
}}
.jinjv-text {{
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 3px;
  line-height: 1.5;
}}
.jinjv-sub {{
  font-size: 11px;
  color: #a89880;
  margin-top: 3px;
}}

/* ===== 总结表 ===== */
.summary-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 3mm;
  margin-bottom: 6mm;
}}
.summary-box {{
  text-align: center;
  padding: 3mm;
  border-radius: 4px;
}}
.summary-box.red {{ background: #f5e6e0; }}
.summary-box.yellow {{ background: #f5ede0; }}
.summary-box.green {{ background: #e6f0e0; }}
.summary-num {{
  font-size: 28px;
  font-weight: 700;
}}
.summary-box.red .summary-num {{ color: #c8513a; }}
.summary-box.yellow .summary-num {{ color: #c89a3a; }}
.summary-box.green .summary-num {{ color: #5a8a5a; }}
.summary-label {{
  font-size: 11px;
  color: #6a5e4b;
}}

.footer {{
  font-size: 10px;
  color: #b8aa90;
  text-align: center;
  border-top: 1px solid #e0d9c8;
  padding-top: 3mm;
  margin-top: 4mm;
}}

@media print {{
  body {{ background: white; padding: 0; }}
  .page {{ box-shadow: none; margin: 0; }}
  .floorplan-img {{ max-height: 90mm; }}
}}
</style>
</head>
<body>

<div class="page">
  <!-- 封面 -->
  <div class="cover">
    <div class="cover-badge">🏡 宅居断事</div>
    <div class="cover-title">栖月云居 · 户型诊断</div>
    <div class="cover-sub">成县 · 民宿改造项目 &nbsp;|&nbsp; 禅院宅居断事师出品</div>
    <div class="cover-meta">
      <span>📐 建筑面积 约300m²</span>
      <span>🏗 二层框架结构</span>
      <span>📅 2026.05.01</span>
    </div>
  </div>

  <!-- 总金句 -->
  <div class="jinjv">
    <div class="jinjv-text">「栖月云居底子好，干湿隔音最紧要，布草收纳不可少」</div>
    <div class="jinjv-sub">—— 三处🔴问题解决，民宿运营品质提升60%</div>
  </div>

  <!-- 优先级统计 -->
  <div class="section">
    <div class="section-title">📊 问题总览 <span class="count">共诊断 12 项</span></div>
    <div class="summary-grid">
      <div class="summary-box red">
        <div class="summary-num">3</div>
        <div class="summary-label">🔴 必改</div>
      </div>
      <div class="summary-box yellow">
        <div class="summary-num">5</div>
        <div class="summary-label">🟡 建议改</div>
      </div>
      <div class="summary-box green">
        <div class="summary-num">4</div>
        <div class="summary-label">🟢 可优化</div>
      </div>
    </div>
  </div>

  <!-- ===== 一楼 ===== -->
  <div class="section">
    <div class="section-title">🏛 一层 · 动区诊断</div>

    <div class="floorplan">
      <div class="floorplan-label">📐 一层平面图</div>
      <img class="floorplan-img" src="data:image/png;base64,{floor1_b64}" alt="一层平面图">
    </div>

    <div class="cards">
      <!-- 1. 卫生间干湿分离 -->
      <div class="card red">
        <div class="card-header">
          <span class="badge-red">🔴必改</span>
          <span class="card-title">01 · 卫生间未干湿分离</span>
        </div>
        <div class="card-jue">一句诀：洗澡一地水，客人最忌讳</div>
        <div class="card-body">
          <p>一层客卫无干湿分离设计，淋浴区与马桶、洗手台同处一室。</p>
          <div class="chain">
            <span class="chain-item">洗澡水花四溅</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">马桶区常年潮湿</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">霉味、滑倒风险、差评</span>
          </div>
        </div>
      </div>

      <!-- 2. 厨房排烟 -->
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡建议改</span>
          <span class="card-title">02 · 厨房排烟管道过长</span>
        </div>
        <div class="card-jue">一句诀：排烟百里远，油烟满屋转</div>
        <div class="card-body">
          <p>厨房位于西北角，排烟需穿越主要空间至外墙，弯多路长。</p>
          <div class="chain">
            <span class="chain-item">管道长+弯头多</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">排烟效率下降</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">油烟倒灌、厨房异味</span>
          </div>
        </div>
      </div>

      <!-- 3. 大门穿堂 -->
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡建议改</span>
          <span class="card-title">03 · 大门直对客厅（穿堂煞）</span>
        </div>
        <div class="card-jue">一句诀：开门见山不见底，民宿留客靠藏气</div>
        <div class="card-body">
          <p>入户大门打开后直接看穿客厅至后墙，缺乏视觉缓冲与空间层次。</p>
          <div class="chain">
            <span class="chain-item">大门对穿全厅</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">无隐私/无层次</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">客人进门一览无余</span>
          </div>
        </div>
      </div>

      <!-- 4. 玄关收纳 -->
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡建议改</span>
          <span class="card-title">04 · 玄关无落尘收纳区</span>
        </div>
        <div class="card-jue">一句诀：进门没地放鞋包，客人尴尬你烦恼</div>
        <div class="card-body">
          <p>入口无独立玄关空间，无换鞋凳、无挂衣区、无落尘过渡。</p>
          <div class="chain">
            <span class="chain-item">无落尘过渡区</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">泥土带入室内</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">保洁压力大、第一印象差</span>
          </div>
        </div>
      </div>

      <!-- 5. 上菜动线 -->
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡建议改</span>
          <span class="card-title">05 · 厨房到餐厅动线穿越客厅</span>
        </div>
        <div class="card-jue">一句诀：端菜穿厅过，住客看烟火</div>
        <div class="card-body">
          <p>从厨房出菜到餐厅需经过客厅区域，与休闲客人动线交叉。</p>
          <div class="chain">
            <span class="chain-item">上菜路线穿越客厅</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">服务与休闲动线冲突</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">互相干扰、体验打折</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ===== 二楼 ===== -->
  <div class="section">
    <div class="section-title">🛏 二层 · 静区诊断</div>

    <div class="floorplan">
      <div class="floorplan-label">📐 二层平面图</div>
      <img class="floorplan-img" src="data:image/png;base64,{floor2_b64}" alt="二层平面图">
    </div>

    <div class="cards">
      <!-- 6. 卧室隔音 -->
      <div class="card red">
        <div class="card-header">
          <span class="badge-red">🔴必改</span>
          <span class="card-title">06 · 卧室间无隔音处理</span>
        </div>
        <div class="card-jue">一句诀：墙薄不如纸，隔壁打呼你听死</div>
        <div class="card-body">
          <p>相邻卧室共用轻质隔墙，无隔音加强，民宿大忌。</p>
          <div class="chain">
            <span class="chain-item">轻质隔墙无隔音</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">声音互传</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">差评集中投诉点</span>
          </div>
        </div>
      </div>

      <!-- 7. 布草间 -->
      <div class="card red">
        <div class="card-header">
          <span class="badge-red">🔴必改</span>
          <span class="card-title">07 · 缺布草/保洁储物间</span>
        </div>
        <div class="card-jue">一句诀：布草保洁无处放，运营起来手忙脚乱</div>
        <div class="card-body">
          <p>整层无独立布草间或保洁储物空间，换洗床品、清洁工具无处存放。</p>
          <div class="chain">
            <span class="chain-item">无布草间</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">床品堆在走廊/客房</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">观感差、效率低、卫生隐患</span>
          </div>
        </div>
      </div>

      <!-- 8. 佛堂 -->
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡建议改</span>
          <span class="card-title">08 · 佛堂邻接卫生间</span>
        </div>
        <div class="card-jue">一句诀：佛堂挨着卫生间，香火灵气两头难</div>
        <div class="card-body">
          <p>二层佛堂与公共卫生间仅一墙之隔，民俗禁忌中为"秽冲"。</p>
          <div class="chain">
            <span class="chain-item">佛堂紧邻卫生间</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">民俗风水不利</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">部分客人介意、氛围冲突</span>
          </div>
        </div>
      </div>

      <!-- 9. 二楼卫生间 -->
      <div class="card green">
        <div class="card-header">
          <span class="badge-green">🟢可优化</span>
          <span class="card-title">09 · 二层卫生间改干湿分离</span>
        </div>
        <div class="card-jue">一句诀：楼上也干湿分离，全体客人都满意</div>
        <div class="card-body">
          <p>同层如条件允许增设淋浴隔断或浴帘，提升客房使用体验。</p>
        </div>
      </div>

      <!-- 10. 露台利用 -->
      <div class="card green">
        <div class="card-header">
          <span class="badge-green">🟢可优化</span>
          <span class="card-title">10 · 露台利用率不足</span>
        </div>
        <div class="card-jue">一句诀：露台空着是浪费，设个茶座客自醉</div>
        <div class="card-body">
          <p>二层露台面积不小，目前无功能规划。建议增设户外休闲区/晾晒区。</p>
          <div class="chain">
            <span class="chain-item">大露台空置</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">浪费景观资源</span>
            <span class="chain-arrow">→</span>
            <span class="chain-item">建议：茶座+晨练+晾晒三用</span>
          </div>
        </div>
      </div>

      <!-- 11. 储物优化 -->
      <div class="card green">
        <div class="card-header">
          <span class="badge-green">🟢可优化</span>
          <span class="card-title">11 · 客房收纳可升级</span>
        </div>
        <div class="card-jue">一句诀：客房收纳多一点，客人好评每一天</div>
        <div class="card-body">
          <p>现有卧室储物空间偏少，建议增设入墙衣柜或行李架，满足民宿连住需求。</p>
        </div>
      </div>

      <!-- 12. 采光通风 -->
      <div class="card green">
        <div class="card-header">
          <span class="badge-green">🟢可优化</span>
          <span class="card-title">12 · 中央走廊采光一般</span>
        </div>
        <div class="card-jue">一句诀：走廊暗了不要怕，玻璃砖墙透光法</div>
        <div class="card-body">
          <p>二楼中央走廊自然采光有限，建议用玻璃砖隔断或天窗引入光线。</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 落地建议 -->
  <div class="section">
    <div class="section-title">📋 落地路线图</div>
    <div class="cards">
      <div class="card red">
        <div class="card-header">
          <span class="badge-red">🔴第一阶段</span>
          <span class="card-title">改造期（施工前）</span>
        </div>
        <div class="card-body">
          <p>① 卫生间增加淋浴隔断墙/玻璃推拉门 → 干湿分离完成<br>
          ② 卧室隔墙中填塞隔音棉+双层石膏板 → 隔音达标<br>
          ③ 划出布草间（可利用楼梯下或阳台端部空间）</p>
        </div>
      </div>
      <div class="card yellow">
        <div class="card-header">
          <span class="badge-yellow">🟡第二阶段</span>
          <span class="card-title">软装期（施工中）</span>
        </div>
        <div class="card-body">
          <p>④ 入口增设玄关柜+换鞋凳+落尘垫<br>
          ⑤ 佛堂与卫生间之间增加隔断柜缓冲<br>
          ⑥ 厨房排烟管优化（减少弯头/加大管径）</p>
        </div>
      </div>
      <div class="card green">
        <div class="card-header">
          <span class="badge-green">🟢第三阶段</span>
          <span class="card-title">运营期（开业前）</span>
        </div>
        <div class="card-body">
          <p>⑦ 露台布置户外家具+景观植物+晾衣区<br>
          ⑧ 客房增加入墙衣柜/行李架<br>
          ⑨ 走廊墙面改玻璃砖或加感应灯带</p>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    禅院宅居断事师 · 栖月云居项目 · 诊断时间 2026.05.01 · 第1版
  </div>
</div>

</body>
</html>"""

with open("/Users/mac/Desktop/栖月云居-户型诊断信息图_v2.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("HTML generated!")
print(f"Size: {len(HTML)} chars")
