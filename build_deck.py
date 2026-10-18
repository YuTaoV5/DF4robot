"""DF4robot — offline Keynote-style teaching deck, based on the kelip-slide frame."""
from pathlib import Path
import html, json, math, re

ROOT=Path(__file__).resolve().parent
D=ROOT/'deck'
P={p['id']:p for p in json.loads((ROOT/'research/papers.json').read_text(encoding='utf-8'))}
slides=[]
def esc(s): return html.escape(str(s))
def txt(x,y,s,size=30,color='#1D1D1F',anchor='start',weight=500):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'
def box(x,y,w,h,title,sub='',hi=False):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{"#E8F0FE" if hi else "#F5F5F7"}"{chr(32)+"stroke=\"#0071E3\" stroke-width=\"2\"" if hi else ""}/>'+txt(x+w/2,y+h/2-7 if sub else y+h/2+10,title,31,'#0071E3' if hi else '#1D1D1F','middle',600)+(txt(x+w/2,y+h/2+38,sub,23,'#6E6E73','middle') if sub else '')
def line(x1,y1,x2,y2,hi=False,arrow=True):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{"#0071E3" if hi else "#8E8E93"}" stroke-width="3"'+(f' marker-end="url(#{"arB" if hi else "ar"})"' if arrow else '')+'/>'
def svg(body): return '<div class="diagbox pad"><svg class="sv" viewBox="0 0 1600 560" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'+body+'</svg></div>'
def flow(items,desc='',highlight=-1):
 n=len(items); w=min(340, (1500-(n-1)*55)/n); start=(1600-(w*n+55*(n-1)))/2
 s=''
 for i,(a,b) in enumerate(items):
  x=start+i*(w+55); s+=box(x,175,w,170,a,b,i==highlight)
  if i<n-1:s+=line(x+w+8,260,x+w+45,260,i==highlight)
 if desc:s+=txt(800,460,desc,29,'#6E6E73','middle')
 return svg(s)
def cards(items):
 return '<div class="cards">'+''.join(f'<div class="card"><div class="big">{a}</div><div class="h">{b}</div></div>' for a,b in items)+'</div>'
def table(headers,rows):
 return '<div class="tblwrap"><table class="tbl left wrap"><thead><tr>'+''.join('<th>'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def big(rows):return '<div class="bigline">'+''.join('<div class="row">'+r+'</div>' for r in rows)+'</div>'
def formula(eq,explain,lower=''):
 return f'<div class="mathcard"><div class="eq">{eq}</div><div class="explain">{explain}</div><div class="lower">{lower}</div></div>'
def add(sec,title,body,sub='',refs=(),note='',kind=''):
 i=len(slides)+1
 src=' · '.join(f'<a href="{P[r]["url"]}" target="_blank" rel="noopener">{esc(P[r]["name"])}</a>' for r in refs)
 head=f'<div class="kicker"><b>{i:02d}</b>{sec}'+(' · '+src if src else ' · 自绘 / 综合分析')+'</div>'
 s=f'<section class="slide {kind}" data-sec="{esc(sec)}" data-title="{esc(re.sub("<[^>]*>","",title))}">'+head+f'<h1>{title}</h1>'+(f'<div class="sub">{sub}</div>' if sub else '')+body+'</section>'
 slides.append(dict(sec=sec,title=re.sub('<[^>]*>','',title),html=s,note=note,refs=list(refs)))
def divider(num,title,sub):
 add(title,title,f'<div class="dividerword"><span>{num}</span>{sub}</div>',kind='chapter')

# 01–04 · executive overview
add('导览','机器人如何融合<span class="acc">不同的世界</span>',
 svg(box(30,45,310,125,'IMU','运动连续性')+box(30,205,310,125,'Camera','纹理与语义')+box(30,365,310,125,'LiDAR / Radar','几何 / 多普勒')+line(365,105,650,260)+line(365,270,650,270)+line(365,425,650,280)+box(670,160,400,220,'状态与不确定性','时间 · 几何 · 概率',True)+line(1090,270,1220,270,True)+box(1240,175,330,190,'机器人行动','定位 → 规划 → 操作')),
 'IMU × 视觉 × LiDAR × Radar ｜ 高台感知 RL 与无地图导航 ｜ 2026-10-19',
 note='这份讲解用同一套状态估计问题串联传统和前沿方向。雷达明确分为激光 LiDAR 与射频 Radar。53 项阅读条目形成方法地图，核心机制展开推导；不是统一硬件上的性能复测。')
add('导览','建议立项：先验收定位，再按失效场景扩模态',
 cards([('基本盘','轻量平台 → VIO<br>普通巡检 → LIO'),('补短板','几何 / 纹理互补 → LIVO<br>低能见度 → 评估 Radar'),('任务层','语义操作 → VLA<br>精细接触 → 触觉 / 力')]),
 '每加一种模态，都要证明失败率下降，并覆盖算力、标定和维护成本。',
 note='企业技术负责人视角修订：先立可验收的几何概率基线，再按故障矩阵增加模态；不默认采购全套传感器。轻量平台优先 VIO、一般巡检优先 LIO；LIVO 和 Radar 以目标环境中的互补收益立项。VLA 以任务成功率与动作时效验收，不能以定位算法指标替代。此为综合工程建议。')
add('导览','三条轴，避免把所有“融合”混成一类',
 table(['分类轴','可选方案','实际问题'],[
 ['融合层级','原始 / 特征 / 状态或决策','在哪里共享信息？'],
 ['耦合程度','松耦合 / 紧耦合 / 混合','融合独立里程计，还是观测残差？'],
 ['推断方法','滤波 / 平滑 / 学习 / 策略','维护当前状态、历史轨迹，还是动作？'],
 ['时间表示','离散事件 / 预积分 / 连续轨迹','测量在什么时刻约束机器人？']]),
 note='早期特征融合、紧耦合与 EKF 不是同一分类轴。一个系统可以同时是特征级、紧耦合、滤波式、按事件更新。BEV 检测与 VLA 是更广义机器人融合应用，但不能据此宣称完成里程计。',refs=('2302.06643','2408.14035'))
add('导览','传感器的价值来自互补的观测',
 table(['传感器','原始观测','配置示例','主要薄弱点'],[
 ['IMU','角速度、比力','100–1,000 Hz','偏置 / 积分漂移 / 振动'],
 ['帧相机','像素、特征、亮度','10–60 Hz','暗光 / 模糊 / 低纹理'],
 ['LiDAR','距离、方向、点时间','5–20 扫描/s','长廊 / 平面 / 烟尘'],
 ['毫米波 Radar','距离、角度、径向速度','10–30 帧/s（成像配置）','多径 / 动态点 / 角分辨率']]),
 '频率仅为教学配置范围；扫描内仍异步。旋转 Radar 与事件相机须另建数据模型。',
 note='频率来自常见配置量级示意，不是设备规格承诺。4D Radar 中第四维通常指径向速度，不意味着直接测得完整三维速度。传感器数据率、前端计算率、状态发布率和控制率是不同量。',refs=('2311.08608','2410.15480'))

# 05–12 · probability
divider('01','概率建模','先统一状态，再解释噪声')
add('概率建模','像素、米和米每秒，共同约束同一个状态',
 svg(txt(800,60,'x = { Rᵂᴮ, pᵂᴮ, vᵂᴮ, bᵍ, bᵃ }',49,'#0071E3','middle')+box(20,185,440,155,'视觉残差','像素投影 / 光度差')+box(580,185,440,155,'LiDAR 残差','点到面距离')+box(1140,185,440,155,'Radar 残差','径向速度差')+txt(800,440,'zₛ(t) = hₛ(x(t), 外参) + nₛ',43,'#1D1D1F','middle')+txt(800,510,'B = IMU 机体坐标系；W = 世界系；Rᵂᴮ 把 B 中向量旋转到 W',25,'#6E6E73','middle')),
 refs=('1711.02508','1512.02363'),note='世界系下的位置和速度、机体姿态、陀螺及加速度偏置构成基本 15 维局部误差状态。按需要增广重力、时差、外参、曝光、轮速比例与地图。不要直接把像素与米的原始数据加权平均。')
add('概率建模','“高斯”描述局部误差，不是整张图像',
 svg(f'<ellipse cx="390" cy="280" rx="250" ry="100" transform="rotate(-25 390 280)" fill="#E8F0FE" stroke="#0071E3" stroke-width="3"/>'+line(100,420,690,420,arrow=False)+line(150,480,150,90,arrow=False)+txt(370,295,'δp ~ N(0, P)',36,'#0071E3','middle')+txt(380,510,'协方差椭圆有方向',27,'#6E6E73','middle')+box(860,130,620,130,'R = R̂ Exp(δθ)','在 SO(3) 切空间近似旋转误差',True)+box(860,320,620,130,'nₛ ~ N(0, Σₛ)','每类观测拥有自己的噪声模型')),
 refs=('1711.02508','1512.02363'),note='原始场景、像素值、回波强度和错误关联通常不是高斯变量。高斯近似常放在局部状态误差或筛选后的观测残差上。姿态不是三个任意欧氏角的全局高斯；误差注入后还需协方差重置雅可比。')
add('概率建模','每一种残差，都要有自己的噪声预算',
 table(['来源','可用初始模型','超出模型的因素'],[
 ['IMU','白噪声 + 偏置随机游走','温漂、振动、轴间耦合、饱和'],
 ['视觉','像素协方差 / 光度方差','误匹配、滚动快门、曝光、动态物体'],
 ['LiDAR','距离 / 角度噪声传播到点面残差','地图面不确定性、掠入射、离群点'],
 ['Radar','距离 / 角度 / Doppler 联合误差','多径、鬼影、动态目标、角度误差']]),
 '参数来源：离线标定 + 静态数据 + 运动数据验证；再检查创新统计。',
 refs=('1711.02508','2311.08608','2408.14035'),note='不能只给每个传感器一个永恒标量权重。外参和地图若不作为状态联合估计，应考虑其不确定性贡献。白噪声密度与每样本标准差不同；残差维度、单位和相关性都影响权重。')
add('概率建模','白化之后，异构残差才能一起优化',
 formula('r̃ₛ = Lₛ⁻¹ rₛ　　Σₛ = Lₛ Lₛᵀ','minₓ ∑ₛ ρ( rₛᵀ Σₛ⁻¹ rₛ )','像素 / 米 / 米每秒 → 无量纲残差 → 同一状态增量'),
 refs=('1512.02363','2408.14035'),note='这里 Σₛ 是该观测残差的噪声协方差；L 为 Cholesky 因子。需要统一变量定义、测量时刻和坐标系。先验同样作为白化项加入。ρ 表示鲁棒代价；纯 Gaussian 取线性平方代价。测量数量很多但相关性强时，不应获得虚假的无限信息。')
add('概率建模','调大噪声，它对后验的拉动就变小',
 '<div class="gauss-layout"><div class="plot"><svg id="gaussPlot" class="sv" viewBox="0 0 1100 500"></svg></div><div class="gauss-controls"><label>视觉位置示例 σ<sub>c</sub><input id="sigma" type="range" min="0.2" max="3" step="0.1" value="1"></label><div id="gaussValue"></div><p>先验 μ=0，σ=2<br>观测 c：z=1<br>观测 l：z=1.2，σ=0.5</p><button id="gaussReset">重置</button></div></div>',
 '一维、同一时刻、独立位置观测的教学例子；不是直接融合像素和 IMU 原始值。',
 refs=('1512.02363',),note='精度相加 P⁻¹=P₀⁻¹+σc⁻²+σl⁻²；均值为精度加权。默认 P=1/5.25=0.190476，μ=5.8/5.25=1.104762，σ=0.436436。曲线由实际公式计算。真实系统 hₛ(x) 非线性且噪声可能相关，需要雅可比和联合协方差。')
add('概率建模','重尾和多峰，需要超出单高斯的处理',
 svg('<path d="M60 400 Q180 400 270 370 Q340 330 400 170 Q450 330 520 370 Q650 400 770 400" fill="none" stroke="#A1A1A6" stroke-width="5"/>'+ '<path d="M60 400 Q170 390 270 340 Q340 320 400 260 Q470 320 540 340 Q650 390 770 400" fill="none" stroke="#0071E3" stroke-width="5"/>'+txt(410,470,'离群值：门限 + 鲁棒损失 / Student-t',27,'#0071E3','middle')+'<path d="M860 400 Q930 400 990 180 Q1050 400 1110 390 Q1190 380 1280 220 Q1370 400 1530 400" fill="none" stroke="#1D1D1F" stroke-width="5"/>'+txt(1210,470,'多假设：混合分布 / 粒子方法',27,'#1D1D1F','middle')+txt(800,80,'定性分布示意，非论文实测曲线',24,'#6E6E73','middle')),
 refs=('2204.11098','2506.00383'),note='重尾通常对应少量大误差；多峰常来自多个数据关联或定位假设。Huber/Cauchy 等 M-estimator 主要降低离群点影响；不能把所有错误关联修正为正确关联。UKF 传播 sigma points，但通常仍近似单峰均值协方差，不自动解决多峰问题。')
add('概率建模','共有 IMU，会让两个里程计彼此相关',
 svg(box(40,215,250,130,'同一 IMU','共有信息')+line(310,265,555,140)+line(310,285,555,400)+box(580,65,390,150,'VIO','视觉 + IMU')+box(580,325,390,150,'LIO','LiDAR + IMU')+line(990,140,1170,260)+line(990,400,1170,300)+box(1190,195,360,160,'融合接口','必须处理交叉协方差',True)+txt(800,535,'已知相关性：联合建模；未知相关性：考虑保守融合，避免重复计算信息',25,'#6E6E73','middle')),
 note='独立假设下简单相乘 VIO 和 LIO 的输出，可能双重使用同一 IMU 和先验。可使用共享原始状态/因子、传播交叉协方差，或在一致性条件下采用 Covariance Intersection：Pci⁻¹=ωP1⁻¹+(1−ω)P2⁻¹。CI 保守，不保证比单路更精确。重复插值也不会创造独立信息。')

# 13–19 · time
divider('02','时间处理','各按各的节奏，约束同一条轨迹')
add('时间处理','按采集时间更新，不必强制统一采样率',
 '<div class="diagbox pad"><svg class="sv" id="eventTimeline" viewBox="0 0 1600 560"></svg></div><div class="event-controls"><button data-event="0">0 ms 初始化</button><button data-event="1">50 ms Camera</button><button data-event="2">75 ms Radar</button><button data-event="3">100 ms LiDAR</button><span id="eventText">点击事件：观察先传播、后更新</span></div>',
 '教学配置：IMU 200 Hz、Camera 20 Hz、Radar 20 Hz（相位差）、LiDAR 10 Hz。',
 refs=('1512.02363','2609.03561'),note='事件调度使用采集时间而非到达时间。IMU 每 5 ms 传播；相机每 50 ms 更新；Radar 每 50 ms、相位偏移 25 ms；LiDAR 每 100 ms。状态可高频发布，但不表示所有模态都产生了新的证据。插值只在规定的运动/测量模型下用于对齐。')
add('时间处理','IMU 提供连续运动，但协方差同时增长',
 formula('Ṙ = R[ωₘ − bᵍ]×<br>v̇ = R(aₘ − bᵃ) + g　　ṗ = v','Pₖ₊₁ = Φ Pₖ Φᵀ + Qd','Qd = ∫ Φ(τ) G Qc Gᵀ Φ(τ)ᵀ dτ'),
 refs=('1711.02508','1512.02363'),note='名义状态传播使用去偏后的角速度和比力。Qd 应根据采样间隔从连续噪声谱密度积分获得，不能改变频率后沿用固定 Q。对一维白加速度噪声，位置速度块为 q[[dt³/3,dt²/2],[dt²/2,dt]]。长时间纯惯性传播会使漂移与不确定性增加。')
add('时间处理','预积分压缩 IMU，保留运动与不确定性',
 svg(box(30,180,270,170,'关键帧 i','Rᵢ, pᵢ, vᵢ, bᵢ')+''.join(f'<circle cx="{380+k*48}" cy="265" r="9" fill="#A1A1A6"/>' for k in range(12))+txt(660,155,'多次高频 IMU 测量',31,'#6E6E73','middle')+box(1080,180,480,170,'关键帧 j','Rⱼ, pⱼ, vⱼ, bⱼ')+line(340,390,1045,390,True)+txt(700,455,'ΔRᵢⱼ, Δvᵢⱼ, Δpᵢⱼ, Σᵢⱼ, Jᵦ',40,'#0071E3','middle')),
 refs=('1512.02363',),note='预积分在帧 i 局部坐标构造，减少优化迭代时重新遍历原始 IMU 的成本。因子仍同时关联端点姿态、位置、速度、偏置。Σ 与偏置雅可比 Jb 必须保留；它不是把测量做平均，也不是把 IMU 低通到相机频率。')
add('时间处理','迟到的图像，必须回到它的拍摄时刻',
 flow([('缓存历史','状态 + IMU'),('回到 tₘ','插入测量'),('更新 / 平滑','修正历史'),('重传播至今','发布新状态')], '或使用固定滞后窗口；超出窗口的数据按明确策略丢弃 / 转入后端。',2),
 note='假设图像 t=100 ms 采集，t=140 ms 到达，不能把它当作 140 ms 测量。缓存重放时要保存相关状态和协方差；延迟因子可插入仍活跃的滑窗。真采集时间偏差与网络传输延迟是不同问题。外参时差标定也不能修复所有乱序。',refs=('1808.00692','isam2'))
add('时间处理','20 ms 的时差，足以产生 10 cm 偏移',
 cards([('Δp ≈ vΔt','5 m/s × 0.02 s = 0.10 m<br>教学计算，非实测'),('Δθ ≈ ωΔt','1 rad/s × 0.02 s = 0.02 rad<br>约 1.15°'),('先标定','外参 + 时间偏移 + 内参<br>记录采集与到达时间')]),
 refs=('1808.00692','2407.11420','2408.02444'),note='这是局部一阶量级估计。常速度/单轴运动可能让时差与外参难区分，需激励多个转轴及平移。硬件同步降低误差源；在线时差估计可辅助但不是硬同步的无条件替代。温度或时间漂移可能要求更丰富的模型。')
add('时间处理','连续时间轨迹，在每个测量时刻求值',
 svg('<path d="M80 400 C350 90 500 460 790 240 S1250 140 1520 310" fill="none" stroke="#0071E3" stroke-width="7"/>'+''.join(f'<rect x="{x}" y="{y}" width="20" height="20" fill="#A1A1A6"/>' for x,y in [(120,290),(390,150),(680,380),(960,80),(1260,190),(1500,320)])+txt(800,65,'T(t) 由 B-spline / Gaussian process 等参数化',34,'#1D1D1F','middle')+txt(800,465,'rₛ = zₛ − hₛ(T(tₛ))',43,'#0071E3','middle')+txt(800,530,'自然处理逐点扫描、滚动快门和异步输入；仍需选择轨迹带宽与标定时间偏移',25,'#6E6E73','middle')),
 refs=('2202.08894','2609.03561'),note='曲线仅示意。连续轨迹以有限控制点表示，可在不同 t_s 上计算位姿、角速度和加速度；因此不一定为每条 IMU 新增独立位姿节点。过稀控制点会欠拟合快速运动，过密会增加计算与病态性。连续时间不等于零延迟。')

# 20–27 · inference
divider('03','推断算法','同一贝叶斯问题，不同计算取舍')
add('推断算法','预测给出先验，观测把它修正为后验',
 flow([('上一时刻','p(xₖ₋₁ | Z)'),('运动传播','p(xₖ | Zₖ₋₁)'),('观测似然','p(zₖ | xₖ)'),('后验','p(xₖ | Zₖ)')], 'p(xₖ | Zₖ) ∝ p(zₖ | xₖ) ∫ p(xₖ | xₖ₋₁) p(xₖ₋₁ | Zₖ₋₁) dxₖ₋₁',3),
 refs=('1711.02508','1512.02363'),note='各传感器的似然形式和频率可以完全不同，只要定义在一致状态与时刻上。条件独立时可顺序相乘；线性高斯系统的精确序贯更新与联合更新等价。非线性重线性化、共享地图及噪声相关会使实际实现具有顺序效应。')
anim=''
for k,(a,b) in enumerate([('传播','x̂⁻, P⁻'),('创新','r = z − h(x̂⁻)'),('增益','K = P⁻HᵀS⁻¹'),('注入','x̂⁺ = x̂⁻ ⊞ Kr'),('重置','更新 P 并重置 δx')]):
 anim+=f'<g data-a="s{k+1}">'+box(90,15+k*108,900,88,a,b,k==3)+'</g>'
add('推断算法','ESKF：在小误差上计算，在流形上修正',
 '<div class="row anim"><div class="diagbox pad"><svg class="sv" data-anim viewBox="0 0 1100 620">'+anim+'</svg></div><div class="stepcol">'+''.join(f'<div class="step-item"><div class="sn">{i+1}</div><div class="st"><b>{a}</b>{b}</div></div>' for i,(a,b) in enumerate([('IMU 传播','名义状态与误差协方差一起前进'),('计算创新','S = HP⁻Hᵀ + Σ；用 NIS 做门控'),('求增益','解线性方程，避免显式矩阵求逆'),('注入状态','姿态通过 Exp(δθ) 更新'),('协方差重置','Joseph 形式 + 误差重置雅可比')]))+'</div></div>',
 '按 J / K 逐步展开；这是单次 ESKF 更新，迭代版本重复线性化而不重复计入信息。',refs=('1711.02508',),note='步骤图按 J/K 手动推进。Joseph 形式 P+=(I−KH)P−(I−KH)ᵀ+KΣKᵀ，再应用误差重置的坐标变换。IESKF 迭代必须保持同一先验，不能每迭代一次就把同一测量当新信息累加。')
add('推断算法','滤波族的差异，在误差表示与近似方式',
 table(['方法','核心处理','适合 / 限制'],[
 ['KF / EKF','线性精确 / 雅可比局部线性化','EKF 初始化差时可能不稳定'],
 ['ESKF / 迭代 ESKF','名义状态 + 局部误差 / 迭代重线性化','适合惯性；迭代不增加独立测量'],
 ['InEKF','利用群对称性定义不变误差','结构满足条件时改善误差性质'],
 ['UKF','sigma points 传播均值协方差','减少手推雅可比；高维更贵'],
 ['Particle / Mixture','保留样本或多个分量','能表多峰；高维计算和退化问题']]),
 'IEKF 一词可能指 Iterated 或 Invariant；阅读论文时必须展开缩写。',refs=('1711.02508','1410.1465','2506.00383'),note='ESKF 是状态/误差表示选择，不能简单说精度永远高于 EKF。Invariant 与 iterated 是不同维度，可以结合。UKF 仍通常压缩成均值协方差。粒子法更常用于全局定位或低维假设，而非默认全状态惯性 SLAM。')
add('推断算法','MSCKF 保留相机历史，消去特征点',
 svg(''.join(box(70+i*510,130,350,130,f'相机克隆 {i+1}','位姿与交叉协方差',i==1) for i in range(3))+''.join(line(245+i*510,280,800,380) for i in range(3))+'<circle cx="800" cy="390" r="18" fill="#0071E3"/>'+txt(800,445,'同一静态特征点',29,'#6E6E73','middle')+txt(800,525,'r ≈ Hₓδx + Hfδf + n   →   Nᵀr ≈ NᵀHₓδx + Nᵀn',34,'#1D1D1F','middle')),
 refs=('msckf','openvins'),note='N 是特征雅可比 Hf 的左零空间基，NᵀHf=0。MSCKF 从多视角特征轨迹中约束相机克隆状态，避免长期维护所有路标。投影后的噪声协方差也要变换。保持不可观方向的一致性（如 FEJ）是关键，而不只是减少状态维数。')
add('推断算法','因子图让每条约束找到自己的状态',
 svg(''.join(f'<circle cx="{x}" cy="265" r="62" fill="#F5F5F7" stroke="#A1A1A6" stroke-width="2"/>'+txt(x,275,f'x{i}',34,'#1D1D1F','middle') for i,x in enumerate([250,800,1350]))+line(312,265,738,265,arrow=False)+line(862,265,1288,265,arrow=False)+''.join(f'<rect x="{x-18}" y="247" width="36" height="36" rx="4" fill="#0071E3"/>'+txt(x,220,'IMU',27,'#0071E3','middle') for x in [525,1075])+line(250,203,800,75,arrow=False)+line(1350,203,800,75,arrow=False)+'<rect x="782" y="57" width="36" height="36" rx="4" fill="#0071E3"/>'+txt(800,35,'回环 / 多视角因子',28,'#0071E3','middle')+line(800,327,800,425,arrow=False)+'<rect x="782" y="425" width="36" height="36" rx="4" fill="#0071E3"/>'+txt(800,503,'单时刻 Doppler / 已知地图观测',29,'#1D1D1F','middle')+line(90,265,188,265,arrow=False)+'<rect x="54" y="247" width="36" height="36" rx="4" fill="#A1A1A6"/>'+txt(75,330,'先验',25,'#6E6E73','middle')+txt(1330,485,'圆：状态变量',27,'#6E6E73','middle')+txt(1330,535,'方：概率因子',27,'#0071E3','middle')),
 refs=('1512.02363','isam2','2007.00258'),note='教授视角修订：变量用圆、因子用方，无向边表达依赖而非信息流。回环/多视角因子连接两个历史状态；单时刻 Doppler 在点方向和外参视作已知时可连接单个含速度状态。若同时估地图和外参，应显式增加相关变量。滑窗用 Schur 补保留旧状态先验，边缘化会使先验更稠密且冻结线性化；iSAM2 用 Bayes tree 增量求解。')
add('推断算法','低延迟选滤波，回溯能力选平滑',
 table(['维度','滤波 / 克隆滤波','固定滞后 / 因子图'],[
 ['维护状态','当前 + 有限历史克隆','窗口中的一段轨迹'],
 ['延迟观测','缓存回滚、增广或近似','插入仍活跃窗口的因子'],
 ['重新线性化','通常有限；迭代滤波可加强','可对活跃变量多次进行'],
 ['资源代价','通常可控；协方差可变稠密','依赖窗口、稀疏性与关联'],
 ['典型搭配','IMU 高频前端','后端回环 / 标定 / 历史修正']]),
 refs=('openvins','isam2','1512.02363'),note='这是计算取舍，不是精度绝对排名。固定时滞平滑仍有延迟预算，滤波也可含克隆历史。工程上可用低延迟前端与较慢后端并存，注意 map→odom 与 odom→base 的接口，避免回环跳变直接送给控制器。')
add('推断算法','融合只能补充已有信息，不能凭空制造可观性',
 svg('<rect x="50" y="140" width="760" height="270" fill="#F5F5F7" rx="20"/>'+line(100,180,760,180,arrow=False)+line(100,370,760,370,arrow=False)+box(280,225,260,90,'长廊机器人')+line(560,270,750,270,True)+txt(420,480,'沿长廊方向，几何约束可能很弱',27,'#6E6E73','middle')+txt(1190,180,'Λ = HᵀΣ⁻¹H',45,'#0071E3','middle')+txt(1190,280,'小特征值 → 弱方向',32,'#1D1D1F','middle')+txt(1190,380,'先统一量纲、子块与线性化点',29,'#6E6E73','middle')+txt(1190,480,'局部退化 ≠ 全局 gauge 自由度',27,'#1D1D1F','middle')),
 refs=('1410.1465','2609.03561','2606.25699'),note='全局平移和绕重力的全局航向在无外部参考的一般 VIO 中不可观；单目视觉还有尺度自由度，惯性需足够激励才能恢复尺度。局部 Hessian 小特征值诊断依赖变量单位、归一化、先验和线性化，不是严格可观性证明。')

# 28–36 · odometry systems
divider('04','里程计系统','从可复现基线，到多模态退化互补')
add('里程计系统','轻量平台，先建立可解释的 VIO 基线',
 table(['路线','代表','优先理由','主要约束'],[
 ['克隆滤波','MSCKF / OpenVINS','机制清楚、评估工具完整','初始化 / 纹理 / 一致性'],
 ['滑窗优化','VINS-Mono','预积分、标定、重定位','视差 / 算力 / 边缘化'],
 ['多地图 SLAM','ORB-SLAM3','回环和重定位重要','设置与纯里程计比较分开'],
 ['事件融合','事件相机 + IMU 等','高速、高动态范围任务','传感器成本与事件建模']]),
 refs=('openvins','1708.03852','2007.11898','2410.15480'),note='VIO 常适合重量和功耗敏感平台。先比较相同输入、相同回环设置和相同硬件，再讨论精度。事件相机不等于普通相机的高帧率替代，事件流需要自己的观测模型。')
add('里程计系统','LIO 用 IMU 去畸变，用地图抑制漂移',
 flow([('IMU 传播','逐点位姿'),('LiDAR 去畸变','扫描映射到参考时刻'),('点面配准','对应关系 + 鲁棒残差'),('状态 / 地图','滤波或图优化')], 'FAST-LIO2：迭代滤波 + 增量地图；LIO-SAM：因子图接入全局约束。',2),
 refs=('2107.06829','2007.00258'),note='扫描中各点采集时间不同，高速转动时整帧同时间假设造成畸变。原始点直接配准仍需要局部几何关联，不能理解为完全没有特征或数据关联。点面法在平面或长廊会退化；IMU 只能短时填补。')
add('里程计系统','FAST-LIVO2：LiDAR 更新后，再做视觉更新',
 flow([('扫描重组','按图像时刻切点'),('传播 / 去畸变','IMU 先验'),('LiDAR 更新','几何 → 体素地图'),('视觉更新','光度 + 曝光')], '已知时差与外参；统一体素地图共享几何和图像 patch。',3),
 refs=('2408.14035',),note='根据论文 IV 节 Algorithm 1：先扫描重组，再前向传播与反向去畸变；点面迭代更新，接着多层图像金字塔的视觉迭代更新。它不是所有测量自由到达即更新，也不能据其序贯概率分解声称任意非线性实现都严格顺序无关。')
add('里程计系统','LIVO 的分歧，在状态组织与视觉残差',
 table(['系统','组织方式','视觉 / 地图特点'],[
 ['LIC-Fusion 2.0','滤波、滑窗平面跟踪','在线时空标定与退化分析'],
 ['LVI-SAM','视觉惯性 / 激光惯性子系统互助','特征、深度支持与回环'],
 ['R3LIVE','LIO / VIO 协同估计','彩色点地图、光度对齐'],
 ['FAST-LIVO2','序贯 ESIKF、统一体素地图','直接 patch、平面先验、曝光估计']]),
 refs=('2008.07196','2104.10831','2109.07982','2408.14035'),note='这些方法不是同一个模块换名字。需要按目标平台的数据形式、视场重叠、同步条件、地图输出和维护成本选型。表为架构比较；不横向拼接不同论文 ATE 形成虚假排行榜。')
add('里程计系统','Doppler 约束速度在视线方向上的投影',
 svg(box(120,260,330,150,'Radar 原点','vᴿ = 平移 + 杆臂速度')+line(450,300,920,90)+line(450,320,1240,320)+line(450,350,1000,490)+''.join(f'<circle cx="{x}" cy="{y}" r="15" fill="#A1A1A6"/>' for x,y in [(940,85),(1260,320),(1020,500)])+txt(1050,170,'静态散射点',28,'#6E6E73','middle')+txt(1000,250,'dᵢ = −uᵢᵀ vᴿ + εᵢ',43,'#0071E3','middle')+txt(970,410,'不同视线 → 联立估计 vᴿ',31,'#1D1D1F','middle')+txt(800,550,'单点只有一个径向分量；视线分布不足时，完整速度仍不可观',25,'#6E6E73','middle')),
 refs=('2311.08608','2609.03561'),note='这里采用远离为正的距离变化率约定，对静态世界点 d=−uᵀvRadar。vRadar=Rᴿᴮ(RᴮᵂvWorld + ωB×tᴮᴿ)。需补偿雷达安装杆臂的旋转速度；动态目标不满足静态假设。角度不确定性也会映射到 Doppler 残差。')
add('里程计系统','Radar 既能测自速度，也能做扫描配准',
 table(['路线','代表','适用性与边界'],[
 ['速度 + IMU','Multi-Radar / DeRO','低纹理仍有速度；漂移与视向退化仍在'],
 ['速度 + 子图匹配','4D iRIOM','用几何补充姿态和地图；关联更难'],
 ['物理增强','Physical-enhanced RIO','多普勒 / RCS 帮助剔动态点和关联'],
 ['强度直接匹配','DRO','旋转 Radar、SE(2)、运动畸变建模'],
 ['Radar 原生学习','Radarize','Radar-only 对照；不是 IMU 融合方案']]),
 refs=('2311.08608','2303.13962','2402.02200','2504.20339'),note='可把速度残差作为紧耦合因子，也可先估完整速度及其协方差再输入滤波器。两阶段方法的速度协方差必须可靠。Radar 对低能见度有价值，但多径与动态场景并不会自动消失。')
add('里程计系统','四模态系统，先建立一个共享状态',
 svg(''.join(box(20,15+i*133,320,100,a,b) for i,(a,b) in enumerate([('IMU','传播 / 预积分'),('Camera','重投影 / 光度'),('LiDAR','点面 / 几何'),('Radar','多普勒 / 几何')]))+''.join(line(355,65+i*133,650,260) for i in range(4))+box(675,165,410,190,'共享估计器','x, P / 轨迹窗口',True)+line(1100,260,1210,260,True)+box(1230,160,340,200,'质量管理','门控 / 退化 / 降级')+txt(800,530,'联合建模时间、外参、误差与地图；避免叠加多个相关黑盒位姿',27,'#6E6E73','middle')),
 refs=('2609.05325','2609.03561'),note='这是综合建议架构，并非某一论文的完整复现图。因子图或滤波均可实现。共享状态可减少重复融合问题，但共享地图仍会带来相关性；系统复杂度也随同步、标定和维护接口增长。')
add('里程计系统','2026 前沿，把权重细化到方向与失效模式',
 table(['论文','核心增量','阅读边界'],[
 ['TRaIL-Odom · 09月','沿 LiDAR 弱方向增强 Doppler','连续时间；工程权重 ≠ 标定协方差'],
 ['SA-LIVO · 06月','联合信息矩阵的特征方向门控','弱方向抑制；不等于主动增强'],
 ['FIRE-LIVWO · 09月','轮速与 Radar 辅助矿井退化切换','额外轮式运动约束；场景有条件']]),
 '原始摘要与 TRaIL 方法正文已核验；公开结果仍需目标平台独立复现。',
 refs=('2609.03561','2606.25699','2609.05325'),note='TRaIL 原文说明名义权重是工程残差缩放系数，不能称为已学习或已统计校准的噪声精度。其摘要报告在三条退化序列的消融中，相对固定权重降低 RMSE ATE 86.0%、RTE 78.5%；这是限定基线与子集，不能代表所有序列或任意机器人。SA-LIVO 和 TRaIL 的方向处理逻辑不同。')

# 37–44 · learning and VLA
divider('05','学习与 VLA','让学习补充模型，再连接动作')
add('学习与 VLA','学习可以放在前端、噪声模型或整个策略',
 table(['插入位置','代表','保留下来的约束'],[
 ['特征 / 关联','DROID-SLAM 等几何学习','几何优化；原模型为视觉'],
 ['位移 + 协方差','TLIO','EKF 状态和惯性运动模型'],
 ['模态选择','Selective VIO / Raci-Net','依模型设计；需检验跨域泛化'],
 ['偏置 / 动力学','LBDU-VIO','MSCKF 框架 + 学习传播模型'],
 ['任务到动作','OpenVLA / π0','任务数据；几何约束需显式接入']]),
 refs=('2108.10869','2007.01867','1903.01534','2609.39125'),note='从外部特征到内部动力学的侵入程度逐步增加。可先冻结后端，只替换一个模块做消融。不可把一个网络的注意力权重直接解释成物理可靠度，也不能把 VLA token 融合等价为贝叶斯状态融合。')
add('学习与 VLA','学习协方差，需要准确，也需要诚实',
 flow([('训练输入','IMU / 图像 / 历史'),('网络输出','Δp 与 Σ，或偏置动力学'),('概率接口','Σ = LLᵀ + εI'),('统计检验','NIS / NEES / 覆盖率')], '用分布外数据检验不确定性；低平均误差不保证置信区间可信。',3),
 refs=('2007.01867','2609.39125'),note='典型高斯负对数似然包含 rᵀΣ⁻¹r + log det Σ，省略 log det 项会鼓励无限膨胀协方差。TLIO 学习相对位移和不确定性，LBDU 学习偏置动力学与过程噪声；后者是 2026 新预印本，不能推断长期稳定或跨 IMU 通用。')
add('学习与 VLA','状态估计回答“在哪里”，VLA 决定“做什么”',
 svg(box(60,65,650,170,'状态估计','IMU / 几何 → 位姿、速度、偏置、协方差',True)+box(890,65,650,170,'VLA 策略','视觉 / 语言 / 本体感知 → 动作块')+line(730,150,870,150,True)+line(1215,255,1215,345)+box(890,365,650,130,'控制与执行','反馈、约束、接触、目标到达')+line(865,430,385,430)+line(385,405,385,255)+txt(620,390,'新的传感器观测',28,'#6E6E73','middle')),
 refs=('2406.09246','2410.24164'),note='VLA 可能学习隐式空间表示，但典型 OpenVLA / π0 没有提供完整外部状态估计器所需的坐标系、可观性和协方差保证。移动操作机器人可把里程计、地图、任务策略和低层反馈组合起来。这个图是工程综合，不声称上述模型原生输入原始 Radar 和 IMU。')
add('学习与 VLA','VLA 从动作 token，走向连续动作块',
 table(['代表','融合与动作表示','对本任务的意义'],[
 ['RT-2 / OpenVLA','视觉语言条件 → 动作 token','语义知识进入操作决策'],
 ['Octo','模块化观测 → 扩散动作头','适配新输入，但仍需训练'],
 ['π0','VLM + flow matching 动作专家','连续、多步动作生成'],
 ['π0.5','异构数据与语义子任务共训练','扩展长时任务泛化'],
 ['TacVLA','接触门控触觉 token','操作阶段有条件启用额外感知']]),
 refs=('2307.15818','2406.09246','2405.12213','2410.24164','2603.12665'),note='不要用 VLA 参数规模或单数据集成功率替代选型。需要同一任务、相同观测历史、相同动作范围与训练预算比较。π0.5 的数据共训练也不同于传感器级的高斯融合。')
add('学习与 VLA','动作块的生成与执行，发生在两条时间线上',
 svg(box(30,180,300,160,'多模态条件','图像 / 语言 / 本体')+line(345,260,500,260)+box(520,180,400,160,'Flow / Diffusion','噪声 → 条件动作分布',True)+line(940,260,1080,260,True)+box(1100,180,460,160,'动作块 aₜ:ₜ₊H','执行部分，再重新规划')+txt(800,65,'训练：拟合条件动作分布；执行：受反馈约束的滚动控制',30,'#6E6E73','middle')+txt(800,455,'动作输出可高频执行 ≠ 大模型每个控制周期都重新推理',31,'#1D1D1F','middle')+txt(800,525,'推理时间、观测年龄、动作缓冲长度，需要分别测量',26,'#6E6E73','middle')),
 refs=('2303.04137','2410.24164'),note='Diffusion Policy 使用动作去噪分布；π0 使用 flow matching 向量场，不能把两者训练目标混同。二者可以通过滚动执行提供动作块。高控制频率不会消除观测延迟；执行旧动作块可能降低对突发接触的反应。')
add('学习与 VLA','触觉只在有接触时启用，是有条件的融合',
 flow([('接触检测','触觉 / 力信号'),('门控 token','无接触时抑制'),('跨模态策略','视觉 + 语言 + 触觉'),('动作反馈','抓取 / 拆卸 / 调整')], 'TacVLA：接触感知门控；Tactile-VLA：触觉反馈与位置 / 力控制。',1),
 refs=('2603.12665','2507.09160'),note='TacVLA v4 的摘要明确提出接触感知门控，并在拆卸、箱内拾取等任务评估。这里不引用其百分比以避免基线与分母口径不清。该机制启发“按任务阶段选模态”，但尚不能证明 IMU-Camera-Radar 统一 VLA 已替代经典里程计。')
add('学习与 VLA','异步策略的输入，也应携带时间与有效性',
 svg(box(30,50,410,150,'几何状态通路','IMU 传播 + 多模态修正',True)+box(30,340,410,150,'语义观测通路','最新图像 / 触觉 / 语言')+line(460,125,660,255)+line(460,415,660,285)+box(680,185,440,175,'策略输入契约','值 + 时间戳 + age + mask')+line(1140,270,1230,270)+box(1250,185,310,175,'动作管理','时效 / 反馈 / 降级')),
 '工程建议架构：多速率估计器与较慢策略并行，明确每份输入的采集时间。',
 note='不同频率可通过短历史窗口、时间编码、有效性 mask、年龄 age、按任务触发的查询处理。训练时应覆盖丢帧和时差，部署时设置最大观测年龄和动作缓存长度。此为设计建议，不声称现有 OpenVLA 原生实现全部接口。')

# 45–52 · deployment
from task_slides import register
register(globals())

divider('06','落地选择','按环境与验收选型，而不是按模型热度')
add('落地选择','先识别失效环境，再决定增加什么传感器',
 table(['机器人任务','建议起点','升级触发条件'],[
 ['轻量无人机 / XR','相机 + IMU：OpenVINS / VINS','暗光高速 → 事件 / 额外测距'],
 ['室内 AMR / 巡检','LiDAR + IMU：FAST-LIO2 / LIO-SAM','长廊低几何 → 相机 / 轮速等'],
 ['室外建图 / 移动操作','LIVO：FAST-LIVO2 等','天气 / 退化 → Radar 速度约束'],
 ['矿井 / 烟尘 / 低能见度','Radar + IMU，并评估轮速 / LiDAR','多径动态 → 鲁棒关联与方向检测'],
 ['接触操作','状态估计 + VLA / 专用策略','遮挡与精细接触 → 触觉 / 力反馈']]),
 '以上为工程选型建议，最终以目标平台的数据回放与闭环实测决定。',
 refs=('openvins','2107.06829','2408.14035','2609.05325','2603.12665'),note='并不建议所有机器人都装齐四类传感器。新增传感器只有在补充有效约束且维护成本可接受时才有价值。轮式、腿式、飞行平台的运动先验不同，不能复制同一套参数。')
add('落地选择','失效时，应明确降级而不是继续输出高置信度',
 flow([('质量监测','残差 / 可观性 / age'),('局部降权','隔离坏模态或方向'),('短时惯性','不确定性增长'),('恢复 / 停止','重定位 / 限速 / 请求接管')], '恢复必须有滞回和一致性检查，避免在好坏模态之间反复跳变。',3),
 refs=('2609.05325','2609.03561'),note='质量管理不应只看单一残差均值，还包括内点率、观测年龄、特征方向和连续异常。设定可操作的限速或停止规则由任务风险决定；这里是架构说明，不提供未经验证的安全保证。')
add('落地选择','一个数据集，无法验证所有融合主张',
 table(['数据层','候选数据','要检验的问题'],[
 ['VIO','EuRoC / TUM-VI','初始化、视觉中断、时间偏差'],
 ['LIVO','论文配套 / HILTI / 自采','点时间、曝光、几何与纹理退化'],
 ['多季节 / Radar','Boreas / Boreas Road Trip','天气、旋转扫描、Doppler 可用性'],
 ['4D Radar 多模态','NTU4DRadLM','相机、IMU、LiDAR 与成像 Radar'],
 ['策略闭环','固定任务集 + 新物体 / 新场景','成功率、恢复、接触与长期运行']]),
 refs=('2203.10168','2309.00962','2602.16870'),note='确认真实发布数据包含所需原始量，尤其是 Doppler、独立 IMU 和逐点时间戳。训练/测试按场景、机器人、传感器或采集日期隔离，不能随机切相邻帧制造数据泄漏。VLA 使用任务成功率，不能与 ATE 直接排名。')
add('落地选择','准确率、可信度与实时性，必须同时验收',
 table(['维度','记录指标','常见误判'],[
 ['精度','ATE / RPE；旋转与平移分开','混用 SE(3) 与 Sim(3) 对齐'],
 ['鲁棒性','失败率 / 重定位时间 / 最差序列','删除失败轨迹后只报均值'],
 ['可信度','NIS / NEES / 覆盖率','NEES 需真值及一致误差坐标'],
 ['实时性','端到端延迟 P50/P95/P99','只报模型推理平均耗时'],
 ['资源 / 任务','功耗、内存、任务成功率','跨硬件横比 FPS / ATE']]),
 '时效预算示例：若 eₜ = 0.10 m、vₘₐₓ = 5 m/s，则 age ≤ eₜ / vₘₐₓ = 20 ms。',
 note='企业与教授视角修订：时效预算由任务导出，示例 20 ms 仅限制一阶时间滞后误差，不是总定位误差保证。ATE/RPE 要固定对齐和间隔；NEES 需真值、一致误差坐标及 gauge 处理。NIS 在模型和近似成立时才可与参考分布比较；门控后的选择偏差会影响统计。记录失败率和延迟尾部，不能只报告成功片段与均值。')
add('落地选择','证明融合有效，要做可归因的消融',
 table(['消融维度','保持不变','观察变化'],[
 ['IMU+V / IMU+L / IMU+R / 联合','同数据、标定、硬件与回环设置','互补收益和额外计算'],
 ['固定 / 自适应噪声或方向权重','同前端与关联','覆盖率、失败率与最坏误差'],
 ['正确 / 错误时间偏移、丢帧、乱序','同轨迹与种子','延迟敏感度、恢复能力'],
 ['纯几何 / 学习增强','相同训练测试隔离','分布外泛化和不确定性'],
 ['策略带 / 不带状态与触觉','任务、示教与执行预算一致','闭环成功及接触失效']]),
 '先冻结基线和评价协议，再看新模态是否带来可重复的增益。',
 note='需要报告完整序列、失败数、运行配置、随机种子和置信区间。若方法使用更好同步、更高端 IMU 或额外先验，应单独列出。不要把回环导致的全局改善归因于前端多传感器融合。')
add('落地选择','四个阶段，每一步都有继续投入的门槛',
 table(['阶段','交付与责任','继续投入的条件'],[
 ['A · 基线','估计团队：标定 + 数据回放 + 基线','达到任务精度与时效预算'],
 ['B · 退化','系统团队：故障矩阵 + 降级恢复','新增模态降低关键场景失败率'],
 ['C · 学习','算法团队：消融 + 跨设备测试','增益覆盖算力与数据维护成本'],
 ['D · 策略','产品 / 控制团队：闭环任务验证','成功率提升且动作时效达标']]),
 '总投入 = 传感器 + 同步与标定 + 算力 / 功耗 + 数据 + 持续维护。',
 note='企业技术负责人视角修订：用阶段门槛管理投入，不杜撰设备单价和项目周期。每阶段归档硬件版本、数据、配置、指标与失败分析。若增模态只提升均值却增加失效或维护成本，应回退或限定应用范围。此为建议责任分工和验收框架，并非实际项目排期。')
add('落地选择','明确结论：统一的是状态、时间与证据',
 big(['<span class="acc">不同频率：</span>传播到观测时刻，再更新或优化。','<span class="acc">不同噪声：</span>在残差空间建模，白化并检验一致性。','<span class="acc">工程主线：</span>几何概率基线 + 鲁棒退化管理。','<span class="acc">前沿增量：</span>学习可靠性与策略，保留可验证接口。']),
 note='选型没有脱离场景的冠军。优先投资正确时间戳、标定、关联、观测质量和评估闭环。在这之上比较算法才能得到可信结论。')

def reading(ids):
 return '<div class="reading">'+''.join(f'<a href="{P[i]["url"]}" target="_blank" rel="noopener"><b>{esc(P[i]["name"])}</b><span>{P[i]["year"]} · {i}</span><p>{esc(P[i]["idea"])}</p></a>' for i in ids)+'</div>'
add('阅读入口','核心阅读：从误差状态到联合里程计',reading(['1711.02508','msckf','1512.02363','1708.03852','2107.06829','2408.14035']), '点击卡片打开原始资料；完整 53 项索引见配套材料。',note='核心理论先读 ESKF 与预积分，随后读 MSCKF/OpenVINS、VINS、FAST-LIO2 和 FAST-LIVO2。每次阅读都回答状态、观测、时间、噪声、关联和可观性六个问题。')
add('阅读入口','前沿阅读：自适应几何与多模态行动',reading(['2609.03561','2606.25699','2609.39125','2406.09246','2410.24164','2603.12665']), '检索截止 2026-10-13 ｜ 新论文单独标注证据边界 ｜ 角色审阅见附文',note='2026 年条目已核验 arXiv 原始页面；方法接收状态只按页面评论转述，不能据此推断已完成独立复现。两类角色审阅为模拟视角，不代表华为或任何高校的实际评价。')

extra_css='''
:root{--font:"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif}
.sv text{font-family:var(--font)}
h1{font-size:62px}.kicker{letter-spacing:.045em;font-size:20px}.kicker a{color:inherit;text-decoration:none}
.kicker a:hover{color:var(--accent)}.tbl.left td{font-size:27px;line-height:1.4;padding:21px 18px}.tbl th{letter-spacing:0;font-size:25px}.tbl.left td:nth-child(2){color:var(--ink)}
.mathcard{flex:1;margin-top:44px;border-radius:26px;background:#fff;padding:60px;display:flex;flex-direction:column;justify-content:center;text-align:center;gap:44px}
.eq{font-size:49px;line-height:1.7;color:var(--accent);font-family:var(--font)}.explain{font-size:37px;line-height:1.5}.lower{font-size:28px;color:var(--muted)}
.dividerword{flex:1;display:flex;flex-direction:column;justify-content:center;font-size:79px;font-weight:600;line-height:1.4}.dividerword span{font-size:140px;color:var(--accent);font-family:var(--mono)}
.chapter h1{font-size:46px;color:var(--muted)}.chapter .kicker{display:none}
.gauss-layout{display:flex;gap:40px;flex:1;min-height:0;margin-top:44px}.plot{flex:2;background:#fff;border-radius:26px;display:flex;align-items:center;padding:20px}.plot svg{width:100%}.gauss-controls{flex:1;background:#fff;border-radius:26px;padding:40px;display:flex;flex-direction:column;justify-content:center;gap:25px;font-size:29px}.gauss-controls p{color:var(--muted);font-size:26px;line-height:1.7}input[type=range]{width:100%;margin-top:22px;accent-color:var(--accent)}#gaussValue{font-size:32px;line-height:1.6;color:var(--accent)}
button{font-family:var(--font);border:1px solid #D2D2D7;background:#fff;padding:12px 20px;border-radius:12px;font-size:22px;cursor:pointer}button:hover{background:#E8F0FE;color:#0071E3}.event-controls{display:flex;align-items:center;gap:16px;margin-top:24px}.event-controls span{font-size:22px;color:var(--muted);margin-left:12px}
.reading{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:22px;flex:1;min-height:0;margin-top:42px}.reading a{display:block;padding:26px 32px;background:#fff;border-radius:22px;text-decoration:none;color:var(--ink)}.reading b{font-size:29px}.reading span{display:block;font-size:21px;color:var(--accent);margin-top:8px}.reading p{font-size:24px;color:var(--muted);line-height:1.4;margin-top:9px}
#notes{display:none;position:fixed;right:20px;bottom:20px;width:min(800px,85vw);max-height:70vh;overflow:auto;padding:28px;background:#fff;border:1px solid #D2D2D7;border-radius:18px;box-shadow:0 12px 60px #0003;z-index:30;font-size:20px;line-height:1.7}#notes.open{display:block}#notes h2{font-size:24px;margin-bottom:12px}#notes a{color:#0071E3}#notes-toggle{position:fixed;right:16px;bottom:14px;z-index:25;opacity:.6;font-size:16px}
.bigline .row{font-size:44px}.card .big{font-size:49px}.card .h{font-size:29px;line-height:1.65}
'''
extra_js=r'''
const notesData=__NOTES__;
const nPanel=document.getElementById('notes');
function renderNotes(){const i=Number(location.hash.slice(1)||1)-1;const n=notesData[i];if(!n)return;nPanel.innerHTML='<h2>'+String(i+1).padStart(2,'0')+' · '+n.title+'</h2><p>'+n.note+'</p><div>'+n.sources.map(s=>'<a href="'+s.url+'" target="_blank" rel="noopener">'+s.name+'</a>').join(' · ')+'</div>';}
document.getElementById('notes-toggle').onclick=e=>{e.stopPropagation();renderNotes();nPanel.classList.toggle('open');};nPanel.onclick=e=>e.stopPropagation();
addEventListener('keydown',e=>{if(e.key.toLowerCase()==='n'){renderNotes();nPanel.classList.toggle('open');}});
new MutationObserver(renderNotes).observe(document.getElementById('nb-pg'),{childList:true});
function drawGaussian(){const sigma=+document.getElementById('sigma').value;const precision=.25+1/(sigma*sigma)+4;const v=1/precision;const m=(1/(sigma*sigma)+4.8)/precision;const st=Math.sqrt(v);const g=document.getElementById('gaussPlot');let s='';
 const peak=1/(Math.min(2,sigma,.5,st)*Math.sqrt(2*Math.PI));
 const X=x=>70+(x+4)/8*960,Y=y=>420-y*320/peak;
 s+='<line x1="70" y1="420" x2="1030" y2="420" stroke="#A1A1A6"/>';
 for(let x=-4;x<=4;x++)s+='<text x="'+X(x)+'" y="458" text-anchor="middle" fill="#6E6E73" font-size="24">'+x+'</text>';
 for(const [mu,sd,c,dash] of [[0,2,'#A1A1A6',''],[1,sigma,'#6E6E73','10 6'],[1.2,.5,'#1D1D1F','3 5'],[m,st,'#0071E3','']]){let p='';for(let k=0;k<=400;k++){const x=-4+k*.02,y=Math.exp(-.5*((x-mu)/sd)**2)/(sd*Math.sqrt(2*Math.PI));p+=(k?' L':'M')+X(x)+','+Y(y);}s+='<path d="'+p+'" fill="none" stroke="'+c+'" stroke-width="4" stroke-dasharray="'+dash+'"/>';}
 s+='<text x="80" y="45" fill="#6E6E73" font-size="26">灰：先验 / 视觉 / 测距似然　蓝：后验</text><text x="80" y="85" fill="#6E6E73" font-size="22">密度峰值 '+peak.toFixed(2)+' /m · 纵轴自适应</text><text x="550" y="490" text-anchor="middle" font-size="23" fill="#6E6E73">位置 x（m） · 纵轴为概率密度（1/m）</text>';g.innerHTML=s;document.getElementById('gaussValue').innerHTML='σc = '+sigma.toFixed(1)+' m<br>后验 μ = '+m.toFixed(3)+' m<br>后验 σ = '+st.toFixed(3)+' m';window.gaussianResult={mean:m,variance:v,sigma:st};}
document.getElementById('sigma').addEventListener('input',drawGaussian);document.getElementById('gaussReset').onclick=()=>{document.getElementById('sigma').value=1;drawGaussian();};drawGaussian();
function timeline(which=0){const g=document.getElementById('eventTimeline');let s='';const selected=[0,50,75,100][which];const rows=[['IMU · 200 Hz',Array.from({length:21},(_,k)=>k*5)],['Camera · 20 Hz',[0,50,100]],['Radar · 20 Hz',[25,75]],['LiDAR · 10 Hz',[0,100]]];
 rows.forEach(([label,ts],i)=>{const y=80+i*115;s+='<text x="25" y="'+(y+10)+'" font-size="29" fill="#1D1D1F">'+label+'</text><line x1="370" y1="'+y+'" x2="1510" y2="'+y+'" stroke="#D2D2D7" stroke-width="2"/>';for(const t of ts){const x=400+t*10.7;s+='<circle cx="'+x+'" cy="'+y+'" r="'+(i?13:7)+'" fill="'+(t<=selected?'#0071E3':'#A1A1A6')+'"/>';}});
 [0,25,50,75,100].forEach(t=>s+='<text x="'+(400+t*10.7)+'" y="535" text-anchor="middle" font-size="24" fill="#6E6E73">'+t+' ms</text>');g.innerHTML=s;document.getElementById('eventText').textContent=['初始状态与起始观测','传播至 50 ms → 视觉更新','传播至 75 ms → Doppler 更新','传播至 100 ms → 几何 / 视觉更新'][which];}
document.querySelectorAll('[data-event]').forEach(b=>b.onclick=()=>timeline(+b.dataset.event));timeline();
'''

def build():
 assert len(slides)==70, len(slides)
 template=(D/'template.html').read_text(encoding='utf-8')
 start=template.index('<!-- ===== 1 '); end=template.index('\n</div>\n<div id="nav-hot">',start)
 result=template[:start]+'\n'.join(s['html'] for s in slides)+template[end:]
 result=re.sub(r'<title>.*?</title>','<title>DF4robot · 多传感器融合，从 Kalman 到 VLA</title>',result)
 result=result.replace('</style>',extra_css+'\n</style>')
 result=result.replace("const PH=[ ['s1'], ['s1','s2'] ];", "const PH=Array.from({length:5},(_,i)=>Array.from({length:i+1},(_,j)=>'s'+(j+1)));")
 result=result.replace("a,#nav-panel,#nav-btn,#nav-hot", "a,button,input,#notes,#nav-panel,#nav-btn,#nav-hot")
 result=result.replace("addEventListener('keydown',e=>{", "addEventListener('keydown',e=>{ if(e.target.matches('input,textarea,select')) return;")
 result=result.replace("if(n===cur) return;", "if(n===cur) return;")
 notes=[dict(title=s['title'],note=s['note'],sources=[dict(name=P[r]['name'],url=P[r]['url']) for r in s['refs']]) for s in slides]
 result=result.replace('</body>','<button id="notes-toggle">N · 讲稿</button><aside id="notes"></aside><script>'+extra_js.replace('__NOTES__',json.dumps(notes,ensure_ascii=False))+'</script></body>')
 (D/'deck.html').write_text(result,encoding='utf-8')
 (D/'slides.json').write_text(json.dumps([dict(page=i+1,**{k:v for k,v in s.items() if k!='html'}) for i,s in enumerate(slides)],ensure_ascii=False,indent=2),encoding='utf-8')
 md=['# 逐页讲稿\n','与 `deck.html` 同源生成；演示时按 N 可查看。\n']
 for i,s in enumerate(slides):
  md.append(f"## {i+1:02d} · {s['title']}\n\n{s['note']}\n")
  if s['refs']:md.append('来源：'+'；'.join(f"[{P[r]['name']}]({P[r]['url']})" for r in s['refs'])+'。\n')
 (D/'讲稿.md').write_text('\n'.join(md),encoding='utf-8')
 print('Built',len(slides),'slides;',len(result),'characters')

if __name__=='__main__':build()
