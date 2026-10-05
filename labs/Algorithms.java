import java.util.*;

/** Reference exercises. No external libraries; Java 8+. */
public final class Algorithms {
    public static int lowerBound(int[] a, int target) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] < target) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    // Return the first pair found while scanning; no pair -> empty array.
    public static int[] twoSum(int[] a, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < a.length; i++) {
            long other = (long) target - a[i];
            if (other >= Integer.MIN_VALUE && other <= Integer.MAX_VALUE) {
                Integer j = seen.get((int) other);
                if (j != null) return new int[]{j, i};
            }
            seen.put(a[i], i);
        }
        return new int[0];
    }

    // UTF-16 char units, not Unicode code points or grapheme clusters.
    public static int longestUnique(String s) {
        Map<Character, Integer> last = new HashMap<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            Integer prev = last.put(s.charAt(right), right);
            if (prev != null) left = Math.max(left, prev + 1);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    public static final class Node {
        public final int value;
        public Node next;
        public Node(int value) { this.value = value; }
    }
    public static Node reverse(Node head) {
        Node prev = null, current = head;
        while (current != null) {
            Node next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        return prev;
    }

    // Closed intervals; touching intervals merge. Does not mutate input.
    public static int[][] mergeIntervals(int[][] intervals) {
        int[][] a = new int[intervals.length][2];
        for (int i = 0; i < a.length; i++) {
            if (intervals[i].length != 2 || intervals[i][0] > intervals[i][1])
                throw new IllegalArgumentException("invalid interval");
            a[i] = intervals[i].clone();
        }
        Arrays.sort(a, (x, y) -> Integer.compare(x[0], y[0]));
        List<int[]> result = new ArrayList<>();
        for (int[] interval : a) {
            if (result.isEmpty() || result.get(result.size() - 1)[1] < interval[0])
                result.add(interval.clone());
            else {
                int[] last = result.get(result.size() - 1);
                last[1] = Math.max(last[1], interval[1]);
            }
        }
        return result.toArray(new int[result.size()][]);
    }

    // Descending frequency; equal frequency -> smaller integer first.
    public static List<Integer> topKFrequent(int[] a, int k) {
        if (k < 0) throw new IllegalArgumentException("k must be nonnegative");
        Map<Integer, Integer> freq = new HashMap<>();
        for (int x : a) freq.put(x, freq.getOrDefault(x, 0) + 1);
        Comparator<Integer> worstFirst = (x, y) -> {
            int c = Integer.compare(freq.get(x), freq.get(y));
            return c != 0 ? c : Integer.compare(y, x);
        };
        PriorityQueue<Integer> heap = new PriorityQueue<>(worstFirst);
        for (int x : freq.keySet()) {
            heap.offer(x);
            if (heap.size() > k) heap.poll();
        }
        List<Integer> result = new ArrayList<>(heap);
        result.sort(worstFirst.reversed());
        return result;
    }

    public static final class Tree {
        public final int value;
        public Tree left, right;
        public Tree(int value) { this.value = value; }
    }
    public static List<List<Integer>> levelOrder(Tree root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        Deque<Tree> q = new ArrayDeque<>();
        q.offer(root);
        while (!q.isEmpty()) {
            int size = q.size();
            List<Integer> level = new ArrayList<>();
            for (int i = 0; i < size; i++) {
                Tree node = q.remove();
                level.add(node.value);
                if (node.left != null) q.offer(node.left);
                if (node.right != null) q.offer(node.right);
            }
            result.add(level);
        }
        return result;
    }

    // Four-neighbor adjacency. Rectangular 0/1 grid, mutated to mark visits.
    public static int numIslands(char[][] grid) {
        if (grid.length == 0) return 0;
        int rows = grid.length, cols = grid[0].length;
        for (char[] row : grid) {
            if (row.length != cols) throw new IllegalArgumentException("ragged grid");
            for (char c : row) if (c != '0' && c != '1')
                throw new IllegalArgumentException("only 0/1 cells");
        }
        int count = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        Deque<int[]> q = new ArrayDeque<>();
        for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) {
            if (grid[r][c] != '1') continue;
            count++;
            grid[r][c] = '0';
            q.offer(new int[]{r, c});
            while (!q.isEmpty()) {
                int[] cell = q.remove();
                for (int[] d : dirs) {
                    int nr = cell[0] + d[0], nc = cell[1] + d[1];
                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == '1') {
                        grid[nr][nc] = '0';
                        q.offer(new int[]{nr, nc});
                    }
                }
            }
        }
        return count;
    }

    // Bounded exercise allocation, not a production policy.
    public static int coinChange(int[] coins, int amount) {
        if (amount < 0 || amount > 1_000_000)
            throw new IllegalArgumentException("exercise amount range: 0..1000000");
        for (int coin : coins) if (coin <= 0)
            throw new IllegalArgumentException("positive coins required");
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1);
        dp[0] = 0;
        for (int x = 1; x <= amount; x++) for (int coin : coins)
            if (coin <= x) dp[x] = Math.min(dp[x], dp[x - coin] + 1);
        return dp[amount] > amount ? -1 : dp[amount];
    }

    // Single-thread demonstration. get changes access order; not thread-safe.
    public static final class Lru<K, V> extends LinkedHashMap<K, V> {
        private final int capacity;
        public Lru(int capacity) {
            super(16, 0.75f, true);
            if (capacity < 0) throw new IllegalArgumentException("negative capacity");
            this.capacity = capacity;
        }
        @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return size() > capacity;
        }
    }

    private static int checks = 0;
    private static void check(boolean ok, String label) {
        checks++;
        if (!ok) throw new AssertionError(label);
    }
    private static void rejects(Runnable code, String label) {
        boolean rejected = false;
        try { code.run(); } catch (IllegalArgumentException expected) { rejected = true; }
        check(rejected, label);
    }
    public static void main(String[] args) {
        check(lowerBound(new int[]{}, 0) == 0, "empty lower bound");
        check(lowerBound(new int[]{1, 2, 2, 4}, 2) == 1, "first duplicate");
        check(lowerBound(new int[]{1, 2}, 3) == 2, "past end");
        check(lowerBound(new int[]{1}, 0) == 0, "before start");
        // Compare to a simple oracle over many deterministic generated cases.
        Random random = new Random(7);
        for (int t = 0; t < 100; t++) {
            int[] a = new int[random.nextInt(30)];
            for (int i = 0; i < a.length; i++) a[i] = random.nextInt(21) - 10;
            Arrays.sort(a);
            int target = random.nextInt(25) - 12, expected = 0;
            while (expected < a.length && a[expected] < target) expected++;
            check(lowerBound(a, target) == expected, "lower bound oracle " + t);
        }
        check(Arrays.equals(twoSum(new int[]{3, 3}, 6), new int[]{0, 1}), "duplicate pair");
        check(twoSum(new int[]{1}, 2).length == 0, "cannot reuse index");
        check(twoSum(new int[]{Integer.MAX_VALUE, 1}, Integer.MIN_VALUE).length == 0, "no overflow pair");
        check(longestUnique("abba") == 2, "window cannot move left");
        check(longestUnique("") == 0, "empty string");
        check(longestUnique("abcabcbb") == 3, "repeated pattern");
        Node a = new Node(1), b = new Node(2), c = new Node(3);
        a.next = b; b.next = c;
        check(reverse(a) == c && c.next == b && b.next == a && a.next == null, "reverse links");
        check(reverse(null) == null, "empty list");
        int[][] intervals = {{5, 7}, {1, 3}, {3, 4}, {2, 2}};
        check(Arrays.deepEquals(mergeIntervals(intervals), new int[][]{{1, 4}, {5, 7}}), "merge contained/touching");
        check(intervals[0][0] == 5, "input unchanged");
        check(mergeIntervals(new int[][]{}).length == 0, "empty intervals");
        rejects(() -> mergeIntervals(new int[][]{{3, 1}}), "bad interval");
        check(topKFrequent(new int[]{1, 1, 2, 2, 3}, 2).equals(Arrays.asList(1, 2)), "tie ordering");
        check(topKFrequent(new int[]{1}, 0).isEmpty(), "zero k");
        check(topKFrequent(new int[]{1}, 3).equals(Arrays.asList(1)), "k exceeds distinct");
        Tree root = new Tree(1); root.left = new Tree(2); root.right = new Tree(3);
        check(levelOrder(root).equals(Arrays.asList(Arrays.asList(1), Arrays.asList(2, 3))), "tree levels");
        check(levelOrder(null).isEmpty(), "empty tree");
        char[][] grid = {{'1', '0'}, {'0', '1'}};
        check(numIslands(grid) == 2, "diagonals separate");
        check(numIslands(grid) == 0, "documented mutation");
        check(numIslands(new char[][]{}) == 0, "empty grid");
        rejects(() -> numIslands(new char[][]{{'1'}, {}}), "ragged grid");
        check(coinChange(new int[]{1, 2, 5}, 11) == 3, "minimum coins");
        check(coinChange(new int[]{2}, 3) == -1, "unreachable");
        check(coinChange(new int[]{}, 0) == 0, "zero amount");
        rejects(() -> coinChange(new int[]{0}, 3), "zero coin");
        Lru<String, Integer> cache = new Lru<>(2);
        cache.put("A", 1); cache.put("B", 2); cache.get("A"); cache.put("C", 3);
        check(!cache.containsKey("B") && cache.containsKey("A"), "access refresh");
        cache.put("A", 4); cache.put("D", 5);
        check(cache.get("A") == 4 && !cache.containsKey("C"), "update refresh");
        Lru<String, Integer> zero = new Lru<>(0); zero.put("A", 1);
        check(zero.isEmpty(), "zero capacity");
        rejects(() -> new Lru<String, Integer>(-1), "negative capacity");
        System.out.println("PASS: " + checks + " checks across 10 algorithm groups");
    }
}
