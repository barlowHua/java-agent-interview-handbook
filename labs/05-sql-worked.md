# 实验 05 · SQL 手推与隔离执行核对

## 目的与范围

配合 [23 数据库与 SQL 深挖](../modules/23-database-sql-deep.md) 的九组小数据查询：先在纸上写结果，再执行 SQL 比较。理解结果后才增加数据量看索引与执行计划，避免把错误查询优化得更快。

本轮实际验证时间：2026-10-04。环境提供 MySQL **9.3.0 for macOS 15.2 on arm64（Homebrew）**。Docker CLI 存在但 daemon 未运行，因此没有把这次验证标为 MySQL 8.4 容器实验。所有查询在新建 `/tmp/handbook-sql-*` 数据目录、独立 Unix socket、禁用 TCP 的实例执行；没有连接现有数据库。完成后实例已通过自己的 socket 正常关闭，并删除本轮临时数据目录。

**验证结论：九组查询输出全部与讲义预期一致。** 此结论限于小数据 SQL 的实际结果，不证明 MySQL 8.4 的锁行为、优化器计划、复制、DDL 或故障恢复。课程的这些版本敏感机制仍按 8.4 官方材料说明，应在目标环境再做对应实验。

## 精确启动与关闭参数

实际验证程序使用 Python 的 `tempfile.mkdtemp(prefix='handbook-sql-')` 创建唯一目录，再用 `subprocess` 参数数组启动进程。以下命令以变量表示该次临时目录，其他参数与执行时一致；二进制路径需按个人环境调整。只对这个新目录操作，不指向已有数据目录。

```bash
HANDBOOK_SQL_TMP=$(mktemp -d /tmp/handbook-sql-XXXXXX)
/opt/homebrew/bin/mysqld --no-defaults --initialize-insecure \
  --datadir="$HANDBOOK_SQL_TMP/data" \
  --log-error="$HANDBOOK_SQL_TMP/init.log"

/opt/homebrew/bin/mysqld --no-defaults \
  --datadir="$HANDBOOK_SQL_TMP/data" \
  --socket="$HANDBOOK_SQL_TMP/mysql.sock" \
  --pid-file="$HANDBOOK_SQL_TMP/pid" \
  --log-error="$HANDBOOK_SQL_TMP/server.log" \
  --skip-networking --mysqlx=OFF --skip-log-bin &

/opt/homebrew/bin/mysql --no-defaults --protocol=socket \
  --socket="$HANDBOOK_SQL_TMP/mysql.sock" -uroot \
  --batch --raw --skip-column-names
```

客户端只连该 socket，先执行 `SELECT 1` 确认就绪，再建 `handbook_drill` 测试库。验证程序从第 23 章提取 **10 段 sql 代码块**：第 1 段创建数据，随后 9 段依次运行；没有重新抄写另一套查询。每组输出与固定预期逐字比较，区别仅在 AVG 实际显示为 `82.5000`，数值等于讲义 `82.5`。

```sql
CREATE DATABASE handbook_drill;
USE handbook_drill;
-- 在此依次执行第23章的数据准备和9组查询。
```

完成后正常关闭本轮实例。临时目录只在对应进程退出后清理；若中途失败，应先保留日志排查。

```bash
/opt/homebrew/bin/mysqladmin --no-defaults --protocol=socket \
  --socket="$HANDBOOK_SQL_TMP/mysql.sock" -uroot shutdown
```

`--initialize-insecure` 仅用于这个无 TCP 的短期本地实验实例；它不是线上实例的初始化建议。

## 九组实际输出与解释

| 组 | 内容 | 实际输出摘要 | 结果 |
| --- | --- | --- | --- |
| 1 | WHERE + HAVING | `(1,200)` | 一致 |
| 2 | COUNT、SUM、AVG | `5,4,330,82.5000` | 一致 |
| 3 | LEFT JOIN 已付订单计数 | `(1,2),(2,1),(3,1),(4,0)` | 一致 |
| 4 | 每组最新订单与金额排名 | `(102,1,100,1),(104,2,NULL,2),(105,3,80,1)` | 一致 |
| 5 | 降序游标下一页 | `103,102` | 一致 |
| 6 | NOT IN 与 NOT EXISTS | 含 NULL 的 NOT IN 无结果；NOT EXISTS 为 `1,3,4` | 一致 |
| 7 | 库存条件更新 | 两次 ROW_COUNT 为 `1,0`，最终库存 `0` | 一致 |
| 8 | 一对多重复累计 | 错误求和 `101,200`；先聚合后连接 `101,100,100` | 一致 |
| 9 | 去重后连续日期分组 | `(1,2026-10-04,2026-10-06,3)`；重复登录不延长天数 | 一致 |

[机器可读验证结果](sql-validation-results.json) 保存服务器版本、每组 expected/actual 和通过状态。九组使用单会话按序运行；第 7 组的并发等待推理还需另外启动两客户端控制时序验证，不计入本次已完成结果。

## 继续练习与过关

1. 不看参考结果，给客户 4 添加一笔 PENDING 订单。参考：ON 内过滤仍保留客户 4 且计数为 0；移到 WHERE 后不能简单靠 `OR o.id IS NULL` 保留它。
2. 给客户 1 再添加同金额订单，重算窗口函数和 JOIN 聚合。参考：并列名次与确定行号不同，按金额 DISTINCT 不是业务去重。
3. 在游标第一页之后插入一笔更晚订单，再修改一笔旧订单的排序时间。参考：游标缩小了范围，但没有自动冻结全部数据视图。
4. 在 MySQL 8.4 的隔离测试实例做 RR/RC 双会话实验，记录每一步 SQL、提交次序和输出，勿把本轮 9.3.0 的通用查询结果当作所有版本的并发证明。

过关要求是能解释每一行结果为什么出现或消失，而不是仅复制 SQL 看到查询成功。
