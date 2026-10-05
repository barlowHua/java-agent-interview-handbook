"""Rebuild the Java / Spring mechanism figures (modules 01–05)."""
from pathlib import Path
from svgkit import Diagram

ASSETS = Path(__file__).resolve().parents[1] / 'modules' / 'assets'


def save(diagram, name):
    diagram.save(ASSETS / name)


d = Diagram('值传递：复制的是引用值，对象可以继续共享', height=309,
            desc='左侧修改共享对象内容，调用方可以观察到；右侧只让形参指向新对象，调用方引用仍指向原对象。')
d.group('mutation', 25, 65, 352, 194, '① 修改对象：p.status = PAID')
d.group('rebind', 403, 65, 352, 194, '② 重绑形参：p = new Order()')
for key, x, label in [('caller-a',45,'调用方 order'), ('param-a',214,'形参 p'),
                      ('caller-b',423,'调用方 order'), ('param-b',592,'形参 p')]:
    d.node(key,x,100,143,54,[label, '引用 A' if key != 'param-b' else '引用 B'])
d.node('shared',45,180,312,54,['对象 A：status = PAID','两个独立变量指向同一对象'],'green')
d.node('original',423,180,143,54,['对象 A','仍由 order 引用'],'green')
d.node('new',592,180,143,54,['新对象 B','由 p 引用'],'orange')
d.path('M 116.5,159 C 116.5,170 135,158 135,169','blue')
d.path('M 285.5,159 C 285.5,170 267,158 267,169','blue')
d.edge('caller-b','original','bottom',color='blue')
d.edge('param-b','new','bottom',color='orange')
d.footer('箭头表示对象引用；方法调用先复制引用值，图中展示两种操作完成后的状态。',284)
save(d,'01-value-passing.svg')

d = Diagram('HashMap：先定位桶，再判相等；扩容只看新增容量位', height=312,
            desc='上方是查找主线，下方是容量翻倍时的桶拆分。适用于常见 OpenJDK 17/21 实现。',
            subtitle='实现基线：OpenJDK 17/21；容量 n 为二次幂，h 为扰动后的哈希')
for key,x,lines,color in [
    ('key',25,['① 输入 key','计算扰动哈希 h'],'blue'),
    ('index',277,['② 桶索引','index = (n - 1) & h'],'orange'),
    ('lookup',529,['③ 桶内查找','比较 hash 与身份 / equals'],'green')]:
    d.node(key,x,80,226,54,lines,color)
d.edge('key','index'); d.edge('index','lookup')
d.text(390,161,'命中：get 取值 / put 替换；未命中：get 返回 null / put 新增。',10,'#64748b')
for key,x,lines,color in [
    ('old',25,['扩容：oldCap → 2 × oldCap','旧桶 i 中的各个条目'],'blue'),
    ('bit',277,['检查新增的容量位','h & oldCap'],'orange'),
    ('new',529,['该位为 0：仍在桶 i','该位为 1：到 i + oldCap'],'green')]:
    d.node(key,x,187,226,54,lines,color)
d.edge('old','bit'); d.edge('bit','new')
d.footer(['例：oldCap = 16，h = 3 与 h = 19 原来都在桶 3；翻倍后分别在桶 3 和桶 19。',
          '树化和退化取决于容量及具体分支；此图不表示 HashMap 可以安全并发写。'],271)
save(d,'02-hashmap-path.svg')

d = Diagram('happens-before：用一条同步边发布普通数据', height=309,
            desc='线程 A 先写普通字段 data=42，再写 volatile ready=true；线程 B 读到该 true 后读取 data，程序顺序与 volatile 同步边传递保证读取结果。',
            subtitle='初始 data = 0、ready = false；只有 A 写入一次；ready 声明为 volatile')
d.group('writer',25,75,352,184,'写线程 A：发布数据')
d.group('reader',403,75,352,184,'读线程 B：消费已发布数据')
d.node('data-write',45,110,312,54,['① 普通字段写入','data = 42'],'blue')
d.node('flag-write',45,190,312,54,['② volatile 写','ready = true'],'purple')
d.node('flag-read',423,110,312,54,['③ volatile 读','确认读到 ready == true'],'purple')
d.node('data-read',423,190,312,54,['④ 后续读取 data','在本例条件下必须得到 42'],'green')
d.edge('data-write','flag-write','bottom',color='blue')
d.edge('flag-read','data-read','bottom',color='blue')
d.path('M 362,217 C 388,217 386,137 412,137','purple')
d.footer('蓝色：同线程程序顺序；紫色：同一 volatile 的同步边；两类边可传递。',284)
save(d,'03-happens-before.svg')

d = Diagram('ThreadPoolExecutor：一次 execute 的接纳路径', height=517,
            desc='主线依次尝试核心线程、入队、最大线程，最终拒绝；入队成功还需二次检查运行状态和 worker 数。',
            subtitle='左列由上向下；蓝色向右是本步成功路径，橙色向下是不适用或尝试未成功')
rows = [
    ('core',80,['① workerCount < corePoolSize？','满足时尝试 addWorker(task, true)','创建成功则走右侧；否则继续'],
     'core-ok',['新 worker 接收此任务','无需先进入队列','即便已有空闲线程也可能创建']),
    ('queue',180,['② 池运行中且 offer(task) 成功？','满足时走右侧复查','不能入队则继续'],
     'queued',['入队成功仍要二次检查','停机且移除成功 → 拒绝','否则 worker 为 0 时尝试补 worker']),
    ('max',280,['③ 尝试 addWorker(task, false)','受 maximumPoolSize 与状态约束','成功走右侧；不能创建则继续'],
     'max-ok',['新 worker 直接接收此任务','扩容发生在不能入队之后','并非先创建到 max 再排队']),
    ('reject',380,['④ 无法接纳任务','执行 RejectedExecutionHandler','返回语义取决于拒绝策略'],
     'result',['抛错、调用者执行或其他策略','静默丢弃可能遗留未完成 Future','拒绝和排队时间必须可观测'])]
for key,y,lines,out,output in rows:
    d.node(key,25,y,352,72,lines,'pink' if key=='reject' else 'orange')
    d.node(out,403,y,352,72,output,'pink' if key=='reject' else 'green')
    d.edge(key,out,color='blue')
for a,b in [('core','queue'),('queue','max'),('max','reject')]:d.edge(a,b,'bottom',color='orange')
d.footer(['无界队列通常让任务持续排队，max 难以扩容；SynchronousQueue 没有常规存储容量。',
          '图概括 OpenJDK 21 execute 主线；线程工厂故障、状态竞态与关闭过程需结合源码。'],476)
save(d,'03-threadpool-admission.svg')

d = Diagram('JVM 内存：线程执行状态、Java 堆与本地开销', height=350,
            desc='线程私有的执行状态可持有指向共享堆的引用；HotSpot 进程还包含元空间、代码缓存、直接内存等，不受 Xmx 统一限制。',
            subtitle='规范运行时区域与 HotSpot 进程内存的教学映射；并非操作系统虚拟地址排列图')
for key,x,label in [('thread',25,'线程私有：每线程一份'),('heap',277,'共享：Java 堆'),('native',529,'HotSpot 本地内存：部分')]:
    d.group(key,x,75,226,222,label)
d.node('frames',45,110,186,72,['PC / JVM 栈','帧保存局部变量与操作数','局部变量可持有对象引用'],'blue')
d.node('native-stack',45,210,186,54,['本地方法栈','实现可与 JVM 栈结合'],'blue')
d.node('objects',297,110,186,72,['对象 / 数组','业务对象与关联引用','GC 的主要工作集'],'green')
d.node('class-mirror',297,210,186,54,['Class 镜像等堆对象','不能全部算进元空间'],'green')
d.node('native-areas',549,110,186,72,['元空间：类元数据','代码缓存：JIT 机器码','直接内存 / 本地库分配'],'orange')
d.node('budget',549,210,186,54,['线程栈也占进程内存','RSS 不等于已用堆'],'orange')
d.edge('frames','objects',color='blue')
d.footer('Xmx 主要约束 Java 堆；容器预算还要为线程、本地内存及运行时开销留余量。',325)
save(d,'04-jvm-memory.svg')

d = Diagram('GC 可达性：保留对象的是引用路径，不是业务意图', height=405,
            desc='GC Roots 经强引用保留缓存与对象 A；缓存强引用 WeakReference，但到对象 B 只有弱引用；独立的 U V 循环没有根路径。',
            subtitle='实线表示强引用；紫色虚线表示 WeakReference 的 referent 关系')
for key,x,lines,color in [
    ('root',25,['GC Roots（示意）','活动栈引用、VM / JNI 根等'],'blue'),
    ('cache',277,['长期存活的缓存对象','由根强引用路径到达'],'blue'),
    ('a',529,['对象 A：业务早已结束','缓存未删除 → 仍被保留'],'pink')]:d.node(key,x,80,226,72,lines,color)
d.edge('root','cache',color='blue');d.edge('cache','a',color='blue')
d.node('weak-condition',25,180,226,72,['判断 B 弱可达的前提','没有强引用或软引用路径','不能只看这一条虚线'],'gray')
d.node('weak',277,180,226,72,['WeakReference 包装对象','本身仍由缓存强引用','get() 可能返回 null'],'purple')
d.node('b',529,180,226,72,['对象 B：仅弱可达','GC 发现弱可达后清除引用','回收时点不由业务控制'],'green')
d.edge('cache','weak','bottom',color='blue');d.edge('weak','b',color='purple',dashed=True)
d.node('u',25,280,226,72,['孤立对象 U','强引用 V'],'orange')
d.node('v',277,280,226,72,['孤立对象 V','强引用 U'],'orange')
d.node('cycle-note',529,280,226,72,['没有任何根路径到 U / V','整体不可达','互相引用不阻止回收'],'green')
d.path('M 256,307 L 266,307');d.path('M 272,325 L 262,325')
d.footer('可回收不等于立即回收；需分析所有根路径，并区分强、软、弱、虚引用语义。',380)
save(d,'04-gc-reachability.svg')

d = Diagram('G1 周期：并发标记与暂停疏散承担不同任务', height=321,
            desc='示意一次 G1 周期的年轻代收集、并发启动、并发标记、Remark、Cleanup 以及 Mixed 回收；STW 阶段明确标记。',
            subtitle='按 ①→⑥ 阅读，第二行从右向左；STW 表示应用线程暂停')
for key,x,y,lines,color in [
    ('young',25,80,['① Young-only','常规年轻代收集（STW）','达到触发条件后启动标记'],'blue'),
    ('start',277,80,['② Concurrent Start（STW）','伴随年轻代收集','建立并发标记的起点'],'orange'),
    ('mark',529,80,['③ Concurrent Mark','与应用并发追踪存活性','期间仍可发生 Young GC'],'purple'),
    ('remark',529,180,['④ Remark（STW）','完成标记、处理引用等','随后并发整理后续所需信息'],'orange'),
    ('cleanup',277,180,['⑤ Cleanup（STW）','完成候选集等准备','决定是否进入混合回收'],'orange'),
    ('mixed',25,180,['⑥ Prepare Mixed 之后','多次 Mixed（STW）','年轻代＋选中的老年代'],'green')]:d.node(key,x,y,226,72,lines,color)
d.edge('young','start');d.edge('start','mark');d.edge('mark','remark','bottom')
d.edge('remark','cleanup','left');d.edge('cleanup','mixed','left')
d.footer(['混合回收结束后回到 Young-only；不是每次标记都必然进入 Mixed。',
          '标记回答“谁还活着”；疏散把存活对象复制到其他 Region；暂停目标不是硬保证。'],280)
save(d,'04-g1-cycle.svg')

d = Diagram('Spring 事务代理：边界取决于调用是否穿过拦截器', height=307,
            desc='外部调用穿过代理进入 outer，内部 this.inner 不再次触发事务拦截；同线程 DAO 可参与已有事务，最终由外层拦截器完成事务。',
            subtitle='命令式 JDBC＋默认代理模式；本例 outer 开启事务，再调用 this.inner')
for key,x,y,lines,color in [
    ('caller',25,80,['① 外部调用','调用者持有代理引用','执行 outer()'],'blue'),
    ('proxy',277,80,['② 事务拦截器','读取事务配置与传播规则','创建 / 参与事务'],'purple'),
    ('outer',529,80,['③ 目标对象 outer()','开始执行业务逻辑','继续调用 this.inner()'],'orange'),
    ('inner',529,180,['④ this.inner()','不重新经过代理','内层注解不重新生效'],'pink'),
    ('database',277,180,['⑤ DAO / 数据库','使用同线程、同事务资源','仍可参与外层物理事务'],'green'),
    ('finish',25,180,['⑥ 控制返回拦截器','依据结果与回滚标记处理','提交 / 回滚，清理绑定'],'purple')]:d.node(key,x,y,226,72,lines,color)
d.edge('caller','proxy');d.edge('proxy','outer');d.edge('outer','inner','bottom')
d.edge('inner','database','left');d.edge('database','finish','left')
d.footer('inner 标注 REQUIRES_NEW 也不会在自调用时新开事务；“注解未拦截”不等于“必定无事务”。',282)
save(d,'05-transaction-proxy.svg')

d = Diagram('Spring Bean 生命周期：定义、实例、代理与销毁', height=405,
            desc='展示典型应用单例从 BeanDefinition 处理到实例化、依赖填充、初始化、后置代理、使用与销毁的主要路径。',
            subtitle='按 ①→⑧ 蛇形阅读；这是典型应用单例主线，真实容器有提前引用等分支')
for key,x,y,lines,color in [
    ('definition',25,80,['① 注册 / 修改 BeanDefinition','BeanFactoryPostProcessor','处理定义与配置元数据'],'blue'),
    ('instance',277,80,['② 实例化','选择构造器 / 工厂方法','得到对象实例'],'orange'),
    ('populate',529,80,['③ 填充依赖','属性注入等扩展处理','@Autowired 也依赖后处理器'],'orange'),
    ('before',529,180,['④ 初始化入口','Aware / 初始化前 BPP','其中可触发 @PostConstruct'],'purple'),
    ('init',277,180,['⑤ 初始化方法','afterPropertiesSet()','然后执行自定义 init-method'],'orange'),
    ('after',25,180,['⑥ 初始化后 BPP','可将对象包装成 AOP 代理','对外暴露最终对象'],'purple'),
    ('ready',25,280,['⑦ 被其他对象使用','单例不自动获得线程安全','调用仍受代理边界约束'],'green'),
    ('destroy',277,280,['⑧ 容器关闭：销毁回调','@PreDestroy → destroy()','→ 自定义 destroy-method'],'orange'),
    ('scope',529,280,['作用域边界：prototype','容器负责创建与初始化','不自动执行完整销毁回调'],'pink')]:d.node(key,x,y,226,72,lines,color)
d.edge('definition','instance');d.edge('instance','populate');d.edge('populate','before','bottom')
d.edge('before','init','left');d.edge('init','after','left');d.edge('after','ready','bottom');d.edge('ready','destroy')
d.footer('BPP = BeanPostProcessor：处理实例；FactoryPostProcessor：处理定义，不能混为一谈。',380)
save(d,'05-bean-lifecycle.svg')

print('Generated 9 Java / Spring SVG diagrams.')
