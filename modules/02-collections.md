# 02 集合、哈希与并发容器

> 优先级：P0。基线：Java 17/21。L1～L4 是学习深度，不对应职级。前置：对象相等、泛型、基本时间复杂度。

## 学习目标

能按访问模式选容器，解释 HashMap 与 ConcurrentHashMap 的关键路径，并识别“单个方法安全”之外的业务竞态。学习时用同一个例子串联：按订单号保存订单、按商户统计次数、按时间维护最近访问。

## L1 必会：先描述访问模式

ArrayList 是动态数组，随机访问通常 O(1)，尾部追加均摊 O(1)，中间插入删除需要移动元素。LinkedList 通过索引定位仍是 O(n)，节点有额外空间开销；不能仅凭“删除快”就用它做普通业务列表。已持有迭代器位置时的局部插入删除才符合它的优势。栈或双端队列通常先考虑 ArrayDeque。

HashMap 适合无序键值检索，平均复杂度依赖良好哈希分布；TreeMap 维护排序，基本操作通常 O(log n)，适合范围查询与前驱后继。LinkedHashMap 可维护插入序或访问序，后者可表达简单 LRU，但生产缓存还涉及过期、容量、并发加载和统计。Set 的去重语义来自 equals 或比较器，应与领域定义一致。

集合“只读”不等于快照，“线程安全”不等于复合业务原子。需要先回答：谁修改、谁读取、是否允许读到变化、是否要求多个键一起一致，再挑 API。[HashMap 的容量与并发约束](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)

## L2 原理：沿着一次 put/get 解释

在常见 OpenJDK 17/21 HashMap 实现中，哈希扰动后通过容量掩码定位桶；桶内比较哈希与 equals，存在则覆盖，不存在则添加；超过阈值触发扩容。容量为二次幂使索引计算与扩容拆分更方便，但这属于实现细节，不是 Map 接口契约。预估容量能减少扩容，却会增加闲置空间与遍历成本。

严重碰撞时，桶可能从链表转为红黑树。常见实现有树化阈值 8、最小树化表容量 64；小表优先扩容。不要把“有 8 个节点就一定树化”当普遍规则，也不要背成每次删除到 6 就立即退化：拆分与删除的具体路径不同。树化缓解某些最坏情况，不代替良好 hashCode；自定义不可比较键的极端碰撞仍要结合源码判断。

Java 8 起常见 ConcurrentHashMap 实现已不是以 Segment 数组承担主体并发控制。空桶插入使用 CAS 等机制，有碰撞的更新可在桶层协调，扩容有迁移标记与协作迁移。get 通常不加互斥锁，依靠内存语义与结构规则观察已完成的更新。不能由此推出整表快照，也不能说它所有操作无锁。[ConcurrentHashMap API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

## L3 工程：原子性必须覆盖业务不变量

错误示例：`if (!map.containsKey(id)) { map.put(id, order); createRemoteOrder(); }`。两个线程可能同时通过检查，即使换成 ConcurrentHashMap 也一样。`putIfAbsent` 能解决单个键的占位，但不能把外部副作用变成原子操作，远端失败还可能留下占位。涉及跨进程重复请求时，需要数据库唯一约束、状态机或幂等协议。

计数可用 `merge(key, 1L, Long::sum)`，或 `computeIfAbsent` 配合 LongAdder；后者适合高竞争统计，但并发 sum 不是线性一致快照，不能直接用来判断最后一张票。映射函数应短小，不能在持有协调机制时执行慢 RPC 或递归更新同一映射。若要合并重复加载，可把代表加载结果的 Future 放进表，再处理失败清理、超时与容量。

缓存故障先区分：键数量爆炸、值过大、过期缺失、热点竞争、加载放大。ConcurrentHashMap 本身没有容量淘汰或过期策略；对用户自由输入做无上限缓存容易形成内存压力。导出报表若要求一致快照，应从带一致性语义的数据源读取，不能遍历一个正在变化的 Map 后声称总账精确。

## L4 拓展：迭代一致性与版本

P1：ArrayList/HashMap 的 fail-fast 是尽力检测错误的机制，不能作为并发正确性的保证。ConcurrentHashMap 迭代器弱一致，可继续遍历但不代表某一时刻的整表状态。CopyOnWriteArrayList 迭代基于快照，写入复制数组，适合少写多读的小集合，不适合高频订单更新。P2：JDK 21 Sequenced Collections 统一有序集合的首尾与反向视图接口，迁移时仍要检查视图是否可修改及底层集合约束。[SequencedCollection](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/SequencedCollection.html)

## 机制图解：查找路径与扩容拆分

![HashMap 查找路径与容量翻倍时的桶拆分](assets/02-hashmap-path.svg)

**读图顺序：** 上半图沿着 key、桶索引、桶内匹配看一次查找；下半图看容量从 `n` 变成 `2n` 后同一个桶如何拆分。典型 OpenJDK 实现先计算 `h = key.hashCode() ^ (key.hashCode() >>> 16)`，null 键的哈希按 0 处理；再用 `(n - 1) & h` 定位。桶内仍需判断键相等，因此碰撞不等于同一个键。

**记忆点：** 查找是“哈希定位＋相等确认”；容量翻倍是“新增一位决定去向”。例如旧容量 16，扰动哈希 3 和 19 的旧索引均为 3；新容量 32 时，一个留在 3，一个去 19。此路径不需要重新调用每个键的 `hashCode()`。因此扩容既不是把旧桶整体搬到同一位置，也不是每次从头计算所有键的用户哈希。[OpenJDK 21 HashMap 实现](https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/util/HashMap.java)

**图中未覆盖的边界：** 图省略惰性初始化、树桶分支、容量上限与迭代器维护；具体阈值属于实现。HashMap 允许 null 值，`get(k) == null` 不能单独区分“没有映射”和“映射的值是 null”；ConcurrentHashMap 禁止 null 键和值。任何一张内部结构图都不能证明跨方法、跨键、跨远端调用的业务原子性。

**闭卷重画：** 旧容量 16，三个条目的扰动哈希分别为 5、21、37。画出扩到 32 后的去向，再解释若其中一个键在入表后改变了参与 `hashCode()` 的字段，为什么扩容也不能作为修复方案。参考自检：新索引分别是 5、21、5；已存条目的哈希与键的新业务状态可能不再一致。

### 并发容器还需要哪些额外约束

`ConcurrentHashMap<String, List<Order>>` 的安全发布不意味着 List 的后续修改自动同步。一次 `put` 能为观察到该值的对应读取提供可见性，但不能保证后来不受保护的 `list.add` 与遍历没有竞态。可选择不可变值整体替换、用 `compute` 协调单键更新，或让值自己具有明确的并发协议；不能把“外层是并发 Map”当成所有对象图都线程安全。[ConcurrentHashMap 并发契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

面试中还应主动澄清操作的范围：单键原子更新可用容器方法；两个账户一起转账需要更大的原子边界；多实例的重复扣款需要持久化幂等与数据库约束。由此才能把集合题回答成工程题。

## 六道核心题与追问

### 1. HashMap 查询为什么通常很快？

**60～90 秒参考答案：** 它通过哈希把键分散到桶，先定位桶，再在桶内判断 equals，分布较好且负载受控时平均查询接近常数。冲突增加会拉长查找路径，扩容通过更多桶分摊数据，现代实现还可在满足条件时树化。代价是额外内存和扩容搬迁，因此我会根据数量预估容量，检查键的稳定性与哈希质量。回答时区分接口契约与某版 OpenJDK 的具体阈值，不把平均 O(1) 当成无条件保证。

**追问：** 为什么修改键后 get 可能失败？**要点：** 对象仍在旧哈希对应的位置，但新查询按新哈希定位；即使偶然找到也已破坏使用约束。

### 2. 为什么不默认用 LinkedList？

**60～90 秒参考答案：** 容器选择取决于完整操作成本。LinkedList 删除一个已知节点很便宜，但通过索引查找节点要遍历，节点对象还带来内存、指针访问与 GC 成本。常见业务列表主要遍历和尾部追加，ArrayList 更简单且局部性通常更好。需要队列时先考虑 ArrayDeque；只有已经持有迭代位置、且确实频繁局部插入删除时，才评估链表是否合适。最终要用真实数据规模和访问模式验证。

**追问：** ArrayList 扩容为何仍说尾插均摊 O(1)？**要点：** 单次扩容可能 O(n)，但按一定比例增长使一系列追加的总搬迁量保持线性；均摊不等于尾延迟稳定。

### 3. ConcurrentHashMap 为什么能并发读写？

**60～90 秒参考答案：** 它把协调范围尽可能局部化，读路径通常不通过互斥锁，更新根据桶状态使用 CAS、桶级同步等手段，并在扩容时协调迁移。对某个键，读到新值时有对应更新的可见性保证。但整体 size、遍历和批量操作不提供一个全表原子快照。工程上我使用它提供的原子方法表达单键操作，不会把 get 加 put 当作天然原子，也不会把 Java 7 的 Segment 结构当成现代版本通用解释。

**追问：** 为什么不能保存 null？**要点：** API 明确禁止；并发环境下 null 能明确表示没有映射，避免与“映射存在但值为空”混淆。

### 4. computeIfAbsent 可以放心做远程查询吗？

**60～90 秒参考答案：** 它能把某个键的缺失判断与计算安装协调起来，但映射函数执行期间相关更新可能受阻，因此不适合直接放不可控的慢 RPC。函数异常或返回 null 时也不能认为完成了永久缓存。更稳妥的设计是先明确是否需要去重加载，把 Future 等加载状态原子放入，再在协调范围外执行调用，并处理超时、失败移除和重试。即便进程内只加载一次，也不能代表多个实例间只调用一次。

**追问：** 为什么不要在映射函数里递归更新同一 Map？**要点：** 可能违反方法契约、导致递归更新异常或协调问题，函数应短小且不修改该映射结构。

### 5. 安全集合为什么还会超卖？

**60～90 秒参考答案：** 线程安全通常保证单个方法的语义。库存先读取再减一是两个操作，多个线程可能同时观察到正库存并一起成功。需要把检查和扣减放到同一原子边界，例如单进程用锁或 CAS 状态更新，多实例用数据库条件更新并检查受影响行数。还要把请求幂等、扣减后的订单落库和失败补偿纳入设计。把 HashMap 换成 ConcurrentHashMap 只能修复容器内部竞争，不能自动维护跨步骤业务约束。

**追问：** LongAdder 能做库存吗？**要点：** 更适合统计；sum 不提供与并发更新同一时刻的原子快照，也没有检查剩余量并扣减的业务操作。

### 6. 三种常见迭代语义有什么差别？

**60～90 秒参考答案：** 普通集合的 fail-fast 尝试发现结构被意外修改，抛异常是帮助暴露错误，不是同步协议。ConcurrentHashMap 弱一致迭代允许与更新共存，结果可能混合不同时间的状态。CopyOnWriteArrayList 迭代持有创建时的数组快照，读过程稳定，但每次写都可能复制数组，旧快照也会暂时保留内存。选择依据是读写比例、数据量与一致性要求；涉及财务汇总时必须明确快照来源，不能只看是否抛异常。

**追问：** unmodifiableList 是否就是快照？**要点：** 只是限制通过该视图修改；底层变化仍可见，结构隔离需要复制，元素隔离还需看元素可变性。

## 常见误区

- 把树化阈值当接口承诺，背诵“达到 8 必树化，降到 6 必退化”。
- 把 ConcurrentHashMap 当分布式锁、限流器或自动过期缓存。
- 用并发中的 size 决定是否还能接受最后一个名额。

## 练习与参考验证

实现按商户统计订单数的三个版本：普通 HashMap 的 get/put、ConcurrentHashMap 的 get/put、ConcurrentHashMap 的 merge。使用起跑闩锁并发执行，结束后 join，再比较期望总数。前两者可能错且不保证每次复现；merge 在所有任务成功完成后应精确。进一步把值换成 ArrayList，解释为什么安全 Map 仍不能保护列表的并发 add。参考修复是不可变值配合 compute、独立同步或合适并发队列，不是只给变量加 volatile。可复现实验见 [并发实验](../labs/01-java-concurrency.md)。

## 过关标准

能画出一次 HashMap 查找与扩容的主要路径；能为四种访问模式选容器并说代价；能找出并修复复合操作竞态；能解释快照、弱一致与业务强一致的区别。

## 官方来源

1. [HashMap API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
2. [ConcurrentHashMap API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)
3. [CopyOnWriteArrayList API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html)
4. [SequencedCollection API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/SequencedCollection.html)
5. [OpenJDK 21 HashMap 源码](https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/util/HashMap.java)
