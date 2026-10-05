# 扩充版验收记录

日期：2026-10-04。当前34章、445组问答、41张SVG、5个实验专题。这里区分实际执行与待实施的训练设计。

## 内容与发布物

- 34章逐组补充与交叉复查；L1–L4层级、追问、练习/闭卷验收、图和来源均有可定位内容。完整覆盖清单见 [矩阵](guide/06-knowledge-coverage.md)，发现和修正见 [审校记录](REVIEW.md)。
- 本地Markdown链接、题卡数量与唯一ID、文档集合、章节正文与离线HTML同步检查通过。原119张卡片的ID与问题文本逐一对照，未因新增图解/章节发生错位。
- 校验器同时检查脚本/样式/模板及嵌入SVG是否落后于磁盘源文件，避免“正文已改但阅读器未更新”。依赖文件固定版本；阅读器运行不请求CDN或外部脚本。

## 图与阅读器

- 41张SVG均通过XML解析、节点相交、CJK字体与marker规则检查。
- 浏览器实际字体下检查41图：文字未越出viewBox或所属节点，文字之间无重叠，采样连接线未穿过节点内部；分批截图逐张查看，补查了后加的KRaft、ZooKeeper和修改后的prefill图。
- 桌面1440px与手机390px验证：正文无页面横向溢出；图可打开、缩放、适应窗口、关闭，放大溢出仅发生在图形滚动区；下载入口指向嵌入的SVG与正确文件名。
- 搜索KRaft、模块筛选、章节跳转、答案隐藏/揭晓、安排复习、新章节笔记与状态刷新恢复通过。旧题15-q1仍为原问题并能保存复习状态。
- 基线已验证进度合并/导出、非法记录拒绝、损坏原数据保留、存储额度失败提示、未知路由回退；扩充版继续使用同一数据格式与存储键，并增加笔记长度约束。

## 实际执行的代码与SQL

| 内容 | 环境与结果 | 证明范围 |
|---|---|---|
| Algorithms.java | JDK8/21基线通过；本轮再次运行133项检查通过 | 10组教学算法及边界 |
| 原算法差分 | twoSum/topKFrequent/longestUnique各2000生成样本，基线通过 | 对相应参考算法的一致性 |
| HandwrittenLru.java | 本轮行为及1000步链表/索引不变量通过 | 单线程LRU，不含TTL和并发 |
| CodingPatterns.java | JDK8/17均通过2527检查，含500轮固定种子差分 | 8个新增算法模式；详见实验04 |
| Java并发实验01 | 基础实验JDK17/21；JDK21观察到monitor pinning | 本机教学结果，不是通用性能倍数 |
| 20/21章内代码 | JDK17编译运行；PermitLab输出false、1 | 语言/许可边界示例 |
| 28章Java工具执行 | JDK17编译运行，8项边界检查 | 租户+对象授权、参数、幂等提议边界；未调用外部退款 |
| Outbox实验02 | 五个真实子进程崩溃位置全部通过 | orders=1、outbox=1、deliveries=2、ledger=1、points=100；SQLite协议模拟 |
| Agent实验03 | self-test与JSON模式通过 | fixture指标、路由、ACL、旧资料、拒答、幂等；未调用真实模型 |
| 26/27章算例 | KV数量级、RRF与nDCG代码和预期通过 | 算术及指标语义 |
| SQL实验05 | 隔离MySQL9.3.0，9组查询与预期一致，实例已关闭 | 通用SQL小数据结果；机器记录见实验05 |

## 验证范围之外

- 未启动真实Redis、Kafka/RabbitMQ/RocketMQ、ZooKeeper或完整Spring业务系统；相关故障、复制、事务传播和迁移演练是训练设计。
- SQL实跑版本为9.3.0，未将它当作MySQL8.4的锁/优化器/复制/DDL验证；双会话隔离实验仍需在目标版本执行。
- 未在本机JDK24运行虚拟线程对照，该差异由对应版本官方文档核对。
- 未做真实LLM/embedding质量实验、生产压测、全面安全审计或实际招聘结果验证。fixture里的高分不能用于声称真实Agent达到同样质量。
- 外部材料按关键技术结论核对版本，不宣称所有外链长期可用或所有后续版本配置不变。

## 重复验证

```sh
python3 tools/make_atlas.py
.venv/bin/python tools/build.py
.venv/bin/python tools/validate.py
python3 tools/check_svg.py --gallery /tmp/handbook-svg-gallery.html
node --check web/app.js
python3 labs/consistency_demo.py
python3 labs/agent_eval_demo.py --self-test
mkdir -p /tmp/handbook-final-java
javac -encoding UTF-8 -d /tmp/handbook-final-java labs/Algorithms.java labs/HandwrittenLru.java labs/CodingPatterns.java
java -cp /tmp/handbook-final-java Algorithms
java -cp /tmp/handbook-final-java HandwrittenLru
java -cp /tmp/handbook-final-java CodingPatterns
```

浏览器打开图形画廊进行实际字体和视觉复查；静态脚本不替代视觉判断。Java并发步骤见 [实验01](labs/01-java-concurrency.md)，SQL命令及逐组结果见 [实验05](labs/05-sql-worked.md)。
