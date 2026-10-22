// Original teaching diagrams; paper images are embedded, attributed, and zoomable.
const projectFlows={
 parkour:[['深度观测','58 × 87 / 视觉约10 Hz'],['视觉编码','CNN + GRU / 历史特征'],['运动策略','视觉 + 本体 / 约50 Hz'],['输出动作','关节目标 → PD执行']],
 dronepc:[['输入','点云 + 状态 + 目标'],['表示','3200个方向距离 / 未知区'],['推理','MLP / 控制50 Hz'],['执行','总推力 + 机体角速度']],
 dronedepth:[['输入','100 × 60深度 + 状态'],['推理','CNN + GRU / 历史记忆'],['输出','姿态参考 + 推力 / 100 Hz'],['执行','HOCBF / QP安全层 → 飞控']],
 scanflow:[['输入','点云 + 位姿 + 目标/路线'],['规划','占据地图 → A* → B-spline'],['输出','/planning/bspline → cmd_vel'],['执行','速度门 → Go2 SDK → 步态']],
 vbotflow:[['云端输入','图像历史 + 指令 + 路线'],['云端输出','4B策略 → 子目标 / 标称2 Hz'],['机载输出','RGB + LiDAR → 轨迹 / 10 Hz'],['运动执行','10点轨迹 → 控制器 / 50 Hz']],
};
const resourceRows={
 scanbudget:[['芯片 / 计算','Jetson Orin NX','论文实机平台；未给最低TOPS'],['地图 / 尺度','400万体素','10 × 10 × 5 m；分辨率0.05 m'],['内存 / 推算','约76 MB','仅七个体素数组；不含LIO与点云'],['部署 / 验收','测全链路延迟','峰值RAM、p95/p99、功耗与温控']],
 vbotbudget:[['云端 / 权重','4B × 2 B ≈ 8 GB','FP16纯权重估算；运行时另计'],['机载 / 计算','视觉 + LiDAR + 轨迹','不能用云端4B参数量代替机载预算'],['时限 / 周期','10 Hz → 100 ms','标称周期；不是已测推理耗时'],['未知 / 待测','芯片 · RAM · 码率','论文未给完整部署资源清单']],
 navbandwidth:[['相机 / 原始RGB','73.7 Mb/s','640 × 480 × 3 B × 10 Hz'],['深度 / 点云示例','49.2 / 25.6 Mb/s','16位深度 / 2万点 × 16 B × 10 Hz'],['上云 / JPEG假设','1.6 Mb/s','100 kB / 张 × 2张 / 秒'],['轨迹 / 纯载荷','12.8 kb/s','10点 × 4个float32 × 10 Hz']],
};
const navigationHints={
 scanbudget:'论文硬件 ≠ 最低配置；76 MB是数组推算，不是整机内存。',
 vbotbudget:'8 GB不含激活、KV缓存、视觉分支、框架与并发；未公开项不猜数。',
 navbandwidth:'十进制单位；以上未含协议开销。云端推理频率 ≠ 上传帧率。',
 navcontract:'定位地图用于配准；障碍地图用于避碰；参考路线用于任务引导。',
 liochain:'可靠位姿是必要接口；LIO可被满足同一时空契约的其他定位系统替换。',
 navdeploy:'组合建议，非VbotNav原版复现；云端目标必须检查时效与坐标系。',
 scanflow:'主分支ROS1 Noetic；世界点云、机身位姿与路径高度必须一致。',
 vbotflow:'2 / 10 / 50 Hz是论文标称配置；依赖预先提供的参考路线。',
 dronepc:'论文机载：Jetson Orin NX；最低RAM未给出，训练硬件另计。',
 dronedepth:'100 Hz不是相机新帧率；机载芯片与峰值RAM未明确，需连安全层一起测。',
 parkour:'官方封面作案例入口；蓝色数据流为讲解重绘，不是论文实验动画。',
};

function navigationScene(kind,k,u){
 if(projectFlows[kind]){
  const d=DATA.find(x=>x.kind===kind),items=projectFlows[kind];
  let s=R(15,20,690,485,'#F5F5F7',18);
  s+=`<g data-paper="${kind}" role="button" tabindex="0" aria-label="放大${E(d.figure_label)}"><image x="30" y="35" width="660" height="407" preserveAspectRatio="xMidYMid meet" href="${MEDIA[kind]}"/>`;
  s+=T(360,474,d.figure_label,22,M,'middle')+T(360,503,'点击查看原图 ↗',20,B,'middle')+'</g>';
  items.forEach(([title,detail],j)=>{
   const y=20+j*124;
   s+=R(770,y,805,104,j===k?'#E8F0FE':'#F5F5F7')+T(798,y+38,`${j+1}  ${title}`,27,j===k?B:I)+T(798,y+80,detail,28,j===k?I:M);
   if(j<3)s+=L(1170,y+108,1170,y+120,F,3);
   if(j===k)s+=C(790+u*760,y+100,5,B);
  });return s;
 }
 if(resourceRows[kind]){
  let s=T(35,45,'资源接口',24,M)+T(465,45,'已知数值 / 状态',24,M)+T(1000,45,'适用范围',24,M);
  resourceRows[kind].forEach(([label,value,detail],j)=>{
   const y=70+j*108;
   s+=R(20,y,1560,94,j===k?'#E8F0FE':'#F5F5F7',14)+T(45,y+57,label,29,j===k?B:I)+T(465,y+57,value,33,j===k?B:I)+T(1000,y+57,detail,23,M);
   if(j===k)s+=L(45,y+84,45+u*1505,y+84,B,3);
  });return s;
 }
 if(kind==='navcontract'){
  return pipe([['我在哪','位姿 + 时间戳'],['去哪里','目标 / 参考路径'],['怎么绕','局部无碰撞轨迹'],['怎样执行','速度 → 关节']],k,u,95)+
   T(800,335,['没有位姿，历史点云就无法放稳','没有路线，局部避障不知道任务终点','轨迹要考虑机器人尺寸和运动限制','规划方向与保持平衡，是两层工作'][k],36,B,'middle')+
   L(200,400,1400,400,F,3)+C(200+1200*u,400,9,B)+T(800,480,'同一条链，每个接口都有时间、坐标与资源预算',29,M,'middle');
 }
 if(kind==='liochain'){
  let s=card(30,30,380,'IMU预测','姿态 / 速度 / 位置',k===0)+A(430,86,570,86)+card(590,30,400,'扫描去畸变','逐点时间 → 同一时刻',k===1)+A(1010,86,1150,86)+card(1170,30,400,'几何配准','点到局部地图表面的误差',k===2);
  s+=L(160,200,160,420,I,6)+T(175,222,'参考墙面',24,M);
  for(let j=0;j<16;j++){const y=238+j*10,x=250+(j%3)*8-(k>=2?u*90:0);s+=C(x,y,4,B)+L(160,y,x,y,F,1);}
  s+=T(310,470,'LIO局部地图：服务配准',25,M,'middle');
  s+=A(420,330,590,330)+card(610,270,400,'输出：位姿 + 点云','携带时间戳和坐标系',k===3)+A(1030,330,1160,330)+card(1180,270,390,'SCAN障碍地图','服务碰撞检查',k===3);
  s+=T(1070,470,'先把测量放对，再判断哪条路能走',29,B,'middle');return s;
 }
 if(kind==='navdeploy'){
  let s=R(30,25,1530,135,'#F5F5F7')+T(65,65,'云端：意图与路线',25,M)+T(65,118,'图像摘要 + 指令 → 语义子目标',33,I)+T(1130,112,'时间戳 / 坐标 / 有效期',24,B);
  s+=A(1350,170,1350,245)+T(970,215,'机载先检查，再接纳目标',24,M);
  s+=pipe([['LIO','IMU + 点云 → 位姿'],['SCAN','局部地图 → 轨迹'],['速度门','时效 / 限幅 / 控制权'],['SDK执行','速度 → 原厂步态']],k,u,270);
  s+=T(800,475,'公网可慢；局部避障、执行与失效处理留在机载',34,B,'middle');return s;
 }
 return null;
}

function closePaper(){document.getElementById('figure-modal').hidden=true;}
function openPaper(kind){
 const d=DATA.find(x=>x.kind===kind);if(!d?.figure)return;
 playing=false;draw();
 document.getElementById('figure-full').src=MEDIA[kind];
 document.getElementById('figure-full').alt=d.figure_label;
 document.getElementById('figure-title').textContent=d.figure_label;
 document.getElementById('figure-modal').hidden=false;
 document.getElementById('figure-close').focus();
}
document.addEventListener('click',e=>{const el=e.target.closest('[data-paper]');if(el)openPaper(el.dataset.paper);});
document.addEventListener('keydown',e=>{
 if(!document.getElementById('figure-modal').hidden){if(e.key==='Escape')closePaper();e.stopImmediatePropagation();return;}
 if(['Enter',' '].includes(e.key)&&e.target.matches('[data-paper]')){e.preventDefault();openPaper(e.target.dataset.paper);e.stopImmediatePropagation();}
},true);
document.getElementById('figure-close').onclick=closePaper;
