import java.util.*;

/** Teaching implementations, Java 8+. Inputs are non-null unless stated. */
public final class CodingPatterns {
    // Empty prefix is a valid start; query before inserting current prefix.
    public static long countSubarraySum(int[] a, long k) {
        Map<Long, Long> counts = new HashMap<>();
        counts.put(0L, 1L);
        long prefix = 0, answer = 0;
        for (int value : a) {
            prefix += value;
            // A long k near its limit could make subtraction overflow.
            long needed = prefix - k;
            boolean overflow = ((prefix ^ k) & (prefix ^ needed)) < 0;
            if (!overflow) answer += counts.getOrDefault(needed, 0L);
            counts.put(prefix, counts.getOrDefault(prefix, 0L) + 1);
        }
        return answer;
    }

    // Edge [u,v] means u must precede v. Cycles are rejected.
    public static int[] topologicalOrder(int n, int[][] edges) {
        if (n < 0) throw new IllegalArgumentException("negative node count");
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
        int[] indegree = new int[n];
        for (int[] edge : edges) {
            if (edge.length != 2 || edge[0] < 0 || edge[0] >= n || edge[1] < 0 || edge[1] >= n)
                throw new IllegalArgumentException("invalid edge");
            graph.get(edge[0]).add(edge[1]);
            indegree[edge[1]]++;
        }
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indegree[i] == 0) queue.add(i);
        int[] order = new int[n];
        int used = 0;
        while (!queue.isEmpty()) {
            int u = queue.remove();
            order[used++] = u;
            for (int v : graph.get(u)) if (--indegree[v] == 0) queue.add(v);
        }
        if (used != n) throw new IllegalArgumentException("cycle");
        return order;
    }

    public static final class UnionFind {
        private final int[] parent, size;
        private int components;
        public UnionFind(int n) {
            if (n < 0) throw new IllegalArgumentException("negative size");
            parent = new int[n]; size = new int[n]; components = n;
            for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
        }
        public int find(int x) {
            if (x < 0 || x >= parent.length) throw new IllegalArgumentException("invalid node");
            while (x != parent[x]) { parent[x] = parent[parent[x]]; x = parent[x]; }
            return x;
        }
        public boolean union(int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) return false;
            if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
            parent[rb] = ra; size[ra] += size[rb]; components--; return true;
        }
        public int components() { return components; }
    }

    public static int[] mergeSort(int[] input) {
        int[] a = input.clone();
        mergeSort(a, new int[a.length], 0, a.length);
        return a;
    }
    private static void mergeSort(int[] a, int[] buffer, int lo, int hi) {
        if (hi - lo < 2) return;
        int mid = lo + (hi - lo) / 2;
        mergeSort(a, buffer, lo, mid); mergeSort(a, buffer, mid, hi);
        int left = lo, right = mid, out = lo;
        while (left < mid || right < hi) {
            if (right >= hi || (left < mid && a[left] <= a[right])) buffer[out++] = a[left++];
            else buffer[out++] = a[right++];
        }
        System.arraycopy(buffer, lo, a, lo, hi - lo);
    }

    public static int lisLength(int[] a) {
        int[] tails = new int[a.length];
        int length = 0;
        for (int value : a) {
            int lo = 0, hi = length;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (tails[mid] < value) lo = mid + 1; else hi = mid;
            }
            tails[lo] = value;
            if (lo == length) length++;
        }
        return length;
    }

    // At most capacity; optional items, strictly positive weights.
    public static long knapsack01(int[] weight, int[] value, int capacity) {
        if (capacity < 0 || weight.length != value.length) throw new IllegalArgumentException("invalid sizes");
        long[] dp = new long[capacity + 1];
        for (int i = 0; i < weight.length; i++) {
            if (weight[i] <= 0) throw new IllegalArgumentException("weight must be positive");
            for (int c = capacity; c >= weight[i]; c--) dp[c] = Math.max(dp[c], dp[c - weight[i]] + value[i]);
        }
        return dp[capacity];
    }

    // Unit insertion/deletion/substitution cost over UTF-16 char units.
    public static int editDistance(String a, String b) {
        int[] previous = new int[b.length() + 1];
        for (int j = 0; j <= b.length(); j++) previous[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            int[] current = new int[b.length() + 1]; current[0] = i;
            for (int j = 1; j <= b.length(); j++) {
                current[j] = Math.min(Math.min(previous[j] + 1, current[j - 1] + 1),
                    previous[j - 1] + (a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1));
            }
            previous = current;
        }
        return previous[b.length()];
    }

    public static int[] dailyTemperatures(int[] temperatures) {
        int[] answer = new int[temperatures.length];
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < temperatures.length; i++) {
            while (!stack.isEmpty() && temperatures[stack.peek()] < temperatures[i]) {
                int old = stack.pop(); answer[old] = i - old;
            }
            stack.push(i);
        }
        return answer;
    }

    private static int checks;
    private static void check(boolean condition) { checks++; if (!condition) throw new AssertionError("check " + checks); }
    private static void rejects(Runnable r) {
        try { r.run(); } catch (IllegalArgumentException expected) { checks++; return; }
        throw new AssertionError("expected rejection");
    }
    private static long bruteSum(int[] a, long k) {
        long count = 0;
        for (int i = 0; i < a.length; i++) { long sum = 0; for (int j = i; j < a.length; j++) { sum += a[j]; if (sum == k) count++; } }
        return count;
    }
    private static int quadraticLis(int[] a) {
        int[] dp = new int[a.length]; int best = 0;
        for (int i = 0; i < a.length; i++) {
            dp[i] = 1;
            for (int j = 0; j < i; j++) if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
            best = Math.max(best, dp[i]);
        }
        return best;
    }
    public static void main(String[] args) {
        check(countSubarraySum(new int[]{0,0,0}, 0) == 6);
        check(countSubarraySum(new int[]{Integer.MAX_VALUE,1}, 2147483648L) == 1);
        check(countSubarraySum(new int[]{1,-1}, Long.MIN_VALUE) == 0);
        int[][] edges = {{0,2},{1,2},{2,3},{2,3}};
        int[] order = topologicalOrder(5, edges), pos = new int[5];
        Set<Integer> seen = new HashSet<>();
        for (int i = 0; i < order.length; i++) { pos[order[i]] = i; seen.add(order[i]); }
        check(seen.size() == 5);
        for (int[] e : edges) check(pos[e[0]] < pos[e[1]]);
        check(topologicalOrder(0, new int[0][]).length == 0);
        rejects(() -> topologicalOrder(2, new int[][]{{0,1},{1,0}}));
        rejects(() -> topologicalOrder(1, new int[][]{{0,0}}));
        rejects(() -> topologicalOrder(2, new int[][]{{0,2}}));
        UnionFind uf = new UnionFind(5);
        check(uf.union(0,1)); check(uf.union(1,2)); check(!uf.union(0,2));
        check(uf.find(0) == uf.find(2)); check(uf.components() == 3);
        rejects(() -> uf.find(5));
        check(knapsack01(new int[]{2}, new int[]{3}, 4) == 3);
        check(knapsack01(new int[]{1,3,4}, new int[]{15,20,30}, 4) == 35);
        check(knapsack01(new int[]{1}, new int[]{-2}, 2) == 0);
        rejects(() -> knapsack01(new int[]{0}, new int[]{1}, 1));
        check(editDistance("horse","ros") == 3); check(editDistance("", "abc") == 3);
        check(editDistance("same","same") == 0); check(editDistance("kitten","sitting") == 3);
        check(Arrays.equals(dailyTemperatures(new int[]{73,74,75,71,69,72,76,73}),new int[]{1,1,4,2,1,1,0,0}));
        Random random = new Random(20261004);
        for (int round = 0; round < 500; round++) {
            int[] a = new int[random.nextInt(20)];
            for (int i = 0; i < a.length; i++) a[i] = random.nextInt(21) - 10;
            int[] sorted = a.clone(); Arrays.sort(sorted);
            check(Arrays.equals(mergeSort(a), sorted));
            long target = random.nextInt(21) - 10;
            check(countSubarraySum(a, target) == bruteSum(a, target));
            check(lisLength(a) == quadraticLis(a));
            int[] expected = new int[a.length];
            for (int i = 0; i < a.length; i++) for (int j = i + 1; j < a.length; j++) if (a[j] > a[i]) { expected[i] = j - i; break; }
            check(Arrays.equals(dailyTemperatures(a), expected));
            int n = random.nextInt(10), cap = random.nextInt(15);
            int[] w = new int[n], v = new int[n];
            for (int i = 0; i < n; i++) { w[i] = random.nextInt(5) + 1; v[i] = random.nextInt(20) - 5; }
            long best = 0;
            for (int mask = 0; mask < (1 << n); mask++) {
                int totalW = 0; long totalV = 0;
                for (int i = 0; i < n; i++) if ((mask & (1 << i)) != 0) { totalW += w[i]; totalV += v[i]; }
                if (totalW <= cap) best = Math.max(best, totalV);
            }
            check(knapsack01(w,v,cap) == best);
        }
        System.out.println("PASS CodingPatterns: " + checks + " checks (fixed seed, 500 differential rounds)");
    }
}
