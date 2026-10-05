# 知识覆盖矩阵：用它检查遗漏与学习深度

本矩阵针对**资深 Java 后端 + Agent 应用工程**，将面试范围落实到资料内的讲解、问答、图与练习。它不是公司题库全集，也不声称任何面试的覆盖率为 100%。你可以用这一份资料完成系统复习；涉及自己履历上的特殊技术、岗位明确要求的底层实现时，再按对应官方来源延伸。

范围参考公开招聘准备说明中的编码、设计、项目和沟通能力，再对照常见 Java/Agent 技术主题检查缺口；技术结论以各章列出的规范、官方文档、原论文为依据。本项目题目和参考回答为面向学习的原创组织，不复制网上题库答案。

## 如何判定“覆盖”与“掌握”

- **覆盖**：资料中有解释或可定位回答，不能只有目录名、链接或一句定义。
- **L1**：90 秒准确说出概念；**L2**：能画机制、走流程；**L3**：能解决给定工程问题；**L4**：能解释约束、反例、故障与取舍。扩展章把大量 L3 问答放在一起，题目本身也会跨越多层。
- **P0**：后端主线优先；**P1**：核心广度/岗位相关，Agent 岗把 Agent 主线提到 P0；**P2**：按岗位和项目选学。优先级是教学安排，未伪装成统计面试频率。
- 阅读器“已通过模拟”应在闭卷回答与变式追问过关后再选。能复述参考答案但无法改一个条件继续推理，还未达到 L3。

## Java 语言、集合、并发、JVM

| 知识块 | 资料内入口 | 最低产出 | 优先级 |
|---|---|---|---|
| 值传递、对象身份、equals/hashCode、不可变 | [01](../modules/01-java-language.md)、[20](../modules/20-java-language-deep.md) | 手画引用变化，指出可变 key 反例 | P0 |
| String、常量池、拼接、包装类型、精度与时间 | [20](../modules/20-java-language-deep.md) | 解释比较语义、BigDecimal 和时区边界 | P0 |
| 泛型擦除、上下界、PECS、数组协变 | [01](../modules/01-java-language.md)、[20](../modules/20-java-language-deep.md) | 写一个能编译的生产者/消费者签名 | P0 |
| 异常、资源关闭、反射、注解、SPI | [20](../modules/20-java-language-deep.md) | 区分编译期与运行期责任、展示关闭顺序 | P0 |
| Stream/Lambda、序列化、IO/NIO、版本迁移 | [20](../modules/20-java-language-deep.md) | 解释副作用、反序列化边界及迁移验证 | P1 |
| ArrayList/链表、HashMap、树化/扩容 | [02](../modules/02-collections.md) | 按 hash 和 equals 走查找与扩容图 | P0 |
| ConcurrentHashMap、COW、迭代一致性 | [02](../modules/02-collections.md)、[21](../modules/21-concurrency-jvm-deep.md) | 区分单操作安全和复合业务原子性 | P0 |
| JMM、happens-before、volatile、final 发布 | [03](../modules/03-concurrency.md)、[21](../modules/21-concurrency-jvm-deep.md) | 画出可见性证明，识别丢更新 | P0 |
| synchronized、Lock、AQS、CAS/ABA、Condition | [21](../modules/21-concurrency-jvm-deep.md) | 解释竞争、排队、唤醒与重试条件 | P0 |
| 原子类、同步工具、ThreadLocal、死锁 | [03](../modules/03-concurrency.md)、[21](../modules/21-concurrency-jvm-deep.md) | 清理上下文，识别等待环与错误计数语义 | P0 |
| 线程池、队列、拒绝、关闭与取消 | [03](../modules/03-concurrency.md)、[21](../modules/21-concurrency-jvm-deep.md) | 画 execute 接纳决策，完成实验01 | P0 |
| CompletableFuture、ForkJoin、虚拟线程 | [03](../modules/03-concurrency.md)、[21](../modules/21-concurrency-jvm-deep.md) | 解释异常传播、阻塞与下游并发预算 | P0 |
| 类加载/初始化、双亲委派、JIT/逃逸分析 | [04](../modules/04-jvm.md)、[21](../modules/21-concurrency-jvm-deep.md) | 区分规范保证和 HotSpot 优化 | P0 |
| 内存区域、对象可达性、GC、G1/ZGC | [04](../modules/04-jvm.md)、[21](../modules/21-concurrency-jvm-deep.md) | 读 GC 日志思路，画引用与收集周期 | P0 |
| OOM、CPU、JFR、jcmd、容器内存 | [04](../modules/04-jvm.md)、[12](../modules/12-reliability.md)、[34](../modules/34-senior-engineering-scenarios.md) | 给出低风险取证路径与可证伪假设 | P0 |

## Spring、数据库、缓存与消息

| 知识块 | 资料内入口 | 最低产出 | 优先级 |
|---|---|---|---|
| IoC、生命周期、扩展点、作用域、循环依赖 | [05](../modules/05-spring.md)、[22](../modules/22-spring-mybatis-deep.md) | 画定义到销毁过程，说明代理对象何时形成 | P0 |
| AOP、事务传播/隔离、回滚、自调用 | [05](../modules/05-spring.md)、[22](../modules/22-spring-mybatis-deep.md) | 推演代理边界与 rollback-only | P0 |
| Boot 自动配置、配置绑定、MVC 链路 | [22](../modules/22-spring-mybatis-deep.md) | 解释条件装配、Filter/Interceptor/Advice | P0 |
| MyBatis 绑定、映射、插件、缓存、分页/N+1 | [22](../modules/22-spring-mybatis-deep.md) | 指出SQL注入与缓存失效边界 | P0 |
| JDBC 连接池、事务占用、超时 | [05](../modules/05-spring.md)、[23](../modules/23-database-sql-deep.md)、[29](../modules/29-os-network-deep.md) | 从请求到连接给出时间预算 | P0 |
| B+树、聚簇/二级/覆盖索引、联合索引 | [06](../modules/06-mysql.md)、[23](../modules/23-database-sql-deep.md) | 手推执行访问路径并评估写放大 | P0 |
| MVCC、ReadView、隔离、当前读与锁 | [06](../modules/06-mysql.md)、[23](../modules/23-database-sql-deep.md) | 画事务交错与可见版本 | P0 |
| redo/undo/binlog、恢复、复制/切换 | [06](../modules/06-mysql.md)、[23](../modules/23-database-sql-deep.md) | 解释持久化与复制确认的不同边界 | P0 |
| 慢 SQL、EXPLAIN、统计信息、分页 | [23](../modules/23-database-sql-deep.md) | 从扫描量、排序、回表、锁验证改进 | P0 |
| JOIN、聚合、NULL、窗口、排名、连续日期 | [23 SQL 工作题](../modules/23-database-sql-deep.md) | 根据给定数据算出并核对9组结果 | P0 |
| 分库分表、路由、扩容、CDC/迁移 | [09](../modules/09-distributed.md)、[23](../modules/23-database-sql-deep.md)、[33](../modules/33-system-design-cases.md) | 说明全量与增量衔接、对账与回滚 | P1 |
| Redis 数据结构与编码、复杂度、大 key | [07](../modules/07-redis.md)、[24](../modules/24-cache-messaging-deep.md) | 按访问模式选结构，指出阻塞风险 | P0 |
| RDB/AOF、fork/COW、过期/淘汰 | [24](../modules/24-cache-messaging-deep.md) | 区分持久化策略、资源峰值和恢复窗口 | P0 |
| Cluster/Sentinel、slot、MOVED/ASK、复制 | [24](../modules/24-cache-messaging-deep.md) | 解释客户端路由与故障时丢写条件 | P1 |
| 缓存穿透/击穿/雪崩、一致性/Bloom | [07](../modules/07-redis.md)、[24](../modules/24-cache-messaging-deep.md) | 手画删除后仍读旧值的竞态 | P0 |
| 租约锁、续租、唯一 token/fencing | [07](../modules/07-redis.md)、[09](../modules/09-distributed.md) | 解释旧持有者写入为什么仍危险 | P0 |
| 投递确认、业务幂等、顺序、重试/死信 | [08](../modules/08-messaging.md)、[24](../modules/24-cache-messaging-deep.md) | 不跨越未完成offset，画业务提交与ACK窗口 | P0 |
| Kafka 分区、ISR/HW/LSO、幂等/事务 | [24](../modules/24-cache-messaging-deep.md) | 区分 broker 保证与外部业务效果 | P0 |
| Kafka KRaft控制面、重平衡、位点、保留/压缩 | [24](../modules/24-cache-messaging-deep.md) | 推演消费者崩溃重启与重复处理 | P1 |
| RabbitMQ、RocketMQ 的差异与边界 | [24](../modules/24-cache-messaging-deep.md) | 能按自身栈继续深挖，避免不同产品术语混用 | P1 |

## 分布式、服务治理、搜索与系统工程

| 知识块 | 资料内入口 | 最低产出 | 优先级 |
|---|---|---|---|
| CAP、一致性模型、Raft、仲裁 | [09](../modules/09-distributed.md) | 画网络分区，解释读写承诺 | P0 |
| 2PC/TCC/Saga、Outbox、幂等/对账 | [09](../modules/09-distributed.md)、[33](../modules/33-system-design-cases.md) | 标出本地事务与外部副作用，跑实验02 | P0 |
| ZooKeeper会话、临时顺序节点与前驱watch | [25](../modules/25-governance-search-deep.md) | 推演会话失效、一次性watch与重新判断条件 | P1 |
| 发现、负载均衡、RPC/序列化、配置 | [25](../modules/25-governance-search-deep.md)、[29](../modules/29-os-network-deep.md) | 解释摘流延迟、客户端缓存和兼容 | P0 |
| deadline、重试预算、退避、熔断、隔离 | [09](../modules/09-distributed.md)、[25](../modules/25-governance-search-deep.md) | 计算放大倍数，制定过载策略 | P0 |
| 限流、令牌桶、ID、调度/租约 | [25](../modules/25-governance-search-deep.md)、[33](../modules/33-system-design-cases.md) | 说明精度、时钟、唯一性和资源边界 | P0 |
| 倒排索引、分词、BM25、segment | [25](../modules/25-governance-search-deep.md)、[27](../modules/27-rag-memory-retrieval-deep.md) | 画从词到文档候选的路径 | P1 |
| 搜索 refresh/flush/merge、shard/replica | [25](../modules/25-governance-search-deep.md) | 区分可搜索、持久化、合并与副本 | P1 |
| 深分页、PIT/search_after、重建与删除 | [25](../modules/25-governance-search-deep.md)、[33](../modules/33-system-design-cases.md) | 给稳定排序、增量追平与权限删除方案 | P1 |
| 进程/线程、虚拟内存、page fault、fork | [29](../modules/29-os-network-deep.md) | 区分地址空间与物理内存，解释COW | P0 |
| IO模型、epoll、Reactor/Netty | [10](../modules/10-network-os.md)、[29](../modules/29-os-network-deep.md) | 区分就绪和完成，不阻塞事件循环 | P0 |
| TCP握手/挥手、可靠性、窗口/拥塞、粘包 | [10](../modules/10-network-os.md)、[29](../modules/29-os-network-deep.md) | 画连接与应用分帧，诊断超时 | P0 |
| DNS、HTTP缓存/版本、TLS、SSE/WebSocket | [29](../modules/29-os-network-deep.md) | 走完整请求路径并识别重放/缓存边界 | P0 |
| 容量估算、Little定律、故障域、热点 | [11](../modules/11-system-design.md)、[33](../modules/33-system-design-cases.md) | 给有单位的数量级与单域失效余量 | P0 |
| SLI/SLO、错误预算、指标/日志/trace | [12](../modules/12-reliability.md)、[34](../modules/34-senior-engineering-scenarios.md) | 定义分母、窗口和告警行动 | P0 |
| AuthN/AuthZ、JWT/OAuth/OIDC、租户隔离 | [13](../modules/13-security-delivery.md)、[31](../modules/31-security-cloud-delivery.md) | 列对象级允许/拒绝测试矩阵 | P0底线 |
| CSRF/XSS/CORS、SQL注入、SSRF、密钥 | [31](../modules/31-security-cloud-delivery.md) | 区分攻击前提与每条防线的限制 | P1 |
| 测试分层、供应链、CI/CD、兼容演进 | [13](../modules/13-security-delivery.md)、[31](../modules/31-security-cloud-delivery.md) | 给发布、回滚、迁移和验收证据 | P1 |
| Docker/K8s、探针/资源、HPA、优雅退出 | [29](../modules/29-os-network-deep.md)、[31](../modules/31-security-cloud-delivery.md) | 画健康决策，解释节流与OOMKilled | P1 |
| 备份恢复、RPO/RTO、容灾演练 | [12](../modules/12-reliability.md)、[31](../modules/31-security-cloud-delivery.md) | 给实际恢复步骤与数据校验证据 | P1 |
| 模式、SOLID、DDD、聚合/领域服务、CQRS | [30](../modules/30-design-domain.md) | 从业务不变量划分边界，拒绝无收益抽象 | P1 |

## LLM、RAG、Agent 工程

| 知识块 | 资料内入口 | 最低产出 | 优先级 |
|---|---|---|---|
| token、上下文、采样、结构化输出 | [15](../modules/15-llm-foundations.md)、[26](../modules/26-llm-training-inference-deep.md) | 区分语法合格与业务正确 | P1/Agent P0 |
| Transformer、QKV、mask、位置、归一化 | [26](../modules/26-llm-training-inference-deep.md) | 画因果注意力与下一token预测 | P1/Agent P0 |
| MHA/MQA/GQA、MoE、训练与推理 | [26](../modules/26-llm-training-inference-deep.md) | 解释计算/缓存取舍，不用参数量代替效果 | P1 |
| prefill/decode、KV cache、批处理/量化 | [15](../modules/15-llm-foundations.md)、[26](../modules/26-llm-training-inference-deep.md) | 区分TTFT/生成速率，算显存数量级 | P1/Agent P0 |
| SFT、LoRA、DPO/RL、蒸馏/评测泄漏 | [26](../modules/26-llm-training-inference-deep.md) | 能选检索、提示或微调；训练数学深挖按JD | P1/P2 |
| RAG入库/查询、解析、分块、版本/引用 | [16](../modules/16-rag.md)、[27](../modules/27-rag-memory-retrieval-deep.md) | 画双链路与更新删除流程 | P1/Agent P0 |
| BM25/向量、embedding、HNSW/IVF、混合 | [27](../modules/27-rag-memory-retrieval-deep.md) | 解释近似召回与参数/资源权衡 | P1/Agent P0 |
| rerank、RRF、改写、父子块、GraphRAG | [27](../modules/27-rag-memory-retrieval-deep.md) | 根据失败类型改组件，而非随意加链路 | P1 |
| ACL、记忆、失效、撤权、数据来源 | [16](../modules/16-rag.md)、[27](../modules/27-rag-memory-retrieval-deep.md) | 明确权限生效窗口与来源可信度 | P1/Agent P0 |
| Recall/MRR/nDCG、groundedness、任务成功 | [16](../modules/16-rag.md)、[18](../modules/18-agent-production.md)、[27](../modules/27-rag-memory-retrieval-deep.md) | 手算分母、空样本及宏微平均 | P1/Agent P0 |
| Workflow/Agent/ReAct、规划、并行/取消 | [17](../modules/17-agent-architecture.md)、[28](../modules/28-agent-protocol-delivery-deep.md) | 按任务选择自治程度与停止条件 | P1/Agent P0 |
| Tool schema、身份/权限、幂等/审批 | [17](../modules/17-agent-architecture.md)、[28](../modules/28-agent-protocol-delivery-deep.md) | 模型建议与真实执行权分离 | P1/Agent P0 |
| checkpoint、恢复、UNKNOWN、重放 | [17](../modules/17-agent-architecture.md)、[28](../modules/28-agent-protocol-delivery-deep.md) | 画副作用状态机并注入崩溃 | P1/Agent P0 |
| MCP架构/传输/授权、A2A、Skills、多Agent | [28](../modules/28-agent-protocol-delivery-deep.md) | 区分互操作协议与安全/可靠性承诺 | P1 |
| 提示注入、外泄、沙箱、脱敏与审计 | [18](../modules/18-agent-production.md)、[28](../modules/28-agent-protocol-delivery-deep.md) | 给攻击样本与服务端拒绝证据 | P1/Agent P0 |
| 评测集、judge校准、版本/灰度、成本/SLO | [18](../modules/18-agent-production.md)、[34](../modules/34-senior-engineering-scenarios.md) | 跑实验03并解释fixture与真实评测差距 | P1/Agent P0 |
| Java模型集成与框架选型 | [28](../modules/28-agent-protocol-delivery-deep.md) | 设计超时、流式取消、连接与预算边界 | P1/Agent P0 |

## 编码、设计与真实项目

| 知识块 | 资料内入口 | 最低产出 | 优先级 |
|---|---|---|---|
| 哈希/前缀、窗口、双指针、二分/单调栈 | [14](../modules/14-algorithms.md)、[32](../modules/32-algorithm-coding-deep.md) | 正确代码、复杂度与边界用例 | P0 |
| 链表、树、图、BFS/DFS、拓扑、并查集 | [32](../modules/32-algorithm-coding-deep.md)、[实验04](../labs/04-coding.md) | 解释visited、状态与依赖顺序 | P0 |
| 堆/排序、TopK、回溯/DP/贪心、LRU | [32](../modules/32-algorithm-coding-deep.md) | 给不变量、反例与可运行实现 | P0 |
| 订单秒杀/支付、短链、IM/Feed、调度 | [33](../modules/33-system-design-cases.md) | 一份有假设和故障窗口的完整设计 | P0 |
| 文件/导出、网关、搜索/报表、Agent平台 | [33](../modules/33-system-design-cases.md) | 容量、权限、恢复与演进路线 | P0/P1 |
| 项目深挖、STAR/证据、失败复盘、协作 | [19](../modules/19-project-interview.md)、[34](../modules/34-senior-engineering-scenarios.md) | 两份真实项目叙事和一份失败复盘 | P0 |
| CPU/内存/锁/积压/尾延迟/Agent事故 | [12](../modules/12-reliability.md)、[34](../modules/34-senior-engineering-scenarios.md) | 根据新证据修正假设，而非背工具清单 | P0 |

## 按岗位增加的深度，不伪装成通用必修

| 岗位信号 | 本资料提供的起点 | 还需围绕岗位做的准备 |
|---|---|---|
| 数据库/中间件内核研发 | JVM、MVCC、日志、复制、消息、共识机制 | 目标产品源码路径、存储格式、性能基准与真实修复 |
| 高性能网络/基础架构 | OS、TCP、epoll、Netty、容量与故障域 | 内核/硬件细节、特定传输栈和可复现性能工程 |
| 模型训练/算法研究 | Transformer、训练方法、推理与评测基础 | 数学推导、优化器、分布式训练、实验论文复现 |
| 推荐/广告/流计算/大数据 | Feed、搜索、数据链路和事件时间概念 | 特定算法、Flink/Spark等执行与状态机制；本项目未写成专岗教材 |
| 管理或专家级别强领域岗位 | 技术判断、协作、复盘、领域设计 | 组织规模、业务战略、预算及目标行业的真实成果 |

这些边界不是将主线内容外包给链接。主线答案已写在资料内；岗位专门化的深度没有统一上限，应根据 JD 与履历确定。

## 复习顺序与漏项处理

先做 [诊断](02-assessment.md)，按 [路线](01-roadmap.md)补主线，再逐行抽查矩阵：随机选一个点，90秒解释、3分钟画图、5分钟变式。答不出时把“术语不清/机制断层/条件错误/无证据/代码错误”记入 [复盘模板](../practice/review-template.md)。每周根据错因调整，不以翻完页数衡量掌握。

来源范围核对：[Amazon SDE III 官方准备](https://www.amazon.jobs/content/en/how-we-hire/sde-iii-interview-prep)、[Microsoft 官方技术面试准备](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing.html/)。它们支持能力维度，不能推出某一道题必考或某个章节等于某个职级。
