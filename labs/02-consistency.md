# 实验 02 · Outbox、崩溃窗口与业务幂等

## 目标与前置

P0 实验，建议 60～90 分钟。前置：阅读 [消息](../modules/08-messaging.md) 与 [分布式](../modules/09-distributed.md)。只需 Python 3.10+ 标准库与其内置 SQLite，无需安装依赖或外部服务。先预测每个崩溃点的持久状态，再运行验证；不要把输出 PASS 当作已经理解协议。

你要证明三条不变量：订单与待发事件一起提交；一个消费身份对一个事件的积分效果最多一次；未确认事件可以恢复处理。第三条具有前提：恢复执行最终会发生、存储可用且消息未超过保留期，因此不是对所有故障的无限保证。

## 模型与边界

脚本创建三个独立 SQLite 文件：producer 保存订单及 Outbox，broker 保存投递和确认标志，consumer 保存 Inbox、积分流水和余额。三者没有跨库事务。broker 允许同一个 event ID 对应多个 delivery ID，用来区分业务事件与网络投递。

工作进程在指定位置调用 `os._exit(97)` 真正退出，不走正常清理和事务提交；主进程重新连接并验证持久状态。这样可以模拟进程在提交前后崩溃的协议窗口。临时数据自动清理；不连接公司系统，不写项目以外的业务数据。

SQLite 的事务恢复与真实消息系统不同：本实验没有网络、broker 复制、Kafka 分区、RabbitMQ confirm、消费者组重平衡、多个 relay 并发或操作系统掉电。它验证应用提交边界和重复处理，不证明任一中间件部署的可靠性。[SQLite 原子提交说明](https://www.sqlite.org/atomiccommit.html) · [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)

## 运行

在项目根目录执行：

```bash
python3 labs/consistency_demo.py
```

预期输出五个 `PASS`，最终：

```text
RESULT: orders=1, outbox=1, broker_deliveries=2, ledger=1, points=100
All invariants passed. This verifies local protocol windows, not real middleware guarantees.
```

每次运行使用全新临时目录，可以重复执行。脚本失败会抛异常并返回非零状态；不要删除检查语句来获得通过。

## 逐步推演与参考答案

| 步骤与崩溃位置 | 恢复后应看到什么 | 为什么 |
|---|---|---|
| producer 写订单和事件，提交前崩溃 | 两表都为 0 | 同一本地事务尚未提交 |
| producer 提交后、发送前崩溃 | 订单 1，待发事件 1，broker 0 | 本地事务已经提供可恢复发送凭据 |
| relay 发布成功后、标记已发前崩溃 | broker 1，Outbox 仍待发 | 发送与标记分属两个原子边界 |
| relay 重启 | broker 2，同 event ID | 无法区分上次未发与已发未标记，只能允许重发 |
| consumer 写 Inbox 与积分，提交前崩溃 | Inbox 0，积分 0 | 去重与副作用一起回滚 |
| consumer 提交后、确认前崩溃 | Inbox 1，积分 100，仍未确认 | 已完成业务，但投递方不知道 |
| consumer 恢复并处理两次投递 | 两次确认，积分仍为 100 | Inbox 唯一约束识别重复，事务不再次加积分 |

注意：一个业务事件实际会被投递、读取或尝试处理多次。本例达到的是限定条件下消费者数据库内单次业务效果，不能称为端到端“只执行一次”。外部邮件、第三方扣款没有参加 consumer 的 SQLite 事务。

## 阅读关键代码

`create_order` 的 `BEGIN IMMEDIATE` 到 `commit` 覆盖订单与 Outbox。`relay` 的两个存储提交之间故意留下重复窗口。`consume` 把 Inbox 插入、积分流水和余额更新放在一个事务里，提交后再设置 broker 确认。

`(consumer_name,event_id)` 表达按消费身份去重的作用域。本实验仅模拟一个积分消费者；积分流水表另以 event_id 唯一，不能通过更换 consumer_name 在同一业务表重复记账。其他独立消费者应使用自己的业务存储与约束。重复消息沿用原 event ID；delivery ID 只代表投递。若重试重新生成 event ID，本示例会当成新事件，幂等语义就不成立。真实系统还要校验相同事件 ID 携带的关键内容一致，避免数据冲突被静默吞掉。

## 扩展练习与验证方法

1. **删除 Inbox 与业务共同事务。**先单独提交 Inbox 再故障退出。预测：恢复后认为已处理，积分却是 0。验证时复制脚本到个人练习目录修改，保留原版作为对照。
2. **改成先确认再执行业务。**确认后退出。预测：消息不再被拉取，但积分没增加，这是丢处理窗口。
3. **在 relay 标记已发后才发送。**标记后退出。预测：Outbox 不再重试，broker 没记录；用它说明调换顺序无法凭空创造分布式事务。
4. **删除旧 Inbox 后回放。**预测：旧事件可能再次产生效果。本脚本还有流水唯一约束，因此将暴露唯一冲突；讨论真实业务如何选择持久业务唯一键及幂等记录保留期。
5. **把加分换成 HTTP 扣款。**不要调用真实支付接口，只画时间线。参考答案：需要支付方稳定请求号和结果查询；单个本地事务不能原子包含外部 HTTP 效果。
6. **多个 relay 与 worker。**写出需要添加的抢占、租约、版本、并发唯一冲突与重试规则。不要声称现有顺序脚本已验证并发协议。

## 面试表达模板与过关标准

“我们将订单与 Outbox 写在同一本地事务，relay 允许重复投递。消费者把去重记录和积分变化放在另一份本地事务，提交后确认。用五个真实子进程退出点验证：提交前全部回滚，发送后崩溃可重投，消费提交后崩溃不重复加分。该实验覆盖应用进程崩溃，不覆盖真实 broker 集群或外部副作用。”

过关：运行前准确预测表中结果；能解释每条唯一约束的作用域；能指出两处结果未知窗口；至少完成一项反例练习并写下失败证据。回到 Java 时，将这个协议映射为 Spring 本地事务、数据库唯一约束和真实消息客户端确认，不要把事务注解错误扩展到 broker。

## 官方来源

核对日期：2026-10-04。上述 SQLite、Python 文档说明本地实验机制；[Debezium Outbox 文档](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) 提供真实 CDC 集成入口，轮询 relay 与 CDC 的实现不同，但同样要讨论重放及消费者幂等。
