import importlib.util
import os
import random
import unittest
from collections import deque


def _load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _selected_impl_paths(here: str) -> list[str]:
    """Return a list of implementation file paths to test.

    Selection:
      - Requires env var A2_IMPLS: comma-separated file names or paths.
        Examples:
          A2_IMPLS=A2_kth_smallest_path_solution.py
          A2_IMPLS=A2_kth_smallest_path_solution.py,A2_kth_smallest_path_solution_fast.py
          A2_IMPLS=/abs/path/to/impl.py
    """
    raw = os.environ.get("A2_IMPLS", "").strip()
    if not raw:
        raise RuntimeError(
            "Set A2_IMPLS to the implementation file(s) to test, e.g. "
            "A2_IMPLS=A2_kth_smallest_path_solution.py"
        )

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    out: list[str] = []
    for p in parts:
        out.append(p if os.path.isabs(p) else os.path.join(here, p))
    return out


def _build_rooted_parent(adj, root=0):
    n = len(adj)
    parent = [-1] * n
    depth = [0] * n
    q = deque([root])
    parent[root] = -1
    depth[root] = 0
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v == parent[u]:
                continue
            parent[v] = u
            depth[v] = depth[u] + 1
            q.append(v)
    return parent, depth


def _path_nodes(u, v, parent, depth):
    # Return list of nodes on simple path u->v (inclusive), order doesn't matter for k-th.
    seen = set()
    x = u
    while x != -1:
        seen.add(x)
        x = parent[x]
    y = v
    while y not in seen:
        y = parent[y]
    lca = y

    path = []
    x = u
    while x != lca:
        path.append(x)
        x = parent[x]
    path.append(lca)
    stack = []
    y = v
    while y != lca:
        stack.append(y)
        y = parent[y]
    path.extend(reversed(stack))
    return path


def _brute_process(n, edges, values, queries):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent, depth = _build_rooted_parent(adj, 0)

    vals = list(values)
    out = []
    for q in queries:
        if q[0] == "U":
            _, u, x = q
            vals[u] = x
        else:
            _, u, v, k = q
            nodes = _path_nodes(u, v, parent, depth)
            arr = sorted(vals[t] for t in nodes)
            out.append(arr[k - 1])
    return out


class TestA2KthSmallestPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        impl_paths = _selected_impl_paths(here)
        cls.impls = []
        for p in impl_paths:
            mod_name = "a2_impl_" + os.path.splitext(os.path.basename(p))[0]
            cls.impls.append((os.path.basename(p), _load_module_from_path(mod_name, p)))

    def test_small_fixed(self):
        n = 5
        edges = [(0, 1), (1, 2), (1, 3), (3, 4)]
        values = [5, 1, 7, 3, 9]
        queries = [
            ("Q", 2, 4, 2),  # path 2-1-3-4 values [7,1,3,9] -> 3
            ("U", 1, 8),
            ("Q", 0, 2, 2),  # path 0-1-2 values [5,8,7] -> 7
            ("Q", 4, 4, 1),  # single node -> 9
        ]

        want = _brute_process(n, edges, values, queries)
        for label, impl in self.impls:
            with self.subTest(impl=label):
                got = impl.Solution().processQueries(n, edges, values, queries)
                self.assertEqual(want, got)

    def test_random_bruteforce(self):
        rng = random.Random(123456)
        for _case in range(50):
            n = rng.randint(2, 25)
            # Random tree: connect node i to random previous node.
            edges = []
            for i in range(1, n):
                p = rng.randrange(0, i)
                edges.append((i, p))
            values = [rng.randint(-20, 20) for _ in range(n)]

            # Prepare adjacency for picking valid k
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            parent, depth = _build_rooted_parent(adj, 0)

            qn = rng.randint(1, 60)
            queries = []
            for _ in range(qn):
                if rng.random() < 0.35:
                    u = rng.randrange(n)
                    x = rng.randint(-50, 50)
                    queries.append(("U", u, x))
                else:
                    u = rng.randrange(n)
                    v = rng.randrange(n)
                    nodes = _path_nodes(u, v, parent, depth)
                    k = rng.randint(1, len(nodes))
                    queries.append(("Q", u, v, k))

            want = _brute_process(n, edges, values, queries)
            for label, impl in self.impls:
                with self.subTest(impl=label, case=_case):
                    got = impl.Solution().processQueries(n, edges, values, queries)
                    self.assertEqual(want, got)


if __name__ == "__main__":
    unittest.main()
