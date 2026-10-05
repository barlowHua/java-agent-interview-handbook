"""Original mechanism diagrams for modules 06–12; run from any directory."""
from pathlib import Path
from svgkit import Diagram

OUT = Path(__file__).resolve().parents[1] / 'modules' / 'assets'
def save(d, name):
    d.save(OUT / name)

# Secondary-tree lookup, leaf ordering, then a second tree traversal.
d = Diagram('B+ 树：二级索引定位与回表是两次树查找', height=334,
    subtitle='示意索引 (status, id)，查询 status=PAID 并返回 amount；页与记录数量被简化')
d.group('secondary',25,78,350,196,'二级索引：按 (status, id) 排序')
d.group('clustered',405,78,350,196,'聚簇索引：按主键 id 排序')
d.node('sroot',45,108,310,54,['非叶页：分隔键 + 子页指针','① 选择包含 PAID 的子页'],'blue')
d.node('sleaf1',45,187,142.5,54,['叶页：CANCELLED','… 主键 id …'],'gray')
d.node('sleaf2',212.5,187,142.5,54,['叶页：PAID','id=42，id=58'],'blue')
d.node('proot',425,108,310,54,['② 以主键 id=42 再定位','非叶页：键 + 子页指针'],'orange')
d.node('pleaf1',425,187,142.5,54,['叶页：完整行','id=42, amount=99'],'green')
d.node('pleaf2',592.5,187,142.5,54,['相邻叶页','id=58, amount=80'],'green')
d.edge('sroot','sleaf1','bottom');d.edge('sroot','sleaf2','bottom',color='blue')
d.edge('proot','pleaf1','bottom',color='orange');d.edge('proot','pleaf2','bottom')
d.edge('sleaf1','sleaf2',color='gray');d.edge('pleaf1','pleaf2',color='gray')
d.path('M 360,214 C 390,214 384,135 414,135','orange')
d.footer(['横向叶页连接用于范围扫描；箭头只画前进方向，省略反向链与中间页。',
          '只取 status、id 时可能覆盖；树高、Buffer Pool 命中和 MVCC 检查共同决定访问成本。'])
save(d,'06-index-path.svg')

# ReadView's frozen active set and version traversal.
d = Diagram('MVCC：沿 undo 版本链寻找本次读视图可见的版本',height=330,
    subtitle='教学快照：创建者=100，活跃集合={98,103}，最小活跃=98，下一事务边界=105')
d.node('view',25,78,225,72,['Read View 固定判定规则','自身修改可见','其他版本看创建时状态'],'blue')
d.node('latest',277.5,78,225,72,['当前行：trx_id=105','值 v3；快照之后产生','不可见 → 找前一版'],'pink')
d.node('later',530,78,225,72,['undo 重建：trx_id=103','值 v2；创建快照时活跃','不可见 → 找前一版'],'orange')
d.node('rule',25,175,225,90,['RC：每次一致性读新视图','RR：通常复用首次视图','SELECT FOR UPDATE','不按这个快照规则读取'],'gray')
d.node('result',277.5,175,225,90,['本次读返回 v1','不是简单取最大 trx_id','也不是取读取瞬间','最新已提交值'],'blue')
d.node('old',530,175,225,90,['undo 重建：trx_id=97','值 v1；早于活跃下界','已提交，可见','停止沿链查找'],'green')
d.edge('view','latest');d.edge('latest','later','right',color='orange')
d.edge('later','old','bottom',color='orange');d.edge('old','result','left',color='green')
d.footer(['103 之后即便已经提交，仍不改变旧 Read View 对它的判断；新 RC 视图可能看到新版本。',
          '图只展示普通一致性读与存活行；删除标记、不可见插入和二级索引路径另行处理。'])
save(d,'06-mvcc.svg')

# Race rather than a happy-path cache overview.
d = Diagram('Cache-aside 反例：删除成功后仍可回填旧值',height=418,
    subtitle='按 ①→⑤ 阅读；左侧读请求 A，右侧写请求 B，中间是共享数据的变化')
d.node('a1',25,78,225,54,['① A：缓存未命中','② 读 DB 得 v1，随后暂停'],'blue')
d.node('state1',277.5,78,225,54,['起点','DB=v1，cache 不存在'],'gray')
d.node('b1',530,78,225,54,['B 准备写入 v2','A 已持有旧结果 v1'],'orange')
d.node('a2',25,157,225,54,['A 仍在暂停','尚未执行缓存 SET'],'gray')
d.node('state2',277.5,157,225,54,['③ DB=v2 提交完成','④ cache 删除成功'],'green')
d.node('b2',530,157,225,54,['B：先提交数据库','再删除缓存，已完成'],'orange')
d.node('a3',25,236,225,54,['⑤ A 恢复','SET cache=v1，并设置 TTL'],'pink')
d.node('state3',277.5,236,225,54,['结果：DB=v2，cache=v1','TTL 从旧值回填时开始'],'pink')
d.node('b3',530,236,225,54,['后续读取可能命中 v1','成功删除不等于原子一致'],'pink')
d.edge('a1','a2','bottom');d.edge('a2','a3','bottom',color='pink')
d.edge('b1','b2','bottom',color='orange');d.edge('b2','state2','left',color='orange')
d.edge('a3','state3',color='pink');d.edge('state3','b3',color='pink')
d.node('guard',25,315,730,54,['关键决策查权威源；展示缓存定义陈旧窗口，配合可靠失效与回填版本栅栏。',
    '固定延迟双删与 TTL 都不能覆盖任意长暂停、持续旧回填或副本滞后。'],'green')
d.footer('思考：若 A 在 B 提交后暂停了 20 秒，TTL=5 秒，能承诺从 B 提交起最多旧 5 秒吗？')
save(d,'07-cache-race.svg')

# Ownership token versus downstream fencing token.
d = Diagram('租约过期后，随机 token 与 fencing 保护的是不同边界',height=418,
    subtitle='编号表示发生顺序；假设 fencing 由可靠的单调序号源签发，资源端原子校验')
d.node('a',25,78,225,54,['① A 获租约','fence=41，随后暂停'],'blue')
d.node('lease',277.5,78,225,54,['② TTL 到期','锁记录已不再属于 A'],'orange')
d.node('b',530,78,225,54,['③ B 获新租约','fence=42'],'blue')
d.node('old',25,157,225,54,['⑤ A 恢复并发出旧写','仍携带 fence=41'],'pink')
d.node('resource',277.5,157,225,54,['④ 资源端接受 B 的写入','保存 maxFence=42'],'green')
d.node('bwrite',530,157,225,54,['④ B 写资源','携带 fence=42'],'blue')
d.node('unlock',25,236,225,54,['比较随机 token 再 DEL','只能避免误删 B 的锁'],'orange')
d.node('reject',277.5,236,225,54,['⑥ 41 < maxFence 42','资源拒绝 A 的迟到写入'],'green')
d.node('limit',530,236,225,54,['资源若不检查 fence','锁服务无法阻止旧写'],'pink')
d.edge('a','lease');d.edge('lease','b');d.edge('b','bwrite','bottom',color='blue')
d.edge('bwrite','resource','left',color='green');d.edge('a','old','bottom',color='pink')
d.edge('old','resource','right',color='pink');d.edge('resource','reject','bottom',color='green')
d.node('boundary',25,315,730,54,['随机 token 回答“谁能解锁”；fencing 回答“资源是否接受这次写入”。',
    'fencing 防旧持有者，不会自动去重同一持有者的重复业务请求；仍需业务幂等。'],'gray')
d.footer('旧持有者的写入和资源的版本比较必须在同一原子边界；仅在客户端比较序号仍有竞态。')
save(d,'07-lease-fencing.svg')

# Ack semantics and the offset gap under parallel completion.
d = Diagram('消费确认：业务已提交，才允许推进连续完成边界',height=391,
    subtitle='上半图为本地业务事务；下半图以 Kafka 单分区 offset 为例')
d.node('delivery',25,78,225,72,['消息 event_id=E7','broker 投递 / consumer poll','可能重复到达'],'blue')
d.group('consume-tx',277.5,78,225,72,'同一本地事务：共同提交或回滚')
d.text(390,116,'去重唯一键 + 业务变更',12,'#166534')
d.text(390,137,'提交成功后再向外确认',10,'#64748b')
d.node('ack',530,78,225,72,['RabbitMQ ack','或 Kafka 提交下一读取位置','丢确认 → 重投 → 幂等挡住'],'green')
d.path('M 255,114 L 266.5,114');d.path('M 507.5,114 L 519,114','green')
d.node('o10',25,175,225,54,['offset 10：已完成','若此前都完成，可提交 11'],'green')
d.node('o11',277.5,175,225,54,['offset 11：仍在处理','当前空洞：禁止跨过'],'orange')
d.node('o12',530,175,225,54,['offset 12：已完成','不能据此直接提交 13'],'green')
d.node('restart',25,254,225,72,['正确恢复：从 11 重读','11 继续处理','12 可能重复，由幂等裁决'],'green')
d.node('watermark',277.5,254,225,72,['11 完成后形成连续前缀','10、11、12 均已成功','此时可提交 13'],'blue')
d.node('loss',530,254,225,72,['错误：提前提交 13','重启从 13 读取','未完成的 11 被跳过'],'pink')
d.edge('o10','o11');d.edge('o11','o12');d.edge('o10','restart','bottom')
d.edge('o11','watermark','bottom',color='blue');d.edge('o12','loss','bottom',color='pink')
d.footer(['Kafka 已拉取的位置 ≠ 已完成的位置；RabbitMQ 批量 ack 也不能越过未完成的投递。',
          '分区 / channel 的确认规则不同；外部 HTTP 副作用不参加上图数据库事务，须另做幂等或查询。'])
save(d,'08-consumer-boundary.svg')

# Separate local atomic commit domains; repeatable relay delivery.
d = Diagram('Outbox：两个本地事务，中间允许重复投递',height=411,
    subtitle='虚线框是原子提交边界；框之间的箭头不属于一个跨库事务')
d.group('order-tx',25,78,350,183,'事务 A：订单数据库')
d.group('fulfil-tx',405,78,350,183,'事务 B：履约数据库')
d.node('orders',45,108,310,54,['订单状态修改','订单 ID / 版本 / 请求唯一键'],'blue')
d.node('outbox',45,187,310,54,['Outbox 插入事件 E7','与订单一起提交或一起回滚'],'green')
d.node('inbox',425,108,310,54,['Inbox / processed_event','唯一键 (consumer, event_id)'],'blue')
d.node('fulfil',425,187,310,54,['创建履约任务','与去重记录一起提交或回滚'],'green')
d.node('relay',25,286,225,54,['relay 轮询或 CDC','仅转发已提交事件'],'orange')
d.node('broker',277.5,286,225,54,['broker 保存并投递','同一个 E7 可能出现多次'],'purple')
d.node('consumer',530,286,225,54,['消费者处理 E7','事务 B 提交后才确认'],'orange')
d.path('M 137.5,266 L 137.5,275','orange')
d.edge('relay','broker',color='orange');d.edge('broker','consumer',color='purple')
d.path('M 642.5,281 L 642.5,272','orange')
d.footer(['发送确认后、记录发送进度前崩溃：relay 会重发 E7；事务 B 的唯一约束使业务效果不重复。',
    'Outbox 保证待发凭据与业务同生共灭；它不自动保证跨聚合顺序、及时送达或外部支付恰好一次。'])
save(d,'09-outbox-boundaries.svg')

# Majority partition with leaders and follower fanout, not a generic consensus list.
d = Diagram('Raft 网络分区：多数派可以推进，旧 leader 不能独自承诺',height=398,
    subtitle='5 个节点分成 2 + 3；箭头代表新 leader 向两个 follower 复制日志')
d.group('minority',25,78,350,244,'少数侧：2 / 5，无法组成多数')
d.group('majority',405,78,350,244,'多数侧：3 / 5，可按协议选举')
d.node('oldleader',45,108,310,54,['旧 leader：任期 7','仍活着 ≠ 仍可提交新写入'],'pink')
d.node('oldfollower',45,187,310,54,['follower A','两份复制仍不足以提交'],'orange')
d.node('noquorum',45,266,310,36,'写请求等待或失败，不能编造成功','pink')
d.node('newleader',425,108,290,54,['新 leader：任期 8','通过合法选举产生'],'blue')
d.node('f1',425,187,290,54,['follower B','匹配日志后确认复制'],'green')
d.node('f2',425,266,290,36,'follower C：确认复制','green')
d.edge('oldleader','oldfollower','bottom',color='pink');d.edge('newleader','f1','bottom',color='blue')
d.path('M 720,135 C 745,135 745,162 745,212 C 745,252 745,284 726,284','blue')
d.footer(['多数相交只是前提，还依赖任期、投票、日志匹配和当前任期提交规则；不是任意三份数据都安全。',
    '图假设崩溃故障与多数侧通信可用；线性一致读也须验证权限/提交进度，不能无条件读旧 leader。'])
save(d,'09-raft-partition.svg')

# Order architecture includes payment callback and distinct async fulfilment state.
d = Diagram('订单设计：同步受理与异步履约使用不同事务边界',height=409,
    subtitle='教学架构；每个编号对应正文演例 A 的可恢复业务动作')
d.node('client',25,78,225,72,['客户端：稳定请求号','① 创建订单 / 查询状态','总 deadline 与重试次数有界'],'blue')
d.node('api',277.5,78,225,72,['订单 API','鉴权、租户隔离、限流','幂等冲突校验原始参数'],'blue')
d.node('order',530,78,225,72,['事务 A：订单 + Outbox','唯一 (tenant, request_id)','响应丢失 → 原身份查询'],'green')
d.node('fulfil',25,175,225,72,['履约数据库：事务 B','消费去重 + 创建任务','履约状态可独立查询'],'green')
d.node('worker',277.5,175,225,72,['履约消费者','本地提交后确认','失败有界重试与隔离'],'orange')
d.node('queue',530,175,225,72,['② relay → MQ','事件 ID + 订单版本','监控最老事件年龄'],'purple')
d.node('channel',25,272,225,72,['支付渠道','原支付请求号查询','签名回调可能重复或晚到'],'blue')
d.node('callback',277.5,272,225,72,['③ 支付回调校验','验签、金额、币种、订单','超时未知不能直接判失败'],'orange')
d.node('payment',530,272,225,72,['事务 C：支付流水 + 订单','条件推进状态 + Outbox','渠道流水唯一；晚成功补偿'],'green')
d.edge('client','api');d.edge('api','order');d.edge('order','queue','bottom',color='orange')
d.edge('queue','worker','left',color='purple');d.edge('worker','fulfil','left',color='orange')
d.edge('channel','callback');d.edge('callback','payment');d.edge('payment','queue','top',color='orange')
d.footer(['横向看每次调用；纵向看事件传播。事务 A/C 可在同一订单库，但不与履约库组成一个本地事务。',
          '图省略支付发起箭头与副本拓扑；库存、渠道侧扣款和取消补偿仍须分别论证不变量。'])
save(d,'11-order-architecture.svg')

# Fault-domain capacity arithmetic and explicit teaching assumptions.
d = Diagram('容量设计：先满足丢失一个故障域后的安全吞吐',height=386,
    subtitle='假设：峰值 1000 QPS，压测确定单实例满足目标延迟的安全容量为 300 QPS')
d.node('load',277.5,78,225,54,['全局入口：1000 QPS','限流与路由避免局部过载'],'blue')
for key,x,name in [('aza',25,'可用区 A'),('azb',277.5,'可用区 B'),('azc',530,'可用区 C')]:
    d.node(key,x,157,225,72,[name,'2 实例 × 300 = 600 QPS','应用故障域彼此独立'],'green' if key!='aza' else 'pink')
    d.edge('load',key,'bottom',color='gray')
d.node('proof',25,254,730,72,['A 区故障后：B + C = 4 × 300 = 1200 QPS ≥ 1000 QPS，余量 200 QPS。',
    '这只是应用层算术：数据库、MQ、身份服务、网络和配额也必须承受切换流量。',
    '若平均耗时 200ms，稳定态平均在途约 200；不能把 P99 直接代入得到线程池大小。'],'orange')
d.footer(['原始容量 1800 QPS 不等于可承诺容量；验证切流、冷缓存、偏斜和故障恢复时的实际延迟。',
          '数字仅用于方法演示；真实设计按观测流量、压测容量与目标冗余重新计算。'])
save(d,'11-failure-capacity.svg')

# Diagnostic evidence tree and intervention step.
d = Diagram('接口 P99 激增：用证据区分计算、等待与 GC 压力',height=457,
    subtitle='先确认真实用户影响、发生范围与时间，再选择能区分假设的观测')
d.node('symptom',277.5,78,225,54,['同版本 / 同请求类型对比','P99、错误率、吞吐一起看'],'blue')
d.node('cpu',25,157,225,54,['计算压力假设','CPU 或调度等待升高'],'orange')
d.node('wait',277.5,157,225,54,['等待压力假设','CPU 不高、响应变慢'],'orange')
d.node('gc',530,157,225,54,['内存压力假设','分配 / GC 暂停同步变化'],'orange')
d.node('cpu-e',25,236,225,90,['线程采样 / CPU profile','热点方法与调用栈','容器 CPU 配额与节流','区分忙循环、计算和调度'],'green')
d.node('wait-e',277.5,236,225,90,['trace + 池指标 + 线程栈','拆连接等待 / SQL / 网络','核对锁等待与慢依赖','不要只凭低 CPU 就扩线程'],'green')
d.node('gc-e',530,236,225,90,['GC 日志 / JFR','停顿时刻与请求对齐','GC 后存活量、分配率','区分缓存增长与泄漏'],'green')
for target in ['cpu','wait','gc']:d.edge('symptom',target,'bottom')
for source,target in [('cpu','cpu-e'),('wait','wait-e'),('gc','gc-e')]:d.edge(source,target,'bottom')
d.node('verify',25,351,730,54,['保留关键证据 → 可逆止损 → 对照验证 → 补故障实验与长期修复',
    '例：回滚后连接池等待消失，继续追查事务持有时间；相关性支持假设，但不能替代因果验证。'],'blue')
d.footer('这是诊断分支，不是互斥分类：慢依赖可以引发排队、分配增长和 GC，多个证据需要对齐时间。')
save(d,'12-diagnostic-evidence.svg')

# Inverted index with a concrete corpus and query; doc values are a different access direction.
d = Diagram('搜索索引：从词项找到文档，再按相关性返回',height=409,
    subtitle='最小教学语料：D1=“java 缓存”，D2=“java 事务”；省略词频、位置等细节')
d.node('docs',25,78,225,72,['原始文档','D1：java 缓存','D2：java 事务'],'blue')
d.node('analyze',277.5,78,225,72,['索引分析器','规范化、分词、过滤','写入词项与文档关系'],'orange')
d.node('postings',530,78,225,72,['倒排表 postings','java → D1,D2','缓存 → D1；事务 → D2'],'green')
d.node('query',25,175,225,72,['用户查询：java 缓存','本例采用 AND 语义','同时带租户与 ACL 条件'],'blue')
d.node('q-analyze',277.5,175,225,72,['查询分析器','java、缓存','分析规则须与索引兼容'],'orange')
d.node('match',530,175,225,72,['取词项对应文档集合','java ∩ 缓存','并应用授权过滤'],'purple')
d.node('result',25,272,225,72,['结果：D1','带原文片段与必要字段','最终顺序符合排序契约'],'green')
d.node('score',277.5,272,225,72,['对候选计算相关性','BM25：词频、稀有度、长度','分数不代表事实正确概率'],'purple')
d.node('candidate',530,272,225,72,['候选文档 D1','读取评分需要的统计','越权文档不能进入结果'],'green')
d.edge('docs','analyze');d.edge('analyze','postings');d.edge('query','q-analyze');d.edge('q-analyze','match')
d.edge('postings','match','bottom',color='green');d.edge('match','candidate','bottom',color='purple')
d.edge('candidate','score','left',color='purple');d.edge('score','result','left',color='green')
d.footer(['倒排索引：词项 → 文档；doc values：文档 → 字段值，常用于排序和聚合。',
    '实际系统还需分片归并、分析器版本和更新可见性；本图不是某个生产集群的完整部署图。'])
save(d,'25-inverted-index.svg')

d = Diagram('Elasticsearch：搜索可见与崩溃可恢复是两道边界',height=409,
    subtitle='以 8.19 单分片副本内部机制示意；完整写入还涉及主副本协议与确认条件')
d.node('index',25,78,350,72,['写操作先更新内部 Lucene 索引','数据进入索引缓冲等结构','不意味着搜索立即可见'],'blue')
d.node('translog',405,78,350,72,['随后记录 translog','在对外确认前记录操作','不是每次都做完整 Lucene commit'],'orange')
d.node('refresh',25,175,350,72,['refresh：打开新 segment 的 reader','新变更进入搜索视图','可见 ≠ 已完成持久化 commit'],'green')
d.node('fsync',405,175,350,72,['translog durability=request','按相应确认规则 fsync/commit','async 策略有不同丢失窗口'],'green')
d.node('flush',25,272,350,72,['后台 flush：Lucene commit','开始新 translog generation','限制恢复需要重放的范围'],'blue')
d.node('recover',405,272,350,72,['崩溃后恢复','最近有效 Lucene commit','再重放需要恢复的 translog'],'purple')
d.edge('index','translog');d.edge('index','refresh','bottom',color='green')
d.edge('translog','fsync','bottom',color='green');d.edge('flush','recover',color='purple')
d.edge('fsync','recover','bottom',color='purple',dashed=True)
d.footer(['左侧 refresh 与 flush 是不同后台动作，图未画成固定先后；refresh 不等于 fsync，merge 不等于 flush。',
    '段合并负责整理 segment / 回收删除空间；不应把提高 refresh 频率当作免费的实时一致性。'])
save(d,'25-search-visibility.svg')

# Controller metadata replication and broker data replication have separate memberships.
d = Diagram('Kafka KRaft：控制器仲裁与分区 ISR 是不同的复制集合',height=440,
    subtitle='实线表示该层日志复制；层间虚线表示分区等元数据影响 broker 的运行状态')
d.group('control',25,78,730,136,'控制面：controller quorum，复制集群元数据日志')
d.node('active',45,108,210,72,['活动 controller','协调分区与选主','元数据日志 leader'],'blue')
d.node('controller2',280,108,210,72,['controller 2','复制元数据日志','参与控制器仲裁'],'purple')
d.node('controller3',515,108,220,72,['controller 3','复制元数据日志','参与控制器仲裁'],'purple')
d.edge('active','controller2',color='purple')
d.path('M 150,185 C 150,212 625,212 625,191','purple')
d.group('data',25,239,730,136,'数据面：示例业务分区 P0，按该分区 leader / ISR 协议复制')
d.node('broker1',45,269,210,72,['broker 1：P0 leader','保存业务消息','接受该分区生产与读取'],'blue')
d.node('broker2',280,269,210,72,['broker 2：P0 follower','假设当前处于 ISR','复制业务分区日志'],'green')
d.node('broker3',515,269,220,72,['broker 3：P0 follower','假设当前处于 ISR','复制业务分区日志'],'green')
d.edge('broker1','broker2',color='green')
d.path('M 150,346 C 150,373 625,373 625,352','green')
d.path('M 390,219 L 390,228','gray',dashed=True)
d.footer(['控制器的多数派不等于 P0 的 ISR；上层健康也不能证明某个业务分区的数据可用或已提交。',
          '按 Kafka 4.1 角色语义示意：角色可配置分离或组合；省略元数据拉取、成员变化及其他分区。'])
save(d,'24-kraft-planes.svg')

# Watch the immediate predecessor, then re-read state; ownership does not fence old processes.
d = Diagram('ZooKeeper 锁配方：监听前驱，醒来后重新判断资格',height=419,
    subtitle='同一父路径下创建临时顺序节点；第一行箭头表示“监听直接前驱”，不是业务写入')
d.node('a',25,78,225,72,['A：lock-0001','序号最小，取得资格','节点依附 A 的 session'],'blue')
d.node('b',277.5,78,225,72,['B：lock-0002','等待并 watch A','只监听直接前驱'],'orange')
d.node('c',530,78,225,72,['C：lock-0003','等待并 watch B','避免全部竞争者被唤醒'],'orange')
d.edge('b','a','left',color='orange');d.edge('c','b','left',color='orange')
d.node('expired',25,175,225,72,['服务端判定 A 会话过期','删除 lock-0001','短暂断线不等于立即过期'],'pink')
d.node('notify',277.5,175,225,72,['B 收到变化通知','重读候选列表并检查','重新注册所需 watch'],'purple')
d.node('still',530,175,225,72,['C 的前驱 B 仍存在','继续等待 B 的变化','不凭别人的通知抢占'],'gray')
d.edge('a','expired','bottom',color='pink');d.edge('expired','notify',color='purple')
d.node('old',25,272,225,72,['A 的旧进程可能恢复','会话节点已消失','但进程仍可能发出旧写入'],'pink')
d.node('resource',277.5,272,225,72,['资源端：原子校验 token','已记录 B 的更新 token','拒绝随后到达的 A 旧写'],'green')
d.node('holder',530,272,225,72,['B 重查后成为最小者','获得新的有效资格','携带可验证 token 写入'],'blue')
d.edge('expired','old','bottom',color='pink');d.edge('old','resource',color='pink')
d.edge('holder','resource','left',color='blue');d.edge('notify','holder','bottom',color='purple')
d.footer(['watch 是重读状态的提示，不是完整事件日志；前驱已删除时要重新计算，不能永久等待旧事件。',
          '下层栅栏属于业务资源的额外机制，ZooKeeper 锁本身不会自动阻止旧进程写入外部数据库。'])
save(d,'25-zookeeper-predecessor.svg')

print('Generated 14 systems SVG diagrams.')
