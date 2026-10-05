from pathlib import Path
from svgkit import Diagram
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'modules/assets'

d=Diagram('一次请求：链路、等待与总时间预算',780,410,desc='请求依次经过客户端、入口、业务执行与下游；底部另用800ms预算展示串行耗时相加。',subtitle='先分清排队和执行，再沿同一个请求追踪证据')
items=[('client',24,80,['1 客户端','DNS / TCP / TLS'],'blue'),('entry',278,80,['2 入口与队列','限流 / 排队 / deadline'],'orange'),('service',532,80,['3 业务执行','线程 / 锁 / 序列化'],'orange'),('pool',532,180,['4 获取下游连接','连接池等待 / 连接超时'],'orange'),('remote',278,180,['5 下游处理','SQL / RPC / 锁等待'],'green'),('response',24,180,['6 结果返回','响应丢失 ≠ 未执行'],'pink')]
for key,x,y,lines,c in items:d.node(key,x,y,224,72,lines,c)
d.edge('client','entry');d.edge('entry','service');d.edge('service','pool','bottom');d.edge('pool','remote','left');d.edge('remote','response','left')
d.text(390,284,'独立预算示例：100 + 300 + 300 + 100 = 800ms',12)
for i,(k,lines,c) in enumerate([('budget1',['池等待','100ms'],'orange'),('budget2',['串行调用 A','300ms'],'blue'),('budget3',['串行调用 B','300ms'],'blue'),('budget4',['返回与安全余量','100ms'],'green')]):d.node(k,24+i*190,302,162,54,lines,c)
d.footer(['预算数字是教学假设；并行调用看关键路径，不能把各阶段 P99 直接相加。'])
d.save(A/'10-request-budget.svg')

d=Diagram('服务端授权：身份、对象、动作三者相交',780,360,desc='不可信输入经认证变为可信身份，业务授权决定可操作对象范围，数据层收窄查询和输出。',subtitle='认证通过只是入口；对象级授权必须在业务边界落实')
for k,x,y,lines,c in [('client',24,80,['不可信客户端','订单 ID / 自报 tenantId'],'pink'),('authn',278,80,['认证与凭据校验','签名 / 受众 / 有效期'],'blue'),('authz',532,80,['业务授权','身份 × 对象 × 动作'],'orange'),('scope',532,180,['权限限定的数据访问','租户过滤 / 字段白名单'],'green'),('data',278,180,['权威数据与缓存','缓存键匹配权限作用域'],'green'),('audit',24,180,['响应与审计','最小字段 / 不泄漏密钥'],'blue')]:d.node(k,x,y,224,72,lines,c)
d.edge('client','authn');d.edge('authn','authz');d.edge('authz','scope','bottom');d.edge('scope','data','left');d.edge('data','audit','left')
d.text(390,294,'拒绝路径：认证或授权失败即停止；不得等数据返回后再靠前端隐藏。',12,'#9d174d')
d.footer('示意省略具体 RBAC / ABAC 规则；后台任务与 Agent 工具也要带可信身份。')
d.save(A/'13-authorization-boundary.svg')

d=Diagram('数据库演进：扩展、迁移、切换、收缩',780,350,desc='六步兼容迁移，直到验证旧版本不再使用后才收缩旧字段。',subtitle='回滚代码之前，先确认新旧数据格式仍然兼容')
items=[('expand',24,80,['1 扩展','新增字段 / 保留旧字段'],'blue'),('coexist',278,80,['2 兼容运行','新旧实例均可读写'],'orange'),('backfill',532,80,['3 回填与核对','历史补齐 / 增量追平'],'orange'),('switch',532,180,['4 切换读路径','灰度 / 业务指标验证'],'green'),('observe',278,180,['5 观察并停旧写','确认消费者与旧版退场'],'green'),('contract',24,180,['6 收缩','删除旧路径 / 旧字段'],'pink')]
for k,x,y,lines,c in items:d.node(k,x,y,224,72,lines,c)
for a,b,side in [('expand','coexist','right'),('coexist','backfill','right'),('backfill','switch','bottom'),('switch','observe','left'),('observe','contract','left')]:d.edge(a,b,side)
d.text(390,291,'不可逆边界：收缩与数据变换后，旧镜像可能已无法正确工作。',12,'#9d174d')
d.footer('示意不规定双写实现；一致性、回填校验、迁移失败恢复必须单独设计。')
d.save(A/'13-schema-evolution.svg')

d=Diagram('二分边界：把未知区间持续缩小',660,342,desc='数组1、3、3、6、9中查找第一个大于等于3的位置。首次mid=2，hi收缩为2，再用不变量推到答案1。',subtitle='lowerBound · [lo, hi) · target = 3 · 重复值不能随便返回')
d.text(330,80,'初态：lo=0，hi=5，mid=2；未知区间为 [0,5)',12)
for i,v in enumerate([1,3,3,6,9]):d.node('before'+str(i),24+i*128,98,100,54,[f'a[{i}]',str(v)],'orange' if i==2 else 'blue')
d.text(330,178,'a[2] ≥ 3，因此 hi=2；右侧 [2,5) 已知满足条件',12)
for i,v in enumerate([1,3,3,6,9]):d.node('after'+str(i),24+i*128,196,100,54,[str(v),'待查 [0,2)' if i<2 else '已知 ≥ 3'],'orange' if i<2 else 'green')
d.text(330,282,'不变量：i < lo → a[i] < target；i ≥ hi → a[i] ≥ target',12)
d.footer('继续检查 mid=1、mid=0 后，lo=hi=1；找到的是第一个满足位置。')
d.save(A/'14-binary-search-invariant.svg')

d=Diagram('LRU：哈希定位节点，链表维护访问顺序',780,448,desc='get B先用哈希表定位B，再把B从A-B-C链表摘下移到尾部，得到A-C-B。表里保存节点引用，移动不需扫描链表。',subtitle='约定：左侧最久未使用，右侧最近使用；容量为 3')
d.text(390,80,'访问前：HashMap 持有 key → 节点；get(B) 平均 O(1) 定位',12)
for i,k in enumerate(['A','B','C']):d.node('pre'+k,24+i*254,98,224,54,[k,'最久未使用' if i==0 else ('待访问' if i==1 else '最近使用')],'orange' if k=='B' else 'blue')
for a,b in [('preA','preB'),('preB','preC')]:
    x,y,w,h=d.boxes[a];tx,ty,tw,th=d.boxes[b]
    d.path(f'M {x+w+5},{y+h/2-7} L {tx-11},{y+h/2-7}')
    d.path(f'M {tx-5},{y+h/2+7} L {x+w+11},{y+h/2+7}')
d.node('get',278,180,224,54,['get(B)：摘下 B','将同一节点放到尾部'],'orange')
d.text(390,260,'访问后：A 仍最旧；新插入 D 时应淘汰 A',12)
for i,k in enumerate(['A','C','B']):d.node('post'+k,24+i*254,278,224,54,[k,'最久未使用' if i==0 else ('次新' if i==1 else '最近使用')],'green' if k=='B' else 'blue')
for a,b in [('postA','postC'),('postC','postB')]:
    x,y,w,h=d.boxes[a];tx,ty,tw,th=d.boxes[b]
    d.path(f'M {x+w+5},{y+h/2-7} L {tx-11},{y+h/2-7}')
    d.path(f'M {tx-5},{y+h/2+7} L {x+w+11},{y+h/2+7}')
d.text(390,373,'图中双向箭头是 prev / next 引用；中间说明框表示操作，不表示链表节点。',10,'#64748b')
d.footer(['教学图不含并发、TTL、权重与哨兵节点；LinkedHashMap 参考实现按条目数淘汰。'])
d.save(A/'14-lru-access-order.svg')

d=Diagram('项目回答：从背景到可验证的判断',780,350,desc='项目叙事六个相连部分：约束、备选方案、个人决策、验证证据、结果边界、复盘。',subtitle='每一条关键结论，都能回到事实、指标或实验')
for k,x,y,lines,c in [('constraints',24,80,['1 背景与约束','业务 / 规模 / 个人职责'],'blue'),('alternatives',278,80,['2 比较可行方案','代价 / 风险 / 不选理由'],'orange'),('decision',532,80,['3 明确个人判断','决策 / 实现 / 协作边界'],'orange'),('proof',532,180,['4 提供验证证据','指标口径 / 原始记录'],'green'),('result',278,180,['5 说明结果与限制','事实 / 估算 / 未知分开'],'green'),('review',24,180,['6 复盘与迁移','失败原因 / 新约束取舍'],'purple')]:d.node(k,x,y,224,72,lines,c)
for a,b,side in [('constraints','alternatives','right'),('alternatives','decision','right'),('decision','proof','bottom'),('proof','result','left'),('result','review','left')]:d.edge(a,b,side)
d.text(390,290,'追问检验：规模 ×10、预算减半或一致性要求变化，原方案还成立吗？',12)
d.footer('结构用于整理真实经历；练习结果不得包装成生产经历，缺失数据应明确说明。')
d.save(A/'19-project-evidence.svg')

d=Diagram('知识路线：基础机制支撑工程判断',780,462,desc='四条学习路线及其验证产物，最后汇合到项目与模拟面试。',subtitle='章节编号对应正文；横向是依赖顺序，纵向是不同能力线')
rows=[(['01–02 语言与集合','契约 / 数据结构'],['03–05 并发与运行时','线程 / JVM / Spring'],['验证：并发实验','讲清发布与事务边界']),(['06–08 数据与消息','索引 / 缓存 / 投递'],['09–12 分布式与系统','一致性 / 容量 / SLO'],['验证：故障注入','预测崩溃与恢复结果']),(['15 LLM 基础','上下文 / 推理 / 输出'],['16–18 Agent 工程','检索 / 工具 / 评测'],['验证：任务闭环','权限 / 成本 / 恢复']),(['13 安全 + 14 编码','边界 / 正确性 / 测试'],['19 项目与技术判断','事实 / 取舍 / 证据'],['最终：四场模拟','闭卷回答与变式追问'])]
for r,row in enumerate(rows):
    for c,lines in enumerate(row):d.node(f'n{r}{c}',24+c*254,80+r*82,224,54,lines,['blue','orange','green'][c])
    d.edge(f'n{r}0',f'n{r}1');d.edge(f'n{r}1',f'n{r}2')
d.footer(['每次学习：看图讲路径 → 合上图重画 → 改一个约束 → 用练习验证。'])
d.save(ROOT/'guide/assets/00-learning-map.svg')

# Aggregate boundary vs integration boundary.
d = Diagram('领域边界：聚合内守住不变量，跨边界显式协调', height=418,
    desc='订单应用服务调用订单聚合，聚合内事务保存订单与明细及Outbox，独立库存服务消费事件并回复结果。',
    subtitle='教学示例：聚合边界由一致性规则决定，不按表数量机械划分')
d.node('command',30,88,220,72,['应用服务','身份 / 幂等 / 用例编排','调用领域行为'],'blue')
d.node('aggregate',280,88,220,72,['订单聚合根','验证状态与金额不变量','控制订单明细变更'],'purple')
d.node('commit',530,88,220,72,['本地事务','订单 + 明细 + Outbox','共同提交或回滚'],'green')
d.node('result',30,214,220,72,['订单继续推进','根据结果条件更新','接受中间状态与补偿'],'blue')
d.node('inventory',280,214,220,72,['库存边界','自己的可用量不变量','预留请求按业务键幂等'],'orange')
d.node('event',530,214,220,72,['集成事件','已提交事实 / 版本 / ID','异步可靠投递'],'purple')
for a,b in [('command','aggregate'),('aggregate','commit'),('event','inventory'),('inventory','result')]:d.edge(a,b,side='left' if a in ['event','inventory'] else 'right')
d.edge('commit','event',side='bottom')
d.text(390,328,'跨服务没有图中隐含的“大事务”；失败要定义重试、查询、对账与业务补偿。',12)
d.footer(['聚合可以有多张表；分服务后仍需说明事实来源、状态机及并发条件。','闭卷重画：把“取消”和“支付成功”竞争补入订单聚合。'])
d.save(ROOT/'modules/assets/30-aggregate-boundary.svg')

# Probe semantics: separate decisions, not a single sequential pipeline.
d = Diagram('健康探针：不同信号触发不同动作',height=358,
    desc='启动探针保护慢启动，就绪探针决定服务流量，存活探针决定是否重启。',
    subtitle='三列是职责比较；探针成功不等于业务全链路一定成功')
for key,x,top,bottom,col in [('startup',30,['Startup 启动','启动是否在预算内完成？'],['成功后进入常规探测','启动未成功时抑制','常规存活 / 就绪探测'],'blue'),('ready',280,['Readiness 就绪','现在能接受新请求吗？'],['未就绪：停止承接','经 Service 路由的新流量','不因就绪失败直接重启'],'green'),('live',530,['Liveness 存活','进程是否失活需重启？'],['失败达到配置阈值','按重启策略处理容器','慎将下游故障作为条件'],'pink')]:
 d.node(key,x,88,220,54,top,col);d.node(key+'-action',x,180,220,72,bottom,col);d.edge(key,key+'-action',side='bottom')
d.footer(['数据库短暂抖动 → 所有实例存活失败 → 全体重启，可能扩大事故。','探针阈值与时间预算要结合应用启动、摘流传播和真实恢复行为验证。'])
d.save(ROOT/'modules/assets/31-probe-decisions.svg')

# 0/1 knapsack reuse pitfall, with actual values.
d = Diagram('0/1 背包：倒序保留上一轮状态',height=362,
    desc='单件重量2价值3容量4，正序会复用当前件得到6，倒序结果为3。',
    subtitle='只有一件物品：重量 2，价值 3；容量 4；dp 初始全为 0')
d.node('r4',30,98,220,72,['倒序：先更新 c=4','读取旧 dp[2]=0','dp[4] = 3'],'green')
d.node('r3',280,98,220,72,['再更新 c=3','读取旧 dp[1]=0','dp[3] = 3'],'green')
d.node('r2',530,98,220,72,['最后更新 c=2','读取 dp[0]=0','dp[2] = 3'],'green')
d.node('f2',30,214,220,72,['正序：先更新 c=2','dp[2] = 3','本轮已使用当前物品'],'orange')
d.node('f4',280,214,220,72,['随后更新 c=4','读到新的 dp[2]=3','dp[4] = 3 + 3 = 6'],'pink')
d.node('bad',530,214,220,72,['结果违反 0/1 条件','同一物品被使用两次','语义变成可重复使用'],'pink')
for a,b in [('r4','r3'),('r3','r2'),('f2','f4'),('f4','bad')]:d.edge(a,b)
d.footer('先定义“最多容量”还是“恰好装满”；倒序条件不能替代正确的状态初始化。')
d.save(ROOT/'modules/assets/32-knapsack-direction.svg')

print('Generated 10 foundation diagrams')
