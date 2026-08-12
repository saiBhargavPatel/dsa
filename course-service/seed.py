"""Seed rich DSA content into the course service database."""
from sqlalchemy.orm import Session
from models import Topic, Lesson

# Each lesson has real, substantive content a student can actually learn from.
SEED = [
    {
        "slug": "arrays",
        "title": "Arrays & Dynamic Arrays",
        "icon": "📊",
        "difficulty": "Beginner",
        "description": "The most fundamental data structure. Learn contiguous memory layout, indexing, dynamic arrays (ArrayList / vector), and classic array problems.",
        "lessons": [
            {
                "slug": "arrays-intro",
                "title": "Introduction to Arrays",
                "duration_minutes": 12,
                "summary": "What an array is, memory layout, and O(1) random access.",
                "content_md": """# Introduction to Arrays

An **array** is a collection of elements stored in **contiguous memory locations**, each identified by an integer **index** starting at 0.

## Key properties
- **Random access in O(1):** because the address of element `i` is `base + i * element_size`, the CPU can jump directly to it.
- **Fixed size** in most low-level languages (C, Java `int[]`). Dynamic arrays (Python `list`, C++ `vector`, Java `ArrayList`) grow by allocating a new, larger buffer and copying.
- **Cache-friendly:** contiguous memory means excellent CPU-cache locality, making arrays very fast in practice.

## Complexity cheat sheet
| Operation | Static array | Dynamic array |
|-----------|-------------|---------------|
| Access    | O(1)        | O(1)          |
| Search    | O(n)        | O(n)          |
| Insert end| N/A         | O(1) amortized|
| Insert mid| O(n)        | O(n)          |
| Delete    | O(n)        | O(n)          |

## Python example
```python
arr = [3, 1, 4, 1, 5, 9, 2, 6]
print(arr[0])      # 3  -> O(1) access
arr.append(5)      # amortized O(1)
arr.insert(0, 99)  # O(n) — shifts everything right
```

> **Tip:** Dynamic arrays typically double in capacity when full, which is why `append` is *amortized* O(1) — the expensive resize happens rarely enough to average out.
"""
            },
            {
                "slug": "arrays-two-pointer",
                "title": "Two-Pointer Technique",
                "duration_minutes": 15,
                "summary": "Solve sorted-array and pair problems in O(n) with two moving pointers.",
                "content_md": """# Two-Pointer Technique

When an array is **sorted**, two pointers — one at each end — can solve many problems in **O(n)** instead of O(n²).

## Classic: two-sum in a sorted array
```python
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
```

## Why it works
- If the sum is too small, we need a **larger** number → move `left` right.
- If the sum is too large, we need a **smaller** number → move `right` left.
- Each step eliminates one element, so it's **O(n)** total.

## Variants
| Pattern | Use case |
|---------|----------|
| Opposite ends | Two-sum, container-with-most-water, palindrome check |
| Fast & slow (same direction) | Remove duplicates in-place, cycle detection |
| Sliding window | Subarray sums, longest substring without repeating chars |

> **Remember:** Two pointers usually require the array to be **sorted**, or the problem to have monotonic structure. If it's not sorted, sorting first (O(n log n)) is often still worth it.
"""
            },
            {
                "slug": "arrays-sliding-window",
                "title": "Sliding Window",
                "duration_minutes": 16,
                "summary": "Maintain a window over the array to solve subarray problems efficiently.",
                "content_md": """# Sliding Window

The **sliding window** technique maintains a subset (window) of elements and slides it across the array, avoiding recomputation from scratch.

## Fixed-size window: max sum of k consecutive elements
```python
def max_sum_k(arr, k):
    window = sum(arr[:k])
    best = window
    for i in range(k, len(arr)):
        window += arr[i] - arr[i - k]   # add new, drop old
        best = max(best, window)
    return best
```
**O(n)** instead of the naive O(n·k).

## Variable-size window: longest subarray with sum ≤ k
```python
def longest_subarray_sum_le(arr, k):
    left = total = best = 0
    for right in range(len(arr)):
        total += arr[right]
        while total > k:           # shrink from left
            total -= arr[left]
            left += 1
        best = max(best, right - left + 1)
    return best
```

## When to use it
- "Longest/shortest subarray/substring with property X"
- "Number of subarrays satisfying Y"
- The property is **monotonic** — expanding the window keeps it valid or breaks it predictably.

> **Key insight:** The window only ever moves forward — both pointers travel at most n steps, so it's always O(n).
"""
            },
            {
                "slug": "arrays-prefix-sum",
                "title": "Prefix Sums",
                "duration_minutes": 10,
                "summary": "Precompute cumulative sums for O(1) range queries.",
                "content_md": """# Prefix Sums

A **prefix sum** array `P` where `P[i] = arr[0] + arr[1] + ... + arr[i-1]` lets you answer any **range sum** query in O(1).

## Build & query
```python
prefix = [0] * (len(arr) + 1)
for i in range(len(arr)):
    prefix[i + 1] = prefix[i] + arr[i]

# Sum of arr[l..r] inclusive:
def range_sum(l, r):
    return prefix[r + 1] - prefix[l]
```

## Example
```
arr   =  [2, 4, 6, 1, 3]
prefix= [0, 2, 6,12,13,16]
range_sum(1, 3) = prefix[4] - prefix[1] = 13 - 2 = 11  (4+6+1)
```

## Applications
- **Range sum queries** — the canonical use.
- **Equilibrium index** — find `i` where sum(left) == sum(right).
- **2D prefix sums** — sub-matrix sum queries (image processing, grids).
- **Difference arrays** — the dual: apply range updates in O(1).

> Build cost is O(n), then each of Q queries is O(1) — total O(n + Q) vs O(n·Q) naive.
"""
            },
        ],
    },
    {
        "slug": "linked-lists",
        "title": "Linked Lists",
        "icon": "🔗",
        "difficulty": "Beginner",
        "description": "Node-based structures with pointers. Master singly/doubly linked lists, reversal, cycle detection, and merge operations.",
        "lessons": [
            {
                "slug": "linked-lists-intro",
                "title": "Singly & Doubly Linked Lists",
                "duration_minutes": 14,
                "summary": "Node-based storage with pointers; trade-offs vs arrays.",
                "content_md": """# Singly & Doubly Linked Lists

A **linked list** stores elements in **nodes**, each holding a value and a **pointer** to the next node. Memory is *not* contiguous.

## Singly linked list node
```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
```

## Complexity vs arrays
| Operation        | Array  | Linked list |
|------------------|--------|-------------|
| Access by index  | O(1)   | O(n)        |
| Insert at head   | O(n)   | O(1)        |
| Insert at tail*  | O(1) amortized | O(1) if tail ptr kept |
| Delete given node| O(n)   | O(1) if you have the node |

## Doubly linked list
Each node also stores a `prev` pointer, enabling **bidirectional** traversal and O(1) deletion when you hold the node (used by LRU caches).

```python
class DNode:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None
```

## When to use linked lists
- Frequent **insertions/deletions** at the ends or middle (queues, stacks, LRU caches).
- You don't need random access by index.
- Implementing other structures (hash table chaining, adjacency lists, polynomial arithmetic).

> **Trade-off:** You trade O(1) random access for O(1) structural edits. Plus extra memory per node for the pointer(s).
"""
            },
            {
                "slug": "linked-lists-reversal",
                "title": "Reversing a Linked List",
                "duration_minutes": 12,
                "summary": "The iconic interview problem — iterative and recursive reversal.",
                "content_md": """# Reversing a Linked List

The single most famous linked-list problem. Two approaches:

## Iterative (preferred — O(1) space)
```python
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next   # remember rest
        cur.next = prev  # flip pointer
        prev = cur       # advance
        cur = nxt
    return prev          # new head
```
Walk through it: at each step you flip the current node's `next` to point **backward**, then slide `prev`/`cur` forward. After the loop, `prev` is the new head.

## Recursive (O(n) stack space)
```python
def reverse_rec(head):
    if not head or not head.next:
        return head
    new_head = reverse_rec(head.next)
    head.next.next = head   # next node points back to me
    head.next = None        # I point to nothing (will be fixed by caller)
    return new_head
```

## Trace for 1 -> 2 -> 3
```
reverse_rec(1) calls reverse_rec(2) calls reverse_rec(3)
  3 has no next -> return 3 (base case)
  back in 2: 2.next.next = 2 -> 3 points to 2; 2.next=None; return 3
  back in 1: 1.next.next = 1 -> 2 points to 1; 1.next=None; return 3
Result: 3 -> 2 -> 1
```

> **Interview tip:** The iterative version is nearly always what interviewers want — mention recursion shows understanding, then implement iteratively for O(1) space.
"""
            },
            {
                "slug": "linked-lists-cycle",
                "title": "Cycle Detection (Floyd's Algorithm)",
                "duration_minutes": 14,
                "summary": "Detect a cycle with two pointers at different speeds — O(1) space.",
                "content_md": """# Cycle Detection — Floyd's Tortoise & Hare

A linked list has a **cycle** if a node's `next` points back to an earlier node, creating a loop. Traversing naively would loop forever.

## The algorithm
Use two pointers:
- **Slow** moves 1 step at a time.
- **Fast** moves 2 steps at a time.

If there's a cycle, fast will eventually **lap** slow and they'll meet. If there's no cycle, fast reaches the end.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

## Finding the cycle start
Once they meet, reset one pointer to head and move **both at speed 1**; where they meet again is the cycle's entry node.

```python
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            # met — now find entry
            p = head
            while p is not slow:
                p, slow = p.next, slow.next
            return p
    return None
```

## Why finding the entry works
Let the cycle start be at distance `a` from head, cycle length `c`, and meeting point at distance `b` into the cycle.
- slow travelled `a + b`; fast travelled `a + b + n·c` = 2(a+b) → `a = n·c - b`.
- So moving `a` steps from head lands exactly on the cycle entry (same as moving `n·c - b` from the meeting point, which is also the entry).

> **O(n) time, O(1) space** — far better than a hash-set approach, and it's the same idea behind Brent's algorithm and cycle detection in functional graphs.
"""
            },
        ],
    },
    {
        "slug": "stacks-queues",
        "title": "Stacks & Queues",
        "icon": "📚",
        "difficulty": "Beginner",
        "description": "LIFO and FIFO structures. Implement them, then use them for balanced parentheses, monotonic stacks, and BFS.",
        "lessons": [
            {
                "slug": "stacks-intro",
                "title": "Stacks — LIFO and Applications",
                "duration_minutes": 11,
                "summary": "Last-in-first-out structure; parentheses, undo, expression evaluation.",
                "content_md": """# Stacks — Last In, First Out (LIFO)

A **stack** supports two core operations: **push** (add to top) and **pop** (remove from top), both **O(1)**.

```python
stack = []
stack.append(10)   # push
stack.append(20)
stack.pop()        # 20 (LIFO)
stack[-1]          # peek -> 10
```

## Canonical applications
| Application | How |
|-------------|-----|
| **Balanced parentheses** | Push opening, pop on closing, check match |
| **Undo / Redo** | Two stacks |
| **Function call stack** | Recursion = implicit stack |
| **Expression evaluation** | Shunting-yard for infix → postfix |
| **Backtracking** | DFS, maze solving, sudoku |

## Balanced parentheses
```python
def is_balanced(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
```

> **Insight:** A stack is the natural structure whenever a problem has "most recent first" semantics — the last thing you saw is the first thing you need to resolve.
"""
            },
            {
                "slug": "monotonic-stack",
                "title": "Monotonic Stacks",
                "duration_minutes": 18,
                "summary": "Keep a stack sorted to find next greater/smaller elements in O(n).",
                "content_md": """# Monotonic Stacks

A **monotonic stack** stays sorted (increasing or decreasing) as you push. It's the key to "next greater element" problems in **O(n)**.

## Next Greater Element
For each element, find the next element to its right that is larger.

```python
def next_greater(arr):
    n = len(arr)
    res = [-1] * n
    stack = []  # holds indices, values decreasing toward bottom
    for i in range(n):
        while stack and arr[stack[-1]] < arr[i]:
            res[stack.pop()] = arr[i]
        stack.append(i)
    return res
```
`arr = [2, 1, 2, 4, 3]` → `res = [4, 2, 4, -1, -1]`

## How it works
- We keep a stack of indices whose "next greater" is **still unknown**.
- When a new element `arr[i]` arrives, it's the next greater for every smaller element on the stack — pop and resolve them.
- After the loop, anything left on the stack has no greater element → stays `-1`.

## Family of problems
| Problem | Stack type |
|---------|-----------|
| Next greater element | decreasing |
| Next smaller element | increasing |
| Largest rectangle in histogram | increasing |
| Daily temperatures | decreasing |
| Stock span | decreasing |

> **Why O(n):** Each index is pushed once and popped once, so total work is 2n. The "while" loop doesn't make it quadratic.
"""
            },
        ],
    },
    {
        "slug": "trees",
        "title": "Trees & Binary Search Trees",
        "icon": "🌳",
        "difficulty": "Intermediate",
        "description": "Hierarchical structures. Traversals, BST operations, AVL/Red-Black balancing, and common tree problems.",
        "lessons": [
            {
                "slug": "trees-intro",
                "title": "Binary Trees & Traversals",
                "duration_minutes": 16,
                "summary": "Tree terminology, DFS traversals (pre/in/post-order), BFS level-order.",
                "content_md": """# Binary Trees & Traversals

A **binary tree** is a hierarchy of nodes; each has up to two children (`left`, `right`).

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
```

## Depth-First traversals (DFS)
| Order | Visit | Mnemonic |
|-------|-------|----------|
| **Pre-order** | Node, Left, Right | **N**LR — root first |
| **In-order** | Left, Node, Right | L**N**R — sorted for BST |
| **Post-order** | Left, Right, Node | LR**N** — children first |

```python
def inorder(node):
    if not node: return
    inorder(node.left)
    visit(node)
    inorder(node.right)
```

## Breadth-First (BFS / level-order)
Use a **queue**:
```python
from collections import deque
def levelorder(root):
    if not root: return []
    q, out = deque([root]), []
    while q:
        node = q.popleft()
        out.append(node.val)
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
    return out
```

## Key facts
- **Height** of a balanced binary tree with n nodes ≈ log₂ n.
- An **in-order traversal of a BST yields sorted values.**
- **Pre + in** (or **post + in**) uniquely reconstruct a binary tree.

> **Tip:** Recursive DFS uses the call stack (O(h) space). For skewed trees, convert to an explicit stack to avoid stack overflow.
"""
            },
            {
                "slug": "bst-operations",
                "title": "Binary Search Trees",
                "duration_minutes": 18,
                "summary": "Ordered trees with O(log n) search/insert/delete when balanced.",
                "content_md": """# Binary Search Trees (BST)

A **BST** maintains the invariant: for every node, **all left-subtree values < node < all right-subtree values**. This enables **O(log n)** search/insert/delete *when balanced*.

## Search
```python
def search(node, target):
    if not node: return None
    if target == node.val: return node
    return search(node.left, target) if target < node.val else search(node.right, target)
```

## Insert
```python
def insert(node, val):
    if not node: return TreeNode(val)
    if val < node.val:
        node.left = insert(node.left, val)
    elif val > node.val:
        node.right = insert(node.right, val)
    return node
```

## Delete (three cases)
1. **No children** — just remove.
2. **One child** — replace node with its child.
3. **Two children** — replace node's value with its **in-order successor** (smallest in right subtree), then delete that successor.

```python
def delete(node, key):
    if not node: return None
    if key < node.val: node.left = delete(node.left, key)
    elif key > node.val: node.right = delete(node.right, key)
    else:
        if not node.left: return node.right
        if not node.right: return node.left
        succ = node.right
        while succ.left: succ = succ.left
        node.val = succ.val
        node.right = delete(node.right, succ.val)
    return node
```

## The balance problem
An unbalanced BST (e.g., inserting sorted data) degenerates to a linked list → **O(n)** ops. **Self-balancing trees** (AVL, Red-Black) fix this via rotations to keep height ≈ log n.

> **In-order traversal of a BST = sorted order.** This is why BSTs underlie ordered sets/maps (Java `TreeMap`, C++ `std::map`).
"""
            },
            {
                "slug": "avl-trees",
                "title": "AVL Trees (Self-Balancing)",
                "duration_minutes": 20,
                "difficulty_note": "advanced",
                "summary": "Balance factor and rotations keep BST height logarithmic.",
                "content_md": """# AVL Trees — Self-Balancing BST

An **AVL tree** keeps height ≈ log n by maintaining the **balance factor** of every node in {-1, 0, +1}, where balance factor = height(left) − height(right). When an insert/delete violates this, **rotations** restore balance.

## The four rotations
| Imbalance | Rotation to fix |
|-----------|-----------------|
| Left-Left  | Right rotate |
| Right-Right| Left rotate |
| Left-Right | Left-Right double rotate |
| Right-Left | Right-Left double rotate |

## Right rotation (LL case)
```
     z                y
    / \              / \
   y   T4   -->     x   z
  / \              / \ / \
 x  T3            T1 T2 T3 T4
```
The heavy child `y` becomes the new root of this subtree; `z` rotates down to its right.

## Why it's O(log n)
- Height stays between log₂(n) and ~1.44·log₂(n), so search/insert/delete are all **O(log n)**.
- After one insert, at most **one** rotation (single or double) restores balance — so insert is fast.
- After a delete, rotations may cascade up the path (still O(log n) total).

## Balance factor check
```python
def balance(node):
    return height(node.left) - height(node.right)

# Rebalance if balance > 1 or < -1, choosing rotation by where the heavy grandchild is.
```

> AVL is **strictly balanced** (height diff ≤ 1), giving faster lookups than Red-Black trees but slightly slower inserts (more rotations). Good for read-heavy workloads.
"""
            },
        ],
    },
    {
        "slug": "heaps",
        "title": "Heaps & Priority Queues",
        "icon": "⛰️",
        "difficulty": "Intermediate",
        "description": "Complete binary trees satisfying the heap property. Master heapify, heap sort, and the top-K pattern.",
        "lessons": [
            {
                "slug": "heaps-intro",
                "title": "Binary Heaps",
                "duration_minutes": 16,
                "summary": "Array-backed complete tree; min/max heap property; sift up/down.",
                "content_md": """# Binary Heaps

A **binary heap** is a **complete binary tree** (all levels full except possibly the last, filled left-to-right) stored in an **array**:
- Parent of index `i` is `(i-1)//2`
- Children of `i` are `2i+1`, `2i+2`

## Heap property
- **Min-heap:** parent ≤ children → root is the minimum.
- **Max-heap:** parent ≥ children → root is the maximum.

## Core operations (on a min-heap)
```python
import heapq
h = []
heapq.heappush(h, 5)   # O(log n)  — sift up
heapq.heappush(h, 2)
heapq.heappop(h)        # 2, O(log n) — sift down after moving last to root
h[0]                    # peek min -> 5
```

## Sift up / down
- **Sift up** (after push): swap with parent while smaller — O(log n).
- **Sift down** (after pop): swap root with last, then bubble down by swapping with the *smaller* child — O(log n).

## Build-heap in O(n)
Heapifying an array of n elements bottom-up is **O(n)**, not O(n log n) — because most nodes are near the bottom and sift down only a little.
```python
heapq.heapify(arr)   # O(n)
```

## Complexity
| Op            | Time |
|---------------|------|
| peek          | O(1) |
| push / pop    | O(log n) |
| build         | O(n) |
| heap sort     | O(n log n) |

> Heaps are the backbone of **priority queues**, **Dijkstra's** and **Prim's** algorithms, and the **top-K** pattern.
"""
            },
            {
                "slug": "heaps-topk",
                "title": "The Top-K Pattern",
                "duration_minutes": 13,
                "summary": "Use a size-K heap to find the K largest/smallest in O(n log k).",
                "content_md": """# The Top-K Pattern

To find the **K largest** elements in a stream/array, keep a **min-heap of size K**. For the K smallest, use a max-heap of size K.

## K largest elements
```python
import heapq
def top_k_largest(arr, k):
    h = []
    for x in arr:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)   # evict the smallest of the K+1
    return h  # the K largest (root is the K-th largest)
```

## Why it's efficient
- Heap size stays at K, so each push/pop is **O(log k)**.
- Over n elements: **O(n log k)** — when k ≪ n, much better than sorting (O(n log n)).

## Variants
| Problem | Heap |
|---------|------|
| K largest | min-heap, size k |
| K smallest | max-heap, size k (or negate) |
| K closest points to origin | max-heap by distance |
| K most frequent elements | min-heap by frequency |
| Merge K sorted lists | min-heap of (head, list) |

## Merge K sorted lists (classic)
```python
def merge_k(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, li, idx = heapq.heappop(h)
        out.append(val)
        if idx + 1 < len(lists[li]):
            heapq.heappush(h, (lists[li][idx+1], li, idx+1))
    return out
```

> **Interview heuristic:** "K largest/smallest/frequent/closest" → reach for a heap of size K, not a full sort.
"""
            },
        ],
    },
    {
        "slug": "hashing",
        "title": "Hash Tables & Hashing",
        "icon": "#️⃣",
        "difficulty": "Beginner",
        "description": "O(1) average-case lookups via hash functions. Collision resolution, load factor, and the map/set abstraction.",
        "lessons": [
            {
                "slug": "hashing-intro",
                "title": "Hash Maps & Sets",
                "duration_minutes": 14,
                "summary": "Hash function, buckets, O(1) average ops, and collision handling.",
                "content_md": """# Hash Maps & Sets

A **hash table** maps keys to array slots via a **hash function**, achieving **O(1) average** insert/lookup/delete.

## How it works
1. Compute `h = hash(key)`.
2. Map to a bucket: `index = h % table_size`.
3. Store the key-value in that bucket.

```python
freq = {}
for word in words:
    freq[word] = freq.get(word, 0) + 1   # O(1) average
```

## Collisions
Two keys can hash to the same bucket. Two resolution strategies:
- **Chaining:** each bucket holds a linked list (or list) of entries.
- **Open addressing:** probe for the next free slot (linear/quadratic probing, double hashing).

## Load factor & resizing
- **Load factor α = n / m** (entries / buckets).
- When α exceeds a threshold (≈0.75), **rehash** into a larger table to keep operations O(1).
- Without resizing, chaining degrades to O(n) when many keys collide.

## Complexity
| Case | Op |
|------|----|
| Average | O(1) |
| Worst (all collide) | O(n) |

## Sets = maps without values
A **hash set** stores only keys — perfect for "have I seen this?" checks (dedup, two-sum lookup).

> **Python dict/set are hash tables.** Keys must be **hashable** (immutable: int, str, tuple-of-hashables). Lists and dicts aren't hashable because they're mutable.
"""
            },
        ],
    },
    {
        "slug": "graphs",
        "title": "Graphs",
        "icon": "🕸️",
        "difficulty": "Intermediate",
        "description": "Vertices and edges. Representations, BFS/DFS traversal, shortest paths (Dijkstra), and minimum spanning trees.",
        "lessons": [
            {
                "slug": "graphs-intro",
                "title": "Graph Representations & Traversal",
                "duration_minutes": 17,
                "summary": "Adjacency list vs matrix; BFS for shortest unweighted path; DFS.",
                "content_md": """# Graph Representations & Traversal

A **graph** G = (V, E) has **vertices** and **edges**. Edges may be **directed** or **undirected**, **weighted** or **unweighted**.

## Representations
| Representation | Space | Edge check | Iterate neighbors |
|----------------|-------|-----------|-------------------|
| Adjacency list | O(V+E) | O(degree) | O(degree) |
| Adjacency matrix | O(V²) | O(1) | O(V) |

**Adjacency list** (usually best — sparse-friendly):
```python
graph = {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}
```

## BFS — shortest path in unweighted graphs
```python
from collections import deque
def bfs(graph, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```
BFS explores in layers — the first time you reach a node is via the **fewest edges**.

## DFS — exploration & connectivity
```python
def dfs(graph, u, seen=None):
    if seen is None: seen = set()
    seen.add(u)
    for v in graph[u]:
        if v not in seen:
            dfs(graph, v, seen)
    return seen
```
DFS goes deep first. Use it for **connected components, cycle detection, topological sort, finding bridges/articulation points**.

## BFS vs DFS
| | BFS | DFS |
|--|-----|-----|
| Data structure | Queue | Stack/recursion |
| Finds shortest (unweighted) | ✅ | ❌ |
| Space (worst) | O(V) wide | O(V) deep |
| Use for | shortest path, levels | topo sort, components, cycles |

> **Rule of thumb:** Need shortest path in an unweighted graph → BFS. Need to explore structure / detect cycles / topologically sort → DFS.
"""
            },
            {
                "slug": "dijkstra",
                "title": "Dijkstra's Shortest Path",
                "duration_minutes": 19,
                "summary": "Greedy single-source shortest paths for non-negative weights using a priority queue.",
                "content_md": """# Dijkstra's Algorithm

Finds **shortest paths from a source to all vertices** in a graph with **non-negative edge weights**. Greedy + min-heap.

## Algorithm
1. Set `dist[source] = 0`, all others `∞`.
2. Push `(0, source)` onto a min-heap.
3. Pop the closest unvisited node `u`. For each neighbor `v` with weight `w`:
   - If `dist[u] + w < dist[v]`, update and push `(dist[v], v)`.
4. Repeat until the heap is empty.

```python
import heapq
def dijkstra(graph, source):
    dist = {v: float('inf') for v in graph}
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue          # stale entry
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist
```

## Complexity
- With a binary heap: **O((V + E) log V)**.
- With a Fibonacci heap: O(E + V log V).

## Important constraints
- ❌ **Does not work with negative weights.** Use **Bellman-Ford** instead (O(V·E)) — it also detects negative cycles.
- For **all-pairs** shortest paths, use **Floyd-Warshall** (O(V³)).

## The stale-entry trick
We may push the same node multiple times with decreasing distances; the `if d > dist[u]: continue` line skips outdated entries so each node is processed once.

> **Applications:** GPS routing, network routing protocols (OSPF), flight scheduling, and — with a twist — A* search for goal-directed pathfinding.
"""
            },
            {
                "slug": "topological-sort",
                "title": "Topological Sort",
                "duration_minutes": 15,
                "summary": "Order DAG nodes so every edge points forward; Kahn's & DFS approaches.",
                "content_md": """# Topological Sort

A **topological ordering** of a **DAG** (directed acyclic graph) lists vertices so that for every edge u→v, **u comes before v**. Used for task scheduling, build systems, course prerequisites.

## Two algorithms

### 1. DFS-based
Run DFS; **prepend** each node to the output when you finish it (post-order, reversed).
```python
def topo_dfs(graph, n):
    seen, order = set(), []
    def visit(u):
        if u in seen: return
        seen.add(u)
        for v in graph[u]:
            visit(v)
        order.append(u)            # post-order
    for u in range(n):
        visit(u)
    return order[::-1]             # reverse post-order
```

### 2. Kahn's algorithm (BFS via in-degrees)
Repeatedly remove nodes with **in-degree 0**.
```python
from collections import deque
def topo_kahn(graph, n, indeg):
    q = deque([u for u in range(n) if indeg[u] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None  # None => cycle
```

## Detecting cycles
- **Kahn's:** if the output has fewer than n nodes, a cycle exists (some nodes never reach in-degree 0).
- **DFS:** detect a back edge during traversal (a neighbor that's on the current recursion stack).

## Unique ordering?
Only if there's a Hamiltonian path (a single linear chain). Otherwise multiple valid orders exist.

> **Kahn's bonus:** it also detects cycles — making it the go-to for "can these tasks be scheduled?" (course schedule, build order) problems.
"""
            },
        ],
    },
    {
        "slug": "recursion-backtracking",
        "title": "Recursion & Backtracking",
        "icon": "🌀",
        "difficulty": "Intermediate",
        "description": "Self-referential problem solving. Master the recursive mindset, then generate combinations/permutations and solve constraint problems.",
        "lessons": [
            {
                "slug": "recursion-intro",
                "title": "Thinking Recursively",
                "duration_minutes": 14,
                "summary": "Base case + recursive case; the call stack; recursion vs iteration.",
                "content_md": """# Thinking Recursively

**Recursion** solves a problem by solving a smaller instance of the same problem. Every recursive function needs:
1. **Base case** — when to stop (smallest instance, answered directly).
2. **Recursive case** — reduce the problem and call yourself.

## Factorial — the classic
```python
def fact(n):
    if n <= 1: return 1        # base case
    return n * fact(n - 1)     # recursive case
```
Call stack: `fact(4)` → 4·fact(3) → 4·3·fact(2) → 4·3·2·fact(1) → 4·3·2·1 = 24.

## The three-step method
1. **What's the smallest input?** That's your base case.
2. **Assume your function works for smaller inputs.** (The "leap of faith.")
3. **Build the answer for n from the answer for n-1.**

## When recursion shines
- Problems defined self-referentially: trees, fractals, mathematical induction.
- **Divide and conquer:** merge sort, quick sort, binary search.
- **Backtracking:** explore choices, undo on failure.

## Recursion vs iteration
Every recursion can be rewritten as a loop with an explicit stack. Recursion is **clearer** for inherently recursive structures (trees), but uses **O(depth) stack memory** and risks stack overflow on deep calls.

## Tail recursion
If the recursive call is the **last** operation, some languages optimize it to O(1) space (tail-call optimization). Python does **not**, so deep recursion in Python needs an explicit stack or `sys.setrecursionlimit`.

> **Pitfall:** Forgetting the base case → infinite recursion → `RecursionError`. Always define the stop condition first.
"""
            },
            {
                "slug": "backtracking-intro",
                "title": "Backtracking — Generate & Prune",
                "duration_minutes": 18,
                "summary": "Explore choice trees; undo choices that don't lead to a solution.",
                "content_md": """# Backtracking

**Backtracking** is DFS over a **decision tree**: make a choice, recurse, and **undo** the choice if it doesn't lead to a solution. It's how you generate all combinations/permutations and solve constraint-satisfaction puzzles.

## Template
```python
def backtrack(path, choices):
    if is_solution(path):
        solutions.append(path[:])   # copy!
        return
    for choice in choices:
        if is_valid(choice, path):
            path.append(choice)     # choose
            backtrack(path, next_choices(choice))
            path.pop()              # un-choose (backtrack)
```

## Permutations
```python
def permute(nums):
    out = []
    def bt(path, used):
        if len(path) == len(nums):
            out.append(path[:]); return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                bt(path + [nums[i]], used)   # using + avoids manual pop
                used[i] = False
    bt([], [False]*len(nums))
    return out
```

## N-Queens (the classic)
Place N queens on an N×N board so none attack each other.
```python
def solve_n_queens(n):
    res = []
    def bt(row, cols, diag1, diag2, board):
        if row == n:
            res.append(["".join(r) for r in board]); return
        for c in range(n):
            if c in cols or row-c in diag1 or row+c in diag2: continue
            board[row][c] = 'Q'
            bt(row+1, cols|{c}, diag1|{row-c}, diag2|{row+c}, board)
            board[row][c] = '.'
    bt(0, set(), set(), set(), [['.']*n for _ in range(n)])
    return res
```

## Pruning is everything
Without pruning, backtracking is just brute force (exponential). **Prune** branches that can't possibly lead to a valid solution — e.g., in N-Queens we skip a column if it's already attacked. Good pruning turns TLE into AC.

> **Copy at capture:** Always append `path[:]` (a copy) to results — `path` is mutated as you backtrack, so storing the reference would give you a list of empty lists.
"""
            },
        ],
    },
    {
        "slug": "sorting-searching",
        "title": "Sorting & Searching",
        "icon": "🔍",
        "difficulty": "Beginner",
        "description": "Comparison sorts (merge, quick, heap), binary search, and lower bounds. The foundation of efficient algorithms.",
        "lessons": [
            {
                "slug": "sorting-comparison",
                "title": "Merge Sort & Quick Sort",
                "duration_minutes": 18,
                "summary": "Two classic divide-and-conquer sorts; trade-offs and when to use each.",
                "content_md": """# Merge Sort & Quick Sort

Both are **divide and conquer**, O(n log n), but differ in important ways.

## Merge Sort
**Divide** the array in half, sort each half, **merge** the sorted halves.
```python
def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        out.append(a[i] if a[i] <= b[j] else b[j])
        i, j = (i+1, j) if a[i] <= b[j] else (i, j+1)
    out.extend(a[i:]); out.extend(b[j:])
    return out
```
- **Stable** (preserves order of equal elements).
- **O(n log n) guaranteed**, but uses **O(n) extra space**.
- Great for **linked lists** and **external sorting** (huge data on disk).

## Quick Sort
Pick a **pivot**, partition so smaller-left / larger-right, recurse.
```python
def quick_sort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr)//2]
    left  = [x for x in arr if x < pivot]
    mid   = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)
```
- **In-place** versions use O(log n) space.
- **Average O(n log n)**, but **worst case O(n²)** (bad pivot on sorted input) — mitigate with random or median-of-three pivot.
- Typically **faster in practice** than merge sort (cache locality, no merge pass).

## Comparison
| | Merge | Quick |
|--|-------|-------|
| Worst time | O(n log n) | O(n²) |
| Avg time | O(n log n) | O(n log n) |
| Space | O(n) | O(log n) in-place |
| Stable | ✅ | ❌ (usually) |

## The lower bound
Any **comparison-based** sort needs Ω(n log n) comparisons in the worst case (decision-tree argument). To beat it, use **non-comparison sorts** like counting/radix sort when keys are bounded integers.

> **Python's `sorted()`** uses **Timsort** — a hybrid of merge sort and insertion sort, stable and O(n log n), optimized for real-world partially-ordered data.
"""
            },
            {
                "slug": "binary-search",
                "title": "Binary Search",
                "duration_minutes": 15,
                "summary": "Halve the search space each step — O(log n) on sorted/monotonic data.",
                "content_md": """# Binary Search

If the search space is **sorted** (or has a monotonic property), you can halve it each step → **O(log n)**.

## Classic: find target in sorted array
```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Lower bound / bisect (most useful variant)
Find the **first** position where you could insert `target` keeping sorted order:
```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo   # first index with arr[index] >= target
```
This single template handles: search-insert-position, first/last occurrence, count of element, etc.

## Binary search on the answer
When you can **check a candidate answer in polynomial time** and the answer space is monotonic, binary search the answer instead of the array.
- Example: "minimize the maximum subarray sum" (split array into k subarrays). `check(mid)` = "can we split into ≤ k subarrays each with sum ≤ mid?" If yes, try smaller.

## The off-by-one trap
Binary search bugs are famously subtle. Keep these invariants:
- `lo` is always a possible answer, `hi` is always exclusive (for lower-bound style), or
- `lo <= hi` with `mid ± 1` (classic style).

> **Python tip:** Use `bisect` module (`bisect_left`, `bisect_right`) — bug-free binary search in the standard library. Master the *template*, then reach for `bisect`.
"""
            },
        ],
    },
    {
        "slug": "dynamic-programming",
        "title": "Dynamic Programming",
        "icon": "🧩",
        "difficulty": "Advanced",
        "description": "Optimize recursive problems with overlapping subproblems. Memoization, tabulation, and classic DP patterns.",
        "lessons": [
            {
                "slug": "dp-intro",
                "title": "DP Fundamentals — Memoization & Tabulation",
                "duration_minutes": 20,
                "summary": "Overlapping subproblems + optimal substructure; top-down vs bottom-up.",
                "content_md": """# Dynamic Programming Fundamentals

**DP** applies when a problem has:
1. **Optimal substructure** — an optimal solution can be built from optimal solutions to subproblems.
2. **Overlapping subproblems** — the same subproblems recur (so caching pays off).

## Fibonacci — the gateway
Naive recursion is **O(2ⁿ)** because it recomputes the same values over and over.
```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)   # exponential!
```

### Top-down: memoization
Cache results in a dictionary.
```python
from functools import lru_cache
@lru_cache(None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)   # now O(n)
```

### Bottom-up: tabulation
Fill a table from smallest to largest.
```python
def fib(n):
    dp = [0, 1] + [0]*(n-1)
    for i in range(2, n+1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]   # O(n) time, O(n) space
```
Space-optimized (only need last two):
```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a       # O(n) time, O(1) space
```

## Top-down vs bottom-up
| | Memoization (top-down) | Tabulation (bottom-up) |
|--|----------------------|------------------------|
| Direction | big → small | small → big |
| Stack | O(n) recursion | none |
| Computes | only needed states | all states |
| Ease | closer to recurrence | must order states |

## The DP recipe
1. **Define the state** clearly: `dp[i] = ?` (or `dp[i][j] = ?`).
2. **Write the recurrence** — how does `dp[i]` depend on smaller states?
3. **Identify base cases.**
4. **Choose top-down or bottom-up.**
5. **(Optional) optimize space** — usually only the last row/layer matters.

> **First step to mastering DP:** always write the recurrence *before* coding. If you can't express the state and transition, no amount of code will help.
"""
            },
            {
                "slug": "dp-knapsack",
                "title": "0/1 Knapsack & Variants",
                "duration_minutes": 19,
                "summary": "The quintessential DP; capacity-constrained selection with weight/value.",
                "content_md": """# 0/1 Knapsack

Given n items each with weight `w[i]` and value `v[i]`, and a knapsack of capacity `W`, choose a subset to **maximize total value** without exceeding capacity. "0/1" = each item is taken or not.

## State & recurrence
`dp[i][c]` = max value using items `0..i-1` with capacity `c`.
```
dp[i][c] = max(
    dp[i-1][c],                 # don't take item i
    dp[i-1][c - w[i]] + v[i]    # take item i (if c >= w[i])
)
```
Base: `dp[0][*] = 0`.

## Bottom-up
```python
def knapsack(w, v, W):
    n = len(w)
    dp = [[0]*(W+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for c in range(W+1):
            dp[i][c] = dp[i-1][c]
            if c >= w[i-1]:
                dp[i][c] = max(dp[i][c], dp[i-1][c-w[i-1]] + v[i-1])
    return dp[n][W]
```
**O(nW)** time and space.

## Space optimization to O(W)
Since each row depends only on the previous, keep a 1-D array — but iterate capacity **backwards** to avoid reusing an item:
```python
dp = [0]*(W+1)
for i in range(n):
    for c in range(W, w[i]-1, -1):   # backwards!
        dp[c] = max(dp[c], dp[c-w[i]] + v[i])
return dp[W]
```

## The knapsack family
| Variant | Change |
|---------|--------|
| Unbounded knapsack | iterate `c` **forward** (items reusable) |
| Subset sum | "value" = weight, ask if `dp[W] == W` |
| Partition equal subset sum | subset sum with W = total/2 |
| Coin change (min coins) | unbounded; track count not value |

> **Key trick — direction of the inner loop:** backwards = 0/1 (use item once); forwards = unbounded (reuse item). This single distinction governs the whole knapsack family.
"""
            },
            {
                "slug": "dp-lcs",
                "title": "Longest Common Subsequence",
                "duration_minutes": 16,
                "summary": "2-D string DP; the foundation of diff tools and edit distance.",
                "content_md": """# Longest Common Subsequence (LCS)

Given two strings, find the longest subsequence common to both (subsequence = not necessarily contiguous, but in order).

## State
`dp[i][j]` = length of LCS of `s1[0..i-1]` and `s2[0..j-1]`.

## Recurrence
```
if s1[i-1] == s2[j-1]:
    dp[i][j] = dp[i-1][j-1] + 1      # chars match, extend
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])   # skip one char
```
Base: `dp[0][*] = dp[*][0] = 0`.

## Code
```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```
**O(m·n)** time and space (space reducible to O(min(m,n)) by keeping two rows).

## Reconstructing the actual subsequence
Walk back from `dp[m][n]`: if chars matched, include it and move diagonally; otherwise move toward the larger neighbor.

## Related problems
| Problem | Relation |
|---------|----------|
| Edit distance | generalize: insert/delete/replace, each cost 1 |
| Longest common substring | require *contiguous* match → reset to 0 on mismatch |
| Shortest common supersequence | m + n − LCS |
| Diff (file comparison) | LCS of the two files' line sequences |

> **Real-world:** `git diff` and `diff` tools are essentially LCS (or the Myers diff algorithm, a graph-based optimization) over lines of text. String DP is genuinely everywhere.
"""
            },
        ],
    },
    {
        "slug": "greedy",
        "title": "Greedy Algorithms",
        "icon": "🪙",
        "difficulty": "Intermediate",
        "description": "Make the locally optimal choice at each step. When it works, when it fails, and proving correctness.",
        "lessons": [
            {
                "slug": "greedy-intro",
                "title": "Greedy Strategy & Correctness",
                "duration_minutes": 14,
                "summary": "Local optimal → global optimal; exchange argument proofs.",
                "content_md": """# Greedy Algorithms

A **greedy** algorithm builds a solution by making the **locally best choice** at each step, never reconsidering. It's fast (often O(n log n)) but **not always correct** — you must prove it yields the global optimum.

## When greedy works
Greedy is correct when the problem has:
1. **Greedy-choice property:** a locally optimal choice is part of *some* global optimum.
2. **Optimal substructure:** after a choice, the remainder is an independent subproblem.

## Example: Activity selection
Given intervals with start/end times, pick the maximum number of non-overlapping activities.
**Greedy:** always pick the activity that **ends earliest** (and doesn't overlap the last picked).
```python
def activity(intervals):
    intervals.sort(key=lambda x: x[1])   # by end time
    count, last_end = 0, -float('inf')
    for s, e in intervals:
        if s >= last_end:
            count += 1
            last_end = e
    return count
```
**Why correct:** picking an earlier-ending activity leaves the most room for the rest (exchange argument).

## Example: Huffman coding
Build a prefix-free code minimizing total encoded length by repeatedly merging the two least-frequent symbols. Greedy on a min-heap — provably optimal.

## When greedy FAILS
- **0/1 knapsack** (max value/weight ratio first can miss the optimum — e.g., capacity 50, items (10,$60),(20,$100),(30,$120): greedy picks 20+10=$160, but optimal is 30+20? Actually 30 alone=$120... let's use the canonical counterexample: capacity 10, items (6,$6) ratio 1 and (5,$5) ratio1 vs (4,$4)... the point is fractional knapsack greedy works, 0/1 does not).
- **Coin change** with arbitrary denominations (US coins 25/10/5/1 greedy works; denominations {1,3,4} with amount 6 — greedy gives 4+1+1=3 coins, optimal is 3+3=2 coins).

## Proving greedy: the exchange argument
Assume an optimal solution differs from the greedy one. Show you can **exchange** the first difference to match the greedy choice without making the solution worse — inductively, the greedy solution is optimal.

> **Discipline:** Don't *assume* greedy works because it "feels right." Counterexamples are subtle. Use the exchange argument or a matroid/exchange property to prove it, or fall back to DP.
"""
            },
        ],
    },
    {
        "slug": "graphs-advanced",
        "title": "Advanced Graph Algorithms",
        "icon": "🗺️",
        "difficulty": "Advanced",
        "description": "Minimum spanning trees (Kruskal/Prim), union-find, and network flow. The heavier graph toolkit.",
        "lessons": [
            {
                "slug": "mst-kruskal-prim",
                "title": "Minimum Spanning Trees",
                "duration_minutes": 19,
                "summary": "Kruskal (sort edges + union-find) and Prim (greedy with a heap).",
                "content_md": """# Minimum Spanning Trees (MST)

A **spanning tree** of a connected, undirected graph is a subset of edges that connects all vertices with no cycles. The **minimum** spanning tree has the smallest total edge weight.

## Kruskal's algorithm
Sort all edges by weight; add each edge if it connects two different components (no cycle). Use **Union-Find** to detect components.
```python
def kruskal(n, edges):  # edges = [(w, u, v), ...]
    edges.sort()
    uf = UnionFind(n)
    total, tree = 0, []
    for w, u, v in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            total += w
            tree.append((u, v, w))
    return total, tree
```
**O(E log E)** — dominated by the sort. Great for sparse graphs.

## Prim's algorithm
Grow the tree from an arbitrary start: always add the cheapest edge connecting the tree to a new vertex. Use a min-heap.
```python
import heapq
def prim(graph, start):  # graph[u] = [(v, w), ...]
    seen = {start}
    pq = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(pq)
    total = 0
    while pq:
        w, u, v = heapq.heappop(pq)
        if v in seen: continue
        seen.add(v); total += w
        for nv, nw in graph[v]:
            if nv not in seen:
                heapq.heappush(pq, (nw, v, nv))
    return total
```
**O(E log V)** with a binary heap. Good for dense graphs.

## Kruskal vs Prim
| | Kruskal | Prim |
|--|---------|------|
| Approach | edges, union-find | vertices, heap |
| Best for | sparse graphs | dense graphs |
| Time | O(E log E) | O(E log V) |

## Applications
- Network design (connecting cities/computers with minimum cable).
- **Cluster analysis** — remove the k-1 heaviest MST edges to get k clusters.
- Approximation algorithms for NP-hard problems (TSP, Steiner tree).

> Both are **greedy** and provably optimal via the cut property: for any cut of the graph, the lightest edge crossing it belongs to some MST.
"""
            },
            {
                "slug": "union-find",
                "title": "Union-Find (Disjoint Set Union)",
                "duration_minutes": 17,
                "summary": "Near-O(1) component queries with path compression & union by rank.",
                "content_md": """# Union-Find / Disjoint Set Union (DSU)

A data structure tracking elements partitioned into **disjoint sets**, supporting:
- `find(x)` — which set does x belong to? (returns a representative)
- `union(x, y)` — merge the sets containing x and y.

## Naive → optimized
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False          # already same set
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx               # attach smaller under larger
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True
```

## The two optimizations
1. **Path compression:** during `find`, point every node on the path directly to the root — flattens the tree.
2. **Union by rank:** always attach the shorter tree under the taller one — keeps depth small.

With both, any sequence of m operations on n elements runs in **O(m · α(n))** where α is the inverse Ackermann function — effectively **O(1) amortized** for all practical n.

## Applications
| Problem | How DSU helps |
|---------|---------------|
| Kruskal's MST | cycle check via find |
| Connected components | union edges, count distinct roots |
| Dynamic connectivity | "are x and y connected?" |
| Accounts merge | union by shared email |
| Redundant connection | the edge whose union returns False is the cycle |

## Number of connected components
```python
uf = UnionFind(n)
for u, v in edges:
    uf.union(u, v)
components = sum(uf.find(i) == i for i in range(n))
```

> **Why it's so fast:** path compression + union by rank make trees essentially flat — amortized nearly O(1) per op, making DSU one of the most efficient structures in all of algorithmics.
"""
            },
        ],
    },
]


def seed(db: Session):
    # Clear and reseed (idempotent)
    db.query(Lesson).delete()
    db.query(Topic).delete()
    db.commit()

    for ti, t in enumerate(SEED):
        topic = Topic(
            slug=t["slug"],
            title=t["title"],
            description=t["description"],
            icon=t.get("icon", "📘"),
            order_index=ti,
            difficulty=t.get("difficulty", "Beginner"),
        )
        db.add(topic)
        db.flush()  # get id
        for li, lesson in enumerate(t["lessons"]):
            db.add(Lesson(
                topic_id=topic.id,
                slug=lesson["slug"],
                title=lesson["title"],
                summary=lesson["summary"],
                content_md=lesson["content_md"],
                duration_minutes=lesson.get("duration_minutes", 10),
                order_index=li,
            ))
    db.commit()
    print(f"Seeded {len(SEED)} topics with lessons.")


if __name__ == "__main__":
    from config import SessionLocal
    seed(SessionLocal())
