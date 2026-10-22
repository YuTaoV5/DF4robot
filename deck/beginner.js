// All animation state is local. No network, external fonts, or libraries.
const B='#0071E3',I='#1D1D1F',M='#6E6E73',F='#D2D2D7';
const E=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const T=(x,y,s,z=28,c=I,a='start')=>`<text x="${x}" y="${y}" font-size="${z}" fill="${c}" text-anchor="${a}">${E(s)}</text>`;
const R=(x,y,w,h,c='#F5F5F7',r=16)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${c}"/>`;
const L=(x,y,X,Y,c=F,width=3,dash='')=>`<line x1="${x}" y1="${y}" x2="${X}" y2="${Y}" stroke="${c}" stroke-width="${width}" stroke-dasharray="${dash}"/>`;
const C=(x,y,r=6,c=B)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`;
let motion=0;
const A=(x,y,X,Y)=>L(x,y,X,Y,'#8E8E93').replace('/>',' marker-end="url(#ar)"/>')+C(x+(X-x)*motion,y+(Y-y)*motion,6,B);
function card(x,y,w,title,sub,hi=false,h=112){return R(x,y,w,h,hi?'#E8F0FE':'#F5F5F7')+T(x+w/2,y+45,title,30,hi?B:I,'middle')+T(x+w/2,y+83,sub,23,M,'middle');}
function dim(s,on){return `<g opacity="${on?1:.12}">${s}</g>`;}
function pack(x,y,X,Y,u){return C(x+(X-x)*u,y+(Y-y)*u,8,B);}
function pipe(items,k,u,y=185){let s='';items.forEach((it,j)=>{const x=30+j*400;s+=dim(card(x,y,340,it[0],it[1],j===k),j<=k);if(j<3){s+=A(x+350,y+56,x+390,y+56);if(j===k)s+=pack(x+350,y+56,x+390,y+56,u);}});return s;}
function robot(x,y,scale=1,lift=0){return `<g transform="translate(${x} ${y}) scale(${scale})">`+R(0,-65,190,60,'#B8BBC2',18)+R(165,-88,50,40,'#B8BBC2',10)+C(200,-75,5,B)+L(30,-5,8,85,I,8)+L(65,-5,90,85,I,8)+L(125,-5,145,85-lift,I,8)+L(170,-5,195,85-lift,I,8)+C(8,85,8,I)+C(90,85,8,I)+C(145,85-lift,8,B)+C(195,85-lift,8,B)+'</g>';}
function drone(x,y,sc=1){return `<g transform="translate(${x} ${y}) scale(${sc})">`+L(-60,-25,60,25,I,9)+L(-60,25,60,-25,I,9)+R(-32,-22,64,44,'#B8BBC2')+[-1,1].map(a=>[-1,1].map(b=>`<ellipse cx="${a*65}" cy="${b*30}" rx="29" ry="10" fill="#E8F0FE" stroke="${B}" stroke-width="3"/>`).join('')).join('')+'</g>';}
function depth(x,y,w=300,h=190,phase=0){let s='';for(let r=0;r<6;r++)for(let c=0;c<9;c++){const v=(c>4&&r>1)? .65:.12+r*.06;s+=R(x+c*w/9,y+r*h/6,w/9-3,h/6-3,`rgba(0,113,227,${v})`,3);}return s+T(x+w/2,y+h+35,'深浅表示距离',23,M,'middle');}
function cloud(x,y,w=310,h=230,n=100,u=1){let s='';for(let j=0;j<Math.floor(n*u);j++){let a=((j*73)%101)/100,b=((j*37)%97)/96;let yy=b*.5+(a>.53?.1:.4);s+=C(x+a*w,y+yy*h,3.5,j%3?B:'#9B9BA0');}return s;}
function grid(x,y,w=380,h=235,phase=2,age=false){let s='';const cw=w/17,ch=h/11;for(let r=0;r<11;r++)for(let c=0;c<17;c++){let known=(r*17+c*7)%9>2 && c<14;if(age&&c<5)known=false;const hi=c>7&&c<13&&r>2&&r<9;let fill=phase===0?'#F5F5F7':known?(hi?'#529BE5':'#D4E6F9'):'#EEEEF1';s+=R(x+c*cw,y+r*ch,cw-2,ch-2,fill,2);if(!known&&phase>=2)s+=T(x+c*cw+cw/2,y+r*ch+ch*.8,'?',14,M,'middle');}return s;}
function vector(x,y,n,label,hi=true){let s='';for(let j=0;j<24;j++)s+=R(x+j*12,y,8,30+(j*7%29),hi?'#82B3EA':'#D2D2D7',2);return s+T(x+140,y+100,label,24,M,'middle')+T(x+140,y-20,n,37,hi?B:I,'middle');}
function pointsLines(k,u){return pipe([['原始测量','图像 / 点 / IMU'],['时空对齐','时间戳 + 运动状态'],['任务表示','地形 / 特征 + 身体'],['控制动作','关节 / 飞行指令']],k,u);}
function scene(kind,k,u){motion=u;let s='';
 const navigation=navigationScene(kind,k,u);if(navigation!==null)return navigation;
 if(kind==='overview'){
  s=pointsLines(k,u)+robot(90,445,.65,k===3?u*50:0)+T(430,425,'测量不是动作',35,M)+T(930,425,'每一步都在改写数据的含义',35,B);
 }
 if(kind==='sensors'){
  s+=dim(card(25,25,450,'IMU · 200 Hz','6个数 / 条',k===0),true);
  for(let j=0;j<6;j++)s+=dim(R(65+j*62,220,35,55+(j*23%90)+(k===0?Math.sin(u*8+j)*14:0),j%2?B:'#A1A1A6',4)+T(82+j*62,400,['ωx','ωy','ωz','ax','ay','az'][j],24,M,'middle'),true);
  s+=dim(card(575,25,450,'深度 · 20 Hz','640 × 480值 / 张',k===1)+depth(650,200,300,180),k>=1);
  if(k===1)s+=L(650,200+180*u,950,200+180*u,B,3);
  s+=dim(card(1125,25,450,'点云 · 10 Hz','N × (XYZ + 时间)',k===2)+cloud(1190,180,320,230)+T(1350,415,'N可变；还会有无效返回',23,M,'middle'),k>=2);
  if(k===3)s+=T(800,490,'先转换含义，再融合证据',35,B,'middle');
 }
 if(kind==='kalman'){
  const P=4,Rn=noise,z=2,g=P/(P+Rn),mu=g*z,V=(1-g)*P;
  s+=T(40,48,'蓝色越窄，表示越有把握',27,M);
  const X=x=>130+(x+5)*110,Y=d=>385-d*430;
  s+=L(100,385,1230,385,M,2);
  for(let x=-4;x<=4;x++)s+=T(X(x),425,`${x} m`,22,M,'middle');
  const shownMu=k===2?mu*u:mu,shownV=k===3?4+(V-4)*u:k===2?4:V;
  for(const [m,v,c,on,dash] of [[0,4,'#8E8E93',true,''],[2,Rn,'#1D1D1F',k>=1,'8 6'],[shownMu,shownV,B,k>=2,'']]){let d='';for(let j=0;j<=400;j++){const x=-5+j*.025,p=Math.exp(-.5*(x-m)**2/v)/Math.sqrt(2*Math.PI*v);d+=(j?'L':'M')+X(x)+','+Y(p);}s+=dim(`<path d="${d}" fill="none" stroke="${c}" stroke-width="${c===B?5:3}" stroke-dasharray="${dash}"/>`,on);}
  s+=card(1270,180,300,'修正比例',`${(g*100).toFixed(0)}%`,k>=2)+card(1270,315,300,`${mu.toFixed(2)} 米`,`融合方差 ${V.toFixed(2)}`,k>=3);
  s+=T(180,485,'旧估计 0米',28,M)+T(500,485,'测量 2米',28,I)+dim(T(860,485,'融合 '+mu.toFixed(2)+'米',28,B),k>=2);
  window.kalmanResult={gain:g,mean:mu,variance:V};
 }
 if(kind==='predict'){
  const x=k===0?260:k===1?260+u*500:k===2?760:760-u*90;
  s+=L(100,370,1490,370,I,3)+T(170,430,'位置',26,M)+T(1370,430,'时间向前',26,M);
  let width=k===0?90:k===1?90+u*130:k===2?220:220-u*120;
  s+=`<ellipse cx="${x}" cy="275" rx="${width}" ry="65" fill="#E8F0FE"/>`+robot(x-75,280,.75)+T(x,120,k===0?'上次校正':k===1?'根据运动往前猜':k===2?'新测量到达':'缩小估计范围',34,B,'middle');
  if(k>=2)s+=L(670,165,670,370,I,3,'8 6')+T(670,470,'新证据对应的位置',26,M,'middle');
 }
 if(kind==='async'){
  const now=[45*u,50,55+40*u,100][k],X=t=>420+t*10;
  [['IMU',5,'每5 ms · 6个数'],['深度图',50,'每50 ms · 一张图'],['点云',100,'每100 ms · 一包点']].forEach(([name,dt,detail],j)=>{let y=110+j*120;s+=T(25,y,name,32)+T(25,y+37,detail,23,M)+L(400,y,1450,y,F,2);for(let t=0;t<=100;t+=dt)s+=C(X(t),y,j?12:7,t<=now?B:F);});
  s+=L(X(now),50,X(now),425,B,3)+T(X(now),470,`${now.toFixed(0)} ms`,27,B,'middle');
  for(let t=0;t<=100;t+=25)s+=T(X(t),510,String(t),20,M,'middle');
 }
 if(kind==='project'){
  s+=dim(depth(40,180,330,210),true)+T(205,90,'像素 + 距离',33,I,'middle');
  s+=A(390,275,560,275)+dim(cloud(620,130,370,250,110,k===1?u:1)+T(805,90,'相机坐标 XYZ',33,I,'middle'),k>=1);
  s+=A(1030,275,1170,275)+dim(cloud(1210,155,320,240,100)+L(1240,400,1490,400,B)+L(1240,400,1240,170,B)+T(1370,90,'当前机器人坐标',32,B,'middle'),k>=2);
  if(k>=3){s+=L(1260,325,1370,275,B,3,'8 6')+pack(1260,325,1370,275,u)+T(800,480,'先旋转、平移，再补偿采集时刻的差异',32,B,'middle');}
 }
 if(kind==='lio'){
  s+=T(345,65,'一面墙：地图提供的参考平面',29,M,'middle')+L(360,110,360,420,I,8);
  for(let j=0;j<24;j++){let x=460+(j*13%35)-(k>=2?100*u:0),y=120+j*12;s+=C(x,y,5,B);if(k>=2)s+=L(360,y,x,y,'#A1A1A6',1);}
  s+=robot(70,350,.8)+A(550,260,690,260);
  s+=card(720,100,390,'惯性预测','先猜运动状态',k===0)+card(720,300,390,'几何校正','点到墙的距离误差',k===2);
  s+=A(1130,260,1220,260)+dim(card(1240,200,330,'共享运动状态','姿态 / 位置 / 速度',true),k>=3);
  if(k===1)s+=T(750,490,'逐点时间 + 运动估计 → 扫描补偿',29,B);
 }
 if(kind==='twojobs'){
  s+=dim(card(30,60,420,'IMU + 几何','定位：身体在哪'),true)+A(470,115,600,115)+dim(card(620,60,420,'位置与姿态','用于对齐历史点',k===0),true);
  s+=dim(card(30,300,420,'可见点 + 记忆','感知：附近有什么'),k>=1)+A(470,355,600,355)+dim(card(620,300,420,'局部地形 + 目标','导航：朝哪里走',k===2),k>=1);
  s+=A(1060,115,1220,240)+A(1060,355,1220,270)+dim(card(1240,195,330,'运动策略','身体 + 地形 + 指令',true),k>=3);
  if(k===3)s+=robot(1330,460,.6,u*45);
 }
 if(kind==='platform'){
  s+=L(40,425,930,425,I,7)+L(930,425,930,270,I,7)+L(930,270,1540,270,I,7)+robot(350,335,1.05,k===3?u*75:0);
  for(let j=0;j<14;j++){let xx=650+j*58,yy=xx<930?425:270;if(k>=0)s+=L(560,270,xx,yy,k===0?B:'#C9DCEE',1.5);if(k>=2)s+=C(xx,yy,5,B);}
  if(k>=1)for(let j=0;j<14;j++){let a=j*Math.PI/13;s+=L(450,235,450+Math.cos(a)*350,235-Math.sin(a)*140,'#B8BBC2',1.5);}
  if(k===1){const a=u*Math.PI;s+=L(450,235,450+Math.cos(a)*350,235-Math.sin(a)*140,B,4);}
  s+=card(30,30,420,'相机 640条射线','10 Hz · 100 ms',k===0)+dim(card(590,30,420,'雷达 1152条射线','10 Hz · 100 ms',k===1),k>=1);
  if(k>=2)s+=T(1280,100,'有效点 ≤ 1792',35,B,'middle')+T(1280,145,'射线未命中，就没有点',25,M,'middle');
  if(k===3)s+=T(1120,475,'台沿 / 台面 / 未知区',31,B,'middle');
 }
 if(kind==='grid'){
  s+=cloud(40,165,340,260,130)+T(210,80,'可见点 XYZ',34,I,'middle')+A(400,285,560,285);
  s+=grid(600,145,440,285,k,k===3&&u>.6)+T(820,80,'17 × 11 = 187格',34,B,'middle');
  s+=dim(vector(1190,190,'187个高度','高台的局部形状'),k>=1);
  if(k>=2)s+=T(1330,395,'+ 187个有效标记',29,B,'middle')+T(1330,445,k===3?'旧点 → 重投影 / 过期':'? = 没看见',27,M,'middle');
  if(k===0)s+=pack(400,285,560,285,u);
  if(k===0)for(let j=0;j<32;j++){const sx=50+(j*73%300),sy=180+(j*23%200),ex=600+(j%17)*440/17,ey=145+(j%11)*285/11;s+=C(sx+(ex-sx)*u,sy+(ey-sy)*u,4,B);}
 }
 if(kind==='policy'){
  s+=vector(30,130,'374个地形数','高度 + 有效标记',k===0)+dim(vector(30,355,'45个身体数','身体状态 + 指令',false),k>=1);
  s+=A(330,170,520,255)+A(330,380,520,285);
  const layers=[[419,570,170],[512,730,100],[256,890,145],[128,1050,185],[12,1240,225]];
  layers.forEach(([n,x,y],j)=>{s+=dim(R(x,y,82,310-(y-100)*1.1,j===4?'#E8F0FE':'#F5F5F7',12)+T(x+41,y-22,n,28,j===4?B:I,'middle'),k>=2);for(let a=0;a<8;a++)s+=dim(C(x+41,y+25+a*(260-(y-100)*1.1)/8,4,j===4?B:'#A1A1A6'),k>=2);if(j<4)s+=dim(A(x+90,270,layers[j+1][1]-10,270),k>=2);});
  s+=dim(robot(1390,300,.7,k===3?u*60:0)+T(1455,455,'PD → 电机',27,B,'middle'),k>=3);
  if(k===3)s+=T(810,495,'12个关节偏移 → 12个目标角度',29,B,'middle');
 }
 if(kind==='training'){
  s+=dim(card(30,40,400,'理想地形 + 身体','训练可用真值')+A(450,96,575,96)+card(595,40,400,'教师','先通过奖励学会动作',k===0)+A(1015,96,1140,96)+card(1160,40,410,'12维动作标签','学生在当前状态模仿'),k<3);
  s+=dim(card(30,290,400,'可见地形 + 身体','学生能够获得的观测')+A(450,346,575,346)+card(595,290,400,'学生','自己的419维输入',k>=1),k>=1);
  if(k===1)s+=A(1360,170,990,320)+pack(1360,170,990,320,u);
  s+=dim(A(1015,346,1140,346)+card(1160,290,410,k===3?'部署：只算动作':'动作 → 环境 → 奖励',k===3?'参数固定，反复运行':'PPO更新学生参数',true),k>=2);
  if(k===3)s+=T(800,490,'教师、奖励、价值网络留在训练端',31,B,'middle');
 }
 if(kind==='controlclock'){
  const X=t=>410+t*10.8,now=[0,20+20*u,60+20*u,100][k];
  [['感知缓存',100,'10 Hz'],['运动策略',20,'50 Hz'],['PD / 物理',5,'200 Hz']].forEach(([name,dt,hz],j)=>{let y=110+j*120;s+=T(30,y,name,31)+T(30,y+38,hz,25,M)+L(400,y,1510,y,F,2);for(let t=0;t<=100;t+=dt)s+=C(X(t),y,j===2?6:11,t<=now?B:F);});
  for(let a=0;a<5;a++){let xx=X(a*20);s+=R(xx-5,65,15,325,'#0071E30B',2)+T(xx,455,`${a*20}`,22,M,'middle');}
  s+=L(X(now),55,X(now),412,B,3)+T(1490,455,'100 ms',22,M,'middle');
  s+=T(800,510,k===3?'下一轮扫描到来':'同一批感知期间，身体状态与动作持续更新',29,B,'middle');
 }
 if(kind==='parkour'){
  s+=dim(depth(30,170,300,185)+T(180,90,'58 × 87',37,B,'middle'),true);
  s+=A(350,260,440,260)+dim(card(460,200,300,'CNN + GRU','空间编码 + 历史记忆',k===1)+T(610,110,'视觉约10 Hz',31,B,'middle'),k>=1);
  s+=A(780,260,870,260)+dim(vector(890,190,'视觉特征','+ 本体状态')+T(1030,420,'运动策略约50 Hz',31,B,'middle'),k>=2);
  s+=A(1200,260,1280,260)+dim(robot(1330,290,.95,k===3?u*65:0)+T(1420,420,'关节命令',29,I,'middle'),k>=3);
 }
 if(kind==='mapteacher'){
  s+=grid(30,110,370,280,2)+T(215,60,'训练：全局几何',33,I,'middle');
  s+=dim(A(425,180,575,125)+card(595,65,410,'专家答案','给动作，学生模仿',k===1)+A(425,330,575,375)+card(595,315,410,'任务评分','给奖励，PPO练习',k===1),k>=1);
  s+=dim(A(1025,125,1160,245)+A(1025,375,1160,275)+card(1180,200,390,'部署的学生','局部观测 + 状态 + 目标',true),k>=2);
  if(k>=3)s+=T(1230,470,'全局地图留在训练端',28,B,'middle');
 }
 if(kind==='dronepc'){
  s+=dim(cloud(25,170,290,240,150)+T(170,70,'点云 · 10 Hz',33,I,'middle'),true)+A(340,270,430,270);
  for(let j=0;j<28;j++){let a=j*Math.PI*2/28,rr=110+(j*11%60);s+=dim(L(610,265,610+Math.cos(a)*rr,265+Math.sin(a)*rr,j%5?B:'#B8BBC2',3,j%5?'':'5 6')+C(610+Math.cos(a)*rr,265+Math.sin(a)*rr,4,j%5?B:'#B8BBC2'),k>=1);}
  s+=dim(drone(610,265,.55)+T(610,70,'3200个方向分区',33,B,'middle')+T(610,470,'距离 + 未知空间',25,M,'middle'),k>=1);
  s+=A(810,270,890,270)+dim(card(910,210,300,'MLP 融合','感知 + 状态 + 目标',k===2),k>=2)+A(1230,270,1310,270);
  s+=dim(drone(1430,250+(k===3?Math.sin(u*6)*15:0),1)+T(1430,70,'控制 · 50 Hz',33,B,'middle')+T(1430,430,'推力 + 机体角速度',25,I,'middle'),k>=3);
 }
 if(kind==='dronedepth'){
  s+=dim(depth(30,150,280,175)+T(170,80,'100 × 60',35,B,'middle')+T(170,410,'相机新帧率未单列',23,M,'middle'),true);
  s+=A(330,240,405,240)+dim(card(425,185,310,'CNN → GRU','特征 + 状态 + 历史',k===1),k>=1);
  s+=A(755,240,830,240)+dim(card(850,185,300,'策略 · 100 Hz','姿态参考 + 推力',k===2),k>=2);
  s+=A(1170,240,1245,240)+dim(card(1265,185,310,'安全层 → 飞控','局部点云 + QP修正',true),k>=3);
  if(k>=3)s+=cloud(1250,340,250,140,55)+A(170,370,1240,415)+T(730,480,'深度还走另一条几何通路：最近障碍 → 安全约束',27,B,'middle');
 }
 if(kind==='summary'){
  s=pointsLines(k,u);const lines=['原始数值：传感器提供证据','统一时空：历史数据才能重用','压缩表示：保留任务所需信息','闭环更新：每个控制周期重新决策'];
  s+=T(800,410,lines[k],40,B,'middle')+T(800,480,'形状 × 更新节拍 × 含义 × 使用位置',31,M,'middle');
 }
 return s;
}

const slides=[...document.querySelectorAll('.slide')];let current=0,step=0,elapsed=0,playing=false,last=0,noise=1;
function mathHint(kind,k){
 if(navigationHints[kind])return navigationHints[kind];
 const formulas={
  kalman:[`x预测 = 0 m，P = 4 m²；P表示原估计的误差方差`, `z = 2 m，R = ${noise.toFixed(2)} m²；R表示新测量的误差方差`,
   `K = P ÷ (P + R) = ${(4/(4+noise)).toFixed(2)}；K就是向新测量移动的比例`,
   `x新 = x预测 + K × (z − x预测) = ${(8/(4+noise)).toFixed(2)} m；P新 = (1 − K)P = ${(4*noise/(4+noise)).toFixed(2)} m²`],
  predict:['x预测：先记录当前的位置估计','x预测 = 上次位置 + 速度 × Δt；Δt是经过的时间（匀速教学模型）','创新 = 测量 − 预测；先看两条消息差多少','x新 = x预测 + K × 创新；K由双方误差大小决定'],
  project:['d：当前像素测得的光轴深度；u、v：像素位置','X = (u − cx)d / fx，Y = (v − cy)d / fy，Z = d；f和c来自相机内参','p机器人 = R × p相机 + t；R是安装方向，t是安装位置','p当前 = T当前←历史 × p历史；T由这段时间的机器人运动得到'],
  lio:['状态包含：姿态、位置、速度和IMU偏置','同一包点的采集时刻不同，先按运动轨迹补偿','点面误差 r = 法向量 · (变换后的点 − 平面参考点)；点离墙多远','滤波更新：用几何误差修正状态，同时更新误差协方差'],
  grid:['格子编号 = 把点的水平位置按0.1 m分箱','格内高度 = max(有效点的Z)；再转成相对身体的高度值','地形向量 = [187个相对高度, 187个有效标记]','点的年龄 = 当前时刻 − 采集时刻；超过1秒就清除'],
  policy:['374 = 187个高度 + 187个有效标记','45 = 3角速度 + 3重力 + 3指令 + 12关节角 + 12关节速度 + 12上一动作','a = π(o)；o是419个输入数，π是训练好的网络，a是12个动作数','q目标 = q默认 + 0.25 × a；PD根据关节角度与速度误差输出力矩'],
  training:['强化学习：动作改变环境，奖励评价结果，再更新参数','模仿损失 L = 平均[(学生动作 − 教师动作)²]；输出越接近，损失越小','PPO用学生自己的交互轨迹更新；奖励来自前进、完成与接触等反馈','部署只计算 a = π(o)；不再计算训练损失，也不更新参数'],
  controlclock:['周期 Δt = 1 / 频率；10 Hz = 每100 ms一次','50 Hz = 每20 ms一次；读取最新可用地形与新的身体状态','200 Hz = 每5 ms一次；PD持续跟踪最近的关节目标','统计[0,100)毫秒：1次感知、5次策略、20次PD/物理步'],
  parkour:['58 × 87 = 5046个深度值；这是预处理后的图像','z视觉 = 编码器(深度图, 历史)；z是一组学习得到的特征','论文固定深度通路延迟80 ms；身体观测延迟16 ms，交给50 Hz策略','教师的地形表征 → 视觉表征；训练监督动作与航向'],
  mapteacher:['训练几何可提供从当前位置绕障到目标的路径距离','动作监督：学专家怎么动；奖励监督：评自己的动作好不好','在线动作 = 策略(局部观测, 身体状态, 目标)','地图辅助训练 ≠ 在线依赖全局地图；定位与局部记忆仍可存在'],
  dronepc:['把有限历史点变换到当前机体系后再压缩','方向距离 dᵢ = 第i个角分区中最近障碍距离；未知空间另作区分','动作 = MLP(感知表示, 速度, 姿态, 目标, 上一动作)','动作向量 = [总推力, 机体角速度x, y, z]；50 Hz由论文设置给出'],
  dronedepth:['100 × 60 = 6000个深度值；不等于每秒100张新图','h新 = GRU(当前特征与状态, h旧)；h是历史记忆向量','动作向量 = [归一化推力, 横滚参考, 俯仰参考, 偏航参考]','QP选择最接近原动作且满足局部安全约束的修正；依赖模型与观测'],
 };
 return formulas[kind]?.[k]||'';
}
const seconds=3.8,svgFor=()=>slides[current].querySelector('svg');
function fit(){document.getElementById('stage').style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1920,innerHeight/1080)})`;}
function draw(){const d=DATA[current],u=Math.min(1,elapsed/seconds);svgFor().innerHTML=scene(d.kind,step,u);const sl=slides[current];sl.querySelectorAll('.step').forEach((el,i)=>{el.classList.toggle('active',i===step);el.classList.toggle('past',i<step);});let caption=d.steps[step].caption;
 if(d.kind==='kalman'){const g=4/(4+noise);if(step===1)caption=`新测量说是2米，误差方差R为${noise.toFixed(2)}；R越小，越值得信任。`;if(step===2)caption=`向新测量移动${(100*g).toFixed(0)}%，融合位置是${(2*g).toFixed(2)}米。`;if(step===3)caption=`融合方差变成${(4*(1-g)).toFixed(2)}，位置范围比原来更集中。`;}
 sl.querySelector('.caption').textContent=caption;sl.querySelector('.mathhint').textContent=mathHint(d.kind,step);document.getElementById('play').textContent=playing?'P 暂停':'P 播放';}
function setStep(n){step=Math.max(0,Math.min(3,n));elapsed=seconds;playing=false;draw();}
function notes(){const d=DATA[current];document.getElementById('notes').innerHTML=`<h2>${current+1} · ${d.title}</h2><p>${d.note}</p><p><a href="${d.source[1]}" target="_blank" rel="noopener">${d.source[0]}</a></p>`;}
function go(n,autoplay=true){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));step=0;elapsed=0;playing=autoplay&&!matchMedia('(prefers-reduced-motion:reduce)').matches;history.replaceState(null,'','#'+(current+1));document.getElementById('counter').textContent=`${current+1} / ${slides.length}`;document.getElementById('nav').querySelectorAll('button').forEach((b,i)=>b.classList.toggle('current',i===current));notes();draw();}
function tick(t){if(last&&playing){elapsed+=(t-last)/1000;if(elapsed>=seconds){if(step<3){step++;elapsed=0;}else{elapsed=seconds;playing=false;}}draw();}last=t;requestAnimationFrame(tick);}
function toggle(){if(!playing&&step===3&&elapsed>=seconds){step=0;elapsed=0;}playing=!playing;draw();}
document.getElementById('nav').innerHTML=DATA.map((s,i)=>`<button data-page="${i}">${String(i+1).padStart(2,'0')}　${s.title}</button>`).join('');
document.getElementById('nav').onclick=e=>{const b=e.target.closest('button');if(b){go(+b.dataset.page);document.getElementById('nav').classList.remove('open');}};
document.getElementById('prev').onclick=()=>go(current-1);document.getElementById('next').onclick=()=>go(current+1);
document.getElementById('play').onclick=toggle;document.getElementById('replay').onclick=()=>{step=0;elapsed=0;playing=true;draw();};
document.getElementById('backstep').onclick=()=>setStep(step-1);document.getElementById('forwardstep').onclick=()=>setStep(step+1);
document.getElementById('menu').onclick=()=>document.getElementById('nav').classList.toggle('open');
document.getElementById('notesbtn').onclick=()=>document.getElementById('notes').classList.toggle('open');
slides.forEach(sl=>sl.querySelectorAll('.step').forEach(b=>b.onclick=()=>setStep(+b.dataset.step)));
const holder=slides[2].querySelector('.viz'),control=document.createElement('label');control.className='noise-control';control.innerHTML='测量方差 R <input id="noise" aria-label="测量方差" type="range" min="0.25" max="9" step="0.25" value="1"><span id="noiseval">1.00</span>';holder.appendChild(control);
control.querySelector('input').oninput=e=>{noise=+e.target.value;document.getElementById('noiseval').textContent=noise.toFixed(2);playing=false;step=3;elapsed=seconds;draw();};
let buffer='',timer;addEventListener('keydown',e=>{if(e.target.matches('input,textarea,select'))return;const key=e.key.toLowerCase();if(['arrowright','arrowdown','pagedown',' '].includes(key)){e.preventDefault();go(current+1);}else if(['arrowleft','arrowup','pageup'].includes(key)){e.preventDefault();go(current-1);}else if(key==='j')setStep(step+1);else if(key==='k')setStep(step-1);else if(key==='p')toggle();else if(key==='r'){step=0;elapsed=0;playing=true;draw();}else if(key==='g')document.getElementById('nav').classList.toggle('open');else if(key==='n')document.getElementById('notes').classList.toggle('open');else if(key==='home')go(0);else if(key==='end')go(slides.length-1);else if(key==='escape'){document.getElementById('nav').classList.remove('open');document.getElementById('notes').classList.remove('open');}else if(key==='f'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}else if(/^\d$/.test(key)){buffer+=key;clearTimeout(timer);timer=setTimeout(()=>{const n=+buffer;if(n>=1&&n<=slides.length)go(n-1);buffer='';},500);}});
window.deck={go:(n)=>go(n-1,false),setStep,pause:()=>{playing=false;draw();},getState:()=>({page:current+1,step,elapsed,playing}),advance:(dt)=>{elapsed=Math.min(seconds,elapsed+dt);draw();}};
addEventListener('resize',fit);fit();go((Number(location.hash.slice(1))||1)-1);requestAnimationFrame(tick);
