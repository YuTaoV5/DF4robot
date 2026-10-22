"""Navigation chapter: source-backed facts separated from engineering estimates."""

PAPERS = {
 'scan': ('SCAN-Planner · 论文', 'https://arxiv.org/abs/2606.19555'),
 'vbot': ('VbotNav-0 · 论文', 'https://arxiv.org/abs/2610.14634'),
 'liochain': ('FAST-LIO2 · 论文', 'https://arxiv.org/abs/2107.06829'),
 'budget': ('资源口径与推算', '../research/导航章节设计与来源.md'),
}

def extend_slides(slides, sources):
    sources.update(PAPERS)
    new = []
    def add(title, sub, kind, steps, note, src='budget'):
        new.append(dict(sec='从感知走向导航', title=title, sub=sub, kind=kind,
                        steps=[dict(label=a, caption=b) for a,b in steps],
                        note=note, source=sources[src]))

    add('会迈腿以后，还要决定往哪里走','导航的四个接口：我在哪 → 去哪里 → 怎么绕 → 怎样执行。','navcontract',[
        ('定位','把点云放进稳定的坐标系，知道机器人当前在哪里。'),
        ('路线','任务层给目标点或参考路径；一条路线可以跨多个局部地图。'),
        ('轨迹','局部规划结合机身尺寸和障碍，生成下一段可执行运动。'),
        ('执行','跟踪器产生速度指令，底层运动控制器负责关节与平衡。')],
        '接续前面的运动策略：运动能力不等于目标导航。后面用LIO解释定位接口、SCAN解释几何规划、VbotNav解释云边任务分工。四个模块可以替换，但坐标、时间戳、输出类型和失效行为必须保持契约。')

    add('先算清“我在哪”，点云才能对齐','LiDAR-Inertial Odometry：雷达—惯性里程计，为SCAN提供可靠位姿。','liochain',[
        ('预测','IMU先预测姿态、速度和位置，填补两帧雷达之间的运动。'),
        ('去畸变','用逐点时间和运动轨迹，把同一扫描中的点对齐。'),
        ('校正','将点云与局部地图配准，用几何残差修正状态和IMU偏置。'),
        ('交给SCAN','输出带时间戳的位姿与点云；SCAN据此建立局部障碍地图。')],
        'SCAN关联定位项目是Elevator-LIO，源于FAST-LIO2路线。定位内部地图用于配准，SCAN占据地图用于碰撞判断，两者目的不同。可靠位姿是必要接口，但并非只能使用LIO；其他定位系统也可替换。你此前遇到的IMU覆盖不足应先解决，不能通过伪造时间戳或扩大队列掩盖。本文未执行真机修复。', 'liochain')

    add('SCAN：把目标变成绕开障碍的轨迹','点云 + 位姿 + 目标/路径 → 局部地图 → B-spline → 速度指令。','scanflow',[
        ('输入','PointCloud2描述障碍；Odometry描述机身和传感器位姿。'),
        ('规划','双圆柱考虑机身朝向，投影A*提供绕障引导，B-spline优化轨迹。'),
        ('输出','发布 /planning/bspline；闭环跟踪器再输出 cmd_vel。'),
        ('真机接入','Go2还需速度门与SDK执行层；SCAN本身不生成关节步态。')],
        '检查上游提交348e8a5。主分支Noetic；navi_mode=1目标点、2关键点、3参考路径。模式3订阅/initial_path（nav_msgs/Path），会给路径z加body_height，且不自动按frame_id做坐标转换。世界点云不能再按传感器点重复变换。论文边界脱困与当前公开主分支实现不能直接等同。', 'scan')

    add('SCAN主要吃几何计算与地图内存','论文实机：Jetson Orin NX；这不是最低芯片要求，也不是纯GPU任务。','scanbudget',[
        ('计算位置','LIO、点云融合、A*和优化需要机载计算；主规划路径主要是CPU工作。'),
        ('地图规模','默认10×10×5米、5厘米体素，对应400万个体素。'),
        ('内存预算','七个体素数组约76 MB；整套进程还要加LIO、点云、搜索和ROS。'),
        ('测量验收','实测延迟与峰值RAM；5厘米改2.5厘米，同体积体素内存约增8倍。')],
        '论文实机所有模块运行于Orin NX，仿真CPU为i9-14900K，不能混写。76MB来自源码常见ABI：8+1+4+2+2+1+1=19B/体素，乘4百万；仅七个数组，不含A*、点云、LIO地图和RViz，不是整机RAM最低值。GPU仿真渲染选项不等于规划器要求CUDA。原文没有给通用最低RAM/TOPS/传感器带宽；验收需记录全链路p95/p99延迟、内存峰值与温控。', 'scan')

    add('VbotNav：云端想方向，机载持续避障','云端产生子目标；机载用最新RGB与LiDAR，持续重算局部轨迹。','vbotflow',[
        ('云端输入','图像历史 + 导航指令 + 参考路线，交给4B云端策略。'),
        ('云端输出','输出子目标指导；不是给机器人下载新网络权重。'),
        ('机载输出','RGB与LiDAR融合后生成10点轨迹，再交给独立运动控制器。'),
        ('异步协作','云端结果未到时，机载沿用有效指导；过期与断连由监督层处理。')],
        '论文标称2Hz云端、10Hz机载、50Hz运动控制，并非端到端延迟实测。每个轨迹点为(x,y,sinψ,cosψ)。室内依赖提前规划的参考路线，不能当成开箱即用的未知环境探索。公开检索找到VitaDynamics/vbot-lab开发工具和vbot_ros2_msgs接口，尚未找到VbotNav完整模型代码/权重；团队工具仓库不是论文实现。', 'vbot')

    add('VbotNav的算力，要按云端与机载分账','已知模型结构，不等于已知最低芯片、显存与上行网络规格。','vbotbudget',[
        ('云端权重','4B模型若用FP16/BF16，仅权重约8 GB；运行时需求更高。'),
        ('机载计算','视觉编码 + LiDAR BEV + 轨迹网络，适合评估GPU推理与加速。'),
        ('时限预算','标称10Hz机载循环对应100ms周期；须测完整链路，不能只测网络前向。'),
        ('尚未披露','完整芯片、峰值RAM/显存、网络码率未明确；不能据此承诺某板卡可跑。')],
        '8GB为4×10^9参数×2字节的十进制算术下界，不含视觉分支额外开销、KV缓存、激活、框架或并发；不是部署容量建议。机载有DINOv3、DA2-Small、LiDAR BEV融合和flow-matching轨迹网络；没有完整权重和部署配置，不能给可靠TOPS、FPS或内存最低值。要记录输入大小、精度、推理引擎、p95/p99时延、功耗和网络条件。', 'vbot')

    add('带宽先看：跨网络的是图像，还是目标？','下面是可重算的教学载荷，不是任何论文的实测码率。','navbandwidth',[
        ('原始相机','640×480、RGB8、10Hz：约73.7 Mb/s；还没计算协议开销。'),
        ('深度与点云','同尺寸16位深度约49.2 Mb/s；示例点云约25.6 Mb/s。'),
        ('压缩上传','假设每张JPEG 100 kB、每秒2张，约1.6 Mb/s；实际取决于画面与编码。'),
        ('小量指导','10点×4个float32×10Hz仅12.8 kb/s；云端频率不等于传感器上传频率。')],
        '十进制单位：RGB=640×480×3×10×8；深度=640×480×2×10×8；点云假设2万点/包、point_step=16B、10Hz，得到25.6Mb/s，不能当MID360规格。JPEG示例100kB×2×8=1.6Mb/s；历史多帧、多相机或重复上传会增加。轨迹载荷10×4×4×10×8=12800b/s；不是Vbot实测传输协议。公网需测延迟、抖动、丢包和重连；原始点云留机载可减轻网络负担。')

    combination = dict(sec='把方案接回Go2',title='让云端决定意图，让机载守住实时闭环',
        sub='工程建议：可靠定位 → 局部避障 → 有保护的执行，最后再接语言导航。',kind='navdeploy',
        steps=[dict(label=a,caption=b) for a,b in [
            ('先定位','MID360 + IMU → LIO；先验证时序、静止漂移、点云与TF一致性。'),
            ('再规划','SCAN接收点云、位姿和目标，先完成低速、短距离、平地导航。'),
            ('接执行','轨迹跟踪 → 速度门 → Unitree SDK；超时、失定位和急停在机载处理。'),
            ('最后上云','云端下发带时间戳和坐标系的目标；机载检查有效性，再交给SCAN。')]],
        note='这是借鉴云边分工的工程组合，不是VbotNav原版复现。高飞团队两篇论文直接输出飞行动作；SCAN输出轨迹/速度；VbotNav分层输出子目标/轨迹，各自接口不能直接互换。无需为了云端语义推理把Go2 Noetic链整体改为ROS2。验收应覆盖过期目标、乱序结果、断网、定位掉线和控制权接管。',source=sources['budget'])

    result = slides[:15] + new + slides[15:17] + [combination] + slides[17:]
    links = {
        'parkour': [('论文','https://extreme-parkour.github.io/resources/parkour.pdf'),('项目','https://extreme-parkour.github.io/'),('代码','https://github.com/chengxuxin/extreme-parkour')],
        'dronepc': [('论文 · arXiv:2503.00496','https://arxiv.org/abs/2503.00496')],
        'dronedepth': [('论文 · arXiv:2602.08653v2','https://arxiv.org/abs/2602.08653v2')],
        'lio': [('FAST-LIO2论文','https://arxiv.org/abs/2107.06829'),('FAST-LIO代码','https://github.com/hku-mars/FAST_LIO')],
        'liochain': [('FAST-LIO2论文','https://arxiv.org/abs/2107.06829'),('Elevator-LIO','https://github.com/xiaofan4122/Elevator-LIO')],
        'scanflow': [('论文','https://arxiv.org/abs/2606.19555'),('项目','https://wuyi2121.github.io/SCAN-Planner/'),('代码','https://github.com/wuyi2121/SCAN-Planner')],
        'scanbudget': [('论文实机配置','https://arxiv.org/html/2606.19555v1'),('代码与资源推算','../research/导航章节设计与来源.md')],
        'vbotflow': [('论文','https://arxiv.org/abs/2610.14634'),('团队工具 · 非模型代码','https://github.com/VitaDynamics/vbot-lab')],
        'vbotbudget': [('论文','https://arxiv.org/html/2610.14634v1'),('估算口径','../research/导航章节设计与来源.md')],
    }
    images={'parkour':'parkour.jpg','scanflow':'scan.jpg','vbotflow':'vbot.png',
            'dronepc':'dronepc.jpg','dronedepth':'dronedepth.png'}
    labels={'parkour':'Extreme Parkour · 官方演示封面','scanflow':'SCAN-Planner · 官方实机封面',
            'vbotflow':'VbotNav-0 · 论文 Figure 1','dronepc':'Flying on Point Clouds · 论文实机图',
            'dronedepth':'Safety-Shielded RL · 论文室外图'}
    for i,s in enumerate(result):
        s['page']=i+1
        s['links']=links.get(s['kind'],[s['source']])
        if s['kind'] in images:
            s['figure']=images[s['kind']]; s['figure_label']=labels[s['kind']]
    result[-1]['note']='本讲26页。主线从测量对齐、状态估计、局部表示与动作，延伸到LIO、SCAN和云边导航。论文硬件、代码推算、教学带宽例子分别标记；没有把配置频率当作延迟实测，也没有声称新增真机验证。'
    result[-1]['steps'][3]['caption']='闭环动作还要满足时效、算力、内存和带宽预算；接口失效时必须有明确行为。'
    for s in result:
        if s['kind']=='dronepc':
            s['note']+=' 论文机载使用Jetson Orin NX，估计与GPU推理在机载执行；没有给统一最低RAM。未确认2025这篇论文的独立代码库，不链接2018/2019同名pointcloudTraj。'
        if s['kind']=='dronedepth':
            s['note']+=' 本次所读版本未明确机载芯片与峰值内存，不能由100Hz倒推出硬件规格；需连同安全QP一起测试。未确认官方独立代码仓库。'
    return result
