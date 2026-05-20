# Modly 图片转3D工具评估

> 来源：GitHubDaily推文（2026-05-08）
> GitHub: lightningpixel/modly
> ⭐ 3.1k | TypeScript/Electron | 本地GPU运行
> 官网：https://modly3d.app

## 核心能力
- 一张照片一键生成3D网格模型
- 本地GPU运行，不上传数据到云端
- 支持切换不同模型
- 完全免费，开源

## 兼容性判断
- **Intel Mac** ⚠️ — 项目架构依赖GPU推理，Intel Mac无CUDA/MPS支持
- 构建产物可能只提供arm64架构
- 理论可跑但体验不会好

## 融合价值（替代方案）
不推荐本地装Modly，但思路可以借鉴：
1. 接入免费图片转3D API（如SiliconFlow）
2. EPC场景：户型图→3D模型快速呈现给客户
3. 小红书场景：商品图生成3D展示素材
