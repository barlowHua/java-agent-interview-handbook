# 实验 01：用运行结果理解 Java 并发

> 优先级 P0；虚拟线程对照 P1。基础实验使用 Java 17/21，无第三方依赖。以下文件名是你本地保存代码时使用的名称。请只在本地练习目录运行。

## 目标与执行方式

完成四个可复现实验：丢失更新、正确原子更新、有界线程池拒绝、Future 超时与底层任务生命周期。实验使用闩锁和屏障安排顺序，不依赖“多跑几次总会出错”。这种安排是为了展示允许出现的交错，不代表线上发生概率。

先检查 `java -version` 与 `javac -version`，两者必须来自一致版本。macOS 可用 `/usr/libexec/java_home -v 21` 找到 JDK；不要因为机器装了 21 就以为默认 java 已经是 21。保存为 `ConcurrencyLab.java`，执行：

```sh
javac ConcurrencyLab.java
java ConcurrencyLab
```

也可以使用对应 JDK 的绝对路径。本项目编写时本机默认 java 是 8，因此验证明确使用 JDK 17/21 的二进制。

## 可直接运行的完整代码

```java
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ConcurrencyLab {
    private static volatile int broken;
    private static final int ROUNDS = 1000;

    public static void main(String[] args) throws Exception {
        lostUpdate();
        atomicUpdate();
        boundedPool();
        timeoutIsNotCancellation();
        System.out.println("ALL CHECKS PASSED");
    }

    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    static void await(CountDownLatch latch) throws InterruptedException {
        if (!latch.await(5, TimeUnit.SECONDS)) {
            throw new AssertionError("Timed out waiting for latch");
        }
    }

    static void stop(ExecutorService pool) throws InterruptedException {
        pool.shutdownNow();
        check(pool.awaitTermination(5, TimeUnit.SECONDS), "Pool did not stop");
    }

    static void lostUpdate() throws Exception {
        broken = 0;
        Map<String, Integer> counts = new ConcurrentHashMap<>();
        counts.put("merchant", 0);
        CyclicBarrier barrier = new CyclicBarrier(2);
        ExecutorService pool = Executors.newFixedThreadPool(2);
        List<Future<?>> jobs = new ArrayList<>();
        try {
            for (int worker = 0; worker < 2; worker++) {
                jobs.add(pool.submit(() -> {
                    for (int round = 0; round < ROUNDS; round++) {
                        int scalar = broken;
                        int mapped = counts.get("merchant");
                        barrier.await(5, TimeUnit.SECONDS); // both have read
                        broken = scalar + 1;
                        counts.put("merchant", mapped + 1);
                        barrier.await(5, TimeUnit.SECONDS); // both have written
                    }
                    return null;
                }));
            }
            for (Future<?> job : jobs) job.get(10, TimeUnit.SECONDS);
            check(broken == ROUNDS, "Unexpected arranged scalar result");
            check(counts.get("merchant") == ROUNDS, "Unexpected map result");
            System.out.printf("lost: expected=%d volatile=%d mapGetPut=%d%n",
                    2 * ROUNDS, broken, counts.get("merchant"));
        } finally {
            stop(pool);
        }
    }

    static void atomicUpdate() throws Exception {
        AtomicInteger counter = new AtomicInteger();
        ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();
        ExecutorService pool = Executors.newFixedThreadPool(2);
        CountDownLatch start = new CountDownLatch(1);
        List<Future<?>> jobs = new ArrayList<>();
        try {
            for (int worker = 0; worker < 2; worker++) {
                jobs.add(pool.submit(() -> {
                    await(start);
                    for (int round = 0; round < ROUNDS; round++) {
                        counter.incrementAndGet();
                        counts.merge("merchant", 1, Integer::sum);
                    }
                    return null;
                }));
            }
            start.countDown();
            for (Future<?> job : jobs) job.get(10, TimeUnit.SECONDS);
            check(counter.get() == 2 * ROUNDS, "Atomic count mismatch");
            check(counts.get("merchant") == 2 * ROUNDS, "Merge count mismatch");
            System.out.printf("atomic: counter=%d mapMerge=%d%n",
                    counter.get(), counts.get("merchant"));
        } finally {
            start.countDown();
            stop(pool);
        }
    }

    static void boundedPool() throws Exception {
        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                1, 1, 0L, TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(2),
                new ThreadPoolExecutor.AbortPolicy());
        CountDownLatch running = new CountDownLatch(1);
        CountDownLatch release = new CountDownLatch(1);
        List<Future<?>> accepted = new ArrayList<>();
        try {
            accepted.add(pool.submit(() -> {
                running.countDown();
                await(release);
                return null;
            }));
            await(running); // worker is occupied before filling the queue
            accepted.add(pool.submit(() -> {}));
            accepted.add(pool.submit(() -> {}));
            boolean rejected = false;
            try {
                pool.submit(() -> {});
            } catch (RejectedExecutionException expected) {
                rejected = true;
            }
            check(rejected, "Fourth task should be rejected");
            check(pool.getQueue().size() == 2, "Queue should contain two tasks");
            System.out.printf("pool: queued=%d fourthRejected=%s%n",
                    pool.getQueue().size(), rejected);
            release.countDown();
            for (Future<?> job : accepted) job.get(5, TimeUnit.SECONDS);
        } finally {
            release.countDown();
            stop(pool);
        }
    }

    static void timeoutIsNotCancellation() throws Exception {
        ExecutorService pool = Executors.newSingleThreadExecutor();
        CountDownLatch started = new CountDownLatch(1);
        CountDownLatch release = new CountDownLatch(1);
        CountDownLatch finished = new CountDownLatch(1);
        try {
            CompletableFuture<String> result = CompletableFuture.supplyAsync(() -> {
                started.countDown();
                try {
                    await(release); // represents an ongoing underlying operation
                    return "underlying work finished";
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new CompletionException(e);
                } finally {
                    finished.countDown();
                }
            }, pool);
            await(started);
            boolean timedOut = false;
            try {
                result.orTimeout(50, TimeUnit.MILLISECONDS).join();
            } catch (CompletionException e) {
                if (!(e.getCause() instanceof TimeoutException)) throw e;
                timedOut = true;
            }
            check(timedOut, "Future should have timed out");
            check(finished.getCount() == 1, "Underlying task should still be waiting");
            System.out.println("timeout: futureTimedOut=true underlyingFinished=false");
            release.countDown();
            await(finished);
            check(result.isCompletedExceptionally(), "Future should remain exceptional");
            System.out.println("timeout: underlyingFinished=true futureStillExceptional=true");
        } finally {
            release.countDown();
            stop(pool);
        }
    }
}
```

## 预期输出与逐项解释

```text
lost: expected=2000 volatile=1000 mapGetPut=1000
atomic: counter=2000 mapMerge=2000
pool: queued=2 fourthRejected=true
timeout: futureTimedOut=true underlyingFinished=false
timeout: underlyingFinished=true futureStillExceptional=true
ALL CHECKS PASSED
```

1. 屏障让两个线程在每轮都先读取同一个旧值，随后各自写入旧值加一，所以两个“递增”只累计一次。volatile 保证可见性不等于复合操作原子；ConcurrentHashMap 的 get、put 各自安全也不保证两者组合安全。
2. AtomicInteger 的递增与 Map.merge 的单键更新覆盖所需原子边界。此处两个计数分别正确，不代表它们之间的联合一致性获得保证；若要求“两个字段必须一起成功”，应重新设计同步边界。
3. 第一个任务占用唯一工作线程，两个任务进入有界队列，第四个明确被拒绝。拒绝不应被吞成成功。把 max 改成 2 可以观察队列满后扩容，但需要更新预期断言。
4. Future 在 50 毫秒后异常完成，但底层任务仍阻塞在 release。释放后底层工作结束，Future 仍保留已发生的超时状态。生产中需要配套客户端超时和实际取消能力，不要把此处的闩锁误当成网络 I/O 的完整模拟。

## 虚拟线程对照：JDK 21 与 JDK 24+ 的边界

下面可选代码需要 JDK 21 或更高，保存为 `VirtualWaitDemo.java`。每个任务使用自己独立的锁，避免因为所有任务争抢同一把锁而把互斥串行化误认为 pinning。

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class VirtualWaitDemo {
    public static void main(String[] args) throws Exception {
        boolean monitor = args.length > 0 && args[0].equals("monitor");
        long start = System.nanoTime();
        List<Future<?>> jobs = new ArrayList<>();
        try (ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 40; i++) {
                Object privateLock = new Object();
                jobs.add(pool.submit(() -> {
                    if (monitor) {
                        synchronized (privateLock) {
                            Thread.sleep(50);
                        }
                    } else {
                        Thread.sleep(50);
                    }
                    return null;
                }));
            }
            for (Future<?> job : jobs) job.get(10, TimeUnit.SECONDS);
        }
        System.out.printf("mode=%s elapsedMs=%d%n", monitor ? "monitor" : "plain",
                TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start));
    }
}
```

```sh
javac VirtualWaitDemo.java
java -Djdk.virtualThreadScheduler.parallelism=2 -Djdk.virtualThreadScheduler.maxPoolSize=2 VirtualWaitDemo plain
java -Djdk.virtualThreadScheduler.parallelism=2 -Djdk.virtualThreadScheduler.maxPoolSize=2 -Djdk.tracePinnedThreads=short VirtualWaitDemo monitor
```

JDK 21 下，plain 的等待可释放 carrier，monitor 的等待可能占住仅有的两个 carrier，因而对照耗时应明显不同。具体毫秒数不作断言，JIT、启动和系统负载会影响结果；此处也不是严谨微基准。小而固定的 carrier 参数仅用于放大教学现象，不是生产调优建议。

JDK 24 起 synchronized 相关 pinning 已得到改进，用该版本重跑不应机械预期同样差异；native/foreign 调用仍要另行分析。JDK 21 的 `jdk.tracePinnedThreads` 观察方法也不能不核对版本就复制到后续版本，后续观察优先结合相应 JDK 的 JFR 事件说明。[Java 21 虚拟线程](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)、[Java 24 虚拟线程](https://docs.oracle.com/en/java/javase/24/core/virtual-threads.html)

## 验证记录

2026-10-04 已在当前 macOS arm64 环境执行：

- 基础代码分别在 Oracle JDK 17.0.9、Oracle JDK 21.0.8 编译运行，全部断言通过，输出与上述预期一致。
- 可选虚拟线程代码在 JDK 21.0.8 编译运行；本次 plain 为 70 ms，monitor 为 1199 ms，并观察到 `reason:MONITOR` 的 pinned-thread 输出。数值仅是本次运行记录，不构成性能承诺。
- 当前环境未安装并运行 JDK 24，因此其行为边界来自官方文档核对，未声称完成本地对照。

测试从本文提取 Java 代码，在临时目录编译并运行；未启动数据库或访问外部服务。线上压测与其他 JDK 版本仍需单独验证。

## 复盘与过关标准

每项写出：原子边界在哪里、哪个线程等待什么、什么事件释放它、异常由谁观察、系统关闭时如何收尾。能在不看代码的情况下解释全部输出，再完成两个修改：把 Map 值改为可变 List 并解释保护缺口；给任务记录提交、开始、完成三个时间戳，区分排队和执行耗时。

若你只记住“volatile 不保证原子”但不能画出两线程读写顺序，或者只说“线程池满了就拒绝”却不知道队列与 max 的关系，本实验尚未过关。
