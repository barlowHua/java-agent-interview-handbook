import java.util.HashMap;
import java.util.Map;

/** Single-thread, entry-count capacity. Missing get -> null; no TTL. Java 8+. */
public final class HandwrittenLru {
    private static final class Node {
        final int key;
        int value;
        Node prev, next;
        Node(int key, int value) { this.key=key; this.value=value; }
    }
    private final int capacity;
    private final Map<Integer,Node> index=new HashMap<>();
    private final Node head=new Node(0,0), tail=new Node(0,0);
    public HandwrittenLru(int capacity) {
        if(capacity<0) throw new IllegalArgumentException("capacity must be nonnegative");
        this.capacity=capacity;head.next=tail;tail.prev=head;
    }
    private void unlink(Node n) { n.prev.next=n.next;n.next.prev=n.prev; }
    private void newest(Node n) { n.prev=tail.prev;n.next=tail;tail.prev.next=n;tail.prev=n; }
    public Integer get(int key) {
        Node n=index.get(key);if(n==null)return null;
        unlink(n);newest(n);return n.value;
    }
    public void put(int key,int value) {
        Node n=index.get(key);
        if(n!=null){n.value=value;unlink(n);newest(n);return;}
        if(capacity==0)return;
        n=new Node(key,value);index.put(key,n);newest(n);
        if(index.size()>capacity){Node oldest=head.next;unlink(oldest);index.remove(oldest.key);}
    }
    private void invariant() {
        int count=0;Node prev=head;
        for(Node n=head.next;n!=tail;n=n.next){
            if(n==null||n.prev!=prev||index.get(n.key)!=n||++count>capacity)
                throw new AssertionError("broken link or index");
            prev=n;
        }
        if(tail.prev!=prev||count!=index.size())throw new AssertionError("size/tail");
    }
    private static void check(boolean ok){if(!ok)throw new AssertionError();}
    public static void main(String[] args){
        HandwrittenLru c=new HandwrittenLru(2);
        check(c.get(9)==null);c.invariant();
        c.put(1,10);c.put(2,20);c.invariant();
        check(c.get(1)==10);c.put(3,30);c.invariant();check(c.get(2)==null);
        c.put(1,-1);c.put(4,40);c.invariant();check(c.get(3)==null);check(c.get(1)==-1);
        for(int i=0;i<1000;i++){c.put(i,i*2);c.invariant();check(c.get(i)==i*2);}
        HandwrittenLru zero=new HandwrittenLru(0);zero.put(1,1);zero.invariant();check(zero.get(1)==null);
        HandwrittenLru one=new HandwrittenLru(1);one.put(1,1);one.put(1,2);one.invariant();check(one.get(1)==2);
        one.put(2,2);one.invariant();check(one.get(1)==null);
        boolean rejected=false;try{new HandwrittenLru(-1);}catch(IllegalArgumentException e){rejected=true;}check(rejected);
        System.out.println("PASS: hand-written LRU behavior and 1000-step link/index invariants");
    }
}
