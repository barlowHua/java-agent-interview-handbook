# 实验 04｜现场编码与边界验证

前置：JDK 8 或更新版本，终端进入项目根目录。目标：用真实运行结果核对算法，而不是只阅读答案。

```sh
mkdir -p /tmp/interview-algorithms
javac -encoding UTF-8 -d /tmp/interview-algorithms labs/Algorithms.java
java -cp /tmp/interview-algorithms Algorithms
```

程序使用自己的检查函数，不需要 `-ea`，失败会抛出 AssertionError。它覆盖 10 组示例，包括二分对照朴素 oracle、重复值、整数溢出、窗口回退、区间包含、Top K 同频顺序、对角网格、非法硬币与 LRU 淘汰。通过只说明这些样例满足断言，不证明所有输入正确。

## 先做再看

1. 不打开参考实现，45 分钟内完成 lowerBound、twoSum 或 LRU 中一道。
2. 手写输入契约：空数组、重复值、返回不存在的方式、是否允许修改输入。
3. 写至少五个边界例，解释为什么它能揭示一种错误。
4. 再读 [Algorithms.java](Algorithms.java)，比较不变量和边界，不只比较代码长短。

## 实现边界

- longestUnique 按 Java UTF-16 char 单位处理；完整 Unicode code point 或用户感知字符需要改变处理方式。
- numIslands 使用四向邻接且会修改传入网格；如需保留输入，调用方复制或改为 visited。
- mergeIntervals 使用闭区间，端点相接会合并；半开时间段需要重新定义重叠条件。
- Lru 示例通过 LinkedHashMap 说明访问顺序，是单线程、无 TTL、按条目数限容量的教学版本。现场手写题应自行实现双向链表，不用现成类替代考点。
- coinChange 为演示限制 amount 在 0～1,000,000，避免随意分配巨大数组；这不是通用业务上限。

## 加深练习与参考验证

将 twoSum 的减法改为 int，尝试 `[Integer.MAX_VALUE, 1]`、target=`Integer.MIN_VALUE`，应发现溢出可能制造并不存在的数学答案。将最长子串 left 更新去掉 Math.max，输入 `abba` 应暴露左边界回退。修改代码后先预测，再运行验证，最后还原自己的练习副本。

过关：能说清正确性和复杂度，并在失败样例出现后定位不变量被破坏的位置。

## 补充：真正手写 HashMap + 双向链表

上一版用 LinkedHashMap 展示 LRU 行为；现在同时提供 [HandwrittenLru.java](HandwrittenLru.java)。它显式维护两个哨兵节点、key 到节点的映射、摘链和尾插，不调用现成访问顺序容器。

```sh
javac -encoding UTF-8 -d /tmp/interview-algorithms labs/HandwrittenLru.java
java -cp /tmp/interview-algorithms HandwrittenLru
```

缺失返回 null，因此缓存值可以是 -1；容量 0 不保留条目；负容量被拒绝。get 和更新都刷新顺序。断言除检查淘汰行为，还核对链表前后引用、哈希映射与节点数量。它仍是单线程教学实现，锁、TTL、按字节计费和生产可观测性没有实现。


## 扩充：八个算法模式的完整 Java 实现

[第32章](../modules/32-algorithm-coding-deep.md)解释每个算法的状态、不变量、复杂度和反例；[CodingPatterns.java](CodingPatterns.java)给出前缀和、拓扑排序、并查集、归并排序、严格LIS、0/1背包、编辑距离、每日温度的可运行实现。

```sh
mkdir -p /tmp/handbook-pattern-classes
javac -encoding UTF-8 -d /tmp/handbook-pattern-classes labs/CodingPatterns.java
java -cp /tmp/handbook-pattern-classes CodingPatterns
```

本轮实际输出：`PASS CodingPatterns: 2527 checks (fixed seed, 500 differential rounds)`。其中随机对照包含归并排序对标准排序、前缀和对二重循环、LIS对二次DP、温度栈对朴素扫描、背包对枚举子集。固定样例另覆盖有环、重复边、孤立节点、负数、溢出目标和非法权重。它不是生产性能压测；拓扑与并查集使用固定边界测试。
