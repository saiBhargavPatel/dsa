"""Seed DSA quiz questions linked to course topics."""
from sqlalchemy.orm import Session
from models import Quiz, Question

SEED = [
    {
        "topic_slug": "arrays",
        "title": "Arrays Fundamentals Quiz",
        "description": "Test your understanding of arrays, two pointers, sliding windows, and prefix sums.",
        "questions": [
            {
                "prompt": "What is the time complexity of accessing an element by index in a static array?",
                "options": ["O(n)", "O(1)", "O(log n)", "O(n log n)"],
                "correct_index": 1,
                "explanation": "Arrays store elements in contiguous memory, so the address of element i is base + i*size — a direct O(1) computation.",
            },
            {
                "prompt": "In a sorted array, the two-pointer technique for two-sum runs in:",
                "options": ["O(n²)", "O(n log n)", "O(n)", "O(1)"],
                "correct_index": 2,
                "explanation": "Each step moves one of the two pointers inward, so at most 2n steps — O(n). The array must be sorted first (O(n log n) if not already).",
            },
            {
                "prompt": "The amortized cost of append (push back) to a dynamic array that doubles when full is:",
                "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
                "correct_index": 2,
                "explanation": "Although an individual resize is O(n), doubling means resizes happen exponentially less often, averaging to O(1) per append (amortized analysis).",
            },
            {
                "prompt": "What does a prefix sum array let you compute in O(1)?",
                "options": ["The minimum of a range", "The sum of any subarray", "The median", "The sorted order"],
                "correct_index": 1,
                "explanation": "Sum of arr[l..r] = prefix[r+1] - prefix[l], computed in O(1) after O(n) preprocessing.",
            },
            {
                "prompt": "The sliding window technique requires the problem to have:",
                "options": ["Negative numbers only", "A monotonic property", "Sorted input", "Prime-number lengths"],
                "correct_index": 1,
                "explanation": "Sliding window works when expanding/contracting the window changes validity monotonically, so both pointers only move forward — O(n).",
            },
        ],
    },
    {
        "topic_slug": "linked-lists",
        "title": "Linked Lists Quiz",
        "description": "Pointers, reversal, and Floyd's cycle detection.",
        "questions": [
            {
                "prompt": "Deleting a node at the head of a singly linked list is:",
                "options": ["O(n)", "O(1)", "O(log n)", "O(n log n)"],
                "correct_index": 1,
                "explanation": "You only update head = head.next — a constant-time pointer reassignment.",
            },
            {
                "prompt": "In Floyd's cycle-detection algorithm, the fast pointer moves:",
                "options": ["1 step", "2 steps", "3 steps", "half the list length"],
                "correct_index": 1,
                "explanation": "Slow moves 1, fast moves 2 steps per iteration. If there's a cycle, fast laps slow and they meet; O(n) time, O(1) space.",
            },
            {
                "prompt": "The space complexity of recursively reversing a linked list is:",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                "correct_index": 1,
                "explanation": "Recursion uses O(n) call-stack space (one frame per node). The iterative version achieves O(1) space.",
            },
            {
                "prompt": "Which structure does a linked list NOT support efficiently?",
                "options": ["Insertion at head", "Deletion of a known node", "Random access by index", "Iteration"],
                "correct_index": 2,
                "explanation": "Reaching index i requires traversing i nodes — O(n). This is the main disadvantage versus arrays.",
            },
            {
                "prompt": "An LRU cache typically uses which combination?",
                "options": ["Array + stack", "Hash map + doubly linked list", "Heap + queue", "BST + array"],
                "correct_index": 1,
                "explanation": "A hash map gives O(1) lookup; a doubly linked list gives O(1) move-to-front and eviction at the tail.",
            },
        ],
    },
    {
        "topic_slug": "stacks-queues",
        "title": "Stacks & Queues Quiz",
        "description": "LIFO/FIFO, monotonic stacks, and applications.",
        "questions": [
            {
                "prompt": "A stack is the right data structure for:",
                "options": ["Breadth-first search", "Undo/redo operations", "Shortest path in unweighted graph", "Priority scheduling"],
                "correct_index": 1,
                "explanation": "Undo needs last-action-first — a stack's LIFO order. BFS uses a queue; priority scheduling uses a priority queue.",
            },
            {
                "prompt": "A monotonic (decreasing) stack solves which problem in O(n)?",
                "options": ["Finding the minimum", "Next greater element", "Binary search", "Dijkstra's algorithm"],
                "correct_index": 1,
                "explanation": "Keep a stack of unresolved indices (decreasing values). Each new element resolves all smaller stacked elements — each index pushed/popped once, so O(n).",
            },
            {
                "prompt": "Checking balanced parentheses requires at most:",
                "options": ["O(1) space", "O(n) space (worst case)", "O(n²) time", "Sorting first"],
                "correct_index": 1,
                "explanation": "Worst case '((((...))))' pushes all opens before matching — O(n) stack space. Time is O(n).",
            },
            {
                "prompt": "BFS uses a queue because:",
                "options": ["It needs LIFO order", "It processes nodes in the order discovered (FIFO)", "It needs priority", "It sorts edges"],
                "correct_index": 1,
                "explanation": "FIFO order means nodes are visited in increasing distance from the source — which is exactly how BFS guarantees shortest unweighted paths.",
            },
        ],
    },
    {
        "topic_slug": "trees",
        "title": "Trees & BSTs Quiz",
        "description": "Traversals, BST operations, and AVL balancing.",
        "questions": [
            {
                "prompt": "An in-order traversal of a Binary Search Tree produces values in:",
                "options": ["Random order", "Sorted (ascending) order", "Reverse order", "Level order"],
                "correct_index": 1,
                "explanation": "Visiting left, then node, then right — with left < node < right — yields ascending sorted order. This is a defining BST property.",
            },
            {
                "prompt": "Deleting a node with two children from a BST is done by replacing its value with its:",
                "options": ["Left child", "In-order successor (smallest in right subtree)", "Parent", "Root"],
                "correct_index": 1,
                "explanation": "The in-order successor is the smallest value greater than the node — replacing with it preserves the BST property, then you delete the successor (which has ≤1 child).",
            },
            {
                "prompt": "An unbalanced BST (e.g., inserting sorted data) degrades search to:",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct_index": 2,
                "explanation": "Sorted insertion creates a spine (essentially a linked list), so search/insert become O(n). Self-balancing trees (AVL, Red-Black) keep it O(log n).",
            },
            {
                "prompt": "In an AVL tree, a single right rotation fixes which imbalance?",
                "options": ["Right-Right", "Left-Left", "Right-Left", "Any case"],
                "correct_index": 1,
                "explanation": "Left-Left means the left subtree's left side is too heavy. A right rotation lifts the left child up, restoring balance.",
            },
            {
                "prompt": "Level-order traversal of a tree uses:",
                "options": ["A stack", "A queue", "Recursion only", "A heap"],
                "correct_index": 1,
                "explanation": "BFS/level-order uses a FIFO queue — enqueue children as you dequeue each node, visiting level by level.",
            },
        ],
    },
    {
        "topic_slug": "heaps",
        "title": "Heaps & Priority Queues Quiz",
        "description": "Heap operations, heap sort, and the top-K pattern.",
        "questions": [
            {
                "prompt": "Building a binary heap from an unordered array (heapify) runs in:",
                "options": ["O(n)", "O(n log n)", "O(log n)", "O(n²)"],
                "correct_index": 0,
                "explanation": "Bottom-up sift-down is O(n): most nodes are near the leaves and sift down very little. The math sums to a linear total.",
            },
            {
                "prompt": "To find the K largest elements efficiently, use:",
                "options": ["A full sort (O(n log n))", "A min-heap of size K (O(n log k))", "A stack", "Binary search"],
                "correct_index": 1,
                "explanation": "Keep a min-heap of size K; evict the smallest when overflowing. Each push/pop is O(log k), total O(n log k) — far better than sorting when k ≪ n.",
            },
            {
                "prompt": "In a min-heap stored as an array, the children of index i are at:",
                "options": ["i-1 and i+1", "2i and 2i+1", "2i+1 and 2i+2", "i//2 and i//2+1"],
                "correct_index": 2,
                "explanation": "For 0-indexed arrays: left child = 2i+1, right child = 2i+2, parent = (i-1)//2.",
            },
            {
                "prompt": "Heapsort's worst-case time complexity is:",
                "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                "correct_index": 1,
                "explanation": "Build heap O(n), then n pops each O(log n) = O(n log n). Unlike quicksort, heapsort's worst case is also O(n log n) — no degenerate input.",
            },
        ],
    },
    {
        "topic_slug": "hashing",
        "title": "Hashing Quiz",
        "description": "Hash functions, collisions, and the load factor.",
        "questions": [
            {
                "prompt": "The average-case time complexity of a hash table lookup is:",
                "options": ["O(n)", "O(1)", "O(log n)", "O(n log n)"],
                "correct_index": 1,
                "explanation": "With a good hash function and low load factor, keys distribute evenly — O(1) average. Worst case (all collide) is O(n).",
            },
            {
                "prompt": "When the load factor exceeds a threshold, a hash table should:",
                "options": ["Do nothing", "Rehash into a larger table", "Switch to a linked list", "Sort the keys"],
                "correct_index": 1,
                "explanation": "Rehashing into a bigger table redistributes entries, lowering the load factor and keeping operations O(1) on average. The cost is amortized like dynamic arrays.",
            },
            {
                "prompt": "Which is NOT a valid key for a Python dict?",
                "options": ["an integer", "a string", "a tuple of integers", "a list of integers"],
                "correct_index": 3,
                "explanation": "Lists are mutable and therefore unhashable. Tuples of hashables are hashable and valid keys. Hashability requires immutability (of the hash-relevant parts).",
            },
            {
                "prompt": "Separate chaining handles collisions by:",
                "options": ["Finding the next free slot", "Storing a list at each bucket", "Doubling the table", "Using a second hash function"],
                "correct_index": 1,
                "explanation": "Each bucket holds a linked list (or list) of all entries hashing to it. Open addressing (the alternative) probes for the next free slot.",
            },
        ],
    },
    {
        "topic_slug": "graphs",
        "title": "Graphs Quiz",
        "description": "Representations, BFS/DFS, Dijkstra, and topological sort.",
        "questions": [
            {
                "prompt": "For a sparse graph (E ≪ V²), which representation uses less space?",
                "options": ["Adjacency matrix", "Adjacency list", "Both the same", "Edge list only"],
                "correct_index": 1,
                "explanation": "Adjacency list uses O(V+E); a matrix always uses O(V²). For sparse graphs E is small, so the list wins. Matrices suit dense graphs and give O(1) edge queries.",
            },
            {
                "prompt": "BFS finds the shortest path in a graph that is:",
                "options": ["Weighted", "Unweighted", "Directed and weighted", "Cyclic only"],
                "correct_index": 1,
                "explanation": "BFS explores in layers of equal edge-count, so the first arrival at a node is via the fewest edges. For weighted graphs, use Dijkstra (non-negative) or Bellman-Ford.",
            },
            {
                "prompt": "Dijkstra's algorithm does NOT work correctly when:",
                "options": ["The graph is large", "Edges have negative weights", "The graph is directed", "There are many vertices"],
                "correct_index": 1,
                "explanation": "Dijkstra's greedy 'closest settled node' assumption breaks with negative edges. Use Bellman-Ford for negative weights (it also detects negative cycles).",
            },
            {
                "prompt": "Kahn's algorithm for topological sort can also detect:",
                "options": ["Shortest paths", "Cycles in a directed graph", "Bridges", "MST"],
                "correct_index": 1,
                "explanation": "If the output has fewer than n nodes, some nodes never reach in-degree 0 — meaning a cycle exists. This makes Kahn's ideal for 'course schedule / build order' problems.",
            },
            {
                "prompt": "The time complexity of Dijkstra with a binary heap is:",
                "options": ["O(V²)", "O((V+E) log V)", "O(V·E)", "O(E)"],
                "correct_index": 1,
                "explanation": "Each edge may cause a heap push (O(log V)), and each vertex is extracted once (O(log V)) — total O((V+E) log V).",
            },
        ],
    },
    {
        "topic_slug": "recursion-backtracking",
        "title": "Recursion & Backtracking Quiz",
        "description": "Base cases, the call stack, and pruning the search tree.",
        "questions": [
            {
                "prompt": "Every recursive function must have a:",
                "options": ["Loop", "Base case", "Global variable", "Memoization table"],
                "correct_index": 1,
                "explanation": "Without a base case, recursion never terminates → stack overflow. The base case handles the smallest input directly.",
            },
            {
                "prompt": "Why must you append a *copy* of the path when saving a backtracking solution?",
                "options": ["For performance", "Because path is mutated as you backtrack", "To save memory", "Python requires it"],
                "correct_index": 1,
                "explanation": "path is a single list you mutate (push/pop). Storing the reference would capture the final (empty) state. path[:] copies the current state at that moment.",
            },
            {
                "prompt": "What makes backtracking efficient rather than pure brute force?",
                "options": ["Memoization", "Pruning branches that can't lead to a solution", "Sorting the input", "Using a heap"],
                "correct_index": 1,
                "explanation": "Pruning skips entire subtrees of the decision tree that violate constraints early. Good pruning is often the difference between TLE and AC.",
            },
            {
                "prompt": "The space complexity of naive recursive Fibonacci is:",
                "options": ["O(1)", "O(n) call stack", "O(2ⁿ)", "O(n²)"],
                "correct_index": 1,
                "explanation": "Recursion depth is n (one frame per call down to the base case), so O(n) stack space. Time is O(2ⁿ) due to recomputation — memoization fixes the time.",
            },
        ],
    },
    {
        "topic_slug": "sorting-searching",
        "title": "Sorting & Searching Quiz",
        "description": "Merge/quick sort, binary search, and lower bounds.",
        "questions": [
            {
                "prompt": "Mergesort is which of the following? (stable / in-place)",
                "options": ["Stable and in-place", "Stable but NOT in-place (O(n) extra)", "Unstable and in-place", "Unstable and not in-place"],
                "correct_index": 1,
                "explanation": "Merging preserves the order of equal elements (stable) but needs an O(n) auxiliary array. Quicksort is typically in-place but unstable.",
            },
            {
                "prompt": "Quicksort's worst-case time complexity is:",
                "options": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
                "correct_index": 1,
                "explanation": "A consistently bad pivot (e.g., always the smallest on sorted input) gives unbalanced partitions → O(n²). Randomized or median-of-three pivots make this astronomically unlikely.",
            },
            {
                "prompt": "Binary search requires the data to be:",
                "options": ["In a linked list", "Sorted (or monotonic)", "Hashed", "Stored in a tree"],
                "correct_index": 1,
                "explanation": "Binary search halves the search space based on comparing to the middle — only valid if the data is sorted (or has a monotonic predicate).",
            },
            {
                "prompt": "The lower bound for any comparison-based sorting algorithm is:",
                "options": ["O(n)", "Ω(n log n)", "O(n²)", "O(log n)"],
                "correct_index": 1,
                "explanation": "A comparison-based sort corresponds to a decision tree with n! leaves; height ≥ log₂(n!) = Ω(n log n). Non-comparison sorts (counting/radix) can beat this for bounded keys.",
            },
            {
                "prompt": "Binary search 'on the answer' is used when:",
                "options": ["The array has duplicates", "The answer space is monotonic and checkable in polynomial time", "The data is unsorted", "You need a stable sort"],
                "correct_index": 1,
                "explanation": "If you can test 'is X achievable?' and feasibility is monotonic (once it fails for large X it keeps failing), binary search the answer instead of enumerating it.",
            },
        ],
    },
    {
        "topic_slug": "dynamic-programming",
        "title": "Dynamic Programming Quiz",
        "description": "Overlapping subproblems, memoization vs tabulation, and classic patterns.",
        "questions": [
            {
                "prompt": "DP applies when a problem has which two properties?",
                "options": ["Greedy choice + sorted input", "Optimal substructure + overlapping subproblems", "Negative weights + cycles", "Divide and conquer + randomization"],
                "correct_index": 1,
                "explanation": "Optimal substructure lets you build the optimum from subproblem optima; overlapping subproblems make caching those subproblems worthwhile. Both are required.",
            },
            {
                "prompt": "Memoized (top-down) recursion on Fibonacci changes time from O(2ⁿ) to:",
                "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
                "correct_index": 0,
                "explanation": "Each fib(k) is computed once and cached; there are n distinct subproblems, each O(1) work → O(n) total.",
            },
            {
                "prompt": "In the 0/1 knapsack space-optimized version, the capacity loop runs:",
                "options": ["Forward (0 → W) so items can be reused", "Backward (W → w[i]) so each item is used at most once", "Random order", "Only to W/2"],
                "correct_index": 1,
                "explanation": "Backward iteration ensures dp[c-w[i]] still reflects the previous row (item not yet used). Forward iteration would let an item be reused — that's the *unbounded* knapsack.",
            },
            {
                "prompt": "The LCS of two strings of lengths m and n is computed in:",
                "options": ["O(m + n)", "O(m · n)", "O(2ⁿ)", "O(min(m,n))"],
                "correct_index": 1,
                "explanation": "The DP table is (m+1)×(n+1), each cell O(1) → O(m·n). Space can be reduced to O(min(m,n)) by keeping only two rows.",
            },
            {
                "prompt": "The first step when solving a DP problem should be:",
                "options": ["Write code immediately", "Define the state and recurrence before coding", "Sort the input", "Convert to a greedy solution"],
                "correct_index": 1,
                "explanation": "If you can't express dp[i] (or dp[i][j]) and its transition clearly, code won't help. Define the state, write the recurrence, identify base cases — then code.",
            },
        ],
    },
    {
        "topic_slug": "greedy",
        "title": "Greedy Algorithms Quiz",
        "description": "Local optima, exchange arguments, and when greedy fails.",
        "questions": [
            {
                "prompt": "For the activity-selection problem, the optimal greedy choice is to pick the activity that:",
                "options": ["Starts earliest", "Is shortest", "Ends earliest", "Has highest value"],
                "correct_index": 2,
                "explanation": "Picking the earliest-ending activity leaves the most room for remaining activities. Correctness follows from an exchange argument.",
            },
            {
                "prompt": "Greedy fails for the 0/1 knapsack because:",
                "options": ["It's too slow", "Taking the best ratio now can block a better combination later", "Knapsack needs sorting", "Greedy only works on strings"],
                "correct_index": 1,
                "explanation": "Greedy-by-ratio can pick items that fill capacity suboptimally, blocking a higher-value combination. (Fractional knapsack, however, greedy does solve optimally.)",
            },
            {
                "prompt": "The standard way to *prove* a greedy algorithm correct is the:",
                "options": ["Loop invariant", "Exchange argument", "Random sampling", "Empirical testing"],
                "correct_index": 1,
                "explanation": "Assume an optimal solution differs from greedy; show you can exchange the first difference to match greedy without degrading the solution — inductively greedy is optimal.",
            },
            {
                "prompt": "Coin change with denominations {1, 3, 4} and amount 6: greedy gives how many coins?",
                "options": ["2 (3+3)", "3 (4+1+1)", "1", "6"],
                "correct_index": 1,
                "explanation": "Greedy takes 4, then 1+1 = 3 coins. Optimal is 3+3 = 2 coins. This is the classic counterexample showing greedy coin change isn't always optimal.",
            },
        ],
    },
    {
        "topic_slug": "graphs-advanced",
        "title": "Advanced Graph Algorithms Quiz",
        "description": "MST, Union-Find, and the cut property.",
        "questions": [
            {
                "prompt": "Kruskal's algorithm requires which data structure to detect cycles efficiently?",
                "options": ["A hash map", "Union-Find (DSU)", "A heap", "A segment tree"],
                "correct_index": 1,
                "explanation": "Union-Find tells you in near-O(1) whether two endpoints are already connected; if so, adding the edge would create a cycle, so skip it.",
            },
            {
                "prompt": "The amortized time per Union-Find operation with path compression and union by rank is:",
                "options": ["O(log n)", "O(n)", "O(α(n)) ≈ O(1)", "O(n log n)"],
                "correct_index": 2,
                "explanation": "Inverse Ackermann α(n) grows slower than log* n; for any practical n it's ≤ 4, so each operation is effectively O(1) amortized.",
            },
            {
                "prompt": "Prim's algorithm grows the MST by always adding:",
                "options": ["The globally cheapest edge", "The cheapest edge connecting the tree to a new vertex", "A random edge", "The heaviest edge"],
                "correct_index": 1,
                "explanation": "Prim's is greedy on the cut around the current tree: add the lightest edge crossing from visited to unvisited. Implemented with a min-heap → O(E log V).",
            },
            {
                "prompt": "The theoretical basis proving both Kruskal and Prim correct is the:",
                "options": ["Pigeonhole principle", "Cut property", "Master theorem", "Handshaking lemma"],
                "correct_index": 1,
                "explanation": "Cut property: for any cut, the lightest edge crossing it belongs to some MST. Both algorithms only ever add such edges, so their output is an MST.",
            },
        ],
    },
]


def seed(db: Session):
    db.query(Question).delete()
    db.query(Quiz).delete()
    db.commit()
    for q in SEED:
        quiz = Quiz(topic_slug=q["topic_slug"], title=q["title"], description=q.get("description"))
        db.add(quiz)
        db.flush()
        for i, ques in enumerate(q["questions"]):
            db.add(Question(
                quiz_id=quiz.id,
                prompt=ques["prompt"],
                options=ques["options"],
                correct_index=ques["correct_index"],
                explanation=ques.get("explanation"),
                order_index=i,
            ))
    db.commit()
    print(f"Seeded {len(SEED)} quizzes with questions.")


if __name__ == "__main__":
    from config import SessionLocal
    seed(SessionLocal())
