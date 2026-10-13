# DF4robot

**机器人多传感器融合：IMU × Camera × LiDAR × 毫米波 Radar，从 Kalman 到 VLA。**

54 页中文离线交互 slides，53 项论文与经典资料索引，覆盖概率模型、多频异步、算法流程、系统选型、学习方法与机器人应用。检索截止 **2026-10-13**。

![全部页面预览](deck/预览-全部页面.png)

## 打开与阅读

下载或 clone 本仓库，双击 [deck/deck.html](deck/deck.html)，使用 Chrome / Edge 打开即可；不需要网络、服务器、Node.js 或 Python。GitHub 文件预览显示 HTML 源码，演示请下载后打开。

- **10 分钟决策路径**：2 → 4 → 31 → 36 → 40 → 46 → 49 → 51 → 52。
- **45–60 分钟讲解路径**：完整 54 页，按听众背景选择公式深度。
- **深入阅读**：[综述](research/综述.md) · [53 项论文索引](research/论文索引.md) · [逐页讲稿](deck/讲稿.md) · [检索记录](research/检索记录.md)。
- **审阅结果**：[两种角色视角的意见与修改](审阅与修改.md)。

键位：`← →` / 空格翻页，`G` 目录，数字跳页，`F` 全屏，`N` 讲稿。第 10 页拖动 σ 滑块；第 14 页点击异步事件；第 22 页用 `J/K` 推进 ESKF。

## 明确结论

1. 不同频率不妨碍融合：按采集时刻传播、更新、预积分或优化。
2. 不同单位和噪声通过各自观测模型、残差协方差和白化进入统一状态。
3. 正确的标定、时间、数据关联、相关性和可观性决定融合是否可信。
4. 先建立几何概率基线，再按失效场景增加模态与学习模块。
5. VLA 连接语义与动作；典型 VLA 不直接替代具有状态协方差与物理时间模型的里程计。

这些是有条件的工程综合判断，不是统一硬件上的算法性能排行榜。详见每页讲稿和原始论文链接。

## 内容范围

| 页面 | 主题 |
|---|---|
| 1–4 | 决策建议、方法分类、各传感器的观测与频率 |
| 5–12 | 状态、流形误差、高斯/非高斯、白化、相关性 |
| 13–19 | 多速率、IMU 传播、预积分、延迟、标定、连续时间 |
| 20–27 | Bayes、ESKF、InEKF、UKF/粒子、MSCKF、因子图、可观性 |
| 28–36 | VIO/LIO/LIVO/RIO、Doppler、2026 方向自适应融合 |
| 37–44 | 学习式估计、协方差、VLA、动作块、触觉与异步策略 |
| 45–52 | 场景选型、失效降级、数据集、指标、消融、阶段门槛 |
| 53–54 | 核心与前沿阅读入口 |

## 证据与限制

- 使用 DeepXiv CLI 定向搜索，核心算法方法节及 2026 前沿另以 arXiv 原文核验。
- 全部机制图自绘；高斯图按公式计算；设备频率与时效数字明确标注为配置/教学示例。
- 新论文区分版本与作者注明的接收状态，避免将自动摘要的过强结论当成原文。
- 不发布论文全文或第三方自动摘要缓存。`papers.json` 为筛选后的元数据与原创中文注释。
- 两轮审阅是模拟企业高层技术负责人和资深教授视角的自审，不是华为/高校真实背书。
- 没有声称完成机器人实测、论文算法统一复现或所有文献的穷尽检索。

## 维护与重新生成

演示不需要依赖。修改 slides 内容时：

```powershell
python build_deck.py
```

生成 `deck.html`、`slides.json` 和 `讲稿.md`。需要 Python 3.12+；无需外部 Python 包。原始版式来自本机 kelip-slide skill 的模板，附带 `deck/template.html` 以便重建。

渲染自查有两种方式：

```powershell
# 方式一：kelip 模板的 Chrome 渲染脚本；需要 Pillow
$env:CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe'
python deck/render_preview.py deck/deck.html 54 deck/rendered 1

# 方式二：Playwright 逐页截图 + 边界/交互检查；需要 Node.js 与 Playwright
node deck/verify_render.cjs
python deck/make_contact.py
```

若 Playwright 不在默认模块路径，将 `NODE_PATH` 指向其安装目录。截图临时文件不入库；总览图与 `validation.json` 入库。改变页数时需同步说明文档和渲染参数。

`research/collect.py` 可通过已安装的 DeepXiv 读取核心论文；需要网络。`research/build_catalog.py` 从本地缓存重建书目，完整发布版阅读与 slides 重建使用已有 `papers.json`，无需重新检索。

## 文件布局

```text
deck/deck.html             离线 slides（CSS / JS / SVG 全内联）
deck/讲稿.md               逐页说明、假设与引用
deck/预览-全部页面.png     全 54 页视觉检查总览
deck/validation.json       浏览器检查结果
research/综述.md           完整知识整理与推导
research/论文索引.md       53 项条目、贡献、限制与链接
research/papers.json       结构化书目
research/检索记录.md       查询、命令、读取层级和排除记录
审阅与修改.md              模拟审阅与实际落实
build_deck.py              内容与图形生成源
```
