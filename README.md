# Java × Agent 资深工程师面试研修手册

面向约 10 年开发经验，目标为大厂资深 Java 后端或 Agent 应用工程岗位。扩充审校版：2026-10-04。

**打开 [离线阅读器](index.html) 开始学习。** 直接用浏览器打开，不需要服务、账号或 API key。正文保存在 Markdown 中，便于在 IDE 里阅读、补充和版本管理。

## 包含什么

- 34 个专题，按 L1 基础口述、L2 原理解释、L3 工程应用、L4 架构取舍组织。
- 445 组完整问答与追问，同步生成 445 张复习卡片；原有 119 张卡片保持题目与 ID 对应。
- 12 周主干、16 周完整专题、14 天冲刺路线；知识覆盖矩阵、入学诊断与 4 场模拟面试。
- 5 组动手实验：Java 并发、Outbox 崩溃恢复、Agent 离线评测、Java 算法、SQL 推演验证。
- 24 个算法训练任务、19 组 Java 参考实现、9 组 SQL 工作题、10 个完整系统设计案例，以及 2 个综合练习设计。
- 41 张原创 SVG 机制图：可离线放大、缩放、下载；配读图说明、边界与闭卷重画题。
- 全文搜索、专题筛选、章节状态、个人笔记、卡片复习安排、进度导入/导出。

章节优先级是学习安排，不是面试频率统计；层级不映射公司职级。资料覆盖通用准备基础，不能保证录用。理解、闭卷表达、现场编码、工程验证与真实项目证据，需要一起练习。

## 从哪里开始

1. 阅读 [使用方法](guide/00-start.md)，掌握每次 90 分钟的学习流程。
2. 做 [入学诊断](guide/02-assessment.md)，找出得分最低的 P0 模块。
3. 按 [学习路线](guide/01-roadmap.md) 复习；每天留出编码与闭卷回忆时间。
4. 每周做一次 [模拟面试](guide/03-mock-interviews.md)，记录问题，再回到讲义补缺。
5. 用 [综合练习](guide/04-capstone.md) 把知识串成能展示的工程证据。

用 [知识覆盖矩阵](guide/06-knowledge-coverage.md)检查是否遗漏，用 [机制图谱](guide/05-diagram-atlas.md)集中回忆关键机制。本轮扩充与修正见 [审校记录](REVIEW.md)。

## 模块专题

| 专题 | 讲义 | 优先级 |
| --- | --- | --- |
| Java 语言与代码设计 | [01](modules/01-java-language.md) | P0 |
| 集合、哈希与并发容器 | [02](modules/02-collections.md) | P0 |
| 并发、线程池与虚拟线程 | [03](modules/03-concurrency.md) | P0 |
| JVM、GC 与线上诊断 | [04](modules/04-jvm.md) | P0 |
| Spring、Boot 与事务边界 | [05](modules/05-spring.md) | P0 |
| MySQL 索引、事务与锁 | [06](modules/06-mysql.md) | P0 |
| Redis 缓存与租约 | [07](modules/07-redis.md) | P0 |
| 消息、顺序与幂等 | [08](modules/08-messaging.md) | P0 |
| 分布式一致性与恢复 | [09](modules/09-distributed.md) | P0 |
| 网络、Linux 与请求链路 | [10](modules/10-network-os.md) | P0 |
| 系统设计与容量估算 | [11](modules/11-system-design.md) | P0 |
| SLO、排障与稳定性 | [12](modules/12-reliability.md) | P0 |
| 安全、测试与交付 | [13](modules/13-security-delivery.md) | P1；安全底线必修 |
| 算法与现场编码 | [14](modules/14-algorithms.md) | P0 |
| LLM 基础与模型接口 | [15](modules/15-llm-foundations.md) | P1；Agent 岗 P0 |
| RAG、检索与评测 | [16](modules/16-rag.md) | P1；Agent 岗 P0 |
| Agent 工具、状态与记忆 | [17](modules/17-agent-architecture.md) | P1；Agent 岗 P0 |
| Agent 评测、安全与恢复 | [18](modules/18-agent-production.md) | P1；Agent 岗 P0 |
| 项目深挖与技术表达 | [19](modules/19-project-interview.md) | P0 |

### 深挖与综合专题（按主题与01～19配对阅读）

| 专题 | 入口 |
|---|---|
| 语言/OOP、精度、泛型、IO、版本演进 | [20](modules/20-java-language-deep.md) |
| AQS、锁、并发工具、类加载、JIT、GC | [21](modules/21-concurrency-jvm-deep.md) |
| Spring/Boot/MVC、事务、MyBatis | [22](modules/22-spring-mybatis-deep.md) |
| SQL、索引、隔离、日志、复制、迁移 | [23](modules/23-database-sql-deep.md) |
| Redis、Kafka、RabbitMQ、RocketMQ | [24](modules/24-cache-messaging-deep.md) |
| 服务治理、ZooKeeper、调度、Elasticsearch | [25](modules/25-governance-search-deep.md) |
| Transformer、训练选型、推理与KV缓存 | [26](modules/26-llm-training-inference-deep.md) |
| 混合检索、ANN、重排、记忆、评测 | [27](modules/27-rag-memory-retrieval-deep.md) |
| Agent编排、MCP/A2A、工具与可靠交付 | [28](modules/28-agent-protocol-delivery-deep.md) |
| 操作系统、TCP、HTTP、TLS、Netty | [29](modules/29-os-network-deep.md) |
| 设计模式、领域建模、聚合、CQRS | [30](modules/30-design-domain.md) |
| 安全、容器、K8s、测试、发布与灾备 | [31](modules/31-security-cloud-delivery.md) |
| 算法题型、正确性证明与Java实现 | [32](modules/32-algorithm-coding-deep.md) |
| 10个系统设计案例 | [33](modules/33-system-design-cases.md) |
| 排障、项目、决策、协作与资深面试 | [34](modules/34-senior-engineering-scenarios.md) |

每章含机制解释、情境取舍、参考回答、追问、误区、练习、过关标准和来源。Java 以 17/21 为学习基线，历史版本与后续演进分别标注；中间件/框架的配置和协议需匹配目标版本。

## 实验入口

- [Java 并发实验](labs/01-java-concurrency.md)：基础并发与 JDK 21 虚拟线程对照。
- [Outbox 与崩溃恢复](labs/02-consistency.md)：`python3 labs/consistency_demo.py`，要求 Python 3.10+。
- [Agent 离线评测](labs/03-agent-evaluation.md)：`python3 labs/agent_eval_demo.py --self-test`，要求 Python 3.9+。
- [Java 编码实验](labs/04-coding.md)：原10组133检查、手写LRU千步不变量、新8组2527检查，JDK 8+。
- [SQL 手推与验证](labs/05-sql-worked.md)：9组查询实跑与预期一致；实际验证环境为隔离 MySQL 9.3.0。

并发数据库事务、真实中间件故障与综合项目是待你实施的训练任务；离线 fixture、SQLite 模拟不等于真实模型或生产中间件验证。实际已执行的检查详见 [验收记录](VALIDATION.md)。

## 学习进度

进度与笔记保存在当前浏览器的本地存储中，不会上传。浏览器、文件路径或存储策略变化可能影响读取，请定期导出 JSON。导入按更新时间合并；格式错误会拒绝，不会用空值替换已有笔记。原有进度损坏时暂停覆盖，导出会带上原始字符串便于恢复。

## 编辑后重建阅读器

阅读已经生成的 index.html 无需安装依赖。仅编辑正文后重新生成时需要 Python 3.10+ 和 mistune：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --index-url https://pypi.org/simple -r requirements.txt
.venv/bin/python tools/build.py
.venv/bin/python tools/validate.py
python3 tools/check_svg.py
```

以上激活方式用于 macOS/Linux；Windows 使用 `.venv\Scripts\python.exe`。生成器从题目正文提取复习卡，避免题卡与讲义答案不同步。修改后应重新检查链接和代码实验。修改图后先运行 `python3 tools/make_atlas.py`，再重建；SVG可由 `tools/draw_*.py` 对应绘图脚本重生成，并用浏览器做视觉检查。

## 继续学习时怎么提问

> 按这个项目第 03 章面试我。一次一道主问题，先追问再反馈，给出错误类型与复习任务，不要提前展示参考答案。

> 我没有理解第 09 章 Outbox 的崩溃窗口，请用逐步时间线讲解，然后出一道变式题检验我。

模板位于 [个人复盘记录](practice/review-template.md)。本项目不包含个人生产系统资料，后续补充时应使用自己的脱敏事实。
