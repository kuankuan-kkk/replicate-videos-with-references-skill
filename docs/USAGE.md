# 详细使用方法

## 两种使用方式

**创作者：** 在支持 Skill 的 AI 助手里上传完整视频并调用 Skill，使用自然语言确认修改边界、反馈分镜、批准版本。助手依据实际可用工具执行；没有图像编辑工具时，只交付分析和提示词。

**工具维护者：** 用下列 Python 脚本管理证据、版本和流程门禁。这些脚本不会自动调用模型、理解视频或生成成片；不要把 CLI 的结构验证通过当成视频质量通过。

## 准备素材

- 完整视频：需要能访问和解码，不是封面截图。
- 修改清单：明确哪些人物/产品/物体可以修改，哪些不能动。
- 对应参考：替换人物需清楚的脸/发型；替换具体产品需匹配包装和可见使用状态；移植场景需新场景图。
- 使用权和清理授权：字幕、用户名、UI、水印不得默默清理。

多个参考文件应明确用途，不要让助手猜哪个人物对应哪个镜头。人物图仅控制指定身份特征，不自动带入自拍姿态、服装和背景。

## 工作流程

1. **接收与能力检查：** 记录文件和要求，确认可执行的能力等级。检查完整解码，不等于完成语义观察。
2. **逐镜取证：** 用 `S01…` 记录来源、时间码、机位、动作、视线、露脸、服装、产品、光影与剪辑功能。
3. **动作规划：** 用 `B01…` 表示完整动作起始、过程、结果和下镜衔接。不是固定生成 6/12/20 张。
4. **边界和连续性：** 原帧底图、批准区域、服装/房间/产品状态与依赖关系分别记录。冲突先让用户选择。
5. **生成与质检：** 每次生成保存新版本；检查未授权变化、动作、人物、手部、场景、产品、光影与画幅。有 A 级工具时比较原始底图和批准蒙版之外的区域。
6. **局部修复：** 只修授权范围内的问题。一个问题累计两次失败后需人工确认新的修复策略，不能重新生成来清空失败记录。
7. **确认分镜：** 用户只批准实际通过质检的具体版本。新输出或相关约束变化使旧确认失效。
8. **视频提示词：** 全部要求的分镜确认后，还需用户明确请求。此步骤是提示词交付，不是视频生成接口。

## 本地 CLI 快速检查

以下命令从仓库根目录运行。先在仓库外新建一个私有工作目录，将 `PRIVATE_WORK_DIR` 替换为其路径（路径不应提交到 Git）。

```sh
python replicate-videos-with-references-v3/scripts/preflight.py --json
python replicate-videos-with-references-v3/scripts/init_project.py demo --output PRIVATE_WORK_DIR/project.json
python replicate-videos-with-references-v3/scripts/validate_project.py PRIVATE_WORK_DIR/project.json
python -m unittest discover -s replicate-videos-with-references-v3/tests -v
```

初始化不会覆盖已有清单。一个空的 intake 清单通过结构检查，不代表素材/质检/审批已经完成。

实际视频探测和抽帧（需要 FFmpeg、ffprobe；图像检查还需 Pillow）：

```sh
python replicate-videos-with-references-v3/scripts/preflight.py --json --video PRIVATE_WORK_DIR/source.mp4
python replicate-videos-with-references-v3/scripts/inspect_video.py PRIVATE_WORK_DIR/source.mp4
python replicate-videos-with-references-v3/scripts/extract_frame.py PRIVATE_WORK_DIR/source.mp4 1.2 PRIVATE_WORK_DIR/base.png
```

`1.2` 表示视频内的秒数，需在实际时长范围内；输出路径不能覆盖已有文件。preflight 可能打印本地路径，勿上传原始输出。

## 状态操作：不是一键造证据

下列是命令形式，**不是可从空清单连续运行的完整示例**。`N` 替换为清单中的当前 `project.revision`；每次成功变更后重新读取修订号。输入文件、授权、动作规划和实际输出证据必须先满足[契约](../replicate-videos-with-references-v3/references/structured-state-and-gates.md)。

```sh
python replicate-videos-with-references-v3/scripts/manage_project.py update PRIVATE_WORK_DIR/project.json --expected-revision N --actor creator --data PRIVATE_WORK_DIR/verified-inputs.json
python replicate-videos-with-references-v3/scripts/manage_project.py advance PRIVATE_WORK_DIR/project.json --expected-revision N --actor creator --state evidence-ready
python replicate-videos-with-references-v3/scripts/manage_project.py record-version PRIVATE_WORK_DIR/project.json --expected-revision N --actor creator --action-id B01 --version-id B01-v1 --file PRIVATE_WORK_DIR/B01-v1.png
python replicate-videos-with-references-v3/scripts/manage_project.py review PRIVATE_WORK_DIR/project.json --expected-revision N --actor reviewer --action-id B01 --data PRIVATE_WORK_DIR/checks.json
python replicate-videos-with-references-v3/scripts/manage_project.py approve PRIVATE_WORK_DIR/project.json --expected-revision N --actor user --action-ids B01
python replicate-videos-with-references-v3/scripts/manage_project.py authorize-video PRIVATE_WORK_DIR/project.json --expected-revision N --actor user
```

必要状态顺序：intake → evidence-ready → analyzed → planned → generating → qa → storyboard-delivered → storyboard-approved → prompts-delivered。C 级从 planned 走 analysis-delivered，不能假装进入图片生成流程。各状态有独立前置条件；仅写状态名称不能绕过门禁。

`review` 的检查维度由 `scripts/project_contract.py` 中的 `CHECKS` 定义，不要捏造一个全通过模板。`approve` 需要分镜已交付且真实质检通过。`--actor user` 仅记录本地角色，**不提供身份认证，也不能代替用户实际同意**。

## A 级蒙版外质检

```sh
python replicate-videos-with-references-v3/scripts/compare_outside_mask.py PRIVATE_WORK_DIR/base.png PRIVATE_WORK_DIR/B01-v1.png PRIVATE_WORK_DIR/approved-mask.png --authorized-mask-sha256 APPROVED_HASH
```

`APPROVED_HASH` 必须来自此前明确批准的联合蒙版，不是临时为新蒙版计算后冒充已授权。白色为授权区，黑色为锁定区；底图、输出和蒙版尺寸一致。全白蒙版没有可比较的锁定区域，不能当作严格复刻通过。

对比对象一直是原始底图，而不是上一次已变形的生成图。默认每通道容差 2、蒙版外变动比例阈值 0.001；报告不能替代语义质检，也不证明绝对像素相同。A 级版本登记还需保存真实蒙版和对比报告文件。

## 常见问题

**为什么不直接生成视频？** Skill 是助手的工作流和验证工具，不包含视频生成模型或账号额度。能输出已确认分镜对应的提示词，是否生成成片取决于环境。

**缺 FFmpeg 就完全不能用吗？** 不能使用这些本地媒体脚本，但助手可能有其他视频工具。能力等级必须由真实验证决定，不能仅凭本地缺依赖就断言无法处理。

**为什么原视频移动机位时会暂停？** 默认固定机位与原证据冲突。需明确保留源机位还是授权适配，不可同时声称两者都严格不变。

**为什么改了产品后要重新确认？** 输出与约束发生变化，旧确认不再绑定当前版本，重新审批是避免误用旧素材。

**锁文件残留怎么处理？** 先检查 `project.json.lock` 记录的进程是否仍在运行，确认确实过期后才处理该锁。不要批量删锁或绕过修订检查。
