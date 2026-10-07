# Reference Video Replication Skill · 参考视频复刻

**版本 3.1.0** · 以完整视频为证据，只修改明确授权的部分。

这是一套面向 AI 创作助手的 Skill：把参考视频拆成可追溯的镜头与完整动作，规划局部修改、检查连续性，并在用户确认分镜后输出独立的视频提示词。适用于 UGC 素人感短视频制作、产品替换及多视频融合。

它不是独立的视频生成软件，不自带模型、付费额度、API 密钥或托管后端。Python 工具负责文件检查、项目状态与质检证据；视频理解、图像编辑和最终视频生成依赖你使用的平台与实际工具能力。

## 能做什么

| 模式 | 适用需求 | 约束 |
| --- | --- | --- |
| 严格局部重绘 | 更换人物、产品或指定摆件，其他尽量不变 | 原帧作底图；明确修改区域；有工具和证据才承诺未修改区像素保留 |
| 多视频融合 | 组合多条视频的剧情、动作或镜头 | 每条来源都有明确贡献，并可追溯到最终分镜 |
| 场景移植 | 换场景，保留参考的动作和 UGC 质感 | 新场景控制布局，原视频控制动作与光影参考；不冒充严格原场景复刻 |

核心流程：**上传完整视频 → 逐镜取证 → 完整动作拆分 → 修改/锁定区域确认 → 分镜生成与质检 → 用户确认具体版本 → 明确请求视频提示词**。

## 安装

1. 下载本仓库 ZIP 或克隆仓库。
2. 将内层文件夹 `replicate-videos-with-references-v3` 整体复制到你的 Skill 加载目录，保留 `SKILL.md`、`references`、`scripts`、`assets` 和 `agents`。
3. 在 Codex 中通常使用 `$CODEX_HOME/skills`；未自定义时通常为用户目录下的 `.codex/skills`。其他助手需确认其是否支持文件夹型 Skill，不能直接假设通用安装方式。
4. 重新加载/重启支持 Skill 的助手，确认能识别 `replicate-videos-with-references-v3`。

Skill 名称保留 `v3` 以兼容已有调用；内容版本为 **3.1.0**。

### 可选本地工具

使用 Python 辅助脚本时建议 Python 3.10+，在本仓库根目录运行：

```sh
python -m pip install -r requirements.txt
python replicate-videos-with-references-v3/scripts/preflight.py --json
```

抽帧、媒体探测与完整解码需要另行安装 **FFmpeg 和 ffprobe** 并加入 PATH。本仓库不包含这些二进制程序。Pillow 用于图像和蒙版检查；PyYAML 用于普通 YAML/旧版清单，JSON 核心状态不依赖 YAML 解析器。

## 第一次使用

上传你有权使用的完整参考视频，按需求补充人物、产品或新场景参考。不要只提供封面。然后向助手发送：

```text
使用 $replicate-videos-with-references-v3。
请分析我上传的完整参考视频，先生成 3 张分镜测试。
只允许把原产品替换为上传的产品图；人物、服装、机位、房间布局和光影保持原视频参考。
先说明当前工具能保证什么，列出允许修改和必须锁定的内容。
如存在时长、移动机位、画幅或字幕清理冲突，先问我，不要默默改编。
完成分镜质检后停下来等我确认，暂时不要生成视频提示词。
```

看完分镜后，用明确的版本反馈：

```text
B01-v1 可以确认；B02-v1 不确认，产品握持有问题，请只修复授权范围内的握持与接触关系。
```

全部需要的分镜通过后，再明确发送：

```text
确认已通过质检的这些分镜版本，生成视频提示词。
```

每个已确认分镜对应一条提示词；默认 4 秒、固定机位、9:16，**仅在与原动作和已批准方案相容时使用**。不能为了凑 4 秒遗漏动作结果，也不能把移动机位悄悄改成固定机位。最终视频需交给你实际可用的视频生成工具执行，Skill 不会凭空返回成片。

## 能力边界

| 等级 | 实际可用工具 | 可交付内容 |
| --- | --- | --- |
| A | 抽帧、明确区域编辑、批准蒙版、蒙版外对比 | 有证据的局部重绘；仍需人工审核真实性 |
| B | 抽帧与参考图编辑，不能强制像素边界 | 经用户接受的构图约束重建，不宣称像素级不变 |
| C | 能分析/抽帧，无图像编辑工具 | 分析、底图、状态清单与编辑提示词，不伪造生成结果 |
| D | 无法访问或解码完整视频 | 停在素材接收，索要可用视频 |

数值对比通过不等于人物自然、动作合理或视频真实。字幕、用户名、水印与平台 UI 清理也必须先明确授权，不能默认扩大修改范围。

## 文档与验证

- [详细操作与命令](docs/USAGE.md)
- [隐私保护与发布范围](docs/PRIVACY.md)
- [版本说明](CHANGELOG.md)
- [Skill 入口](replicate-videos-with-references-v3/SKILL.md)
- [状态、版本和审批契约](replicate-videos-with-references-v3/references/structured-state-and-gates.md)

运行自动化测试：

```sh
python -m unittest discover -s replicate-videos-with-references-v3/tests -v
```

当前包含 45 项合成数据/模拟工具测试，覆盖状态门禁、版本绑定、连续性依赖、重试记录、蒙版证据和 CLI 基础行为。**不代表真实视频全链路验收、模型质量评分或业务效果证明。**

## 隐私与使用权

仓库不包含个人简历、联系方式、客户素材、运营数据、运行状态、凭据或既往 Git 历史。请把真实工作项目放在仓库外；勿将日志、视频、人物图或项目清单直接提交到 GitHub。详见[隐私说明](docs/PRIVACY.md)。

本项目采用 [MIT 许可证](LICENSE)：可自由使用、修改、再分发与商用，需保留原版权与许可声明。请确保参考素材、人像和产品图具有必要授权；不要制作冒充真实人物或误导观众的内容。

## English summary

A traceable reference-video replication Skill (v3.1.0) for AI assistants. It separates observed evidence, authorized edits, locked regions, continuity states, quality review and version-bound user approvals. Supports strict local redraw, multi-video fusion and scene transplant. Local scripts validate evidence and workflow state; model access and image/video generation are not bundled. Read the Chinese usage and privacy guides before running on real media. Licensed under the MIT License.
