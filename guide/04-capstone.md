# 综合练习：把知识串成可面试的工程证据

下面是自学项目设计，不是已经交付的生产系统。建议在单独练习目录实现，保留失败记录和实际测量，不能把设计假设当作上线结果。先做最小闭环，再逐步引入复杂性。

## 项目 A：可靠订单处理服务

**目标**：建立订单、扣减库存、发布事件、异步履约和查询状态。先用单进程服务与一个数据库，把状态机和幂等做好，再接入真实 MQ/Redis。技术基线可选 Java 21、Spring Boot 与兼容依赖、MySQL 8.x；具体版本在动手时锁定并验证。

### 最小数据模型

- orders：id、tenant_id、request_key、request_hash、status、version、created_at。
- inventory：sku_id、available、version。
- outbox：event_id、aggregate_id、event_type、payload、created_at、published_at。
- consumed_events：consumer、event_id；与业务结果同库事务维护。

唯一性必须包含正确作用域，如 `(tenant_id, request_key)`；不同 payload 复用同一键应被识别为冲突。外部履约仍需自身幂等，不能因为本库有 consumed_events 就宣称全链路原子。

### 分阶段验收

| 阶段 | 交付 | 必须验证的反例 |
| --- | --- | --- |
| A1 同步闭环 | 创建/查询 API、事务、唯一约束 | 并发重复提交、库存不足、payload 冲突 |
| A2 异步闭环 | Outbox、消费者状态机 | 提交后响应丢失、发布后未标记、消费后未确认 |
| A3 容量与隔离 | 限流、有界并发、超时、指标 | 热租户、慢依赖、积压与恢复 |
| A4 交付与复盘 | 灰度/回滚方案、压测报告 | 新旧版本共存、不可逆数据变更 |

### 证据清单

一张状态图、一张事务时间线、一份请求/响应示例、一组并发断言、一份故障注入记录、一份带环境与口径的性能报告。性能报告至少说明请求分布、持续时间、并发、吞吐、错误率、P50/P95/P99 和资源。不要预设“必须十万 QPS”。

**参考设计**：先在一个事务内完成订单/库存与 outbox；发布器可以重复发送；消费者将去重记录与本地业务变化同事务提交。对外调用使用稳定业务操作键，保留处理中/结果不确定状态，通过查询与对账恢复。参考 06～12 章和 [一致性实验](../labs/02-consistency.md)。

## 项目 B：有权限、有状态、可评测的工单 Agent

**目标**：用户问政策时检索文档；问工单时调用只读 API；申请退款时进入确定性授权/确认/执行流程。模型负责理解和提议，服务端负责权限、状态和副作用。

### 最小数据与接口

- documents：doc_id、tenant_id、acl、version、effective_at、content。
- agent_runs：run_id、user_id、tenant_id、goal、status、deadline、budget。
- tool_operations：operation_id、run_id、tool_name、arguments_hash、status、result_ref。
- evaluations：case_id、dataset_version、expected_route、expected_evidence、expected_business_state。

API 示例：`POST /runs`、`GET /runs/{id}`、`POST /runs/{id}/confirm`。确认绑定具体操作参数、身份和版本，参数改变必须重新确认；不能只保存一句模糊的“用户同意”。

### 分阶段验收

| 阶段 | 交付 | 必须验证的反例 |
| --- | --- | --- |
| B1 可测基线 | 固定数据集、规则路由、检索与引用 | 无答案、旧政策、同义问法、精确订单号 |
| B2 工具流程 | Schema/DTO 校验、授权、状态持久化 | 非法参数、越权、撤销权限、重复请求 |
| B3 模型接入 | 工具循环、流式状态、trace | 超时、无效输出、循环、工具失败 |
| B4 恢复与评测 | checkpoint、幂等、离线/线上评测 | 成功后丢响应、重启、提示注入、成本超限 |

**参考设计**：先让 workflow 完成受限目标，再开放必要的模型决策。检索先按可信权限收窄，生成后验证引用支持；检索内容不能改变工具权限。把回答质量、执行安全、最终任务成功分别评测。保留可人工接手的失败状态。参考 15～18 章和 [离线评测实验](../labs/03-agent-evaluation.md)。

## 面试时如何使用练习成果

明确说“这是我为验证某机制做的练习”，展示一个原始失败、修正方案和复测结果。面试官改变条件时，说明哪部分设计需要变，不假装自己经历过没有经历的生产规模。

完成两个项目不是开始投递的绝对前提。已有真实项目且证据充分，可以只用练习补齐没有覆盖过的机制。
