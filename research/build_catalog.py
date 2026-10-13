"""Build an annotated bibliography from verified retrieval metadata; no full text is redistributed."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent
# id | short name | family | contribution | practical boundary
ROWS = '''
1711.02508|ESKF 旋转与误差状态|概率基础|在旋转流形的局部切空间传播误差与协方差|左右扰动、四元数约定和误差重置必须保持一致
1410.1465|Invariant EKF|概率基础|利用系统对称性构造不变误差及结构化误差动力学|理论结论有系统结构和可观性条件；不能声称任意机器人全局收敛
1805.10410|Contact-aided InEKF|机器人扩展|把接触点与惯性状态联合估计，用运动学约束辅助腿式机器人|接触切换和滑移必须建模；IMU 偏置扩展需要谨慎分析
1512.02363|流形 IMU 预积分|时间与优化|把关键帧间高频 IMU 压缩成相对运动因子及协方差|预积分仍依赖偏置线性化点；大幅变化需重积分
1808.00692|在线时间偏移标定|时间与优化|把相机与 IMU 时间偏移加入优化状态|恒定偏移模型不能自动解释随机网络抖动
2202.08894|连续 / 离散时间 SLAM 比较|时间与优化|比较轨迹参数化对异步视觉估计的影响|连续时间依赖样条带宽、节点间距和运动激励
2407.11420|iKalibr|时间与优化|连续时间、无靶标的多传感器时空标定|离线标定需要足够运动激励与合适数据
2408.02444|RIs-Calib|时间与优化|使用旋转与速度样条标定多 Radar 与 IMU|校准目标和传感器观测能力限制可辨识性
1708.03852|VINS-Mono|VIO|关键帧滑窗优化、预积分、初始化与重定位|单目视觉依赖纹理和视差；尺度恢复需要惯性激励
2007.11898|ORB-SLAM3|VIO|视觉 / 惯性估计结合多地图与重定位|完整 SLAM 与纯里程计的回环设置必须分开比较
1903.01534|Selective Sensor Fusion|学习式估计|学习视觉与惯性特征的软 / 硬选择|融合门控不是经过统计校准的协方差
1909.04102|LIC-Fusion|LIVO|LiDAR、IMU、相机的紧耦合里程计|共享状态、标定与退化问题需要联合考虑
2008.07196|LIC-Fusion 2.0|LIVO|滑窗平面跟踪与在线时空标定|退化运动会降低标定参数可观性
2007.00258|LIO-SAM|LIO|预积分、扫描匹配和全局约束接入因子图|回环、GNSS 和 LiDAR 配置影响比较口径
2107.06829|FAST-LIO2|LIO|迭代误差状态滤波、原始点配准与增量地图|几何退化仍存在；快速扫描处理不等于所有平台固定速度
2104.10831|LVI-SAM|LIVO|视觉惯性与激光惯性子系统互助，图优化管理约束|不是把三路原始数据统一拼接后一次求解
2109.07982|R3LIVE|LIVO|共享状态与彩色地图下的 LiDAR / 视觉惯性估计|颜色一致性、曝光和可见性影响直接视觉残差
2203.00893|FAST-LIVO|LIVO|稀疏直接视觉与 LiDAR 惯性紧耦合|视觉和几何同时退化时仍会失败
2408.14035|FAST-LIVO2|LIVO|统一体素地图、LiDAR→视觉序贯 ESIKF、曝光估计|需已知时差和外参；LiDAR 点按图像时刻重组
2311.08608|Multi-Radar Inertial Odometry|Radar|多雷达多普勒速度与 IMU 固定滞后平滑|多视向有助三维速度；不能无条件消除全部不可观方向
2303.13962|4D iRIOM|Radar|鲁棒自速度、扫描子图匹配和迭代滤波，并加入回环|稀疏点和多径会破坏关联；SLAM 与 odometry 指标要区分
2402.02200|Physical-enhanced RIO|Radar|把多普勒和 RCS 用于静态点筛选与关联|物理属性增强不代表反射强度在跨设备下恒定可靠
2403.05136|DeRO|Radar|多普勒速度与陀螺做航位推算，滤波辅助修正|加速度倾角约束需区分重力与动态加速度
2504.20339|DRO|Radar|旋转 Radar 强度直接匹配，并建模连续运动与多普勒畸变|SE(2) 方案；特定调频方式才提供文中额外多普勒约束
2310.18117|Do we need scan-matching?|Radar|比较多普勒加 IMU 与扫描匹配在野外的效果|文中场景结论不能推广为任何 Radar 都无需匹配
2311.11260|Radarize|Radar|Radar 原生多普勒里程计与多径抑制|Radar-only 系统，不能列为 IMU 紧耦合方法
2011.03512|Radar 运动与多普勒畸变|Radar|分析旋转雷达运动畸变及补偿|旋转雷达与 4D 成像雷达的数据形式不同
2411.17289|Loosely coupled 4D RIO|Radar|为地面机器人提供模块化松耦合方案|接口协方差、共有信息和地面运动假设影响一致性
2204.11098|Student-t 多传感器滤波|非高斯与相关性|以重尾噪声与近似闭式融合处理离群值|仿真证据不是机器人现场可靠性证明
2506.00383|Gaussian Mixture Fusion|非高斯与相关性|研究分布式高斯混合估计的一致融合|分量关联和计算规模随多峰数上升
2007.01867|TLIO|学习式估计|网络预测三维位移与不确定性，再通过克隆 EKF 融合|训练来自头戴式行人运动，直接迁移机器人有域偏移
2108.10869|DROID-SLAM|学习式估计|学习迭代更新并结合稠密 bundle adjustment|原论文是视觉 SLAM，不应声称原生融合 Radar 或 IMU
2507.10376|Raci-Net|学习式估计|学习融合相机、惯性和毫米波，用于恶劣天气里程计|Boreas 实验不能代替跨 Radar 型号与机器人验证
2410.15480|Event fusion survey|机器人扩展|梳理事件相机与惯性、帧相机、LiDAR 的里程计融合|事件没有传统帧率；打包事件也会引入窗口选择
2302.06643|Vision-Radar BEV survey|机器人扩展|梳理早期、特征和后期融合用于 BEV 检测|检测精度不等于位姿估计精度
2303.04137|Diffusion Policy|策略与 VLA|生成多峰动作序列并采用滚动执行|基础模型是视觉运动策略，不自动包含语言
2307.15818|RT-2|策略与 VLA|将视觉语言知识转为动作 token|动作 token 的置信度不等价于定位协方差
2406.09246|OpenVLA|策略与 VLA|开源视觉语言动作模型及微调路线|不原生解决 IMU/Radar 的几何标定与里程计
2405.12213|Octo|策略与 VLA|模块化观测与动作接口的通用机器人策略|扩展新模态仍需适配和训练，不是即插即用
2410.24164|π0|策略与 VLA|VLM 条件下用 flow matching 生成连续动作块|动作执行频率与策略重规划频率需要分别计量
2504.16054|π0.5|策略与 VLA|异构数据共训练及语义子任务支持长时操作|成功率受任务、环境和训练分布影响
2507.09160|Tactile-VLA|策略与 VLA|通过触觉反馈与位置力控制支持接触任务|触觉作用于操作，不直接提供全局里程计
2603.12665|TacVLA|2026 前沿|接触感知门控激活触觉 token，联合视觉语言处理|arXiv v4；任务级证据，未证明普适鲁棒性
2606.25699|SA-LIVO|2026 前沿|联合信息矩阵分解，在特征方向上进行门控|arXiv v2；抑制弱方向与主动补强弱方向不是同一机制
2609.03561|TRaIL-Odom|2026 前沿|连续时间 Radar-IMU-LiDAR，按几何弱方向重加权多普勒|arXiv 页面注明 RA-L 接收；权重为工程调节，不是已标定噪声协方差
2609.05325|FIRE-LIVWO|2026 前沿|矿井场景联合轮速、视觉、LiDAR、IMU 和 Radar 的退化切换|arXiv 页面注明 IROS 2026 接收；Failure-Immune 是方法名而非失效保证
2609.39125|LBDU-VIO|2026 前沿|在 MSCKF 内学习偏置连续动力学和 IMU 不确定性|2026-09 预印本；跨设备泛化和在线稳定性尚需独立复现
2203.10168|Boreas|数据集|多季节相机、LiDAR、旋转 Radar 数据支持天气研究|不得默认所有雷达均输出逐点 Doppler
2309.00962|NTU4DRadLM|数据集|4D Radar、热成像、相机、IMU、LiDAR 与 RTK GPS|应检查实际发布序列、时间戳和真值可用区间
2602.16870|Boreas Road Trip|数据集|新增具多普勒能力的 Radar / LiDAR 与独立 IMU 等|新硬件的数据特性不可与原 Boreas 混用
'''.strip()

def build():
 metadata = {}
 for f in ROOT.glob('search-*.json'):
  try:
   for p in json.loads(f.read_text(encoding='utf-8-sig')).get('result', []): metadata[p['arxiv_id']] = p
  except (ValueError, KeyError): pass
 for f in (ROOT/'briefs').glob('*.txt'):
  txt=f.read_text(encoding='utf-8-sig')
  m=re.search(r'📄\s*(.+)',txt)
  if m:
   p=metadata.setdefault(f.stem,{})
   p['title']=m.group(1).strip()
   g=re.search(r'GitHub:\s*(https?://\S+)',txt)
   if g: p['github_url']=g.group(1).rstrip('.')
 for aid,title in {
  '2203.10168':'Boreas: A Multi-Season Autonomous Driving Dataset',
  '2309.00962':'NTU4DRadLM: 4D Radar-centric Multi-Modal Dataset for Localization and Mapping',
  '2602.16870':'Boreas Road Trip: A Multi-Sensor Autonomous Driving Dataset on Challenging Roads',
 }.items(): metadata.setdefault(aid,{})['title']=title
 papers=[]
 for row in ROWS.splitlines():
  aid,name,family,idea,limit=row.split('|')
  meta=metadata.get(aid,{})
  tier='A' if aid in {'1512.02363','2408.14035','2609.03561'} else 'B' if aid in {'1805.10410','2603.12665','2606.25699','2609.05325','2609.39125','2204.11098','2507.10376','2007.01867','2203.10168','2309.00962','2602.16870','2303.13962','2402.02200','2311.11260','2310.18117','2506.00383','2410.15480','2302.06643','2311.08608','2403.05136','2504.20339'} else 'C'
  evidence={'A':'已读关键方法正文','B':'原始摘要/作者资料已核验','C':'DeepXiv 检索元数据或自动 brief；仅作路线图'}[tier]
  papers.append(dict(id=aid,name=name,title=meta.get('title',name),year=2000+int(aid[:2]),family=family,idea=idea,limit=limit,url=f'https://arxiv.org/abs/{aid}',code=meta.get('github_url'),tier=tier,evidence=evidence,accessed='2026-10-13'))
 for aid,name,title,year,url,idea,limit in [
  ('msckf','MSCKF','A Multi-State Constraint Kalman Filter for Vision-aided Inertial Navigation',2007,'https://intra.ece.ucr.edu/~mourikis/tech_reports/TR_MSCKF.pdf','保留相机克隆位姿，通过零空间投影消去特征点状态','链接为 2006 技术报告；会议论文发表于 ICRA 2007'),
  ('openvins','OpenVINS','OpenVINS: A Research Platform for Visual-Inertial Estimation',2020,'https://docs.openvins.com/','可复现的滤波式 VIO、标定及一致性评估工具','功能与配置应以实际使用的提交版本为准'),
  ('isam2','iSAM2','iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree',2012,'https://people.csail.mit.edu/kaess/pub/Kaess12ijrr.pdf','增量稀疏优化与选择性重线性化','计算代价取决于图结构，非恒定时间保证'),
 ]:
  papers.append(dict(id=aid,name=name,title=title,year=year,family='经典实现',idea=idea,limit=limit,url=url,code=None,tier='B',evidence='作者/项目原始资料',accessed='2026-10-13'))
 (ROOT/'papers.json').write_text(json.dumps(papers,ensure_ascii=False,indent=2),encoding='utf-8')
 md=['# 论文索引\n',f'共 {len(papers)} 项，按方法角色编排。年份为 arXiv 首次提交年（经典条目为会议/期刊年），不混同正式出版年。检索截止 2026-10-13。\n','A：已读取方法正文：预积分、FAST-LIVO2、TRaIL-Odom；B：原始摘要/作者资料核验；C：DeepXiv 摘要或检索元数据用于路线图，不用于精确性能断言。DeepXiv 自动 TLDR 仅作线索，不能等同作者原文。\n']
 families=list(dict.fromkeys(p['family'] for p in papers))
 for family in families:
  md.append(f'## {family}\n')
  for p in papers:
   if p['family']!=family: continue
   md.extend([f"### {p['name']} · {p['year']} · {p['id']}\n", f"[{p['title']}]({p['url']})\n",f"- 核心：{p['idea']}。\n- 边界：{p['limit']}。\n- 读取层级：{p['tier']} — {p['evidence']}。\n"])
   if p['code']: md.append(f"- 检索记录中的代码入口：[作者仓库]({p['code']})；未逐仓库运行验证。\n")
 md.append('## 优先阅读路径\n\nESKF → MSCKF / OpenVINS → 流形预积分 → VINS-Mono → FAST-LIO2 → FAST-LIVO2 → 多 Radar / iRIOM → TRaIL-Odom → TLIO → OpenVLA / π0 → TacVLA。\n\n完整检索策略与排除记录见 `检索记录.md`。不把引用量当作质量证据。\n')
 (ROOT/'论文索引.md').write_text('\n'.join(md),encoding='utf-8')
 return papers

if __name__=='__main__': print(len(build()),'annotated entries')
